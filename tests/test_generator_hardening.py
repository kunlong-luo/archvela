"""Scenario-driven output, no-overwrite, symlink and failure-rollback regression tests."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".agents/skills/archvela-architect"
SCRIPT = BASE / "scripts/new_project_docs.py"
PROFILES = BASE / "references/architecture_profiles.json"

def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *[str(s) for s in args]],
                          capture_output=True, text=True, check=False)

class GeneratorHardeningTests(unittest.TestCase):
    def test_six_domain_profiles_complete(self):
        profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
        self.assertEqual(set(profiles), {"01", "02", "03", "04", "05", "06"})
        fields = ("name", "package", "feature", "chunk", "assets", "fallback",
                  "risk", "m1", "m2", "m3", "quality")
        for entry in profiles.values():
            self.assertTrue(all(entry.get(f) for f in fields))

    def test_all_domains_generate_specific_three_docs(self):
        for scene_id, phrase in [
            ("V3-01", "Hero poster"), ("V3-14", "Monaco"),
            ("V3-25", "Cesium"), ("V3-37", "音频"),
            ("V3-45", "状态机"), ("V3-54", "GeoJSON"),
        ]:
            with self.subTest(scene=scene_id), tempfile.TemporaryDirectory() as folder:
                out = Path(folder) / "demo"
                result = cli("--scene", scene_id, "--project", "demo", "--output", out,
                             "--write")
                self.assertEqual(result.returncode, 0, result.stderr)
                docs = list((out / "docs/architecture").glob("*.md"))
                self.assertEqual(len(docs), 3)
                for doc in docs:
                    content = doc.read_text(encoding="utf-8")
                    self.assertIn(scene_id, content)
                    self.assertIn(phrase, content)

    def test_json_dry_run_is_machine_readable_and_no_write(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "project"
            res = cli("--scene", "V3-26", "--project", "demo",
                      "--output", out, "--json")
            self.assertEqual(res.returncode, 0, res.stderr)
            info = json.loads(res.stdout)
            self.assertEqual(len(info["paths"]), 3)
            self.assertEqual(info["mode"], "dry-run")
            self.assertFalse(out.exists())

    def test_existing_file_does_not_get_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            out = folder / "project"
            dest = out / "docs/architecture"
            dest.mkdir(parents=True)
            old = dest / "frontend-performance-budget.md"
            old.write_text("DO NOT ALTER", encoding="utf-8")
            res = cli("--scene", "V3-26", "--project", "demo",
                      "--output", out, "--write")
            self.assertEqual(res.returncode, 2)
            self.assertEqual(old.read_text(encoding="utf-8"), "DO NOT ALTER")
            self.assertEqual(len(list(dest.iterdir())), 1)

    def test_symlinked_target_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            top = Path(folder)
            victim = top / "victim"
            victim.mkdir()
            project = top / "project"
            project.mkdir()
            (project / "docs").symlink_to(victim, target_is_directory=True)
            res = cli("--scene", "V3-26", "--project", "demo",
                      "--output", project, "--write")
            self.assertEqual(res.returncode, 2, res.stderr)
            self.assertFalse(list(victim.iterdir()))

    def test_rolls_back_if_second_file_fails(self):
        spec = importlib.util.spec_from_file_location("archvela_gen_harden", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = Path.open
        def inject_failure(self, mode="r", *args, **kwargs):
            if self.name == "frontend-performance-budget.md" and mode == "x":
                raise OSError("injected write failure")
            return original(self, mode, *args, **kwargs)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "newproject"
            args = ["generator", "--scene", "V3-26", "--project", "test",
                    "--output", str(target), "--write"]
            with mock.patch.object(sys, "argv", args):
                with mock.patch("pathlib.Path.open", new=inject_failure):
                    result = module.main()
            self.assertEqual(result, 3)
            self.assertFalse(target.exists())

    def test_rejects_control_characters(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "project"
            res = cli("--scene", "V3-26", "--project", "hello\nnew-section",
                      "--output", out, "--write")
            self.assertNotEqual(res.returncode, 0)
            self.assertFalse(out.exists())

if __name__ == "__main__":
    unittest.main()
