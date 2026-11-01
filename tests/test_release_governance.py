"""Read-only governance audit must not infer release approval from GitHub CI."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_release_governance.py"
SPEC = importlib.util.spec_from_file_location("archvela_live_release_governance", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
SHA = "9bd225f49d9d234e72bb4e371c1e203cdb9b1f90"


def example_input(*, protected: bool = False, ci_success: bool = True):
    repo = {"default_branch": "main", "delete_branch_on_merge": False}
    branch = {"name": "main", "protected": protected, "commit": {"sha": SHA}}
    status = "success" if ci_success else "failure"
    runs = {"workflow_runs": [
        {"id": n + 1, "event": "push", "head_branch": "main",
         "head_sha": SHA, "name": title, "status": "completed",
         "conclusion": status}
        for n, title in enumerate(module.EXPECTED_WORKFLOWS)
    ]}
    manifest = json.loads((ROOT / "docs/RELEASE-CANDIDATE.json").read_text(encoding="utf-8"))
    return repo, branch, runs, [], [], manifest


class ReadOnlyGovernanceTests(unittest.TestCase):
    def test_current_unprotected_main_is_a_hard_blocker(self):
        report = module.evaluate(*example_input(), expected_sha=SHA)
        self.assertFalse(report["release_ready"])
        self.assertFalse(report["main_protected"])
        self.assertTrue(report["main_ci_7_of_7_success"])
        self.assertEqual(report["github_releases_observed"], 0)
        self.assertIn("main_unprotected", report["blocked_reasons"])
        self.assertIn("unverified_rights_review_approved", report["blocked_reasons"])
        self.assertIn("unverified_actual_l2_smoke_verified", report["blocked_reasons"])
        self.assertIn("owner_must_confirm_required_pr_checks_and_bypass_settings", report["blocked_reasons"])

    def test_protected_green_repo_still_needs_human_proof(self):
        report = module.evaluate(*example_input(protected=True), expected_sha=SHA)
        self.assertTrue(report["main_protected"])
        self.assertTrue(report["main_ci_7_of_7_success"])
        self.assertNotIn("main_unprotected", report["blocked_reasons"])
        self.assertFalse(report["release_ready"])
        self.assertGreaterEqual(len(report["hard_gate_evidence"]), 5)

    def test_workflow_not_successful_is_not_inferred_from_other_runs(self):
        repo, branch, runs, releases, rules, manifest = example_input()
        runs["workflow_runs"].append({
            "id": 100, "event": "pull_request", "head_branch": "fix",
            "head_sha": SHA, "name": "Security scanning",
            "status": "completed", "conclusion": "success",
        })
        runs["workflow_runs"][6]["conclusion"] = "failure"
        report = module.evaluate(repo, branch, runs, releases, rules, manifest)
        self.assertFalse(report["main_ci_7_of_7_success"])
        self.assertEqual(report["main_ci_workflows"]["Security scanning"],
                         "failed_or_inconclusive")

    def test_missing_and_incomplete_workflows_block_main_ci(self):
        repo, branch, runs, releases, rules, manifest = example_input()
        runs["workflow_runs"] = runs["workflow_runs"][:4]
        report = module.evaluate(repo, branch, runs, releases, rules, manifest)
        self.assertFalse(report["main_ci_7_of_7_success"])
        self.assertIn("missing", report["main_ci_workflows"].values())
        runs["workflow_runs"][-1]["status"] = "in_progress"
        report = module.evaluate(repo, branch, runs, releases, rules, manifest)
        self.assertIn("in_progress", report["main_ci_workflows"].values())

    def test_unverified_remote_rules_are_unknown_not_zero(self):
        repo, branch, runs, releases, _rules, manifest = example_input()
        report = module.evaluate(repo, branch, runs, releases, None, manifest)
        self.assertIsNone(report["rulesets_visible_count"])

    def test_existing_release_and_sha_drift_are_not_silent(self):
        repo, branch, runs, releases, rules, manifest = example_input()
        report = module.evaluate(repo, branch, runs, [{"tag_name": "v0.1.0-alpha.1"}], rules, manifest)
        self.assertIn("a_release_already_exists_check_before_tagging", report["blocked_reasons"])
        with self.assertRaisesRegex(module.Unverifiable, "expected SHA"):
            module.evaluate(repo, branch, runs, releases, rules, manifest, expected_sha="a" * 40)

    def test_fabricated_true_manifest_booleans_cannot_authorize_a_release(self):
        repo, branch, runs, releases, rules, manifest = example_input(protected=True)
        for key in module.HARD_GATES:
            altered = dict(manifest)
            altered[key] = True
            report = module.evaluate(repo, branch, runs, releases, rules, altered)
            self.assertFalse(report["release_ready"])
            self.assertEqual(report["hard_gate_evidence"][key],
                             "requires_independent_verification")

    def test_api_paths_validation_rejects_host_and_repository_injection(self):
        with self.assertRaises(ValueError):
            module.api_get("wrong/owner/extra", "/branches/main")
        with self.assertRaises(ValueError):
            module.api_get("kunlong-luo/archvela", "https://attacker.example")
        with self.assertRaises(ValueError):
            module.api_get("kunlong-luo/archvela", "//attacker.example")


if __name__ == "__main__":
    unittest.main()
