"""Exercise explicit workflow installation without changing project-owned files."""

from pathlib import Path

import pytest

from copilot_engineering_toolkit.catalog import Catalog
from copilot_engineering_toolkit.cli import main


def snapshot(root: Path) -> dict[Path, tuple[bytes, int]]:
    return {
        p.relative_to(root): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize(
    ("skill", "prompt"),
    [
        ("source-behavior-documentation", "map-undocumented-system"),
        ("source-behavior-documentation", "document-subsystem"),
        ("runtime-characterization", "characterize-runtime"),
    ],
)
def test_selective_workflow_preview_and_install_preserve_existing_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], skill: str, prompt: str
) -> None:
    root = tmp_path.resolve()
    existing = {
        "AGENTS.md": b"Project-owned context\n",
        "source.py": b"VALUE = 42\n",
        ".github/prompts/local.prompt.md": b"A local task\n",
    }
    for relative, content in existing.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    before = snapshot(root)
    tree = set(root.rglob("*"))
    args = ["install", "project", str(root), "--skills", skill, "--prompts", prompt]
    assert main([*args, "--dry-run"]) == 0
    preview = capsys.readouterr().out
    assert skill in preview and prompt in preview
    assert snapshot(root) == before
    assert set(root.rglob("*")) == tree
    assert main(args) == 0
    expected = {
        Path(f".github/skills/{skill}/SKILL.md"),
        Path(f".github/prompts/{prompt}.prompt.md"),
    }
    after = snapshot(root)
    assert after.keys() == before.keys() | expected
    assert {p: after[p] for p in before} == before
    catalog = Catalog()
    for item in catalog.select({"skills": [skill], "prompts": [prompt]}):
        assert item.tier == "extended"
        if item.type == "prompts":
            assert item.destinations == {
                "project": f".github/prompts/{prompt}.prompt.md"
            }
        assert (root / item.destinations["project"]).read_bytes() == catalog.read(item)
    assert main(args) == 0
    assert snapshot(root) == after


@pytest.mark.parametrize(
    "skill", ["source-behavior-documentation", "runtime-characterization"]
)
def test_optional_skill_can_be_selected_for_cli_user_scope(
    tmp_path: Path, skill: str
) -> None:
    root = tmp_path.resolve()
    global_file = root / "copilot-instructions.md"
    global_file.write_bytes(b"Existing preferences\n")
    before = snapshot(root)
    args = [
        "install",
        "user",
        "--surface",
        "cli",
        "--home",
        str(root),
        "--skills",
        skill,
    ]
    assert main([*args, "--dry-run"]) == 0
    assert snapshot(root) == before
    assert main(args) == 0
    destination = Path(f"skills/{skill}/SKILL.md")
    after = snapshot(root)
    assert after.keys() == before.keys() | {destination}
    assert {p: after[p] for p in before} == before
    catalog = Catalog()
    (item,) = catalog.select({"skills": [skill]})
    assert item.destinations == {
        "project": f".github/skills/{skill}/SKILL.md",
        "user-cli": destination.as_posix(),
    }
    assert (root / destination).read_bytes() == catalog.read(item)


REVIEW_SELECTION = {
    "agents": ["documentation-reviewer"],
    "skills": [
        "documentation-quality-review",
        "diagram-review",
        "rendered-docs-review",
    ],
    "prompts": ["review-documentation"],
}


@pytest.mark.parametrize("scope", ["project", "user"])
def test_documentation_review_selection_is_optional_and_safe(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], scope: str
) -> None:
    root = tmp_path.resolve()
    (root / "AGENTS.md").write_bytes(b"Project-owned instructions\n")
    (root / "source.py").write_bytes(b"unchanged\n")
    catalog = Catalog()
    selection = REVIEW_SELECTION.copy()
    if scope == "user":
        selection.pop("prompts")
    selected = catalog.select(selection)
    assert len(selected) == (5 if scope == "project" else 4)
    assert all(c.tier == "extended" for c in selected)
    for profile in ("starter", "core"):
        assert not set(c.path for c in selected) & {
            c.path for c in catalog.select({}, profile)
        }
    args = ["install", scope]
    args += (
        [str(root)] if scope == "project" else ["--surface", "cli", "--home", str(root)]
    )
    for kind, identifiers in selection.items():
        args.extend(["--" + kind, ",".join(identifiers)])
        assert {c.id for c in catalog.select({kind: identifiers})} == set(identifiers)
        assert main(["catalog", "--type", kind]) == 0
        output = capsys.readouterr().out
        for identifier in identifiers:
            assert f"{identifier}\textended\t" in output
    before = snapshot(root)
    tree = set(root.rglob("*"))
    assert main([*args, "--dry-run"]) == 0
    assert snapshot(root) == before
    assert set(root.rglob("*")) == tree
    assert main(args) == 0
    after = snapshot(root)
    destination_scope = "project" if scope == "project" else "user-cli"
    expected = {Path(c.destinations[destination_scope]) for c in selected}
    assert after.keys() == before.keys() | expected
    assert {p: after[p] for p in before} == before
    for component in selected:
        assert (
            root / component.destinations[destination_scope]
        ).read_bytes() == catalog.read(component)
    assert main(args) == 0
    assert snapshot(root) == after
    if scope == "user":
        assert main([*args, "--prompts", "review-documentation"]) == 1
        assert snapshot(root) == after
    else:
        customized = root / ".github/agents/documentation-reviewer.agent.md"
        customized.write_bytes(b"Local customization\n")
        custom_snapshot = snapshot(root)
        assert main(args) == 1
        assert snapshot(root) == custom_snapshot
