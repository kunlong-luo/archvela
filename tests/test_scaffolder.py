"""Safe Archvela CLI sample scaffolding tests: no node/model/network access."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/archvela_create.py"
SCENES = ("V3-02", "V3-14", "V3-26")


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                          text=True, check=False)


class ScaffoldTests(unittest.TestCase):
    def test_only_three_supported_runnable_scenes(self):
        result = cli("list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({v["scene"] for v in json.loads(result.stdout)}, set(SCENES))

    def test_preview_has_no_write_for_all_three(self):
        for scene in SCENES:
            with self.subTest(scene=scene), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp) / "workspace"
                result = cli("create", "--scene", scene, "--project", "my-new-app",
                             "--output", folder, "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data["status"], "preview")
                self.assertGreater(data["files"], 10)
                self.assertFalse(folder.exists())

    def test_creates_buildable_layout_and_scene_specific_docs(self):
        for scene in SCENES:
            with self.subTest(scene=scene), tempfile.TemporaryDirectory() as tmp:
                result = cli("create", "--scene", scene, "--project", "my-new-app",
                             "--output", tmp, "--json", "--write")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "created")
                dest = Path(tmp) / "my-new-app"
                package = json.loads((dest / "package.json").read_text(encoding="utf-8"))
                lock = json.loads((dest / "package-lock.json").read_text(encoding="utf-8"))
                self.assertEqual(package["name"], "my-new-app")
                self.assertEqual(lock["name"], "my-new-app")
                self.assertEqual(lock["packages"][""]["name"], "my-new-app")
                plan = json.loads((dest / "docs/architecture/archvela-plan.json").read_text())
                self.assertEqual(plan["scenario"]["id"], scene)
                self.assertEqual(plan["status"], "draft")
                self.assertTrue((dest / "src").is_dir())
                self.assertTrue((dest / "docs/architecture/ADR-001_frontend-architecture.md").is_file())
                self.assertFalse((dest / "node_modules").exists())
                self.assertFalse((dest / ".next").exists())
                first = (dest / "package.json").read_bytes()
                again = cli("create", "--scene", scene, "--project", "my-new-app",
                            "--output", tmp, "--write")
                self.assertEqual(again.returncode, 2)
                self.assertEqual(first, (dest / "package.json").read_bytes())

    def test_unsupported_scene_refuses_project_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = cli("create", "--scene", "V3-45", "--project", "my-app",
                           "--output", tmp, "--write")
            self.assertEqual(response.returncode, 2)
            self.assertIn("architecture-only", response.stderr)
            self.assertFalse((Path(tmp) / "my-app").exists())

    def test_rejects_symlinked_output_and_invalid_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            victim = root / "victim"
            victim.mkdir()
            link = root / "linked"
            link.symlink_to(victim, target_is_directory=True)
            result = cli("create", "--scene", "V3-26", "--project", "demo-home",
                         "--output", link, "--write")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(list(victim.iterdir()))
            bad = cli("create", "--scene", "V3-02", "--project", "../unsafe",
                      "--output", root, "--write")
            self.assertEqual(bad.returncode, 2)
            self.assertFalse((root / "unsafe").exists())


if __name__ == "__main__":
    unittest.main()
