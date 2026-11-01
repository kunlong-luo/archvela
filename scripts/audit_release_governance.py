#!/usr/bin/env python3
"""Read-only live GitHub release governance report; NEVER publishes or approves.

The script checks repository/branch/Actions observations against the frozen
local Alpha candidate manifest. It can find blockers, but GitHub API success
cannot prove legal rights, real native Agent runs or owner authorization.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "kunlong-luo/archvela"
EXPECTED_WORKFLOWS = (
    "Validate Archvela Skill",
    "Cross-Agent Skill Installer Compatibility",
    "Verify dependency lockfiles",
    "Build Runnable Architecture Examples",
    "Generated projects — build smoke",
    "Browser E2E — three starters",
    "Security scanning",
)
HARD_GATES = (
    "release_owner_approved",
    "rights_review_approved",
    "main_protection_verified",
    "actual_l2_smoke_verified",
    "final_ci_verified",
)


class Unverifiable(RuntimeError):
    """An API observation could not be made or authenticated."""


def api_get(repo: str, suffix: str) -> object:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Expected a safe owner/repository name")
    if suffix and (not suffix.startswith("/") or "//" in suffix or "://" in suffix):
        raise ValueError("Invalid GitHub API resource path")
    url = "https://api.github.com/repos/" + repo + suffix
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "archvela-readonly-release-governance/1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(url, headers=headers), timeout=20) as response:
            if response.status != 200:
                raise Unverifiable("Unexpected GitHub API response status")
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        # Never print credentials, Authorization header, or response body.
        status = getattr(exc, "code", None)
        raise Unverifiable(
            "GitHub API unreadable (HTTP " + str(status) + ")" if status
            else "GitHub API unreadable (network or JSON error)"
        ) from None


def evaluate(
    repo_data: dict,
    branch_data: dict,
    runs_data: dict,
    releases_data: list,
    rulesets_data: list | None,
    manifest: dict,
    expected_sha: str | None = None,
) -> dict:
    """Pure function suitable for fixture-based security regression tests."""
    if repo_data.get("default_branch") != "main" or branch_data.get("name") != "main":
        raise Unverifiable("Default branch differs from intended main")
    sha = branch_data.get("commit", {}).get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Unverifiable("Main commit SHA absent/invalid")
    if expected_sha is not None and (not re.fullmatch(r"[0-9a-f]{40}", expected_sha)
                                     or expected_sha != sha):
        raise Unverifiable("Remote main does not match pinned expected SHA")
    if manifest.get("kind") != "archvela_unpublished_release_candidate":
        raise Unverifiable("Local candidate manifest missing/incorrect")
    if (manifest.get("tag") != "v0.1.0-alpha.1"
            or manifest.get("skill_version") != "0.1.0-alpha.1"):
        raise Unverifiable("Candidate tag and Skill version differ")
    if manifest.get("state") != "draft_not_approved":
        raise Unverifiable("Draft manifest has an unreviewed state change")
    if not isinstance(releases_data, list):
        raise Unverifiable("Release API did not return a list")

    observations = {}
    by_workflow = {}
    source_runs = runs_data.get("workflow_runs")
    if not isinstance(source_runs, list):
        raise Unverifiable("Actions runs list unavailable")
    for run in source_runs:
        if (run.get("head_sha") != sha or run.get("head_branch") != "main"
                or run.get("event") != "push"):
            continue
        name = run.get("name")
        if name not in EXPECTED_WORKFLOWS:
            continue
        prior = by_workflow.get(name)
        # GitHub runs may contain repeated attempts/reruns: prefer latest run ID.
        if prior is None or (isinstance(run.get("id"), int)
                             and run["id"] > (prior.get("id") or 0)):
            by_workflow[name] = run
    for name in EXPECTED_WORKFLOWS:
        item = by_workflow.get(name)
        if item is None:
            observations[name] = "missing"
        elif item.get("status") != "completed":
            observations[name] = "in_progress"
        elif item.get("conclusion") == "success":
            observations[name] = "success"
        else:
            observations[name] = "failed_or_inconclusive"
    ci_passed = all(x == "success" for x in observations.values())

    branch_protected = branch_data.get("protected") is True
    ruleset_count = len(rulesets_data) if rulesets_data is not None else None
    auto_delete = repo_data.get("delete_branch_on_merge") is True
    hard_status = {}
    for gate in HARD_GATES:
        # A checked-in, unsigned string or even a true boolean cannot itself
        # prove legal sign-off, owner settings or a real Codex session.
        hard_status[gate] = "pending" if manifest.get(gate) is False else "requires_independent_verification"
    blockers = []
    if not branch_protected:
        blockers.append("main_unprotected")
    if not ci_passed:
        blockers.append("main_ci_not_7_of_7_success")
    if releases_data:
        blockers.append("a_release_already_exists_check_before_tagging")
    if manifest.get("release_created") is not False or manifest.get("tag_created") is not False:
        blockers.append("candidate_artifact_claim_changed")
    if manifest.get("release_sha") is not None:
        blockers.append("candidate_release_sha_requires_independent_review")
    blockers.extend("unverified_" + gate for gate in HARD_GATES)
    # Branch protected=true is only the first layer; required PR/status settings
    # and bypass policies cannot be inferred from this public endpoint.
    blockers.append("owner_must_confirm_required_pr_checks_and_bypass_settings")
    if not auto_delete:
        # Recommended hygiene but not a hard release criterion in isolation.
        maintenance = ["auto_delete_merged_branches_disabled"]
    else:
        maintenance = []
    return {
        "schema_version": 1,
        "kind": "read_only_live_release_governance",
        "candidate": manifest["tag"],
        "main_sha": sha,
        "main_protected": branch_protected,
        "rulesets_visible_count": ruleset_count,
        "auto_delete_merged_branches": auto_delete,
        "main_ci_workflows": observations,
        "main_ci_7_of_7_success": ci_passed,
        "github_releases_observed": len(releases_data),
        "hard_gate_evidence": hard_status,
        "release_ready": False,
        "blocked_reasons": blockers,
        "maintenance_recommendations": maintenance,
        "caveat": "Read-only evidence from public GitHub APIs and unsigned local draft. No owner approval, legal clearance, genuine Codex L2/L3 outcome or tag/Release can be established by this report.",
    }


def live_report(repo: str, expected_sha: str | None = None) -> dict:
    repo_data = api_get(repo, "")
    branch_data = api_get(repo, "/branches/main")
    sha = branch_data.get("commit", {}).get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Unverifiable("Cannot verify main SHA")
    runs_data = api_get(repo, "/actions/runs?head_sha=" + sha + "&per_page=100")
    releases_data = api_get(repo, "/releases?per_page=20")
    try:
        rulesets_data = api_get(repo, "/rulesets")
    except Unverifiable:
        # An inaccessible ruleset API is UNKNOWN, not proof of no rulesets.
        rulesets_data = None
    manifest = json.loads((ROOT / "docs/RELEASE-CANDIDATE.json").read_text(encoding="utf-8"))
    return evaluate(repo_data, branch_data, runs_data, releases_data,
                    rulesets_data, manifest, expected_sha=expected_sha)


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only public GitHub Alpha governance audit")
    p.add_argument("--repo", default=DEFAULT_REPO)
    p.add_argument("--expected-sha", help="40-char commit; reject source drift")
    p.add_argument("--json", action="store_true", help="Print machine-readable report")
    p.add_argument("--require-ready", action="store_true",
                   help="Exit nonzero unless actually approved (never inferred)")
    args = p.parse_args()
    try:
        result = live_report(args.repo, expected_sha=args.expected_sha)
    except (Unverifiable, ValueError, OSError, KeyError, TypeError) as exc:
        print("RELEASE-GOVERNANCE-UNVERIFIABLE: " + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ALPHA-GOVERNANCE: main={result['main_sha'][:12]}, "
              f"protected={result['main_protected']}, "
              f"CI={sum(v == 'success' for v in result['main_ci_workflows'].values())}/7, "
              f"published-releases={result['github_releases_observed']}, "
              "RELEASE NOT APPROVED")
    if args.require_ready and not result["release_ready"]:
        print("RELEASE BLOCKED: independent owner/rights/native-client proof still required",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
