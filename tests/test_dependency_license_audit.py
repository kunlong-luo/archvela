"""Offline tests for npm-lockfile license metadata, not legal permission."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_dependency_licenses.py"
spec = importlib.util.spec_from_file_location("archvela_license_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DependencyLicenseAuditTests(unittest.TestCase):
    def test_actual_lockfiles_are_registered_but_not_cleared(self):
        result = mod.audit()
        self.assertEqual(result["lockfile_count"], 4)
        self.assertEqual(result["dependency_install_rows"], 283)
        self.assertEqual(result["manual_review_rows"], 42)
        self.assertEqual(result["missing_declared_license"], 0)
        self.assertFalse(result["reviewed_and_cleared"])
        self.assertEqual(result["rights_register_state"], "pending_human_review")
        self.assertEqual(result["licenses"]["CC-BY-4.0"], 2)
        self.assertEqual(result["licenses"]["MPL-2.0"], 12)
        self.assertEqual(result["licenses"]["LGPL-3.0-or-later"], 20)

    def test_register_cannot_fake_approval(self):
        observed = mod.collect()
        original = json.loads(mod.REGISTER.read_text(encoding="utf-8"))
        for key, value in (("status", "approved"),
                           ("rights_cleared", True),
                           ("expected_package_rows", 1),
                           ("lockfile_git_blob_sha", {})):
            with self.subTest(key=key):
                modified = dict(original)
                modified[key] = value
                with self.assertRaises(ValueError):
                    mod.verify_register(modified, observed)

    def test_flagged_record_cannot_be_deleted_or_changed(self):
        observed = mod.collect()
        original = json.loads(mod.REGISTER.read_text(encoding="utf-8"))
        changed = dict(original)
        changed["flagged_dependencies"] = [dict(row) for row in original["flagged_dependencies"]]
        changed["flagged_dependencies"].pop()
        with self.assertRaisesRegex(ValueError, "flagged_dependencies"):
            mod.verify_register(changed, observed)
        changed["flagged_dependencies"] = [dict(row) for row in original["flagged_dependencies"]]
        changed["flagged_dependencies"][0]["review_status"] = "approved"
        with self.assertRaisesRegex(ValueError, "flagged_dependencies"):
            mod.verify_register(changed, observed)
        changed["flagged_dependencies"] = [
            dict(original["flagged_dependencies"][0]), *original["flagged_dependencies"]
        ]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            mod.verify_register(changed, observed)

    def test_changed_package_version_or_declared_license_invalidates_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in mod.LOCKFILES:
                source = ROOT / rel
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
            register_path = root / "docs/DEPENDENCY-LICENSE-REVIEW.json"
            register_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(mod.REGISTER, register_path)
            self.assertEqual(mod.audit(root)["dependency_install_rows"], 283)
            target = root / mod.LOCKFILES[0]
            data = json.loads(target.read_text(encoding="utf-8"))
            key = next(k for k in data["packages"] if k)
            data["packages"][key]["license"] = "TEST-FIXTURE-UNVERIFIED"
            target.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "lockfile"):
                mod.audit(root)

    def test_missing_license_is_reported_not_treated_as_clearance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in mod.LOCKFILES:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            target = root / mod.LOCKFILES[3]
            data = json.loads(target.read_text(encoding="utf-8"))
            key = next(k for k in data["packages"] if k)
            del data["packages"][key]["license"]
            target.write_text(json.dumps(data), encoding="utf-8")
            collected = mod.collect(root)
            self.assertEqual(collected["missing_declared_license"], 1)
            self.assertTrue(any(x["license"] is None for x in collected["flagged_dependencies"]))

    def test_cli_is_offline_and_explicit_about_limits(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data["reviewed_and_cleared"])
        self.assertIn("not verified license texts", data["caveat"])


if __name__ == "__main__":
    unittest.main()
