"""Offline documentation integrity and truthful product-scope regressions."""
from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

DOCS = (
    "README.md",
    "README.zh.md",
    "CONTRIBUTING.md",
    "docs/GETTING-STARTED.md",
    "docs/GETTING-STARTED.zh.md",
    "docs/COMPATIBILITY.md",
    "docs/RELEASE-READINESS.md",
)

# Markdown links from edited entrypoint documents; image URLs, anchors and
# external http(s) hosts are not fetched during offline tests.
MARKDOWN_LINK = re.compile(r"!?(?<!\\)\[[^\]\n]+\]\(([^)]+)\)")


class DocumentationIntegrityTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        invalid = []
        for relative in DOCS:
            document = ROOT / relative
            self.assertTrue(document.is_file(), relative)
            body = document.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK.findall(body):
                target = target.strip().split(" ", 1)[0].strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                resolved = (document.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    invalid.append(f"{relative} -> {target}")
        self.assertEqual(invalid, [], "Broken or escaping relative Markdown links")

    def test_english_first_readme_names_and_translation_integrity(self):
        english_path = ROOT / "README.md"
        chinese_path = ROOT / "README.zh.md"
        self.assertTrue(english_path.is_file())
        self.assertTrue(chinese_path.is_file())
        self.assertFalse((ROOT / "README.en.md").exists(),
                         "Do not reintroduce an English README suffix")

        en = english_path.read_text(encoding="utf-8")
        zh = chinese_path.read_text(encoding="utf-8")
        self.assertIn("From ideas to verifiable frontend architecture", en)
        self.assertIn("从产品想法，到可验证的前端架构", zh)
        self.assertIn("[简体中文 / Chinese](./README.zh.md)", en)
        self.assertIn("[English](./README.md)", zh)
        self.assertIn("(./docs/GETTING-STARTED.md)", en)
        self.assertIn("(./docs/GETTING-STARTED.zh.md)", zh)
        for text in (en, zh):
            for token in (
                "npx skills add kunlong-luo/archvela",
                "--agent codex --agent claude-code --agent opencode",
                "V3-02", "V3-14", "V3-26",
                "62", "59", "L1", "L2/L3",
                "benchmarks/", "CONTRIBUTING.md",
            ):
                self.assertIn(token, text)
            self.assertNotIn("ln -s ", text)
            self.assertNotIn("README.en.md", text)
        self.assertIn("尚未", zh)
        self.assertIn("not", en.lower())

    def test_quickstart_languages_are_consistent(self):
        en = (ROOT / "docs/GETTING-STARTED.md").read_text(encoding="utf-8")
        zh = (ROOT / "docs/GETTING-STARTED.zh.md").read_text(encoding="utf-8")
        self.assertIn("# Getting started with Archvela", en)
        self.assertIn("# Archvela · Getting started / 快速上手", zh)
        self.assertIn("(./GETTING-STARTED.zh.md)", en)
        self.assertIn("(./GETTING-STARTED.md)", zh)
        self.assertIn("(../README.md)", en)
        self.assertIn("(../README.zh.md)", zh)
        for text in (en, zh):
            self.assertIn("npx skills add kunlong-luo/archvela", text)
            self.assertIn("--write", text)
            self.assertNotIn("README.en.md", text)

    def test_github_templates_and_safety_docs_exist(self):
        for path in (
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/pull_request_template.md",
            "SECURITY.md",
        ):
            self.assertGreater((ROOT / path).stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()
