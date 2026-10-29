import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path, PurePosixPath, PureWindowsPath

from copilot_engineering_toolkit.catalog import TYPES, Catalog, safe_relative
from copilot_engineering_toolkit.cli import main
from copilot_engineering_toolkit.errors import ToolkitError
from copilot_engineering_toolkit.locations import user_locations


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_cli(self, *args: str | Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = main(list(map(str, args)))
        return result, out.getvalue(), err.getvalue()

    def test_catalog_and_paths_do_not_create_home(self) -> None:
        code, out, _ = self.run_cli("catalog", "--type", "skills")
        self.assertEqual(code, 0)
        self.assertEqual(len(out.splitlines()), 13)
        self.assertEqual(sum("\tcore\t" in line for line in out.splitlines()), 8)
        self.assertEqual(sum("\textended\t" in line for line in out.splitlines()), 5)
        home = self.root / "home"
        code, out, _ = self.run_cli("paths", "--surface", "cli", "--home", home)
        self.assertEqual(code, 0)
        self.assertIn(str(home / "skills"), out)
        self.assertFalse(home.exists())

    def test_integrated_init_install_and_audit(self) -> None:
        code, _, err = self.run_cli("init", self.root, "--template", "dotnet")
        self.assertEqual(code, 0, err)
        original = (self.root / "AGENTS.md").read_bytes()
        code, _, err = self.run_cli(
            "install", "project", self.root, "--profile", "core"
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(
            len(list((self.root / ".github/skills").glob("*/SKILL.md"))), 8
        )
        self.assertEqual(
            len(list((self.root / ".github/agents").glob("*.agent.md"))), 4
        )
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), original)
        self.assertFalse((self.root / ".github/copilot-instructions.md").exists())
        code, out, err = self.run_cli("audit", "project", self.root)
        self.assertEqual(code, 0, err)
        self.assertIn("unresolved placeholders", out)
        self.assertIn("Static diagnostics only", out)

    def test_core_user_install_does_not_change_global_preferences(self) -> None:
        global_file = self.root / "copilot-instructions.md"
        global_file.write_bytes(b"my preferences")
        code, _, err = self.run_cli(
            "install",
            "user",
            "--surface",
            "cli",
            "--home",
            self.root,
            "--profile",
            "core",
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(global_file.read_bytes(), b"my preferences")
        self.assertTrue((self.root / "agents/architect.agent.md").is_file())

    def test_selective_project_components_and_bridge(self) -> None:
        code, _, err = self.run_cli(
            "install",
            "project",
            self.root,
            "--skills",
            "test-design",
            "--instructions",
            "project-context,python",
            "--prompts",
            "review-change",
        )
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / ".github/copilot-instructions.md").is_file())
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / ".github/agents").exists())
        self.assertEqual(len(list((self.root / ".github/skills").iterdir())), 1)

    def test_dry_run_and_conflict_exit_status(self) -> None:
        code, out, err = self.run_cli("init", self.root, "--dry-run")
        self.assertEqual(code, 0, err)
        self.assertIn("+", out)
        self.assertEqual(list(self.root.iterdir()), [])
        (self.root / "AGENTS.md").write_bytes(b"mine")
        code, out, _ = self.run_cli("init", self.root, "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("-mine", out)
        code, _, _ = self.run_cli("init", self.root, "--dry-run", "--force")
        self.assertEqual(code, 0)
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), b"mine")
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_empty_unknown_and_unsupported_selection_refuse_before_writes(self) -> None:
        for args in [
            ("--skills", ""),
            ("--skills", "../escape"),
            ("--skills", "absent"),
        ]:
            with self.subTest(args=args):
                code, _, _ = self.run_cli("install", "project", self.root, *args)
                self.assertEqual(code, 1)
                self.assertEqual(list(self.root.iterdir()), [])
        code, _, _ = self.run_cli(
            "install",
            "user",
            "--surface",
            "cli",
            "--home",
            self.root,
            "--prompts",
            "review-change",
        )
        self.assertEqual(code, 1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_explicit_global_composition_and_jetbrains_override(self) -> None:
        target = self.root / "ide/preferences.md"
        code, _, err = self.run_cli(
            "install",
            "user",
            "--surface",
            "jetbrains",
            "--global-path",
            target,
            "--global",
            "preferences-optional,engineering",
        )
        self.assertEqual(code, 0, err)
        content = target.read_text()
        self.assertLess(
            content.index("# Engineering practice"),
            content.index("# Optional communication"),
        )
        self.assertFalse((self.root / "agents").exists())

    def test_missing_project_root_is_not_created(self) -> None:
        code, _, _ = self.run_cli("init", self.root / "absent")
        self.assertEqual(code, 1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_skill_supporting_resources_are_copied(self) -> None:
        catalog_root = self.root / "catalog"
        catalog_root.mkdir()
        source = Path(str(Catalog().root))
        shutil.copy2(source / "manifest.json", catalog_root / "manifest.json")
        for kind in TYPES:
            shutil.copytree(source / kind, catalog_root / kind)
        resource = catalog_root / "skills/test-design/references/example.txt"
        resource.parent.mkdir()
        resource.write_bytes(b"supporting example")
        catalog = Catalog(catalog_root)
        from copilot_engineering_toolkit.planning import plan

        writes = plan(
            catalog,
            catalog.select({"skills": ["test-design"]}),
            "project",
            root=self.root,
        )
        self.assertIn(
            self.root / ".github/skills/test-design/references/example.txt",
            [w.path for w in writes],
        )


class CatalogAndLocationTests(unittest.TestCase):
    def test_native_platform_paths_and_overrides(self) -> None:
        windows = PureWindowsPath("C:/Users/test")
        paths = user_locations(
            "jetbrains",
            platform="win32",
            environ={"LOCALAPPDATA": "C:/Users/test/AppData/Local"},
            user_home=windows,
        )
        self.assertEqual(
            paths["global"],
            windows
            / "AppData/Local/github-copilot/intellij/global-copilot-instructions.md",
        )
        mac = PurePosixPath("/Users/test")
        self.assertEqual(
            user_locations("jetbrains", platform="darwin", environ={}, user_home=mac)[
                "global"
            ],
            mac / ".config/github-copilot/intellij/global-copilot-instructions.md",
        )
        with self.assertRaisesRegex(ToolkitError, "global-path"):
            user_locations("jetbrains", platform="linux", environ={}, user_home=mac)
        paths = user_locations(
            "cli", environ={"COPILOT_HOME": "/override"}, user_home=mac
        )
        self.assertEqual(paths["root"], PurePosixPath("/override"))
        paths = user_locations(
            "cli",
            home=Path("/explicit"),
            environ={"COPILOT_HOME": "/override"},
            user_home=mac,
        )
        self.assertEqual(paths["root"], Path("/explicit"))

    def test_catalog_paths_are_portable_and_confined(self) -> None:
        for value in (
            "../x",
            "/x",
            "C:/x",
            "x\\y",
            "a/../b",
            "a//b",
            "a/CON",
            "x:stream",
            "a/space ",
        ):
            with self.subTest(value=value), self.assertRaises(ToolkitError):
                safe_relative(value)

    def test_invalid_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = json.loads(Catalog().root.joinpath("manifest.json").read_text())
            data["components"][0]["path"] = "../outside"
            (root / "manifest.json").write_text(json.dumps(data))
            with self.assertRaises(ToolkitError):
                Catalog(root)

    def test_manifest_covers_all_canonical_entrypoints(self) -> None:
        catalog = Catalog()
        paths = {c.path for c in catalog.components}
        source = Path(str(catalog.root))
        actual = {
            p.relative_to(source).as_posix()
            for kind in TYPES
            for p in (source / kind).rglob("*")
            if p.is_file() and p.suffix in (".md", ".tmpl")
        }
        self.assertEqual(paths, actual)
