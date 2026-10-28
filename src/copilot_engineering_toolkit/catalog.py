"""Load the installed catalog and validate its portable native destinations."""

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath, PureWindowsPath

from .errors import ToolkitError
from .resources import catalog_root

TYPES = ("agents", "skills", "prompts", "instructions", "templates", "global")
STARTER = {
    "agents": ["systems-investigator"],
    "skills": ["work-item-analysis", "change-impact-analysis"],
}


def safe_relative(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ToolkitError(f"Invalid catalog path: {value!r}")
    parts = value.split("/")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).drive:
        raise ToolkitError(f"Absolute catalog path: {value!r}")
    for part in parts:
        if (
            part in ("", ".", "..")
            or part.endswith((".", " "))
            or re.search(r'[<>:"|?*\x00-\x1f]', part)
            or PureWindowsPath(part).is_reserved()
        ):
            raise ToolkitError(f"Unsafe catalog path: {value!r}")
    return value


@dataclass(frozen=True)
class Component:
    id: str
    type: str
    tier: str
    path: str
    destinations: dict[str, str]


class Catalog:
    def __init__(self, root: Traversable | None = None) -> None:
        self.root = root if root is not None else catalog_root()
        try:
            manifest = json.loads(
                self.root.joinpath("manifest.json").read_text(encoding="utf-8")
            )
            if manifest["schema_version"] != 1 or not isinstance(
                manifest["components"], list
            ):
                raise ToolkitError("Unsupported catalog manifest schema")
            self.components: list[Component] = []
            identifiers, sources = set(), set()
            for entry in manifest["components"]:
                component = Component(**entry)
                if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", component.id):
                    raise ToolkitError(f"Invalid component ID: {component.id!r}")
                if (component.type, component.id) in identifiers:
                    raise ToolkitError(f"Duplicate component ID: {component.id}")
                identifiers.add((component.type, component.id))
                if component.type not in TYPES or component.tier not in (
                    "core",
                    "extended",
                ):
                    raise ToolkitError(f"Invalid type/tier: {component.id}")
                safe_relative(component.path)
                if not component.path.startswith(component.type + "/"):
                    raise ToolkitError(f"Source outside component type: {component.id}")
                if component.path in sources:
                    raise ToolkitError(f"Duplicate source: {component.path}")
                sources.add(component.path)
                if (
                    not isinstance(component.destinations, dict)
                    or not component.destinations
                ):
                    raise ToolkitError(f"Missing destinations: {component.id}")
                for scope, destination in component.destinations.items():
                    safe_relative(destination)
                    self._check_destination(component, scope, destination)
                # Validate every referenced resource before any installation is planned.
                if not self.read(component):
                    raise ToolkitError(f"Empty catalog source: {component.path}")
                self.components.append(component)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            raise ToolkitError(f"Invalid packaged catalog: {error}") from error

    @staticmethod
    def _check_destination(item: Component, scope: str, destination: str) -> None:
        allowed = False
        if scope == "project" and item.type in (
            "agents",
            "skills",
            "prompts",
            "instructions",
        ):
            allowed = destination.startswith(f".github/{item.type}/")
            allowed |= (
                item.type == "instructions"
                and destination == ".github/copilot-instructions.md"
            )
        elif scope == "user-cli":
            allowed = item.type in ("agents", "skills") and destination.startswith(
                item.type + "/"
            )
            allowed |= (
                item.type == "global" and destination == "copilot-instructions.md"
            )
        elif scope == "user-jetbrains":
            allowed = (
                item.type == "global"
                and destination == "global-copilot-instructions.md"
            )
        elif scope == "init":
            allowed = item.type == "templates" and destination == "AGENTS.md"
        if not allowed:
            raise ToolkitError(
                f"Unsupported destination for {item.id}: {scope}/{destination}"
            )

    def read(self, item: Component) -> bytes:
        return self.root.joinpath(*item.path.split("/")).read_bytes()

    def skill_resources(self, item: Component) -> list[tuple[str, bytes]]:
        """Include supporting resources beside SKILL.md with their relative paths."""
        root = self.root.joinpath(*item.path.split("/")[:-1])

        def walk(folder: Traversable, prefix: str = "") -> Iterator[tuple[str, bytes]]:
            for child in sorted(folder.iterdir(), key=lambda value: value.name):
                relative = safe_relative(prefix + child.name)
                if child.is_dir():
                    yield from walk(child, relative + "/")
                else:
                    yield relative, child.read_bytes()

        return list(walk(root))

    def select(
        self, selections: dict[str, list[str]], profile: str | None = None
    ) -> list[Component]:
        chosen = []
        if profile not in (None, "starter", "core"):
            raise ToolkitError(f"Unknown profile: {profile!r}; choose starter or core")
        if profile == "starter" or (profile is None and not selections):
            chosen = self.select(STARTER)
        elif profile == "core":
            chosen = [
                c
                for c in self.components
                if c.tier == "core" and c.type in ("agents", "skills")
            ]
        for kind, identifiers in selections.items():
            for identifier in identifiers:
                matches = [
                    c for c in self.components if c.type == kind and c.id == identifier
                ]
                if not matches:
                    raise ToolkitError(
                        f"Unknown {kind} component: {identifier!r}; use catalog to list IDs"
                    )
                if matches[0] not in chosen:
                    chosen.append(matches[0])
        if not chosen:
            raise ToolkitError(
                "Empty selection; choose components or --profile starter"
            )
        return chosen
