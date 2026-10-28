from pathlib import Path
import tempfile
import unittest

from copilot_engineering_toolkit.audit import audit_project, audit_user


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_audit_does_not_execute_documented_commands_or_change_files(self):
        instructions = self.root / "AGENTS.md"
        instructions.write_text("# Example\n{{PROJECT_NAME}}\nRun `touch sentinel` then `pytest`.\n")
        before = instructions.stat().st_mtime_ns
        result = "\n".join(audit_project(self.root))
        self.assertIn("unresolved placeholders", result)
        self.assertFalse((self.root / "sentinel").exists())
        self.assertEqual(instructions.stat().st_mtime_ns, before)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_metadata_name_mismatch_empty_and_duplicates(self):
        skill = self.root / ".github/skills/example/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: wrong\ndescription: ''\n---\nBody\n")
        (self.root / "AGENTS.md").write_text("same")
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "AGENTS.md").write_text("same")
        (self.root / "empty.agent.md").write_text("")
        output = "\n".join(audit_project(self.root))
        self.assertIn("name may not match", output)
        self.assertIn("nonempty description", output)
        self.assertIn("identical text", output)
        self.assertIn("empty content", output)

    def test_audit_skips_symlinked_trees_and_files(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "AGENTS.md").write_text("{{PRIVATE_TOKEN}}")
        project = self.root / "project"
        project.mkdir()
        try:
            (project / "linked").symlink_to(outside, target_is_directory=True)
            (project / "AGENTS.md").symlink_to(outside / "AGENTS.md")
        except OSError as error:
            self.skipTest(f"Symlinks unavailable: {error}")
        output = "\n".join(audit_project(project))
        self.assertNotIn("unresolved placeholders", output)
        self.assertIn("skipped", output)

    def test_user_audit_only_reads_selected_configuration_areas(self):
        # Credentials and unrelated folders must never be inspected as guidance.
        (self.root / "credentials.json").write_text("{{SECRET}}")
        hidden = self.root / "unrelated"
        hidden.mkdir()
        (hidden / "AGENTS.md").write_text("{{SECRET}}")
        output = "\n".join(audit_user({"global": self.root / "copilot-instructions.md", "agents": self.root / "agents", "skills": self.root / "skills"}))
        self.assertNotIn("unresolved placeholders", output)
        self.assertNotIn("credentials", output)

    def test_ignored_directories_and_large_files(self):
        hidden = self.root / ".git"
        hidden.mkdir()
        (hidden / "AGENTS.md").write_text("{{PRIVATE}}")
        (self.root / "AGENTS.md").write_bytes(b"x" * (1024 * 1024 + 1))
        output = "\n".join(audit_project(self.root))
        self.assertIn("1 MiB", output)
        self.assertNotIn("unresolved placeholders", output)
