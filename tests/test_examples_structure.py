"""Independent example layout test, no npm installs required."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_examples import check

class ExampleStructureTests(unittest.TestCase):
    def test_three_independent_sample_projects(self):
        self.assertEqual(check(), [])
        for name in ("cinematic-site", "saas-workspace", "home-digital-twin"):
            with self.subTest(name=name):
                location = ROOT / "examples" / name
                self.assertTrue((location / "README.md").is_file())
                pkg = json.loads((location / "package.json").read_text(encoding="utf-8"))
                self.assertEqual(pkg["private"], True)
                self.assertNotIn("workspace:", json.dumps(pkg))
