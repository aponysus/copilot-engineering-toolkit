"""Verify the small default and explicit opt-in to larger selections."""

from pathlib import Path

import pytest

from copilot_engineering_toolkit.catalog import Catalog
from copilot_engineering_toolkit.cli import main
from copilot_engineering_toolkit.errors import ToolkitError


@pytest.mark.parametrize("scope", ["project", "user"])
@pytest.mark.parametrize("profile", [[], ["--profile", "starter"]])
def test_default_and_explicit_starter_copy_only_three_components(
    tmp_path: Path, scope: str, profile: list[str]
) -> None:
    root = tmp_path.resolve()
    (root / "AGENTS.md").write_text("Existing project context\n")
    (root / "copilot-instructions.md").write_text("Existing user preferences\n")
    original = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.iterdir()}
    target = (
        [str(root)] if scope == "project" else ["--surface", "cli", "--home", str(root)]
    )
    args = ["install", scope, *target, *profile]
    assert main([*args, "--dry-run"]) == 0
    assert set(root.iterdir()) == set(original)
    assert main(args) == 0
    base = root / ".github" if scope == "project" else root
    assert {p.name for p in (base / "agents").iterdir()} == {
        "systems-investigator.agent.md"
    }
    assert {p.name for p in (base / "skills").iterdir()} == {
        "work-item-analysis",
        "change-impact-analysis",
    }
    assert len([p for p in root.rglob("*") if p.is_file()]) == 5
    assert original == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in original}


def test_explicit_components_do_not_implicitly_add_starter() -> None:
    selected = Catalog().select({"skills": ["test-design"]})
    assert [(c.type, c.id) for c in selected] == [("skills", "test-design")]


def test_explicit_profile_and_components_combine_without_duplicates() -> None:
    selected = Catalog().select(
        {"skills": ["work-item-analysis", "test-design"]}, "starter"
    )
    assert {c.id for c in selected} == {
        "systems-investigator",
        "work-item-analysis",
        "change-impact-analysis",
        "test-design",
    }
    assert len(selected) == 4
    assert len(Catalog().select({}, "core")) == 12


def test_switching_from_core_to_starter_preserves_installed_content(
    tmp_path: Path,
) -> None:
    root = str(tmp_path.resolve())
    assert main(["install", "project", root, "--profile", "core"]) == 0
    before = {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    assert main(["install", "project", root]) == 0
    after = {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    assert before == after


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ToolkitError, match="Unknown profile"):
        Catalog().select({}, "everything")
