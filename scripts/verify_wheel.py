"""Verify a local wheel offline in a disposable environment outside the checkout."""

import argparse
import json
import os
import subprocess
import tempfile
import venv
import zipfile
from pathlib import Path


def run(command: list[str], cwd: Path) -> str:
    """Run a check and preserve actionable output if it fails."""
    environment = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME"):
        environment.pop(key, None)
    environment["PYTHONNOUSERSITE"] = "1"
    result = subprocess.run(
        command, cwd=cwd, env=environment, capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed: {command}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def verify(wheel: Path) -> None:
    """Compare catalog bytes, install the wheel, and exercise its real entry point.

    Args:
        wheel: Locally built wheel corresponding to this source checkout.

    Raises:
        AssertionError: Packaged content or CLI behavior differs from expectations.
        RuntimeError: A subprocess check fails.
    """
    source = Path(__file__).resolve().parents[1]
    manifest = source / "manifest.json"
    components = json.loads(manifest.read_text())["components"]
    kinds = {item["type"] for item in components}
    resources = [
        manifest,
        *(
            p
            for kind in kinds
            for p in (source / kind).rglob("*")
            if p.is_file()
            and "__pycache__" not in p.parts
            and p.suffix not in {".pyc", ".pyo"}
        ),
    ]
    with zipfile.ZipFile(wheel) as archive:
        expected = {
            "copilot_engineering_toolkit/catalog/" + p.relative_to(source).as_posix(): p
            for p in resources
        }
        actual = {
            name
            for name in archive.namelist()
            if name.startswith("copilot_engineering_toolkit/catalog/")
            and not name.endswith("/")
        }
        assert actual == expected.keys(), "Wheel catalog inventory differs from source"
        for name, path in expected.items():
            assert archive.read(name) == path.read_bytes(), name
    with tempfile.TemporaryDirectory(prefix="copilot-toolkit-wheel-") as directory:
        root = Path(directory).resolve()
        (root / "manifest.json").write_text(
            "invalid unrelated catalog", encoding="utf-8"
        )
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        binary = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binary / ("python.exe" if os.name == "nt" else "python")
        cli = binary / ("copilot-toolkit.exe" if os.name == "nt" else "copilot-toolkit")
        run(
            [
                str(python),
                "-I",
                "-m",
                "pip",
                "--isolated",
                "--disable-pip-version-check",
                "install",
                "--no-index",
                "--no-deps",
                str(wheel),
            ],
            root,
        )
        probe = (
            "from copilot_engineering_toolkit.catalog import Catalog; "
            "from importlib.metadata import requires; import json; "
            "assert not requires('copilot-engineering-toolkit'); "
            "print(json.dumps({c.id: c.tier for c in Catalog().components "
            "if c.type == 'skills'}))"
        )
        skills = json.loads(run([str(python), "-I", "-c", probe], root))
        assert skills == {
            c["id"]: c["tier"] for c in components if c["type"] == "skills"
        }
        assert sum(tier == "core" for tier in skills.values()) == 8
        project = root / "project"
        project.mkdir()
        run([str(cli), "install", "project", str(project), "--dry-run"], root)
        assert not list(project.iterdir()), "Dry-run created files"
        run([str(cli), "install", "project", str(project)], root)
        assert {
            p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()
        } == {
            ".github/agents/systems-investigator.agent.md",
            ".github/skills/work-item-analysis/SKILL.md",
            ".github/skills/change-impact-analysis/SKILL.md",
        }, "Default installation must contain only the starter"
        run([str(cli), "install", "project", str(project), "--profile", "core"], root)
        run([str(cli), "init", str(project), "--template", "dotnet"], root)
        before = {
            p: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in project.rglob("*")
            if p.is_file()
        }
        run([str(cli), "install", "project", str(project), "--profile", "core"], root)
        assert before == {
            p: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in project.rglob("*")
            if p.is_file()
        }
        output = run([str(cli), "audit", "project", str(project)], root)
        assert "unresolved placeholders" in output
        assert len(list(project.glob(".github/skills/*/SKILL.md"))) == 8
        assert len(list(project.glob(".github/agents/*.agent.md"))) == 4
        optional = [
            c
            for c in components
            if c["tier"] == "extended" and c["type"] in {"agents", "skills", "prompts"}
        ]
        selection = [str(cli), "install", "project", str(project)]
        for kind in ("agents", "skills", "prompts"):
            selection.extend(
                [
                    "--" + kind,
                    ",".join(c["id"] for c in optional if c["type"] == kind),
                ]
            )
        run([*selection, "--dry-run"], root)
        assert before == {
            p: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in project.rglob("*")
            if p.is_file()
        }, "Optional preview changed existing files"
        run(selection, root)
        assert set(p for p in project.rglob("*") if p.is_file()) == before.keys() | {
            project / c["destinations"]["project"] for c in optional
        }
        for path, original in before.items():
            assert (path.read_bytes(), path.stat().st_mtime_ns) == original
        for component in optional:
            destination = project / component["destinations"]["project"]
            assert destination.read_bytes() == (source / component["path"]).read_bytes()
    print(
        "Wheel verified: exact catalog bytes, zero runtime dependencies, isolated install/init/audit, unchanged repeat install, and optional workflow selection."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    verify(args.wheel.resolve(strict=True))


if __name__ == "__main__":
    main()
