"""Offline fixture checks of installed license evidence, NOT a legal audit."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts/collect_installed_license_evidence.py"
spec = importlib.util.spec_from_file_location("archvela_installed_license_evidence", SRC)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class InstalledLicenseEvidenceTests(unittest.TestCase):
    def make_fixture(self, base: Path) -> Path:
        base.mkdir(parents=True, exist_ok=True)
        (base / "node_modules").mkdir()
        lock = {
            "name": "isolated-fixture", "lockfileVersion": 3,
            "packages": {
                "": {"name": "isolated-fixture", "version": "1.0.0"},
                "node_modules/@sample/component": {"version": "1.0.1", "license": "MIT"},
                "node_modules/without-text": {"version": "2.0.0", "license": "Apache-2.0"},
                "node_modules/optional-platform": {
                    "version": "3.0.0", "optional": True, "license": "LGPL-3.0-or-later",
                },
            },
        }
        (base / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        for name, version in (("@sample/component", "1.0.1"), ("without-text", "2.0.0")):
            pkg = base / "node_modules" / name
            pkg.mkdir(parents=True)
            (pkg / "package.json").write_text(
                json.dumps({"name": name, "version": version, "license": "MIT"}),
                encoding="utf-8",
            )
        (base / "node_modules/@sample/component/LICENSE").write_text(
            "Fixture license evidence only", encoding="utf-8",
        )
        return base

    def test_observes_text_hash_and_keeps_missing_items_unapproved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_fixture(Path(tmp) / "project")
            result = checker.inventory(root)
            self.assertEqual(result["lockfile_package_rows"], 3)
            self.assertEqual(result["installed_package_rows"], 2)
            self.assertEqual(result["optional_platform_rows_not_installed"], 1)
            self.assertEqual(result["installed_rows_without_top_level_license_or_notice"], 1)
            self.assertFalse(result["rights_cleared"])
            self.assertEqual(result["review_state"], "evidence_only_not_approved")
            file = next(x for x in result["rows"] if x["name"] == "@sample/component")
            self.assertEqual(len(file["license_notice_files"][0]["sha256"]), 64)
            self.assertEqual(file["license_notice_files"][0]["name"], "LICENSE")

    def test_required_package_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_fixture(Path(tmp) / "project")
            (root / "node_modules/without-text/package.json").unlink()
            (root / "node_modules/without-text").rmdir()
            with self.assertRaisesRegex(ValueError, "required lockfile packages"):
                checker.inventory(root)

    def test_package_version_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_fixture(Path(tmp) / "project")
            pkg = root / "node_modules/without-text/package.json"
            pkg.write_text('{"version": "99.0.0"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version differs"):
                checker.inventory(root)

    def test_unsafe_license_symlink_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_fixture(Path(tmp) / "project")
            notice = root / "node_modules/@sample/component/NOTICE"
            notice.symlink_to(root / "package-lock.json")
            with self.assertRaisesRegex(ValueError, "symlink"):
                checker.inventory(root)

    def test_license_filename_matches_notice_variants(self):
        for name in ("LICENSE", "LICENSE-MIT", "LICENCE.txt", "NOTICE.md",
                     "COPYING", "ATTRIBUTION.md", "THIRD_PARTY.txt"):
            self.assertTrue(checker.is_license_filename(name), name)
        for name in ("main.js", "README.md", "LICENSED_TOOLS.md"):
            self.assertFalse(checker.is_license_filename(name), name)


if __name__ == "__main__":
    unittest.main()
