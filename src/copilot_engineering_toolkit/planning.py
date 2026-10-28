"""Map selected packaged content to native files; never write while planning."""

from pathlib import Path

from .catalog import Catalog, Component
from .errors import ToolkitError
from .install import Write, absolute, existing_root


def plan(
    catalog: Catalog,
    selected: list[Component],
    scope: str,
    *,
    root: Path | None = None,
    locations: dict[str, Path] | None = None,
) -> list[Write]:
    """Build a write plan without changing the target filesystem.

    Args:
        catalog: Validated packaged content and destination mappings.
        selected: Components to copy or compose into native files.
        scope: Project, init, user-cli, or user-jetbrains destination scope.
        root: Existing target directory for project installation or scaffolding.
        locations: Resolved user paths, required for user-scoped installation.

    Returns:
        Proposed file contents and absolute destinations, ready for preflight.

    Raises:
        ToolkitError: A target is missing or a component does not support the scope.
    """
    if scope in ("project", "init"):
        if root is None:
            raise ToolkitError("Project installation requires an existing target root")
        root = existing_root(root)
    writes, globals_ = [], []
    for item in selected:
        destination = item.destinations.get(scope)
        if destination is None:
            raise ToolkitError(
                f"{item.type}/{item.id} cannot be installed to {scope}; use project scope or choose supported components"
            )
        if item.type == "global":
            globals_.append(item)
            continue
        base = root if scope in ("project", "init") else None
        if base is None:
            if locations is None or "root" not in locations:
                raise ToolkitError(
                    "User component installation requires a configuration root"
                )
            base = locations["root"]
        target = absolute(base).joinpath(*destination.split("/"))
        if item.type == "skills":
            for relative, content in catalog.skill_resources(item):
                writes.append(
                    Write(target.parent.joinpath(*relative.split("/")), content)
                )
        else:
            writes.append(Write(target, catalog.read(item)))
    if globals_:
        if locations is None or "global" not in locations:
            raise ToolkitError(
                "Global installation requires an instructions file location"
            )
        # Catalog order makes composition deterministic, independent of flag order.
        ordered = [item for item in catalog.components if item in globals_]
        content = (
            b"\n\n".join(catalog.read(item).rstrip(b"\n") for item in ordered) + b"\n"
        )
        writes.append(Write(absolute(locations["global"]), content))
    return writes
