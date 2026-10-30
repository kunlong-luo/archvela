"""Tests only benchmark harness functionality, never benchmark model quality."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks/evaluate.py"
spec = importlib.util.spec_from_file_location("archvela_benchmark", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BenchmarkTests(unittest.TestCase):
    def test_has_12_balanced_six_domain_scenarios(self):
        cases = mod.load_cases()
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({c["scenario_id"] for c in cases}), 12)

    def test_balanced_and_reproducible_blind_assignment(self):
        one = mod.make_manifest(24, "demo-agent-model", 1)
        two = mod.make_manifest(24, "demo-agent-model", 1)
        # Order remains seeded, but opaque reviewer IDs MUST vary on every run.
        self.assertEqual([(r["task_id"], r["arm"]) for r in one["runs"]],
                         [(r["task_id"], r["arm"]) for r in two["runs"]])
        self.assertNotEqual([r["blind_id"] for r in one["runs"]],
                            [r["blind_id"] for r in two["runs"]])
        self.assertTrue(all(len(r["blind_id"]) == 32 for r in one["runs"]))
        self.assertEqual(len(one["runs"]), 24)
        for task in mod.load_cases():
            self.assertEqual({r["arm"] for r in one["runs"] if r["task_id"] == task["id"]},
                             {"baseline", "archvela"})

    def test_blank_scores_must_not_pass(self):
        manifest = mod.make_manifest(24, "demo-agent-model", 1)
        grade_sheet = mod.create_grading_sheet(manifest)
        with self.assertRaisesRegex(ValueError, "Missing/invalid human rubric"):
            mod.score(manifest, grade_sheet)

    def test_paired_scoring_with_only_explicit_test_fixtures(self):
        manifest = mod.make_manifest(24, "demo-agent-model", 1)
        sheet = mod.create_grading_sheet(manifest)
        arms = {run["blind_id"]: run["arm"] for run in manifest["runs"]}
        for entry in sheet["records"]:
            entry["response_artifact"] = "TEST FIXTURE: not a real model output"
            entry["run_log_artifact"] = "TEST FIXTURE: not a real run"
            entry["reviewer"] = "synthetic-test-only"
            grade = 2 if arms[entry["blind_id"]] == "baseline" else 3
            entry["grades"] = {k: grade for k in mod.RUBRIC}
        result = mod.score(manifest, sheet)
        self.assertEqual(result["evaluated_pairs"], 12)
        self.assertAlmostEqual(result["paired_delta"], 0.25)
        sheet["records"][0]["grades"]["scenario_fit"] = None
        with self.assertRaises(ValueError):
            mod.score(manifest, sheet)

    def test_reject_missing_pairs_and_mismatched_trial(self):
        manifest = mod.make_manifest(24, "demo", 1)
        sheet = mod.create_grading_sheet(manifest)
        sheet["records"].pop()
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            mod.score(manifest, sheet)
        sheet = mod.create_grading_sheet(manifest)
        sheet["trial"] = 2
        with self.assertRaisesRegex(ValueError, "trial mismatch"):
            mod.score(manifest, sheet)

    def test_evidence_file_hashes_are_verified_without_agent_execution(self):
        manifest = mod.make_manifest(42, "fixture-model", 1)
        sheet = mod.create_grading_sheet(manifest)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for record in sheet["records"]:
                blind_id = record["blind_id"]
                response = blind_id + "-response.md"
                logfile = blind_id + "-log.txt"
                (root / response).write_text("TEST ONLY — not an agent answer", encoding="utf-8")
                (root / logfile).write_text("TEST ONLY — not a real tool log", encoding="utf-8")
                record["response_artifact"] = response
                record["run_log_artifact"] = logfile
                record["reviewer"] = "fixture-human"
                record["grades"] = {key: 2 for key in mod.RUBRIC}
            mod.score(manifest, sheet)
            inspection = mod.verify_artifact_files(sheet, root)
            self.assertEqual(inspection["files_checked"], 48)
            self.assertEqual(inspection["file_check"], "passed")
            self.assertEqual(len(inspection["fingerprints"]), 24)
            (root / sheet["records"][0]["response_artifact"]).unlink()
            with self.assertRaises((OSError, ValueError)):
                mod.verify_artifact_files(sheet, root)

    def test_reject_symlink_traversal_and_duplicate_evidence(self):
        manifest = mod.make_manifest(42, "fixture-model", 1)
        sheet = mod.create_grading_sheet(manifest)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for record in sheet["records"]:
                record["response_artifact"] = record["blind_id"] + ".md"
                record["run_log_artifact"] = record["blind_id"] + ".log"
                (root / record["response_artifact"]).write_text("sample", encoding="utf-8")
                (root / record["run_log_artifact"]).write_text("sample", encoding="utf-8")
            record = sheet["records"][0]
            old = record["response_artifact"]
            record["response_artifact"] = "../outside.md"
            with self.assertRaisesRegex(ValueError, "Unsafe evidence path"):
                mod.verify_artifact_files(sheet, root)
            record["response_artifact"] = old
            record["run_log_artifact"] = sheet["records"][1]["run_log_artifact"]
            with self.assertRaisesRegex(ValueError, "Duplicate evidence file"):
                mod.verify_artifact_files(sheet, root)
            record["run_log_artifact"] = record["blind_id"] + ".log"
            (root / old).unlink()
            (root / old).symlink_to(root / record["run_log_artifact"])
            with self.assertRaisesRegex(ValueError, "Symlink in evidence path"):
                mod.verify_artifact_files(sheet, root)

    def test_no_external_operations_to_create_study(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "planned"
            self.assertFalse(target.exists())
            manifest = mod.make_manifest(20261028, "demo", 1)
            self.assertEqual(len(manifest["runs"]), 24)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
