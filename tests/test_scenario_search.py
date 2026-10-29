"""Bilingual scenario discovery and domain filter regression tests."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/archvela-architect/scripts/scenes.py"

def call(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                          capture_output=True, check=False)

class ScenarioSearchTests(unittest.TestCase):
    def test_english_aliases(self):
        cases = {
            "digital twin": {"V3-25", "V3-26", "V3-28"},
            "home digital twin": {"V3-26"},
            "tower defense": {"V3-45", "V3-46"},
            "dashboard": {"V3-14", "V3-16", "V3-21"},
            "english pronunciation": {"V3-37", "V3-38"},
            "company website": {"V3-01", "V3-02"},
        }
        for query, wanted in cases.items():
            with self.subTest(query=query):
                response = call("--query", query, "--json")
                self.assertEqual(response.returncode, 0, response.stderr)
                ids = {row["id"] for row in json.loads(response.stdout)}
                self.assertTrue(wanted <= ids, (query, ids))

    def test_domain_filter_and_limit(self):
        res = call("--domain", "03", "--limit", "3", "--json")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(len(json.loads(res.stdout)), 3)
        self.assertTrue(all(row["domain_code"] == "03" for row in json.loads(res.stdout)))
        res = call("--domain", "空间与数字孪生", "--all", "--json")
        self.assertEqual(len(json.loads(res.stdout)), 12)
        self.assertEqual(call("--domain", "99").returncode, 2)

    def test_prefer_exact_id_over_vague_matches(self):
        result = call("--query", "V3-26", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)[0]["id"], "V3-26")

    def test_empty_and_invalid_inputs(self):
        self.assertEqual(call().returncode, 2)
        self.assertEqual(call("--query", "   ").returncode, 2)
        self.assertEqual(call("--all", "--limit", "0").returncode, 2)
        self.assertEqual(call("--id", "V3-99").returncode, 1)

    def test_historical_chinese_query(self):
        result = call("--query", "简单企业官网", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)[0]["id"], "V3-01")
