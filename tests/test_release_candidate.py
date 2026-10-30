"""Release candidate is reviewable but must never silently become published."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_release_candidate.py"
SPEC = importlib.util.spec_from_file_location("archvela_release_check", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CandidatePreparationTests(unittest.TestCase):
    def test_unpublished_candidate_contract_is_structurally_valid(self):
        data = module.check()
        self.assertTrue(data["structural_checks_passed"])
        self.assertEqual(data["candidate"], "v0.1.0-alpha.1")
        self.assertEqual(data["state"], "draft_not_approved")
        self.assertFalse(data["release_created"])
        self.assertFalse(data["tag_created"])
        self.assertEqual(data["hard_gates_verified"], 0)
        self.assertGreaterEqual(len(data["hard_gates_pending"]), 5)

    def test_manifest_cannot_claim_an_unverified_owner_or_rights_approval(self):
        original = json.loads(module.CANDIDATE.read_text(encoding="utf-8"))
        for field in ("release_owner_approved", "rights_review_approved",
                      "main_protection_verified", "actual_l2_smoke_verified",
                      "final_ci_verified", "release_created", "tag_created"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                bad = dict(original)
                bad[field] = True
                path = Path(tmp) / "candidate.json"
                path.write_text(json.dumps(bad), encoding="utf-8")
                with patch.object(module, "CANDIDATE", path):
                    with self.assertRaisesRegex(ValueError, "claimed"):
                        module.check()

    def test_candidate_cannot_fake_release_sha_or_status(self):
        original = json.loads(module.CANDIDATE.read_text(encoding="utf-8"))
        for field, value in (("release_sha", "a" * 40),
                             ("state", "published")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                bad = dict(original)
                bad[field] = value
                path = Path(tmp) / "candidate.json"
                path.write_text(json.dumps(bad), encoding="utf-8")
                with patch.object(module, "CANDIDATE", path):
                    with self.assertRaises(ValueError):
                        module.check()

    def test_cli_reports_draft_and_does_not_create_release_artifacts(self):
        result = subprocess.run([sys.executable, str(SCRIPT)],
                                cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["state"], "draft_not_approved")
        self.assertNotIn("published", data["state"])
        self.assertFalse((ROOT / ".git/refs/tags/v0.1.0-alpha.1").exists())


if __name__ == "__main__":
    unittest.main()
