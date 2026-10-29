"""Offline documentation integrity and truthful product-scope regressions."""
from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

DOCS = (
    "README.md",
    "README.en.md",
    "CONTRIBUTING.md",
    "docs/GETTING-STARTED.md",
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

    def test_both_readmes_present_supported_install_and_limits(self):
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        en = (ROOT / "README.en.md").read_text(encoding="utf-8")
        for text in (zh, en):
            for token in (
                "npx skills add kunlong-luo/archvela",
                "--agent codex --agent claude-code --agent opencode",
                "V3-02", "V3-14", "V3-26",
                "62", "59", "L1", "L2/L3",
                "docs/GETTING-STARTED.md",
                "benchmarks/",
                "CONTRIBUTING.md",
            ):
                self.assertIn(token, text)
            self.assertNotIn("ln -s ", text)
        self.assertIn("尚未", zh)
        self.assertIn("not", en.lower())

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
