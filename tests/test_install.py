"""Exercise preservation and failure boundaries using temporary files only."""

import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from copilot_engineering_toolkit.errors import ToolkitError
from copilot_engineering_toolkit.install import Write, apply, prepare, preview


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Resolve OS-owned aliases such as macOS /var for the test fixture only.
        self.root = Path(self.temp.name).resolve()

    def apply(self, writes, **options):
        events = []
        apply(writes, emit=events.append, **options)
        return events

    def test_preview_has_no_filesystem_side_effects(self):
        stamp = self.root.stat().st_mtime_ns
        plan = prepare([Write(self.root / "missing/file.md", "héllo\n".encode())])
        self.assertIn("+héllo", preview(plan))
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.root.stat().st_mtime_ns, stamp)

    def test_identical_install_keeps_bytes_mtime_and_permissions(self):
        path = self.root / "file"
        writes = [Write(path, b"same\r\n")]
        self.apply(prepare(writes))
        before = path.stat()
        self.apply(prepare(writes))
        self.assertEqual(path.read_bytes(), b"same\r\n")
        self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(path.stat().st_mode, before.st_mode)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_conflict_prevents_all_writes(self):
        path = self.root / "existing"
        path.write_bytes(b"custom")
        plan = prepare([Write(self.root / "new", b"new"), Write(path, b"replacement")])
        with self.assertRaisesRegex(ToolkitError, "Existing files differ"):
            self.apply(plan)
        self.assertFalse((self.root / "new").exists())
        self.assertEqual(path.read_bytes(), b"custom")

    def test_force_backs_up_exact_non_utf8_bytes_and_mode(self):
        path = self.root / "existing"
        old = b"custom\r\n\xff"
        path.write_bytes(old)
        path.chmod(0o640)
        mode = stat.S_IMODE(path.stat().st_mode)
        plan = prepare([Write(path, b"new\n")])
        self.assertIn("Replace", preview(plan))
        events = self.apply(plan, force=True)
        backup, = self.root.glob("existing.bak.*")
        self.assertEqual(backup.read_bytes(), old)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), mode)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), mode)
        self.assertEqual(path.read_bytes(), b"new\n")
        self.assertTrue(events[0].startswith("Backup:"))

    def test_later_invalid_destination_is_rejected_before_writes(self):
        (self.root / "directory").mkdir()
        with self.assertRaisesRegex(ToolkitError, "not a regular file"):
            prepare([Write(self.root / "new", b"x"), Write(self.root / "directory", b"x")])
        self.assertFalse((self.root / "new").exists())

    def test_file_parent_duplicate_and_traversal_are_rejected(self):
        (self.root / "file").write_bytes(b"x")
        cases = [
            [Write(self.root / "file/child", b"x")],
            [Write(self.root / "new", b"x"), Write(self.root / "new", b"y")],
            [Write(self.root / "../escape", b"x")],
            [Write(self.root / "parent", b"x"), Write(self.root / "parent/child", b"y")],
        ]
        for writes in cases:
            with self.subTest(writes=writes), self.assertRaises(ToolkitError):
                prepare(writes)

    def symlink(self, target, path, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            self.skipTest(f"Symlinks unavailable: {error}")

    def test_dangling_link_and_directory_link_are_rejected(self):
        link = self.root / "link"
        self.symlink(self.root / "absent", link)
        with self.assertRaises(ToolkitError):
            prepare([Write(link, b"x")])
        (self.root / "real").mkdir()
        parent = self.root / "alias"
        self.symlink(self.root / "real", parent, True)
        with self.assertRaises(ToolkitError):
            prepare([Write(parent / "file", b"x")])
        self.assertFalse((self.root / "real/file").exists())

    def test_changed_file_prevents_all_writes_after_preflight(self):
        path = self.root / "existing"
        path.write_bytes(b"old")
        plan = prepare([Write(self.root / "new", b"new"), Write(path, b"replacement")])
        path.write_bytes(b"user edit")
        with self.assertRaisesRegex(ToolkitError, "changed since preflight"):
            self.apply(plan, force=True)
        self.assertEqual(path.read_bytes(), b"user edit")
        self.assertFalse((self.root / "new").exists())

    def test_file_appearing_after_preflight_is_not_overwritten(self):
        path = self.root / "new"
        plan = prepare([Write(path, b"proposed")])
        path.write_bytes(b"concurrent")
        with self.assertRaises(ToolkitError):
            self.apply(plan)
        self.assertEqual(path.read_bytes(), b"concurrent")

    def test_edit_during_backup_is_preserved(self):
        path = self.root / "existing"
        path.write_bytes(b"old")
        def edit_on_backup(event):
            if event.startswith("Backup:"):
                path.write_bytes(b"concurrent edit")
        with self.assertRaisesRegex(ToolkitError, "changed since preflight"):
            apply(prepare([Write(path, b"new")]), force=True, emit=edit_on_backup)
        self.assertEqual(path.read_bytes(), b"concurrent edit")
        backup, = self.root.glob("existing.bak.*")
        self.assertEqual(backup.read_bytes(), b"old")

    def test_symlink_parent_introduced_after_preflight_is_rejected(self):
        parent = self.root / "missing"
        plan = prepare([Write(parent / "file", b"x")])
        outside = self.root / "outside"
        outside.mkdir()
        self.symlink(outside, parent, True)
        with self.assertRaises(ToolkitError):
            self.apply(plan)
        self.assertEqual(list(outside.iterdir()), [])

    def test_permission_failure_in_preflight(self):
        with patch("copilot_engineering_toolkit.install.os.access", return_value=False):
            with self.assertRaisesRegex(ToolkitError, "not writable"):
                prepare([Write(self.root / "file", b"x")])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_failed_replacement_keeps_original_and_backup(self):
        path = self.root / "existing"
        path.write_bytes(b"old")
        plan = prepare([Write(path, b"new")])
        with patch("copilot_engineering_toolkit.install.os.replace", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(ToolkitError, "0 file update"):
                self.apply(plan, force=True)
        self.assertEqual(path.read_bytes(), b"old")
        backup, = self.root.glob("existing.bak.*")
        self.assertEqual(backup.read_bytes(), b"old")
        self.assertFalse(list(self.root.glob(".existing.*")))

    def test_partial_failure_reports_completed_count_and_cleans_temp(self):
        actual_link = os.link
        def fail_second(source, destination):
            if destination.name == "second":
                raise OSError("unsupported publication")
            actual_link(source, destination)
        plan = prepare([Write(self.root / "first", b"1"), Write(self.root / "second", b"2")])
        with patch("copilot_engineering_toolkit.install.os.link", side_effect=fail_second):
            with self.assertRaisesRegex(ToolkitError, "1 file update"):
                self.apply(plan)
        self.assertEqual((self.root / "first").read_bytes(), b"1")
        self.assertFalse((self.root / "second").exists())
        self.assertEqual(len(list(self.root.iterdir())), 1)
