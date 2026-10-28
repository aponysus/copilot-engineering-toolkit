"""Check checkout resource lookup independently of the working directory."""

from pathlib import Path

import pytest

from copilot_engineering_toolkit import resources
from copilot_engineering_toolkit.catalog import Catalog
from copilot_engineering_toolkit.errors import ToolkitError


def test_checkout_ignores_unrelated_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = Catalog().root
    (tmp_path / "manifest.json").write_text("not a catalog", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert Catalog().root == expected
    assert len(Catalog().select({}, "starter")) == 3


def test_missing_checkout_catalog_does_not_fall_back_to_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (checkout / "pyproject.toml").write_text("", encoding="utf-8")
    module = checkout / "src/copilot_engineering_toolkit/resources.py"
    monkeypatch.setattr(resources, "__file__", str(module))
    with pytest.raises(ToolkitError, match="Invalid packaged catalog"):
        Catalog()
