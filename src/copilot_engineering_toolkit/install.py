"""Preflight, preview, and apply local writes with recoverable replacements.

Checks detect ordinary concurrent edits. They are not a sandbox against an
adversary concurrently swapping filesystem paths. Multi-file writes are not a
transaction: completed files and backups are reported if a later operation fails.
"""

import difflib
import os
import stat
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePath

from .errors import ToolkitError


@dataclass(frozen=True)
class Write:
    path: Path
    content: bytes


@dataclass(frozen=True)
class Snapshot:
    content: bytes | None
    identity: tuple[int, ...] | None
    mode: int = 0o600


@dataclass(frozen=True)
class Prepared:
    path: Path
    content: bytes
    before: Snapshot
    parents: dict[Path, tuple[int, int]]

    @property
    def unchanged(self) -> bool:
        return self.content == self.before.content


def absolute(path: str | PurePath) -> Path:
    path = Path(path).expanduser()
    if ".." in path.parts:
        raise ToolkitError(
            f"Parent traversal is not allowed: {path}; provide a direct path"
        )
    return path.absolute()


def is_link(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def directories(path: Path) -> dict[Path, tuple[int, int]]:
    """Validate every existing ancestor; never follow links or junctions."""
    result = {}
    for directory in reversed((path, *path.parents)):
        try:
            info = directory.lstat()
        except FileNotFoundError:
            continue
        if is_link(info) or not stat.S_ISDIR(info.st_mode):
            raise ToolkitError(
                f"Parent is a symlink, junction, or not a directory: {directory}"
            )
        result[directory] = (info.st_dev, info.st_ino)
    return result


def existing_root(path: Path) -> Path:
    path = absolute(path)
    directories(path)
    if not path.is_dir():
        raise ToolkitError(f"Target must be an existing directory: {path}")
    return path


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        info.st_mode,
    )


def snapshot(path: Path) -> Snapshot:
    """Read regular-file bytes and identity, or represent an absent destination.

    Raises:
        ToolkitError: The path is unsafe or changes while being read.
        OSError: Filesystem access fails.
    """
    try:
        info = path.lstat()
    except FileNotFoundError:
        return Snapshot(None, None)
    if is_link(info) or not stat.S_ISREG(info.st_mode):
        raise ToolkitError(
            f"Destination is a symlink, junction, or not a regular file: {path}"
        )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or _identity(opened) != _identity(info):
            raise ToolkitError(f"Destination changed while reading: {path}")
        content = stream.read()
        if _identity(os.fstat(stream.fileno())) != _identity(info):
            raise ToolkitError(f"Destination changed while reading: {path}")
    return Snapshot(content, _identity(info), stat.S_IMODE(info.st_mode))


def prepare(writes: list[Write]) -> list[Prepared]:
    """Validate all destinations and capture originals without writing anything.

    Conflicts with existing content remain in the result for preview; ``apply``
    decides whether replacement is authorized by its ``force`` argument.

    Args:
        writes: Proposed file contents and destinations.

    Returns:
        Snapshots used to detect edits between preflight and publication.

    Raises:
        ToolkitError: Paths overlap, are unsafe, or have unwritable parents.
        OSError: Filesystem inspection fails.
    """
    result, seen = [], set()
    for write in writes:
        path = absolute(write.path)
        key = os.path.normcase(str(path))
        if key in seen:
            raise ToolkitError(f"Duplicate destination: {path}")
        seen.add(key)
        parents = directories(path.parent)
        before = snapshot(path)
        if before.content != write.content:
            nearest = next(
                parent
                for parent in (path.parent, *path.parent.parents)
                if parent in parents
            )
            if not os.access(nearest, os.W_OK | os.X_OK):
                raise ToolkitError(f"Destination parent is not writable: {nearest}")
        result.append(Prepared(path, write.content, before, parents))
    paths = {item.path for item in result}
    for item in result:
        if any(parent in paths for parent in item.path.parents):
            raise ToolkitError(
                f"Planned file is also a destination directory: {item.path}"
            )
    return result


