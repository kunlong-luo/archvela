"""Guard against accidental removal of release security checks."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/security.yml"
RELEASE = ROOT / "docs/RELEASE-READINESS.md"


class SecurityWorkflowTests(unittest.TestCase):
    def test_static_analysis_and_four_lockfile_audits(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("github/codeql-action/analyze@v4", workflow)
        self.assertIn("python, javascript-typescript", workflow)
        self.assertIn("npm-audit:", workflow)
        self.assertIn("cinematic-site, saas-workspace, home-digital-twin, browser-tests", workflow)
        self.assertIn("--package-lock-only --include=dev --audit-level=high", workflow)
        self.assertNotIn("\n          npm audit fix", workflow)

    def test_dependency_review_is_not_claimed_without_capability(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("dependency-graph-capability:", workflow)
        self.assertIn("dependency-graph/sbom", workflow)
        self.assertIn("enabled=false", workflow)
        self.assertIn("needs.dependency-graph-capability.outputs.enabled == 'true'", workflow)
        self.assertIn("actions/dependency-review-action@v5", workflow)
        self.assertIn("exit 1", workflow)
        notes = RELEASE.read_text(encoding="utf-8")
        self.assertIn("Dependency Graph", notes)
        self.assertIn("not", notes.lower())


if __name__ == "__main__":
    unittest.main()
