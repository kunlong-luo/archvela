"""Protect the repository after the audited one-time cleanup."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HardeningWorkflowTests(unittest.TestCase):
    def test_privileged_one_time_workflow_was_removed(self):
        self.assertFalse((ROOT / ".github/workflows/cleanup-merged-branches.yml").exists(),
                         "One-time contents:write workflow must not remain on main")
        self.assertTrue((ROOT / "scripts/prune_merged_branches.py").is_file())

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
