"""Regression tests for the real pnpm CI LICENSE/NOTICE observation ledger."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/verify_pnpm_license_ledger.py"
spec = importlib.util.spec_from_file_location("archvela_pnpm_evidence_ledger", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PnpmEvidenceLedgerTests(unittest.TestCase):
    @staticmethod
    def fixture() -> dict:
        return json.loads(mod.FILE.read_text(encoding="utf-8"))

    def test_actual_eight_archives_and_fifteen_nine_package_roots(self):
        report = mod.validate(self.fixture())
        self.assertEqual(report["artifact_archives"], 8)
        self.assertEqual(report["root_notice_gap_occurrences"], 15)
        self.assertEqual(report["distinct_package_versions"], 9)
        self.assertFalse(report["rights_cleared"])
        self.assertIn("NOT_LEGAL_CLEARANCE", report["status"])

    def test_no_fake_approval_or_missing_observations(self):
        data = self.fixture()
        for key, value in (("rights_cleared", True), ("review_status", "approved"),
                           ("root_notice_gap_occurrences", 10)):
            with self.subTest(key=key):
                changed = copy.deepcopy(data)
                changed[key] = value
                with self.assertRaises(ValueError):
                    mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["observations"].pop()
        with self.assertRaises(ValueError):
            mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["observations"][0]["registry_tarball_verified"] = True
        with self.assertRaises(ValueError):
            mod.validate(changed)

    def test_artifact_identity_and_source_cannot_be_falsified(self):
        data = self.fixture()
        changed = copy.deepcopy(data)
        changed["historical_run_evidence"][0]["artifacts"][0]["json_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "artifact identity/digest"):
            mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["historical_run_evidence"][1]["commit_sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "source commit"):
            mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["observations"][0]["version"] = "99.0.0"
        with self.assertRaises(ValueError):
            mod.validate(changed)

    def test_virtual_store_path_and_license_are_original_observations(self):
        data = self.fixture()
        changed = copy.deepcopy(data)
        changed["observations"][0]["virtual_store_path"] += "/untrusted"
        with self.assertRaisesRegex(ValueError, "path changed"):
            mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["observations"][0]["installed_license_metadata"] = "MIT"
        with self.assertRaisesRegex(ValueError, "License declaration"):
            mod.validate(changed)
        changed = copy.deepcopy(data)
        changed["observations"][0]["prior_six_package_source_lead"] = False
        with self.assertRaisesRegex(ValueError, "classification"):
            mod.validate(changed)

    def test_changed_current_pnpm_lock_invalidates_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in mod.EXPECTED_LOCKS:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            history = root / "docs/INSTALLED-LICENSE-EXCEPTIONS.json"
            history.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "docs/INSTALLED-LICENSE-EXCEPTIONS.json", history)
            self.assertEqual(mod.validate(self.fixture(), root)["root_notice_gap_occurrences"], 15)
            target = root / "tests/browser/pnpm-lock.yaml"
            target.write_bytes(target.read_bytes() + b"\\n")
            with self.assertRaisesRegex(ValueError, "pnpm lock changed"):
                mod.validate(self.fixture(), root)


if __name__ == "__main__":
    unittest.main()
