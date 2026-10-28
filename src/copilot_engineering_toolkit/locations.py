"""Resolve user locations without reading or changing client configuration."""

import os
from pathlib import Path
import sys

from .errors import ToolkitError


def user_locations(surface, *, home=None, global_path=None, platform=None, environ=None, user_home=None):
    platform = sys.platform if platform is None else platform
    environ = os.environ if environ is None else environ
    user_home = Path.home() if user_home is None else user_home
    path_type = type(user_home)
    if surface == "cli":
        root = home or (path_type(environ["COPILOT_HOME"]) if environ.get("COPILOT_HOME") else user_home / ".copilot")
        return {"root": root, "global": global_path or root / "copilot-instructions.md",
                "agents": root / "agents", "skills": root / "skills"}
    if surface != "jetbrains":
        raise ToolkitError(f"Unknown surface: {surface}")
    if home is not None:
        raise ToolkitError("--home is the CLI configuration root; use --global-path for JetBrains")
    if global_path is None:
        if platform == "darwin":
            global_path = user_home / ".config/github-copilot/intellij/global-copilot-instructions.md"
        elif platform == "win32" and environ.get("LOCALAPPDATA"):
            global_path = path_type(environ["LOCALAPPDATA"]) / "github-copilot/intellij/global-copilot-instructions.md"
        else:
            raise ToolkitError("JetBrains global location is unverified on this platform; use --global-path with the exact file shown by IDE Customizations")
    return {"global": global_path}
