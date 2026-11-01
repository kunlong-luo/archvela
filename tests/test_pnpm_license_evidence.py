"""Fixture tests for pnpm virtual-store LICENSE/NOTICE evidence (not legal clearance)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "archvela_pnpm_license", ROOT / "scripts/collect_pnpm_license_evidence.py"
)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class PnpmInstalledEvidenceTests(unittest.TestCase):
    def fixture(self, base: Path) -> Path:
        base.mkdir(parents=True, exist_ok=True)
        (base / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\nimporters:\n  .:\n", encoding="utf-8")
        (base / "package.json").write_text(
            json.dumps({"name": "fixture", "private": True, "packageManager": "pnpm@10.22.0",
                        "dependencies": {"@demo/foo": "1.0.0", "thing": "2.0.0"}}),
            encoding="utf-8",
        )
        store = base / "node_modules/.pnpm"
        first = store / "@demo+foo@1.0.0/node_modules/@demo/foo"
        second = store / "thing@2.0.0/node_modules/thing"
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        for pkg, name, version in ((first, "@demo/foo", "1.0.0"), (second, "thing", "2.0.0")):
            (pkg / "package.json").write_text(
                json.dumps({"name": name, "version": version, "license": "MIT"}),
                encoding="utf-8",
            )
        (first / "LICENSE").write_text("Fixture copyright only", encoding="utf-8")
        (store / "thing@2.0.0/node_modules/foreign-link").symlink_to(
            second, target_is_directory=True
        )
        return base

    def test_actual_virtual_store_roots_and_no_legal_clearance(self):
        with tempfile.TemporaryDirectory() as d:
            report = audit.inventory(self.fixture(Path(d) / "app"))
            self.assertEqual(report["installed_package_rows"], 2)
            self.assertEqual(report["installed_rows_without_top_level_license_or_notice"], 1)
            self.assertFalse(report["rights_cleared"])
            self.assertEqual(report["uninstalled_optional_platform_rows"], "not_measured")
            self.assertEqual(len(report["rows"][0]["license_notice_files"][0]["sha256"]), 64)

    def test_missing_required_direct_dependency_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(Path(d) / "app")
            (root / "node_modules/.pnpm/thing@2.0.0/node_modules/thing/package.json").unlink()
            with self.assertRaisesRegex(ValueError, "Required direct"):
                audit.inventory(root)

    def test_unsafe_license_symlink_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(Path(d) / "app")
            pkg = root / "node_modules/.pnpm/thing@2.0.0/node_modules/thing"
            (pkg / "NOTICE").symlink_to(root / "pnpm-lock.yaml")
            with self.assertRaisesRegex(ValueError, "Unsafe license symlink"):
                audit.inventory(root)

    def test_bad_pin_and_missing_lock_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(Path(d) / "app")
            p = root / "pnpm-lock.yaml"
            p.write_text("wrong", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "lockfile format"):
                audit.inventory(root)


if __name__ == "__main__":
    unittest.main()
