"""Resolve user locations without reading or changing client configuration."""

import os
import sys
from collections.abc import Mapping
from pathlib import Path, PurePath

from .errors import ToolkitError


def user_locations(
    surface: str,
    *,
    home: PurePath | None = None,
    global_path: PurePath | None = None,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
    user_home: PurePath | None = None,
) -> dict[str, PurePath]:
    """Resolve configuration paths without inspecting or creating them.

    Args:
        surface: CLI or JetBrains target.
        home: Explicit CLI configuration directory, ahead of COPILOT_HOME.
        global_path: Explicit global instructions file override.
        platform: Platform identifier; defaults to the running platform.
        environ: Environment used for path overrides; defaults to os.environ.
        user_home: User home, optionally a pure path for cross-platform checks.

    Returns:
        Named destinations in the supplied home path's platform syntax.

    Raises:
        ToolkitError: The surface or location is unsupported or ambiguous.
    """
    platform = sys.platform if platform is None else platform
    environ = os.environ if environ is None else environ
    user_home = Path.home() if user_home is None else user_home
    path_type = type(user_home)
    if surface == "cli":
        root = home or (
            path_type(environ["COPILOT_HOME"])
            if environ.get("COPILOT_HOME")
            else user_home / ".copilot"
        )
        return {
            "root": root,
            "global": global_path or root / "copilot-instructions.md",
            "agents": root / "agents",
            "skills": root / "skills",
        }
    if surface != "jetbrains":
        raise ToolkitError(f"Unknown surface: {surface}")
    if home is not None:
        raise ToolkitError(
            "--home is the CLI configuration root; use --global-path for JetBrains"
        )
    if global_path is None:
        if platform == "darwin":
            global_path = (
                user_home
                / ".config/github-copilot/intellij/global-copilot-instructions.md"
            )
        elif platform == "win32" and environ.get("LOCALAPPDATA"):
            global_path = (
                path_type(environ["LOCALAPPDATA"])
                / "github-copilot/intellij/global-copilot-instructions.md"
            )
        else:
            raise ToolkitError(
                "JetBrains global location is unverified on this platform; use --global-path with the exact file shown by IDE Customizations"
            )
    return {"global": global_path}
