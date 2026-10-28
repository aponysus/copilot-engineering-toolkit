"""Bundle the root content catalog without maintaining a second source copy."""

import json
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithCatalog(build_py):
    def run(self) -> None:
        super().run()
        if self.editable_mode:
            # Editable imports read canonical files relative to their source module.
            return
        root = Path(__file__).resolve().parent
        destination = Path(self.build_lib) / "copilot_engineering_toolkit/catalog"
        if destination.resolve().is_relative_to(root / "src"):
            raise ValueError("Catalog build output must not overwrite the source tree")
        # Clear only generated catalog output so removed resources cannot survive
        # in a wheel produced by a subsequent incremental build.
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        manifest = root / "manifest.json"
        shutil.copy2(manifest, destination / "manifest.json")
        directories = {
            component["type"]
            for component in json.loads(manifest.read_text())["components"]
        }
        for name in sorted(directories):
            if name not in {
                "agents",
                "skills",
                "prompts",
                "instructions",
                "templates",
                "global",
            }:
                raise ValueError(f"Unexpected catalog directory: {name!r}")
            shutil.copytree(
                root / name,
                destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )


setup(cmdclass={"build_py": BuildWithCatalog})
