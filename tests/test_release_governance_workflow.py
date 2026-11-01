"""Protect the nonpublishing, owner-run release governance workflow."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GovernanceWorkflowPolicyTests(unittest.TestCase):
    def test_manual_only_no_write_token_and_exact_main(self):
        path = ROOT / ".github/workflows/alpha-governance.yml"
        content = path.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", content)
        self.assertNotIn("  push:", content)
        self.assertNotIn("  pull_request:", content)
        self.assertIn("permissions:\n  actions: read\n  contents: read", content)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', content)
        self.assertIn('--expected-sha "$GITHUB_SHA"', content)
        self.assertIn('assert x["release_ready"] is False', content)
        self.assertNotIn("contents: write", content)
        self.assertNotIn("gh release create", content)
        self.assertNotIn("git tag", content)
        self.assertNotIn("create-release", content)

    def test_real_codex_smoke_is_a_protocol_not_a_claim(self):
        content = (ROOT / "docs/CODEX-NATIVE-SMOKE.md").read_text(encoding="utf-8")
        for token in ("NOT EXECUTED", "0 real client sessions", "real authenticated Codex",
                      "not_observed", "L1", "L2", "L3", "SHA"):
            self.assertIn(token, content)
        self.assertIn("without explicitly naming Archvela", content)
        self.assertIn("4-session randomized paired", content)

    def test_user_owner_runbook_is_specific_and_keeps_false_status(self):
        content = (ROOT / "docs/RELEASE-GOVERNANCE-QUICKSTART.md").read_text(encoding="utf-8")
        for token in ("main.protected=false", "Require a pull request",
                      "Require status checks", "Automatically delete head branches",
                      "cross-agent-install", "validate (3.12)", "chromium",
                      "audit_release_governance.py", "not a GitHub Release"):
            self.assertIn(token, content)


if __name__ == "__main__":
    unittest.main()
