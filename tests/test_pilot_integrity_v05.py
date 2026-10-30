"""Integrity regression fixtures ONLY — no model, payment, or actual results."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
PIN = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
FIELDS = ("scenario_fit", "architecture_reasoning", "four_layer_split",
          "fallback_safety", "verification_plan")


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(BENCH / script), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )


class IntegrityHardeningTests(unittest.TestCase):
    def pilot(self, path, rev=PIN):
        result = run("pilot.py", "--agent", "codex", "--model", "FIXTURE-MODEL",
                     "--skill-sha", rev, "--output", path)
        return result

    def fill(self, path):
        manifest = json.loads((path / "operator-manifest.json").read_text())
        (path / "reviewer/artifacts").mkdir()
        records = []
        for row in manifest["runs"]:
            blind = row["blind_id"]
            target = path / "operator" / blind
            meta = json.loads((target / "session.template.json").read_text())
            meta.update({
                "client_version": "fixture-only",
                "started_at_utc": "2026-10-30T10:00:00Z",
                "finished_at_utc": "2026-10-30T10:01:00Z",
                "execution_status": "completed",
                "skill_discovered": row["arm"] == "archvela",
            })
            (target / "session.json").write_text(json.dumps(meta))
            response = b"FIXTURE test only, not a real model result\n"
            (path / "reviewer/artifacts" / (blind + ".response.md")).write_bytes(response)
            (path / "reviewer/artifacts" / (blind + ".run.log")).write_text("FIXTURE LOG")
            records.append({
                "blind_id": blind, "response_sha256": hashlib.sha256(response).hexdigest(),
                "reviewer": "FIXTURE", "notes": None,
                "grades": {name: 2 for name in FIELDS}
            })
        return manifest, records

    def test_invalid_git_sha_is_rejected_before_directory_created(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "pilot"
            result = self.pilot(path, rev="f" * 40 if PIN != "f" * 40 else "e" * 40)
            self.assertEqual(result.returncode, 2)
            self.assertIn("revision mismatch", result.stderr)
            self.assertFalse(path.exists())

    def test_random_ids_and_operator_only_hmac_key(self):
        with tempfile.TemporaryDirectory() as root:
            first, second = Path(root) / "a", Path(root) / "b"
            self.assertEqual(self.pilot(first).returncode, 0)
            self.assertEqual(self.pilot(second).returncode, 0)
            one = json.loads((first / "operator-manifest.json").read_text())
            two = json.loads((second / "operator-manifest.json").read_text())
            self.assertEqual(one["schema_version"], 2)
            self.assertEqual(one["skills_cli_version"], "1.7.4")
            self.assertEqual(len(one["runs"]), 4)
            self.assertTrue(all(len(row["blind_id"]) == 32 for row in one["runs"]))
            self.assertNotEqual({row["blind_id"] for row in one["runs"]},
                                {row["blind_id"] for row in two["runs"]})
            self.assertTrue((first / "operator/manifest.key").is_file())
            self.assertEqual(run("audit_pilot.py", "--study", first).returncode, 2)
            # No fabricated session files; the metadata-only audit exits missing evidence.
            for row in one["runs"]:
                self.assertFalse((first / "operator" / row["blind_id"] / "session.json").exists())

    def test_manifest_tamper_and_key_swap_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            first, second = Path(root) / "a", Path(root) / "b"
            self.assertEqual(self.pilot(first).returncode, 0)
            self.assertEqual(self.pilot(second).returncode, 0)
            manifest = json.loads((first / "operator-manifest.json").read_text())
            manifest["runs"][0]["arm"] = ("baseline" if manifest["runs"][0]["arm"] == "archvela"
                                         else "archvela")
            (first / "operator-manifest.json").write_text(json.dumps(manifest))
            self.assertIn("modified", run("preflight.py", "--study", first).stderr)
            (first / "operator-manifest.json").write_text(
                (second / "operator-manifest.json").read_text())
            self.assertIn("modified", run("preflight.py", "--study", first).stderr)

    def test_changed_response_cannot_be_scored_from_prior_review_hash(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "pilot"
            self.assertEqual(self.pilot(path).returncode, 0)
            manifest, records = self.fill(path)
            grades = Path(root) / "review.json"
            grades.write_text(json.dumps({
                "schema_version": 1, "kind": "blind_response_only_ungraded",
                "records": records,
            }))
            self.assertEqual(run("summarize_pilot.py", "--study", path, "--review", grades).returncode, 0)
            blind = manifest["runs"][0]["blind_id"]
            (path / "reviewer/artifacts" / (blind + ".response.md")).write_text(
                "FIXTURE MUTATED AFTER REVIEW")
            result = run("summarize_pilot.py", "--study", path, "--review", grades)
            self.assertEqual(result.returncode, 2)
            self.assertIn("fingerprint", result.stderr)

    def test_completed_but_undiscovered_is_not_skill_success(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "pilot"
            self.assertEqual(self.pilot(path).returncode, 0)
            manifest, records = self.fill(path)
            treatment = next(row for row in manifest["runs"] if row["arm"] == "archvela")
            meta_file = path / "operator" / treatment["blind_id"] / "session.json"
            meta = json.loads(meta_file.read_text())
            meta["skill_discovered"] = False
            meta_file.write_text(json.dumps(meta))
            grades = Path(root) / "review.json"
            grades.write_text(json.dumps({
                "schema_version": 1, "kind": "blind_response_only_ungraded",
                "records": records,
            }))
            result = run("summarize_pilot.py", "--study", path, "--review", grades)
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(result.stdout)["clients"][0]
            self.assertIsNone(record["full_study_human_delta"])
            self.assertIsNotNone(record["intention_to_treat_human_delta"])
            self.assertFalse(record["all_treatments_discovered_skill"])
            self.assertEqual(record["treatment_discovery"]["observed_false"], 1)


if __name__ == "__main__":
    unittest.main()
