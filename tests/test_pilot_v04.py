"""V0.4 pilot validity: keep failures, prevent contamination, export no arms."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
PIN = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def run(script: str, *args: str):
    return subprocess.run(
        [sys.executable, str(BENCH / script), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )


class PilotV04Tests(unittest.TestCase):
    def make_study(self, root: Path):
        pilot = run("pilot.py", "--agent", "codex", "--model", "fixture-model",
                    "--skill-sha", PIN, "--output", root)
        self.assertEqual(pilot.returncode, 0, pilot.stderr)
        return json.loads((root / "operator-manifest.json").read_text())

    def populate(self, root: Path, manifest: dict):
        (root / "reviewer/artifacts").mkdir()
        for item in manifest["runs"]:
            blind = item["blind_id"]
            folder = root / "operator" / blind
            meta = json.loads((folder / "session.template.json").read_text())
            meta.update({
                "client_version": "TEST-FIXTURE-ONLY",
                "started_at_utc": "2026-10-30T10:00:00Z",
                "finished_at_utc": "2026-10-30T10:01:00Z",
                "execution_status": "completed",
                "skill_discovered": item["arm"] == "archvela",
            })
            (folder / "session.json").write_text(json.dumps(meta))
            (root / "reviewer/artifacts" / (blind + ".response.md")).write_text(
                "TEST FIXTURE ONLY. Not an AI response.\n"
            )
            (root / "reviewer/artifacts" / (blind + ".run.log")).write_text(
                "TEST FIXTURE ONLY. No model calls.\n"
            )

    def change_meta(self, root, blind, **changes):
        path = root / "operator" / blind / "session.json"
        value = json.loads(path.read_text())
        value.update(changes)
        path.write_text(json.dumps(value))

    def test_preflight_is_read_only_and_fails_dirty_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            fresh = run("preflight.py", "--study", study)
            self.assertEqual(fresh.returncode, 0, fresh.stderr)
            report = json.loads(fresh.stdout)
            self.assertTrue(report["passed"])
            self.assertEqual(report["expected_runs"], 4)
            self.assertEqual(len(report["manual_checks_required"]), 4)
            workspace = study / "workspace" / manifest["runs"][0]["blind_id"]
            (workspace / "contaminated.txt").write_text("TEST")
            fail = run("preflight.py", "--study", study)
            self.assertEqual(fail.returncode, 2)
            self.assertIn("not empty", fail.stdout)

    def test_negative_treatment_failure_is_retained_not_discarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            self.populate(study, manifest)
            negative = next(x for x in manifest["runs"] if x["arm"] == "archvela")
            self.change_meta(study, negative["blind_id"],
                             execution_status="failed", skill_discovered=False,
                             failure_category="skill_discovery_failure",
                             failure_detail="TEST FIXTURE: client did not find the Skill")
            audited = run("audit_pilot.py", "--study", study)
            self.assertEqual(audited.returncode, 0, audited.stderr)
            report = json.loads(audited.stdout)
            self.assertTrue(report["protocol_valid"])
            self.assertEqual(report["evidence_complete_runs"], 4)
            self.assertEqual(report["execution_status_counts"]["failed"], 1)
            self.assertIn("treatment_skill_not_discovered",
                          [d["type"] for d in report["discovery_deviations"]])

    def test_blocked_with_unknown_discovery_is_legal_negative_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            self.populate(study, manifest)
            treated = next(x for x in manifest["runs"] if x["arm"] == "archvela")
            self.change_meta(study, treated["blind_id"],
                             execution_status="blocked", skill_discovered=None,
                             failure_category="installation_error",
                             failure_detail="TEST FIXTURE: pinned installation unavailable")
            report = run("audit_pilot.py", "--study", study)
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertEqual(json.loads(report.stdout)["execution_status_counts"]["blocked"], 1)

    def test_baseline_skill_contamination_invalidates_protocol_but_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            self.populate(study, manifest)
            control = next(x for x in manifest["runs"] if x["arm"] == "baseline")
            self.change_meta(study, control["blind_id"], skill_discovered=True)
            audited = run("audit_pilot.py", "--study", study)
            self.assertEqual(audited.returncode, 2)
            result = json.loads(audited.stdout)
            self.assertFalse(result["protocol_valid"])
            self.assertEqual(result["evidence_complete_runs"], 4)
            self.assertIn("baseline_skill_contamination",
                          [d["type"] for d in result["discovery_deviations"]])

    def test_manifest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            manifest["runs"][0]["arm"] = "baseline" if manifest["runs"][0]["arm"] == "archvela" else "archvela"
            (study / "operator-manifest.json").write_text(json.dumps(manifest))
            audited = run("audit_pilot.py", "--study", study)
            self.assertEqual(audited.returncode, 2)
            self.assertIn("modified", audited.stderr)

    def test_blind_export_requires_redaction_and_leaks_no_operator_manifest_or_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            review = Path(tmp) / "review"
            manifest = self.make_study(study)
            self.populate(study, manifest)
            rejected = run("export_blind_review.py", "--study", study, "--output", review)
            self.assertEqual(rejected.returncode, 2)
            self.assertFalse(review.exists())
            exported = run("export_blind_review.py", "--study", study, "--output", review,
                           "--redaction-confirmed")
            self.assertEqual(exported.returncode, 0, exported.stderr)
            self.assertEqual(len(list((review / "submissions").iterdir())), 4)
            paths = {str(f.relative_to(review)) for f in review.rglob("*") if f.is_file()}
            self.assertEqual(len(paths), 10)  # README, blank review sheet and 4 x (response,prompt)
            self.assertFalse(any(x.endswith("run.log") or "operator" in x
                                 or "manifest" in x or "session" in x for x in paths))
            self.assertEqual(json.loads((review / "blank-review.json").read_text())
                             ["records"][0]["grades"]["scenario_fit"], None)
            repeat = run("export_blind_review.py", "--study", study, "--output", review,
                         "--redaction-confirmed")
            self.assertEqual(repeat.returncode, 2)

    def test_failure_requires_real_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            study = Path(tmp) / "pilot"
            manifest = self.make_study(study)
            self.populate(study, manifest)
            treated = next(x for x in manifest["runs"] if x["arm"] == "archvela")
            self.change_meta(study, treated["blind_id"],
                             execution_status="failed", skill_discovered=False,
                             failure_category=None, failure_detail=None)
            audited = run("audit_pilot.py", "--study", study)
            self.assertEqual(audited.returncode, 2)
            self.assertIn("failure category and detail", audited.stderr)


if __name__ == "__main__":
    unittest.main()
