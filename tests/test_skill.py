"""Archvela v0.1.0 metadata/catalog/CLI safety tests (stdlib only)."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "archvela-architect"
SCRIPT = SKILL / "scripts"
CATALOG = SKILL / "references" / "scenarios.json"
COUNT = {"01": 13, "02": 11, "03": 12, "04": 8, "05": 9, "06": 9}

def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPT / script), *map(str, args)],
                          capture_output=True, text=True, check=False)

class ArchvelaTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        meta = text.split("---", 2)[1]
        self.assertRegex(meta, r"(?m)^name: archvela-architect$")
        description = re.search(r"(?m)^description: (.+)$", meta)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertLess(len(text.splitlines()), 500)

    def test_62_scenarios_and_domain_counts(self):
        items = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(items), 62)
        self.assertEqual([item["id"] for item in items],
                         [f"V3-{i:02d}" for i in range(1, 63)])
        for code, count in COUNT.items():
            self.assertEqual(sum(x["domain_code"] == code for x in items), count)
        for item in items:
            self.assertTrue((SKILL / "references" / item["domain_file"]).is_file())
            self.assertTrue(item["stack"])
            self.assertTrue(item["mvp"])
            self.assertTrue(item["splitting"])
        index = (SKILL / "references" / "07_V3_全场景蓝图与选型索引.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"(?m)^### V3-\d{2} · ", index)), 62)

    def test_search_by_id_and_keywords(self):
        exact = run("scenes.py", "--id", "V3-26", "--json")
        self.assertEqual(exact.returncode, 0, exact.stderr)
        self.assertEqual(json.loads(exact.stdout)[0]["id"], "V3-26")
        self.assertIn("V3-01", run("scenes.py", "--query", "简单企业官网").stdout)
        self.assertNotEqual(run("scenes.py", "--id", "V3-99").returncode, 0)
        domain = run("scenes.py", "--list-domains", "--json")
        self.assertEqual(sum(json.loads(domain.stdout).values()), 62)

    def test_generator_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "project"
            res = run("new_project_docs.py", "--scene", "V3-26", "--project", "test", "--output", out)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertFalse(out.exists())

    def test_generator_create_then_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "project"
            args = ("--scene", "V3-26", "--project", "test", "--output", out, "--write")
            first = run("new_project_docs.py", *args)
            self.assertEqual(first.returncode, 0, first.stderr)
            dest = out / "docs" / "architecture"
            docs = sorted(dest.glob("*.md"))
            self.assertEqual(len(docs), 3)
            snapshot = {p.name: p.read_bytes() for p in docs}
            again = run("new_project_docs.py", *args)
            self.assertEqual(again.returncode, 2)
            self.assertEqual(snapshot, {p.name: p.read_bytes() for p in docs})

    def test_invalid_scene_causes_no_write(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "new"
            result = run("new_project_docs.py", "--scene", "V3-99", "--project", "test",
                         "--output", out, "--write")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())

if __name__ == "__main__":
    unittest.main()