def preview(writes: list[Prepared]) -> str:
    lines = []
    for item in writes:
        action = (
            "Unchanged"
            if item.unchanged
            else (
                "Create" if item.before.content is None else "Replace (backup required)"
            )
        )
        lines.append(f"{action}: {item.path}\n")
        if item.unchanged:
            continue
        before = (item.before.content or b"").decode("utf-8", errors="replace")
        after = item.content.decode("utf-8", errors="replace")
        for line in difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(item.path),
            tofile=f"{item.path} (proposed)",
        ):
            lines.append(line)
            if not line.endswith("\n"):
                lines.append("\n\\ No newline at end of file\n")
    return "".join(lines)


def recheck(item: Prepared) -> None:
    parents = directories(item.path.parent)
    if any(parents.get(path) != identity for path, identity in item.parents.items()):
        raise ToolkitError(f"Destination parent changed since preflight: {item.path}")
    if snapshot(item.path) != item.before:
        raise ToolkitError(
            f"Destination changed since preflight: {item.path}; inspect and retry"
        )


def _create_parents(path: Path) -> None:
    for directory in reversed((path, *path.parents)):
        directories(directory)
        if not directory.exists():
            directory.mkdir(mode=0o700)


def _backup(item: Prepared) -> Path:
    assert item.before.content is not None, "Backups require an existing file"
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    fd, name = tempfile.mkstemp(
        prefix=f"{item.path.name}.bak.{stamp}.", dir=item.path.parent
    )
    backup = Path(name)
    with os.fdopen(fd, "wb") as stream:
        stream.write(item.before.content)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(backup, item.before.mode)
    return backup


def apply(
    writes: list[Prepared], *, force: bool = False, emit: Callable[[str], None] = print
) -> None:
    """Publish prepared files, preserving originals before explicit replacement.

    Args:
        writes: Preflight snapshots and proposed contents.
        force: Permit replacement of differing files after backup.
        emit: Receive completion and backup messages as operations finish.

    Raises:
        ToolkitError: A conflict, concurrent change, or filesystem failure stops
            installation. Completed files, directories, and backups remain;
            the operation is not a multi-file transaction.
    """
    conflicts = [
        item.path
        for item in writes
        if not item.unchanged and item.before.content is not None
    ]
    if conflicts and not force:
        raise ToolkitError(
            "Existing files differ: "
            + ", ".join(map(str, conflicts))
            + "; inspect --dry-run, then use --force for replacement with backups"
        )
    completed = 0
    try:
        # Detect all known changes before creating any directory or file.
        for item in writes:
            recheck(item)
        for item in writes:
            recheck(item)
            if item.unchanged:
                emit(f"Unchanged: {item.path}")
                continue
            _create_parents(item.path.parent)
            recheck(item)
            fd, name = tempfile.mkstemp(
                prefix=f".{item.path.name}.", dir=item.path.parent
            )
            temporary = Path(name)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(item.content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(temporary, item.before.mode)
                recheck(item)
                if item.before.content is not None:
                    backup = _backup(item)
                    emit(f"Backup: {backup}")
                    recheck(item)
                    os.replace(temporary, item.path)
                    action = "Updated"
                else:
                    # Atomic publication without overwriting a newly appeared file.
                    # Filesystems without hard-link support fail instead of falling
                    # back to a potentially destructive replacement.
                    os.link(temporary, item.path)
                    action = "Created"
                completed += 1
                emit(f"{action}: {item.path}")
            finally:
                temporary.unlink(missing_ok=True)
    except (OSError, ToolkitError) as error:
        raise ToolkitError(
            f"Installation stopped after {completed} file update(s): {error}. Completed files, created directories, and reported backups remain; inspect them before retrying. Restore originals from the reported backups if needed."
        ) from error
