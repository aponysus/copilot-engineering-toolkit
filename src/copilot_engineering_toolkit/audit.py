"""Bounded, read-only text diagnostics; no shell or client execution."""

import os
import re
import stat
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NoReturn

from .errors import ToolkitError
from .install import absolute, directories, existing_root, is_link, snapshot

SKIP = {
    ".git",
    ".idea",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
}
PLACEHOLDER = re.compile(r"\{\{[^{}\n]+\}\}|\[(?:TODO|TBD)\]", re.I)


def _known(name: str) -> bool:
    return name in {
        "AGENTS.md",
        "SKILL.md",
        "copilot-instructions.md",
        "global-copilot-instructions.md",
    } or name.endswith((".agent.md", ".instructions.md", ".prompt.md"))


def _walk(root: Path, findings: list[str]) -> Iterator[Path]:
    def failed(error: OSError) -> NoReturn:
        raise error

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=failed):
        directories(Path(directory))
        for name in sorted(dirs[:]):
            path = Path(directory) / name
            if name in SKIP:
                dirs.remove(name)
            elif is_link(path.lstat()) or _known(name):
                findings.append(
                    f"WARN: {path}: symlink/junction or file-shaped directory skipped"
                )
                dirs.remove(name)
        dirs.sort()
        for name in sorted(names):
            if _known(name):
                yield Path(directory) / name


def _metadata(text: str) -> dict[str, str]:
    # Deliberately a scalar-presence heuristic, not a homegrown YAML parser.
    if not text.startswith("---\n"):
        return {}
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        return {}
    header = parts[0][4:]
    fields = {}
    for match in re.finditer(r"^([\w-]+):[ \t]*(.*)$", header, re.M):
        value = match[2].strip().strip("\"'")
        if value in (">", ">-", "|", "|-"):
            rest = header[match.end() :]
            value = " ".join(re.findall(r"^ +(.+)$", rest.split("\n\n", 1)[0], re.M))
        if value and value not in ("null", "~"):
            fields[match[1]] = value
    return fields


def inspect(paths: Iterable[Path], findings: list[str]) -> list[str]:
    texts = {}
    for path in dict.fromkeys(paths):
        directories(path.parent)
        if not path.exists() and not path.is_symlink():
            findings.append(f"WARN: {path}: missing")
            continue
        info = path.lstat()
        if is_link(info) or not stat.S_ISREG(info.st_mode):
            findings.append(f"WARN: {path}: not a regular file; skipped")
            continue
        if info.st_size > 1024 * 1024:
            findings.append(f"WARN: {path}: exceeds 1 MiB diagnostic limit; skipped")
            continue
        try:
            content = snapshot(path).content
            if content is None:
                raise ToolkitError(f"File disappeared during audit: {path}; retry")
            text = content.decode("utf-8")
        except UnicodeError:
            findings.append(f"WARN: {path}: not UTF-8; skipped")
            continue
        findings.append(f"INFO: {path}: found")
        if not text.strip():
            findings.append(f"WARN: {path}: empty content")
        if PLACEHOLDER.search(text):
            findings.append(f"WARN: {path}: unresolved placeholders")
        if path.name == "AGENTS.md" and not re.search(
            r"`[^`\n{}]*(?:test|pytest|unittest|check|lint)[^`\n{}]*`", text
        ):
            findings.append(
                f"WARN: {path}: no concrete verification command detected; inspect manually"
            )
        if path.name == "SKILL.md" or path.name.endswith(
            (".agent.md", ".instructions.md")
        ):
            fields = _metadata(text)
            required = (
                ("name", "description")
                if path.name == "SKILL.md"
                else (
                    ("description",)
                    if path.name.endswith(".agent.md")
                    else ("applyTo",)
                )
            )
            for key in required:
                if not fields.get(key):
                    findings.append(
                        f"WARN: {path}: could not identify nonempty {key} metadata; inspect YAML"
                    )
            if path.name == "SKILL.md" and fields.get("name") != path.parent.name:
                findings.append(f"WARN: {path}: skill name may not match directory")
            if fields.get("model") or fields.get("tools"):
                findings.append(
                    f"WARN: {path}: model/tool settings require host-specific verification"
                )
            if (
                path.name.endswith(".agent.md")
                and fields.get("include-custom-instructions") != "true"
            ):
                findings.append(
                    f"WARN: {path}: CLI subagent repository instruction loading is not enabled"
                )
        normalized = text.strip()
        if normalized and normalized in texts:
            findings.append(
                f"WARN: {path}: identical text also occurs in {texts[normalized]}; inspect possible duplication"
            )
        texts[normalized] = path
    return findings


def audit_project(root: Path) -> list[str]:
    root = existing_root(root)
    findings = []
    paths = list(_walk(root, findings))
    if root / "AGENTS.md" not in paths:
        findings.append(f"WARN: {root / 'AGENTS.md'}: missing readable project context")
    return inspect(paths, findings)


def audit_user(locations: dict[str, Path]) -> list[str]:
    findings, paths = [], [absolute(locations["global"])]
    for kind in ("agents", "skills"):
        if kind not in locations:
            continue
        root = absolute(locations[kind])
        directories(root)
        if root.exists():
            paths.extend(_walk(root, findings))
        else:
            findings.append(f"INFO: {root}: no installed {kind} directory")
    return inspect(paths, findings)
