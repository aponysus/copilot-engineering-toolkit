"""Exercise malformed catalog entries and native destination coverage."""

import json
import shutil
from pathlib import Path

import pytest
import yaml

from copilot_engineering_toolkit.catalog import Catalog
from copilot_engineering_toolkit.cli import main
from copilot_engineering_toolkit.errors import ToolkitError


@pytest.mark.parametrize("defect", ["duplicate", "missing", "escape", "tier", "scope"])
def test_invalid_manifest_fails_before_any_installation(
    tmp_path: Path, defect: str
) -> None:
    root = tmp_path / "catalog"
    shutil.copytree(Path(str(Catalog().root)), root)
    manifest_file = root / "manifest.json"
    manifest = json.loads(manifest_file.read_text())
    item = manifest["components"][0]
    if defect == "duplicate":
        manifest["components"].append(item.copy())
    elif defect == "missing":
        (root / item["path"]).unlink()
    elif defect == "escape":
        item["destinations"]["project"] = "../outside"
    elif defect == "tier":
        item["tier"] = "unknown"
    else:
        item["destinations"]["project"] = ".git/config"
    manifest_file.write_text(json.dumps(manifest))
    with pytest.raises(ToolkitError):
        Catalog(root)


@pytest.mark.parametrize("template", ["base", "dotnet", "python", "go"])
def test_each_template_initializes_only_project_context(
    tmp_path: Path, template: str
) -> None:
    root = tmp_path.resolve()
    assert main(["init", str(root), "--template", template]) == 0
    assert [path.name for path in root.iterdir()] == ["AGENTS.md"]
    catalog = Catalog()
    selected = catalog.select({"templates": [template]})
    assert (root / "AGENTS.md").read_bytes() == catalog.read(selected[0])


@pytest.mark.parametrize(
    ("language", "extension"),
    [("csharp", "cs"), ("sql", "sql"), ("python", "py"), ("go", "go")],
)
def test_native_globs_cover_root_and_nested_files_only(
    tmp_path: Path, language: str, extension: str
) -> None:
    catalog = Catalog()
    item = catalog.select({"instructions": [language]})[0]
    frontmatter = catalog.read(item).decode().split("---", 2)[1]
    pattern = yaml.safe_load(frontmatter)["applyTo"]
    (tmp_path / "nested").mkdir()
    expected = {tmp_path / f"root.{extension}", tmp_path / f"nested/deep.{extension}"}
    for path in expected | {tmp_path / "unrelated.txt"}:
        path.touch()
    assert set(tmp_path.glob(pattern)) == expected
