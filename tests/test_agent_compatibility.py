"""Offline manifest and harness contract validation. Native clients are not invoked."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "archvela-architect"

class CompatibilityMatrixTests(unittest.TestCase):
    def test_matrix_is_complete_and_unique(self):
        manifest = json.loads((ROOT / "compatibility/agents.json").read_text(encoding="utf-8"))
        agents = manifest["agents"]
        self.assertEqual(len(agents), 20)
        ids = [item["id"] for item in agents]
        self.assertEqual(len(set(ids)), 20)
        self.assertTrue({"opencode", "codex", "claude-code", "cursor",
                         "gemini-cli", "github-copilot", "windsurf", "cline", "roo"} <= set(ids))
        for row in agents:
            self.assertTrue(row["project_path"].startswith("."))
            self.assertTrue(row["global_path"].startswith("~/"))
            self.assertNotIn("..", row["project_path"])
            self.assertNotIn("..", row["global_path"])

    def test_agent_skills_frontmatter_portable(self):
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(body.startswith("---\n"))
        head = body.split("---", 2)[1]
        self.assertRegex(head, r"(?m)^name: archvela-architect$")
        self.assertNotRegex(head, r"(?m)^context: fork$")
        self.assertNotRegex(head, r"(?m)^allowed-tools:")
        self.assertRegex(head, r"(?m)^description: .+")
        self.assertLess(len(body.splitlines()), 300)

    def test_reference_paths_are_relative_and_all_present(self):
        references = (SKILL / "references")
        self.assertTrue((references / "scenarios.json").is_file())
        self.assertTrue((SKILL / "scripts" / "scenes.py").is_file())
        self.assertTrue((SKILL / "scripts" / "new_project_docs.py").is_file())
        catalog = json.loads((references / "scenarios.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog), 62)
        for entry in catalog:
            self.assertFalse(Path(entry["domain_file"]).is_absolute())
            self.assertTrue((references / entry["domain_file"]).is_file())
            self.assertTrue(re.fullmatch(r"V3-\d{2}", entry["id"]))
