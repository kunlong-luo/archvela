"""Protect the one-time cleanup gate against accidental expansion of privileges."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HardeningWorkflowTests(unittest.TestCase):
    def test_main_push_only_one_time_cleanup(self):
        path = ROOT / ".github/workflows/cleanup-merged-branches.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("branches: [main]", text)
        self.assertIn('".github/workflows/cleanup-merged-branches.yml"', text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("pull_request_target:", text)
        self.assertIn("github.repository == 'kunlong-luo/archvela'", text)
        self.assertIn("github.ref == 'refs/heads/main'", text)
        self.assertIn("contents: write", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("--expect-sha", text)
        self.assertIn("--execute", text)

    def test_release_readiness_is_explicit_not_fabricated(self):
        readme = (ROOT / "docs/RELEASE-READINESS.md").read_text(encoding="utf-8")
        self.assertIn("PRE-RELEASE", readme)
        self.assertIn("actual cleanup run", readme)
        self.assertIn("NOT", readme)
        self.assertIn("Dependency Graph", readme)
        self.assertIn("L1", readme)
        self.assertIn("L2", readme)
        self.assertIn("third-party", readme.lower())
        self.assertIn("owner approval", readme.lower())


if __name__ == "__main__":
    unittest.main()
