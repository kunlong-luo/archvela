#!/usr/bin/env python3
"""One-time, tightly scoped cleanup of already-merged Archvela Git branches.

The script never deletes by default. Its execute mode is intended ONLY for the
one-time main-branch GitHub Actions workflow, under the repository's ephemeral
contents:write token. Preflight is all-or-nothing; any mismatch aborts deletion.
No arbitrary branch, repository, token or force-delete argument is accepted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = "kunlong-luo/archvela"
MAIN = "main"
SELF_BRANCH = "chore/v03-repository-hardening-20261030"
# Source: 2026-10-30 GitHub PR and branch API audit. All were merged to main.
# Branch heads must match both this inventory and their merged PR records.
MERGED_BRANCHES = {
    "feat/archvela-skill-v0-1": (1, "069cd670e27e7af1fab9e326bcc850d217ca26e5"),
    "feat/runnable-starters-v0-2": (6, "c21a35a9a0ffd629c621f8d9ba58025c365f4ce4"),
    "feat/release-guardrails-agent-benchmarks": (7, "886526a73eadf7a1a70d2c5b37fd4fdedc873bd2"),
    "feat/unified-starter-generator": (8, "5b8d8915f870ddc68dd09e901070787762ce4c31"),
    "docs/post-merge-readiness-20261029": (19, "5f91bcf95a39e7be2e4dc2530146eb165e916246"),
    "chore/dependabot-node24-major-guard-20261029": (20, "9992c9169c15b12e435786f620b8cc7640fb5c3f"),
    "feat/v0-3-agent-pilot-install-ux": (22, "7a16527779e54313f1331629734b7d58f728b950"),
    "test/v0-3-public-source-skill-install": (23, "e59aee9b7896b440535e163c2a5cad7e77079dd4"),
    "docs/readme-open-source-quality-v03": (24, "bd14beb8c44d87138dc5ee45cfb7fbd1d2263552"),
    "docs/english-first-readme-20261029": (25, "14d9f36d23cc596ccc425091fba49a0916c08c38"),
}


class CleanupError(RuntimeError):
    pass


def api(path: str, token: str, *, method: str = "GET"):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + REPOSITORY + "/" + path,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "archvela-one-time-branch-cleanup",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read()
            return json.loads(data) if data else None
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and method == "GET":
            return None
        raise CleanupError(f"GitHub API {method} {path} failed (HTTP {exc.code})") from exc


def branch_path(name: str) -> str:
    # Repo-controlled allowlist only; GitHub REST branch ref accepts slashes.
    return urllib.parse.quote(name, safe="/")


def find_merged_pr(name: str, token: str) -> dict:
    # Only the cleanup PR's own branch is discovered dynamically. It must be
    # merged to main first and must match exactly one qualifying PR.
    encoded = urllib.parse.quote("kunlong-luo:" + name, safe="")
    items = api("pulls?state=closed&head=" + encoded + "&per_page=100", token)
    valid = [
        item for item in (items or [])
        if item.get("head", {}).get("ref") == name
        and item.get("base", {}).get("ref") == MAIN
        and item.get("merged_at")
    ]
    if len(valid) != 1:
        raise CleanupError("Expected exactly one merged cleanup PR for " + name)
    return valid[0]


def preflight(token: str, expected_main: str) -> list[tuple[str, str]]:
    if not token or len(expected_main) != 40:
        raise CleanupError("Authenticated token and 40-character main SHA are required")
    current = api("branches/" + MAIN, token)
    if not current or current.get("commit", {}).get("sha") != expected_main:
        raise CleanupError("Main changed since workflow start; refusing cleanup")
    planned = dict(MERGED_BRANCHES)
    # The branch carrying this one-time cleanup must also be removed after it
    # merges: no new stale remote branch should be left by this operation.
    self_pr = find_merged_pr(SELF_BRANCH, token)
    planned[SELF_BRANCH] = (self_pr["number"], self_pr["head"]["sha"])

    deletions: list[tuple[str, str]] = []
    for name, (number, pinned_sha) in planned.items():
        if name == MAIN or not name or len(pinned_sha) != 40:
            raise CleanupError("Unsafe cleanup allowlist entry")
        remote = api("branches/" + branch_path(name), token)
        if remote is None:
            print("Already absent: " + name)
            continue
        sha = remote.get("commit", {}).get("sha")
        if remote.get("protected") or sha != pinned_sha:
            raise CleanupError("Protected or changed branch: " + name)
        pr = api("pulls/" + str(number), token)
        if not pr or not pr.get("merged_at"):
            raise CleanupError("PR not merged: #" + str(number))
        if pr.get("head", {}).get("ref") != name or pr.get("head", {}).get("sha") != sha:
            raise CleanupError("PR head or SHA mismatch: " + name)
        if pr.get("base", {}).get("ref") != MAIN or (
            pr.get("head", {}).get("repo") or {}
        ).get("full_name") != REPOSITORY:
            raise CleanupError("PR was not merged from this repository to main: " + name)
        comparison = api("compare/" + sha + "..." + expected_main, token)
        if not comparison or comparison.get("behind_by") != 0 or (
            comparison.get("status") not in ("ahead", "identical")
        ):
            raise CleanupError("Branch contains unmerged commits: " + name)
        deletions.append((name, sha))
    return deletions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Perform approved remote deletion after full preflight")
    parser.add_argument("--expect-sha", required=True, help="Pinned main push SHA (full 40 hex characters)")
    args = parser.parse_args()
    try:
        if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
            raise CleanupError("Repository identity mismatch; only Archvela is allowed")
        if os.environ.get("GITHUB_REF") != "refs/heads/main":
            raise CleanupError("Only a trusted push to main can run cleanup")
        if os.environ.get("GITHUB_SHA") != args.expect_sha:
            raise CleanupError("Workflow commit SHA mismatch")
        token = os.environ.get("GH_TOKEN", "")
        plan = preflight(token, args.expect_sha)
        print(f"Preflight passed for {len(plan)} merged, unchanged branches.")
        for name, _ in plan:
            print("Eligible: " + name)
        if not args.execute:
            print("Dry-run only; no GitHub refs were changed.")
            return 0
        # Revalidate each remote branch immediately before its deletion.
        for name, pinned_sha in plan:
            remote = api("branches/" + branch_path(name), token)
            if remote is None or remote.get("protected") or (
                remote.get("commit", {}).get("sha") != pinned_sha
            ):
                raise CleanupError("Branch changed after preflight; abort: " + name)
            api("git/refs/heads/" + branch_path(name), token, method="DELETE")
            print("Deleted merged branch: " + name)
        print(f"Deleted {len(plan)} previously merged branches; main was untouched.")
        return 0
    except (CleanupError, KeyError, TypeError, ValueError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
