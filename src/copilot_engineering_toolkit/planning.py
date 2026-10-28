"""Map selected packaged content to native files; never write while planning."""

from .errors import ToolkitError
from .install import Write, absolute, existing_root


def plan(catalog, selected, scope, *, root=None, locations=None):
    if scope in ("project", "init"):
        root = existing_root(root)
    writes, globals_ = [], []
    for item in selected:
        destination = item.destinations.get(scope)
        if destination is None:
            raise ToolkitError(f"{item.type}/{item.id} cannot be installed to {scope}; use project scope or choose supported components")
        if item.type == "global":
            globals_.append(item)
            continue
        base = root if scope in ("project", "init") else locations["root"]
        target = absolute(base).joinpath(*destination.split("/"))
        if item.type == "skills":
            for relative, content in catalog.skill_resources(item):
                writes.append(Write(target.parent.joinpath(*relative.split("/")), content))
        else:
            writes.append(Write(target, catalog.read(item)))
    if globals_:
        # Catalog order makes composition deterministic, independent of flag order.
        ordered = [item for item in catalog.components if item in globals_]
        content = b"\n\n".join(catalog.read(item).rstrip(b"\n") for item in ordered) + b"\n"
        writes.append(Write(absolute(locations["global"]), content))
    return writes
