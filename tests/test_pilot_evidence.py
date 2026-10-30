"""Only local fixture files; tests do not invoke any AI model."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "benchmarks/pilot.py"
AUDIT = ROOT / "benchmarks/audit_pilot.py"
SHA = "a" * 40


class PilotEvidenceTests(unittest.TestCase):
    def prepare(self, root: Path):
        result = subprocess.run([
            sys.executable, str(PILOT), "--agent", "codex",
            "--model", "test-fixture-model", "--skill-sha", SHA,
            "--output", str(root),
        ], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((root / "operator-manifest.json").read_text())

    def audit(self, root):
        return subprocess.run(
            [sys.executable, str(AUDIT), "--study", str(root)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def complete_fixture(self, root: Path, manifest: dict):
        artifacts = root / "reviewer/artifacts"
        artifacts.mkdir()
        for run in manifest["runs"]:
            blind = run["blind_id"]
            (artifacts / (blind + ".response.md")).write_text("TEST FIXTURE ONLY: no model ran")
            (artifacts / (blind + ".run.log")).write_text("TEST FIXTURE ONLY: no tool events")
            source = root / "operator" / blind / "session.template.json"
            meta = json.loads(source.read_text(encoding="utf-8"))
            meta.update({
                "client_version": "test-fixture-not-real",
                "started_at_utc": "2026-10-30T10:00:00Z",
                "finished_at_utc": "2026-10-30T10:01:00Z",
                "execution_status": "completed",
                "skill_discovered": run["arm"] == "archvela",
            })
            (source.parent / "session.json").write_text(json.dumps(meta), encoding="utf-8")

    def test_initial_pilot_has_no_model_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "pilot"
            manifest = self.prepare(root)
            self.assertEqual(manifest["executed_runs"], 0)
            result = self.audit(root)
            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_complete_runs"], 0)
            self.assertEqual(report["expected_runs"], 4)
            self.assertFalse(report["all_evidence_present"])

    def test_fixture_evidence_presence_and_hash_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "pilot"
            manifest = self.prepare(root)
            self.complete_fixture(root, manifest)
            result = self.audit(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_complete_runs"], 4)
            self.assertEqual(len(report["evidence"][0]["response_sha256"]), 64)
            self.assertIn("cannot be independently verified", report["caveat"])

    def test_reject_missing_actual_client_version_and_treatment_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "pilot"
            manifest = self.prepare(root)
            self.complete_fixture(root, manifest)
            target = manifest["runs"][0]
            filename = root / "operator" / target["blind_id"] / "session.json"
            metadata = json.loads(filename.read_text())
            metadata["client_version"] = ""
            filename.write_text(json.dumps(metadata))
            result = self.audit(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Missing actual client version", result.stderr)
            metadata["client_version"] = "test-fixture"
            metadata["skill_discovered"] = target["arm"] != "archvela"
            filename.write_text(json.dumps(metadata))
            result = self.audit(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Skill discovery", result.stderr)

    def test_reject_symlinked_response_and_modified_prompt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "pilot"
            manifest = self.prepare(root)
            self.complete_fixture(root, manifest)
            blind = manifest["runs"][0]["blind_id"]
            response = root / "reviewer/artifacts" / (blind + ".response.md")
            response.unlink()
            response.symlink_to(root / "operator-manifest.json")
            self.assertIn("symlink", self.audit(root).stderr)
            response.unlink()
            response.write_text("TEST FIXTURE response")
            prompt = root / "operator" / blind / "PROMPT.txt"
            prompt.write_text("changed prompt")
            self.assertIn("prompt was modified", self.audit(root).stderr)


if __name__ == "__main__":
    unittest.main()
