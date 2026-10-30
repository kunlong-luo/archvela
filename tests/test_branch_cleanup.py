"""Unit tests for the one-time branch cleanup's strict, non-destructive preflight."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("archvela_cleanup", ROOT / "scripts/prune_merged_branches.py")
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)

MAIN_SHA = "f" * 40


def fake_api(path, token, *, method="GET"):
    if method != "GET":
        raise AssertionError("No delete request permitted in dry-run preflight")
    if path == "branches/main":
        return {"commit": {"sha": MAIN_SHA}}
    if path.startswith("pulls?"):
        return [{"number": 99, "head": {"ref": cleanup.SELF_BRANCH, "sha": "e" * 40},
                 "base": {"ref": "main"}, "merged_at": "2026-10-30T00:00:00Z"}]
    if path.startswith("branches/"):
        name = path.removeprefix("branches/")
        sha = ("e" * 40) if name == cleanup.SELF_BRANCH else cleanup.MERGED_BRANCHES[name][1]
        return {"protected": False, "commit": {"sha": sha}}
    if path.startswith("pulls/"):
        number = int(path.removeprefix("pulls/"))
        name, sha = next(((n, s) for n, (pr, s) in cleanup.MERGED_BRANCHES.items()
                          if pr == number), (cleanup.SELF_BRANCH, "e" * 40))
        return {"merged_at": "2026-10-30T00:00:00Z",
                "head": {"ref": name, "sha": sha, "repo": {"full_name": cleanup.REPOSITORY}},
                "base": {"ref": "main"}}
    if path.startswith("compare/"):
        return {"behind_by": 0, "status": "ahead"}
    raise AssertionError("Unrecognized API path " + path)


class CleanupTests(unittest.TestCase):
    def test_exact_allowlist_and_merge_checks(self):
        self.assertEqual(len(cleanup.MERGED_BRANCHES), 10)
        self.assertNotIn("main", cleanup.MERGED_BRANCHES)
        self.assertEqual(len(set(cleanup.MERGED_BRANCHES)), 10)
        for name, (number, sha) in cleanup.MERGED_BRANCHES.items():
            self.assertTrue(name.startswith(("feat/", "docs/", "test/", "chore/")))
            self.assertIsInstance(number, int)
            self.assertEqual(len(sha), 40)

    @patch.object(cleanup, "api", side_effect=fake_api)
    def test_preflight_verifies_all_branches_without_deletion(self, mocked):
        found = cleanup.preflight("fixture-token", MAIN_SHA)
        self.assertEqual(len(found), 11)
        self.assertIn((cleanup.SELF_BRANCH, "e" * 40), found)
        self.assertTrue(all(call.kwargs.get("method", "GET") == "GET"
                            for call in mocked.call_args_list))

    @patch.object(cleanup, "api")
    def test_preflight_fails_closed_when_main_moves(self, mocked):
        mocked.return_value = {"commit": {"sha": "a" * 40}}
        with self.assertRaisesRegex(cleanup.CleanupError, "Main changed"):
            cleanup.preflight("fixture-token", MAIN_SHA)

    @patch.object(cleanup, "api", side_effect=fake_api)
    def test_preflight_refuses_diverged_branch(self, mocked):
        def divergent(path, token, *, method="GET"):
            if path.startswith("compare/"):
                return {"status": "diverged", "behind_by": 1}
            return fake_api(path, token, method=method)
        mocked.side_effect = divergent
        with self.assertRaisesRegex(cleanup.CleanupError, "unmerged commits"):
            cleanup.preflight("fixture-token", MAIN_SHA)

    @patch.object(cleanup, "api", side_effect=fake_api)
    def test_preflight_refuses_unmerged_pr(self, mocked):
        def unmerged(path, token, *, method="GET"):
            obj = fake_api(path, token, method=method)
            if path.startswith("pulls/"):
                return {**obj, "merged_at": None}
            return obj
        mocked.side_effect = unmerged
        with self.assertRaisesRegex(cleanup.CleanupError, "PR not merged"):
            cleanup.preflight("fixture-token", MAIN_SHA)

    @patch.object(cleanup, "api", side_effect=fake_api)
    def test_preflight_refuses_moved_or_protected_branch(self, mocked):
        def moved(path, token, *, method="GET"):
            obj = fake_api(path, token, method=method)
            if path == "branches/feat/archvela-skill-v0-1":
                return {**obj, "protected": True}
            return obj
        mocked.side_effect = moved
        with self.assertRaisesRegex(cleanup.CleanupError, "Protected or changed"):
            cleanup.preflight("fixture-token", MAIN_SHA)

    def test_main_requires_trusted_context(self):
        with patch.dict("os.environ", {"GITHUB_REPOSITORY": cleanup.REPOSITORY,
                                      "GITHUB_REF": "refs/heads/not-main",
                                      "GITHUB_SHA": MAIN_SHA, "GH_TOKEN": "fixture"}, clear=True):
            with patch("sys.argv", ["cleanup.py", "--expect-sha", MAIN_SHA]):
                with patch.object(cleanup, "api", side_effect=AssertionError("No API call allowed")):
                    self.assertEqual(cleanup.main(), 2)

    @patch.object(cleanup, "api", side_effect=fake_api)
    def test_preflight_fails_without_token(self, mocked):
        with self.assertRaisesRegex(cleanup.CleanupError, "token"):
            cleanup.preflight("", MAIN_SHA)
        mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
