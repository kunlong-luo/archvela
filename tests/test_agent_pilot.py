"""Offline tests: V0.3 pilot cards are never mistaken for agent runs."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks/pilot.py"
REVISION = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


class PilotPreparationTests(unittest.TestCase):
    def run_pilot(self, destination, *other):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--agent", "codex",
             "--model", "fixture-model", "--skill-sha", REVISION,
             "--output", str(destination), *other],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def test_paired_cards_are_isolated_and_unexecuted(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "pilot"
            result = self.run_pilot(target)
            self.assertEqual(result.returncode, 0, result.stderr)
            study = json.loads((target / "operator-manifest.json").read_text())
            self.assertEqual(study["executed_runs"], 0)
            self.assertEqual(len(study["runs"]), 4)
            self.assertEqual(set(study["task_ids"]), {"AV-01", "AV-03"})
            grouped = {}
            for run in study["runs"]:
                blind_id = run["blind_id"]
                grouped.setdefault(run["task_id"], {})[run["arm"]] = (
                    target / "operator" / blind_id / "PROMPT.txt"
                ).read_text(encoding="utf-8")
                instructions = (target / "operator" / blind_id / "RUN.md").read_text()
                self.assertTrue((target / "workspace" / blind_id).is_dir())
                self.assertEqual(list((target / "workspace" / blind_id).iterdir()), [])
                if run["arm"] == "archvela":
                    self.assertIn("--skill archvela-architect", instructions)
                    self.assertIn(REVISION, instructions)
                else:
                    self.assertNotIn("skills@1.7.4 add", instructions)
            for pair in grouped.values():
                self.assertEqual(set(pair), {"baseline", "archvela"})
                self.assertEqual(pair["baseline"], pair["archvela"])
            self.assertFalse((target / "reviewer" / "artifacts").exists())
            self.assertFalse((target / "blank-human-grades.json").exists())
            self.assertNotIn("operator-manifest", (
                target / "reviewer" / "README.md"
            ).read_text().split("Operator:")[0])

    def test_refuses_to_overwrite_existing_study(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "pilot"
            self.assertEqual(self.run_pilot(target).returncode, 0)
            again = self.run_pilot(target)
            self.assertEqual(again.returncode, 2)
            self.assertIn("already exists", again.stderr)

    def test_rejects_unknown_task_and_invalid_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid_task = self.run_pilot(root / "bad-task", "--task", "AV-99")
            self.assertEqual(invalid_task.returncode, 2)
            self.assertFalse((root / "bad-task").exists())
            invalid_sha = subprocess.run(
                [sys.executable, str(SCRIPT), "--agent", "claude-code",
                 "--model", "fixture", "--skill-sha", "main",
                 "--output", str(root / "bad-sha")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(invalid_sha.returncode, 2)
            self.assertFalse((root / "bad-sha").exists())

    def test_rejects_study_inside_archvela_repository(self):
        result = self.run_pilot(ROOT / "_unsafe_study_should_not_exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside", result.stderr)
        self.assertFalse((ROOT / "_unsafe_study_should_not_exist").exists())


if __name__ == "__main__":
    unittest.main()
