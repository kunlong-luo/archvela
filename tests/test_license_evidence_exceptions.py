"""Freeze exact GitHub CI evidence gaps without inventing legal clearance."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_license_exceptions.py"
spec = importlib.util.spec_from_file_location("archvela_ci_license_exceptions", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RealInstalledLicenseExceptionsTests(unittest.TestCase):
    def register(self) -> dict:
        return json.loads(mod.FILE.read_text(encoding="utf-8"))

    def test_actual_four_job_immutable_evidence_and_six_unique_names(self):
        report = mod.validate(self.register())
        self.assertEqual(report["source_sha"], mod.SOURCE_SHA)
        self.assertEqual(report["lockfile_package_rows"], 283)
        self.assertEqual(report["installed_package_rows"], 118)
        self.assertEqual(report["uninstalled_optional_platform_rows"], 165)
        self.assertEqual(report["root_notice_gaps"], 10)
        self.assertEqual(report["distinct_affected_package_versions"], 6)
        self.assertFalse(report["human_review_approved"])
        self.assertIn("NOT_LEGAL_CLEARANCE", report["status"])

    def test_legal_approval_and_missing_historical_rows_are_rejected(self):
        base = self.register()
        for field, value in (("rights_cleared", True), ("review_status", "approved"),
                             ("source_commit", "a" * 40), ("security_workflow_run_id", 0)):
            with self.subTest(field=field):
                changed = copy.deepcopy(base)
                changed[field] = value
                with self.assertRaises(ValueError):
                    mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["exceptions"].pop()
        with self.assertRaisesRegex(ValueError, "10 observed"):
            mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["exceptions"][0]["review_status"] = "approved"
        with self.assertRaisesRegex(ValueError, "approved"):
            mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["exceptions"][0] = copy.deepcopy(changed["exceptions"][1])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            mod.validate(changed)

    def test_lockfile_changes_invalidate_old_artifact_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for p in mod.EXPECTED_ARTIFACTS:
                f = root / p
                f.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "docs/historical/npm-lockfiles" / p, f)
            self.assertEqual(mod.validate(self.register(), root)["root_notice_gaps"], 10)
            f = root / "examples/cinematic-site/package-lock.json"
            f.write_bytes(f.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source has changed"):
                mod.validate(self.register(), root)

    def test_falsified_version_or_license_does_not_pass(self):
        base = self.register()
        for field, value in (("version", "99.9.9"), ("declared_license", "NOASSERTION"),
                             ("optional", False)):
            with self.subTest(field=field):
                changed = copy.deepcopy(base)
                changed["exceptions"][0][field] = value
                with self.assertRaisesRegex(ValueError, "changed"):
                    mod.validate(changed)

    def test_artifact_identity_cannot_be_dropped_or_fake_approval_substituted(self):
        base = self.register()
        changed = copy.deepcopy(base)
        changed["artifacts"][0]["report_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "digest"):
            mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["artifacts"][0]["id"] = 987654321
        with self.assertRaisesRegex(ValueError, "Historical artifact"):
            mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["artifacts"][0]["report_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "Historical artifact"):
            mod.validate(changed)
        changed = copy.deepcopy(base)
        changed["artifacts"][0]["missing_root_notice"] = 0
        with self.assertRaisesRegex(ValueError, "counts"):
            mod.validate(changed)


if __name__ == "__main__":
    unittest.main()
