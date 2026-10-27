"""Offline cross-agent plan handoff contract tests (no AI credentials)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/archvela-architect/scripts"


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          text=True, capture_output=True, check=False)


class PlanContractTests(unittest.TestCase):
    def generate(self, output, scene="V3-26", write=True):
        args = ["--scene", scene, "--project", "sample", "--output", output,
                "--plan-json", "--json"]
        if write:
            args += ["--write"]
        return run("new_project_docs.py", *args)

    def test_four_artifacts_when_requested_without_changing_legacy_default(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "new-project"
            preview = self.generate(project, write=False)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            data = json.loads(preview.stdout)
            self.assertEqual(data["mode"], "dry-run")
            self.assertEqual(len(data["paths"]), 4)
            self.assertFalse(project.exists())
            write = self.generate(project)
            self.assertEqual(write.returncode, 0, write.stderr)
            self.assertEqual(json.loads(write.stdout)["status"], "created")
            files = sorted((project / "docs/architecture").iterdir())
            self.assertEqual(len(files), 4)
            self.assertIn("archvela-plan.json", [file.name for file in files])
            plan_path = project / "docs/architecture/archvela-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["scenario"]["id"], "V3-26")
            self.assertEqual(set(plan["boundaries"]),
                             {"package", "feature", "chunk", "assets"})
            self.assertEqual(run("plan_contract.py", plan_path, "--level", "draft").returncode, 0)
            stricter = run("plan_contract.py", plan_path, "--level", "reviewed", "--json")
            self.assertEqual(stricter.returncode, 1)
            self.assertFalse(json.loads(stricter.stdout)["ok"])
            self.assertEqual(self.generate(project).returncode, 2)
            self.assertEqual(json.loads(plan_path.read_text())["status"], "draft")

    def test_reviewed_and_delivered_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            self.assertEqual(self.generate(project).returncode, 0)
            target = project / "docs/architecture/archvela-plan.json"
            plan = json.loads(target.read_text(encoding="utf-8"))
            plan["status"] = "reviewed"
            plan["stack"]["selected"] = "Existing React / Vite app"
            plan["stack"]["rationale"] = "Preserve the existing React app until benchmarks prove migration necessary."
            for layer in plan["boundaries"].values():
                layer["selected"] = "Keep as recommended, subject to repository audit."
            plan["fallback"]["selected"] = "Render simple accessible read-only 2D overview."
            plan["repository_audit"] = {
                "completed": True, "evidence": ["package.json reviewed in test fixture"]
            }
            plan["target_environment"] = {"browsers": ["Chromium"], "devices": ["mid-tier Android"]}
            plan["risks"]["mitigations"] = ["Validate geometry provenance before approval"]
            plan["delivery"]["planned_tests"] = ["Unit and browser E2E scenario coverage"]
            target.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            reviewed = run("plan_contract.py", target, "--level", "reviewed", "--json")
            self.assertEqual(reviewed.returncode, 0, reviewed.stdout)
            self.assertEqual(run("plan_contract.py", target, "--level", "delivered").returncode, 1)
            plan["status"] = "delivered"
            plan["delivery"]["test_evidence"] = [
                {"check": "example smoke", "result": "passed",
                 "evidence": "example CI run URL (test fixture only)"}
            ]
            plan["delivery"]["measurements"] = [
                {"name": "FPS", "value": "30", "environment": "sample fixture",
                 "evidence": "example measurement file (test fixture only)"}
            ]
            plan["provenance"]["implementation_verified"] = True
            target.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            verified = run("plan_contract.py", target, "--level", "delivered", "--json")
            self.assertEqual(verified.returncode, 0, verified.stdout)
            # A failed result must never pass a delivered gate, even when
            # "implementation_verified" is claimed to be true.
            plan["delivery"]["test_evidence"].append({
                "check": "broken visual regression",
                "result": "failed",
                "evidence": "fixture failure report",
            })
            target.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            bad = run("plan_contract.py", target, "--level", "delivered", "--json")
            self.assertEqual(bad.returncode, 1)
            self.assertTrue(any("failing tests" in issue for issue in
                                json.loads(bad.stdout)["issues"]))

    def test_detect_catalog_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            self.assertEqual(self.generate(project).returncode, 0)
            target = project / "docs/architecture/archvela-plan.json"
            plan = json.loads(target.read_text())
            plan["scenario"]["domain_code"] = "05"
            target.write_text(json.dumps(plan), encoding="utf-8")
            res = run("plan_contract.py", target, "--level", "draft", "--json")
            self.assertEqual(res.returncode, 1)
            self.assertTrue(any("domain_code" in x for x in json.loads(res.stdout)["issues"]))

    def test_all_62_scenarios_can_preview_plan(self):
        for i in range(1, 63):
            scene = "V3-%02d" % i
            with self.subTest(scene=scene), tempfile.TemporaryDirectory() as temp:
                project = Path(temp) / "not-written"
                res = self.generate(project, scene=scene, write=False)
                self.assertEqual(res.returncode, 0, (scene, res.stderr))
                self.assertEqual(len(json.loads(res.stdout)["paths"]), 4)
                self.assertFalse(project.exists())

    def test_output_root_symlink_cannot_write(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            victim = parent / "victim"
            victim.mkdir()
            linked = parent / "linked"
            linked.symlink_to(victim, target_is_directory=True)
            result = self.generate(linked)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(list(victim.iterdir()))


if __name__ == "__main__":
    unittest.main()
