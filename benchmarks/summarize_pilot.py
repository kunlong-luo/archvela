#!/usr/bin/env python3
"""Summarize real-agent pilot evidence WITHOUT running models or inventing scores.

Inputs: a complete operator pilot directory, optionally a human-edited
blind-review.json matching the exported blank-review schema. Repeat --study
and --review in the same order for Codex, Claude Code and OpenCode.

Output is OPERATOR ONLY until all reviews and privacy checks are complete.
Validation of file structure and self-reported data is NOT model verification.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from audit_pilot import audit, safe_file, validate_manifest
from evaluate import RUBRIC

ARMS = ("baseline", "archvela")
STATUS = ("completed", "failed", "blocked")


def load_review(path: Path, ids: set[str], outcomes: dict[str, str]) -> dict[str, float | None]:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 8_000_000:
        raise ValueError("Review must be a bounded regular non-symlinked file")
    sheet = json.loads(path.read_text(encoding="utf-8"))
    if sheet.get("schema_version") != 1 or sheet.get("kind") != "blind_response_only_ungraded":
        raise ValueError("Review sheet must match the exported blind-review schema")
    rows = sheet.get("records")
    if not isinstance(rows, list) or len(rows) != len(ids):
        raise ValueError("Review sheet has missing or extra records")
    observed = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("blind_id"), str):
            raise ValueError("Invalid review record")
        blind = row["blind_id"]
        if blind in observed or blind not in ids:
            raise ValueError("Review contains duplicated or unknown blind ID")
        grades = row.get("grades")
        if not isinstance(grades, dict) or set(grades) != set(RUBRIC):
            raise ValueError("Review must have the exact five rubric dimensions")
        scores = [grades[key] for key in RUBRIC]
        has_score = any(value is not None for value in scores)
        reviewer = row.get("reviewer")
        if outcomes[blind] != "completed":
            if has_score:
                raise ValueError("Do not grade failed or blocked attempts as completed outputs")
            observed[blind] = None
            continue
        if not has_score:
            # The template is deliberately ungraded; retain pending status.
            if reviewer is not None and (not isinstance(reviewer, str) or not reviewer.strip()):
                raise ValueError("Invalid reviewer identifier")
            observed[blind] = None
            continue
        if (any(type(value) is not int or not 0 <= value <= 4 for value in scores)
                or not isinstance(reviewer, str) or not reviewer.strip()):
            raise ValueError("Partial, invalid or unreviewed human grades")
        observed[blind] = sum(scores) / (4 * len(RUBRIC))
    if set(observed) != ids:
        raise ValueError("Unmatched blind-review IDs")
    return observed


def summarize_study(study_dir: Path, review_path: Path | None = None) -> dict:
    # Audit preserves true negative cases and flags contaminated baselines.
    evidence = audit(study_dir)
    if not evidence["all_evidence_present"]:
        raise ValueError("Pilot evidence is incomplete; do not silently drop missing sessions")
    study = study_dir.expanduser().resolve(strict=True)
    manifest = json.loads(safe_file(study, Path("operator-manifest.json")).read_text(encoding="utf-8"))
    runs = validate_manifest(manifest, study)
    by_id = {row["blind_id"]: row for row in evidence["evidence"]}
    if set(by_id) != {run["blind_id"] for run in runs}:
        raise ValueError("Audit and manifest have different recorded sessions")
    outcomes = {blind: data["execution_status"] for blind, data in by_id.items()}
    grades = load_review(review_path, set(by_id), outcomes) if review_path is not None else {
        blind: None for blind in by_id
    }

    totals = {arm: {status: 0 for status in STATUS} for arm in ARMS}
    treatment_discovery = {"observed_true": 0, "observed_false": 0, "unknown": 0}
    per_task = defaultdict(dict)
    for run in runs:
        blind, arm, task = run["blind_id"], run["arm"], run["task_id"]
        row = by_id[blind]
        totals[arm][row["execution_status"]] += 1
        per_task[task][arm] = (blind, row)
        if arm == "archvela":
            key = {True: "observed_true", False: "observed_false", None: "unknown"}[
                row["skill_discovered"]
            ]
            treatment_discovery[key] += 1

    if any(set(arms) != set(ARMS) for arms in per_task.values()):
        raise ValueError("Unpaired pilot tasks")
    full_pairs = []
    for task, arms in sorted(per_task.items()):
        baseline_id, baseline = arms["baseline"]
        treated_id, treated = arms["archvela"]
        # Report the actual number of eligible completed, reviewed pairs,
        # not just positive outcomes. Failure/dropout counts stay in totals.
        if (baseline["execution_status"] == "completed" and
                treated["execution_status"] == "completed" and
                grades[baseline_id] is not None and grades[treated_id] is not None):
            full_pairs.append({
                "task_id": task,
                "baseline_human_grade": round(grades[baseline_id], 4),
                "treatment_human_grade": round(grades[treated_id], 4),
                "paired_delta": round(grades[treated_id] - grades[baseline_id], 4),
                "treatment_skill_discovered": treated["skill_discovered"],
            })
    # Do not publish an effect estimate if any pair is missing, a baseline
    # is contaminated, or human review is absent. Reporting selected positive
    # completed pairs only would bias the apparent treatment effectiveness.
    full_study_scored = (
        evidence["protocol_valid"]
        and len(full_pairs) == len(per_task)
        and len(per_task) > 0
    )
    paired_mean_delta = (
        round(sum(row["paired_delta"] for row in full_pairs) / len(full_pairs), 4)
        if full_study_scored else None
    )
    return {
        "agent": manifest["agent"],
        "model": manifest["model"],
        "skill_commit": manifest["skill_commit"],
        "cases_sha256": manifest["cases_sha256"],
        "seed": manifest["seed"],
        "trial": manifest["trial"],
        "task_ids": sorted(per_task),
        "expected_sessions": len(runs),
        "evidence_complete_sessions": evidence["evidence_complete_runs"],
        "protocol_valid": evidence["protocol_valid"],
        "outcomes_by_arm": totals,
        "treatment_discovery": treatment_discovery,
        "discovery_deviations": [
            # Reasons are structural labels only; no private response or logs.
            item["type"] for item in evidence["discovery_deviations"]
        ],
        "human_graded_completed_sessions": sum(v is not None for v in grades.values()),
        "human_graded_pairs": len(full_pairs),
        "full_study_human_delta": paired_mean_delta,
        "human_score_coverage": "complete" if full_study_scored else "incomplete_or_contaminated",
        "negative_or_missing_grade_policy": "No imputation, no silent exclusion, no partial-pair treatment effect",
    }


def report(studies: list[Path], reviews: list[Path] | None) -> dict:
    if not studies:
        raise ValueError("At least one study is required")
    if reviews is not None and len(reviews) != len(studies):
        raise ValueError("Exactly one review sheet per study is required")
    results = [
        summarize_study(path, reviews[i] if reviews is not None else None)
        for i, path in enumerate(studies)
    ]
    names = [row["agent"] for row in results]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate client studies are not allowed")
    signatures = {(tuple(row["task_ids"]), row["skill_commit"], row["cases_sha256"],
                   row["seed"], row["trial"]) for row in results}
    if len(signatures) != 1:
        raise ValueError("Clients must share tasks, pinned Skill, cases, seed and trial")
    complete_three_client_pilot = (
        set(names) == {"codex", "claude-code", "opencode"}
        and len(results) == 3
        and all(row["expected_sessions"] == 4 and len(row["task_ids"]) == 2 for row in results)
    )
    summary = {
        "schema_version": 1,
        "kind": "operator_only_self_reported_pilot_summary",
        "client_count": len(results),
        "planned_three_client_pilot": complete_three_client_pilot,
        "total_expected_sessions": sum(row["expected_sessions"] for row in results),
        "total_evidence_complete_sessions": sum(row["evidence_complete_sessions"] for row in results),
        "total_failed_or_blocked": sum(
            row["outcomes_by_arm"][arm][status]
            for row in results for arm in ARMS for status in ("failed", "blocked")
        ),
        "total_human_graded_pairs": sum(row["human_graded_pairs"] for row in results),
        "clients": results,
        "caveat": (
            "Operator-supplied session metadata and blinded human scores are not "
            "independently verified model executions. No pooled cross-client "
            "effect estimate, no imputation, no publication or statistical "
            "significance claim. Fixture data must never be presented as real."
        ),
    }
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description="Summarize one or three paired real-client pilot bundles")
    p.add_argument("--study", action="append", type=Path, required=True)
    p.add_argument("--review", action="append", type=Path,
                   help="Repeat exactly once per --study; independent human-edited blank-review.json")
    args = p.parse_args()
    try:
        result = report(args.study, args.review)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if all(row["protocol_valid"] for row in result["clients"]) else 2
    except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
