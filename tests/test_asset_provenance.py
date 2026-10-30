"""Provenance guard is an inventory check, never legal verification."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/check_asset_provenance.py"
spec = importlib.util.spec_from_file_location("archvela_provenance", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AssetProvenanceTests(unittest.TestCase):
    def make_repo(self, root: Path, assets=None):
        (root / "docs").mkdir(exist_ok=True)
        (root / "docs/ASSET-PROVENANCE.json").write_text(
            json.dumps({"schema_version": 1, "assets": assets or []}),
            encoding="utf-8",
        )

    def test_current_repository_inventory_has_no_unlisted_media(self):
        result = mod.verify(ROOT)
        self.assertEqual(result["inventory_check"], "passed")
        self.assertEqual(result["media_files"], result["manifest_entries"])

    def test_unrecorded_media_file_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_repo(root)
            (root / "sample.png").write_bytes(b"test fixture not a real image")
            with self.assertRaisesRegex(ValueError, "unrecorded"):
                mod.verify(root)

    def test_declared_media_requires_human_rights_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "media").mkdir()
            (root / "media/figure.svg").write_text("<svg/>", encoding="utf-8")
            manifest = {
                "path": "media/figure.svg",
                "origin": "original",
                "rights_holder": "TEST FIXTURE",
                "license": "MIT",
                "source": "TEST FIXTURE",
                "attribution": "none",
                "reviewed_on": "2026-10-30",
                "redistribution_approved": False,
            }
            self.make_repo(root, [manifest])
            with self.assertRaisesRegex(ValueError, "approved"):
                mod.verify(root)
            manifest["redistribution_approved"] = True
            self.make_repo(root, [manifest])
            self.assertEqual(mod.verify(root)["media_files"], 1)
            (root / "media/figure.svg").unlink()
            with self.assertRaisesRegex(ValueError, "stale"):
                mod.verify(root)

    def test_reject_symlinked_media_and_duplicate_records(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_repo(root)
            (root / "real.svg").write_text("<svg/>")
            (root / "linked.svg").symlink_to(root / "real.svg")
            with self.assertRaisesRegex(ValueError, "symlink"):
                mod.verify(root)
            (root / "linked.svg").unlink()
            sample = {
                "path": "real.svg", "origin": "original",
                "rights_holder": "TEST", "license": "MIT",
                "source": "fixture", "attribution": "none",
                "reviewed_on": "2026-10-30", "redistribution_approved": True,
            }
            self.make_repo(root, [sample, sample])
            with self.assertRaisesRegex(ValueError, "duplicate"):
                mod.verify(root)


if __name__ == "__main__":
    unittest.main()
