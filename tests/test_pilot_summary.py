"""Offline fixture-only tests for the pilot summary gate. NO MODEL RUNS."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
SKILL_SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
CLIENTS = ("codex", "claude-code", "opencode")
RUBRIC = ("scenario_fit", "architecture_reasoning", "four_layer_split",
          "fallback_safety", "verification_plan")


def cli(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BENCH / script), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, check=False
    )


class PilotSummaryTests(unittest.TestCase):
    def fixture(self, root: Path, agent: str, seed: int = 20261029,
                sha: str = SKILL_SHA) -> tuple[Path, Path, dict]:
        study = root / ("study-" + agent)
        review = root / ("review-" + agent + ".json")
        model = "FIXTURE-MODEL-" + agent
        gen = cli("pilot.py", "--agent", agent, "--model", model,
                  "--skill-sha", sha, "--seed", seed, "--output", study)
        self.assertEqual(gen.returncode, 0, gen.stderr)
        manifest = json.loads((study / "operator-manifest.json").read_text(encoding="utf-8"))
        (study / "reviewer/artifacts").mkdir()
        rows = []
        for item in manifest["runs"]:
            blind = item["blind_id"]
            op = study / "operator" / blind
            meta = json.loads((op / "session.template.json").read_text(encoding="utf-8"))
            meta.update({
                "client_version": "TEST-FIXTURE",
                "started_at_utc": "2026-10-30T10:00:00Z",
                "finished_at_utc": "2026-10-30T10:01:00Z",
                "execution_status": "completed",
                "skill_discovered": item["arm"] == "archvela",
            })
            (op / "session.json").write_text(json.dumps(meta), encoding="utf-8")
            (study / "reviewer/artifacts" / (blind + ".response.md")).write_text(
                "TEST FIXTURE ONLY — not an AI response.\n", encoding="utf-8")
            (study / "reviewer/artifacts" / (blind + ".run.log")).write_text(
                "TEST FIXTURE ONLY — no model ran.\n", encoding="utf-8")
            score = 2 if item["arm"] == "baseline" else 3
            rows.append({
                "blind_id": blind,
                "response_sha256": hashlib.sha256("TEST FIXTURE ONLY — not an AI response.\\n".encode()).hexdigest(),
                "grades": {key: score for key in RUBRIC},
                "reviewer": "FICTIONAL-TEST-FIXTURE",
                "notes": None,
            })
        review.write_text(json.dumps({
            "schema_version": 1, "kind": "blind_response_only_ungraded",
            "records": rows,
        }), encoding="utf-8")
        return study, review, manifest

    def mutate_session(self, study, blind, **updates):
        file = study / "operator" / blind / "session.json"
        data = json.loads(file.read_text(encoding="utf-8"))
        data.update(updates)
        file.write_text(json.dumps(data), encoding="utf-8")

    def mutate_review(self, review, blind, grades=None, reviewer="FICTIONAL-TEST-FIXTURE"):
        data = json.loads(review.read_text(encoding="utf-8"))
        for row in data["records"]:
            if row["blind_id"] == blind:
                row["grades"] = grades if grades is not None else {key: None for key in RUBRIC}
                row["reviewer"] = reviewer
        review.write_text(json.dumps(data), encoding="utf-8")

    def test_3_clients_12_sessions_no_pooled_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            studies = [self.fixture(Path(tmp), agent) for agent in CLIENTS]
            args = []
            for study, review, _ in studies:
                args += ["--study", study, "--review", review]
            proc = cli("summarize_pilot.py", *args)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertTrue(data["planned_three_client_pilot"])
            self.assertEqual(data["total_expected_sessions"], 12)
            self.assertEqual(data["total_evidence_complete_sessions"], 12)
            self.assertEqual(data["total_human_graded_pairs"], 6)
            self.assertEqual(data["total_failed_or_blocked"], 0)
            self.assertNotIn("pooled_delta", data)
            for client in data["clients"]:
                self.assertEqual(client["human_graded_pairs"], 2)
                self.assertAlmostEqual(client["full_study_human_delta"], 0.25)
                self.assertEqual(client["treatment_discovery"]["observed_true"], 2)

    def test_negative_treatment_failure_does_not_create_cherry_picked_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, manifest = self.fixture(Path(tmp), "codex")
            treated = next(x for x in manifest["runs"] if x["arm"] == "archvela")
            blind = treated["blind_id"]
            self.mutate_session(study, blind, execution_status="failed",
                                skill_discovered=False, failure_category="skill_discovery_failure",
                                failure_detail="TEST FIXTURE: native Skill discovery failed")
            self.mutate_review(review, blind, reviewer=None)
            proc = cli("summarize_pilot.py", "--study", study, "--review", review)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)["clients"][0]
            self.assertEqual(data["outcomes_by_arm"]["archvela"]["failed"], 1)
            self.assertEqual(data["human_graded_pairs"], 1)
            self.assertIsNone(data["full_study_human_delta"])
            self.assertEqual(data["treatment_discovery"]["observed_false"], 1)
            self.assertIn("treatment_skill_not_discovered", data["discovery_deviations"])

    def test_blank_review_produces_no_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, manifest = self.fixture(Path(tmp), "codex")
            for item in manifest["runs"]:
                self.mutate_review(review, item["blind_id"], reviewer=None)
            proc = cli("summarize_pilot.py", "--study", study, "--review", review)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            client = json.loads(proc.stdout)["clients"][0]
            self.assertEqual(client["human_graded_pairs"], 0)
            self.assertIsNone(client["full_study_human_delta"])
            without_review = cli("summarize_pilot.py", "--study", study)
            self.assertEqual(without_review.returncode, 0, without_review.stderr)
            self.assertIsNone(json.loads(without_review.stdout)["clients"][0]["full_study_human_delta"])

    def test_baseline_contamination_stays_visible_but_invalidates_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, manifest = self.fixture(Path(tmp), "codex")
            control = next(x for x in manifest["runs"] if x["arm"] == "baseline")
            self.mutate_session(study, control["blind_id"], skill_discovered=True)
            proc = cli("summarize_pilot.py", "--study", study, "--review", review)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            client = json.loads(proc.stdout)["clients"][0]
            self.assertFalse(client["protocol_valid"])
            self.assertEqual(client["evidence_complete_sessions"], 4)
            self.assertIsNone(client["full_study_human_delta"])

    def test_review_rejects_partial_boolean_forged_or_failed_grades(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, manifest = self.fixture(Path(tmp), "codex")
            target = manifest["runs"][0]
            self.mutate_review(review, target["blind_id"],
                               grades={key: True for key in RUBRIC})
            self.assertIn("invalid", cli("summarize_pilot.py", "--study", study,
                                         "--review", review).stderr)
            self.mutate_review(review, target["blind_id"],
                               grades={key: None for key in RUBRIC})
            self.assertEqual(cli("summarize_pilot.py", "--study", study,
                                 "--review", review).returncode, 0)
            data = json.loads(review.read_text())
            data["records"].append(dict(data["records"][0]))
            review.write_text(json.dumps(data))
            self.assertEqual(cli("summarize_pilot.py", "--study", study,
                                 "--review", review).returncode, 2)

    def test_fails_when_session_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, manifest = self.fixture(Path(tmp), "codex")
            blind = manifest["runs"][0]["blind_id"]
            (study / "reviewer/artifacts" / (blind + ".run.log")).unlink()
            proc = cli("summarize_pilot.py", "--study", study, "--review", review)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("incomplete", proc.stderr)

    def test_fails_on_cross_client_mismatched_skill_or_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.fixture(Path(tmp), "codex")
            second = self.fixture(Path(tmp), "opencode", seed=42)
            args = ["--study", first[0], "--study", second[0]]
            proc = cli("summarize_pilot.py", *args)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("must share", proc.stderr)

    def test_rejects_duplicate_clients_and_reviews_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            study, review, _ = self.fixture(Path(tmp), "codex")
            duplicate = cli("summarize_pilot.py", "--study", study, "--study", study)
            self.assertEqual(duplicate.returncode, 2)
            mixed = cli("summarize_pilot.py", "--study", study, "--review", review,
                        "--review", review)
            self.assertEqual(mixed.returncode, 2)
            self.assertIn("one review sheet per study", mixed.stderr)


if __name__ == "__main__":
    unittest.main()
