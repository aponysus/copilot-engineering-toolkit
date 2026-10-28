"""Locate canonical checkout content or bundled wheel resources."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path


def catalog_root() -> Traversable:
    """Find content relative to this module, never the caller's working directory.

    Source and editable imports retain the ``src/package`` layout. Normal wheel
    installs use the bundled catalog; no checkout or network access is needed.
    """
    package = Path(__file__).resolve().parent
    if (
        package.parent.name == "src"
        and (package.parent.parent / "pyproject.toml").is_file()
    ):
        return package.parent.parent
    return files(__package__).joinpath("catalog")
