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
