#!/usr/bin/env python3
"""Audit operator-supplied evidence WITHOUT running or scoring AI agents.

Valid negative observations (failed calls, missing Skill discovery) MUST survive.
The report includes arm assignments: it is OPERATOR ONLY, never blind review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

from evaluate import DATA, load_cases, make_manifest

ID = re.compile(r"^[0-9a-f]{16}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_BYTES = 8_000_000
OUTCOMES = {"completed", "failed", "blocked"}
FAILURES = {
    "client_error", "model_error", "installation_error",
    "skill_discovery_failure", "budget_exceeded", "safety_refusal",
    "environment_error", "other",
}


def safe_file(study: Path, relative: Path) -> Path:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError("Unsafe relative evidence path: " + str(relative))
    path = study
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Evidence path contains symlink: " + str(relative))
    path = path.resolve(strict=True)
    if not path.is_relative_to(study) or not path.is_file():
        raise ValueError("Evidence must be a regular file within study: " + str(relative))
    size = path.stat().st_size
    if not 0 < size <= MAX_BYTES:
        raise ValueError("Evidence file empty or too large: " + str(relative))
    return path


def evidence_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as reader:
        for part in iter(lambda: reader.read(65536), b""):
            h.update(part)
    return h.hexdigest()


def utc_timestamp(value: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("Timestamp must be an ISO8601 UTC string")
    try:
        timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid UTC timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != dt.timedelta():
        raise ValueError("Timestamp must specify UTC timezone")
    return timestamp


def validate_manifest(manifest: dict) -> list[dict]:
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "operator_only_unexecuted_pilot":
        raise ValueError("Unexpected operator manifest")
    if manifest.get("agent") not in ("codex", "claude-code", "opencode"):
        raise ValueError("Unexpected client in pilot manifest")
    if not SHA.fullmatch(str(manifest.get("skill_commit", ""))):
        raise ValueError("Study must pin a full Git commit")
    if manifest.get("executed_runs") != 0:
        raise ValueError("Pilot generator must not claim execution")
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != manifest.get("cases_sha256"):
        raise ValueError("Benchmark cases changed after pilot preparation")
    model = manifest.get("model")
    task_ids = manifest.get("task_ids")
    if (not isinstance(model, str) or not model.strip()
            or not isinstance(task_ids, list) or not task_ids
            or len(set(task_ids)) != len(task_ids)
            or any(not isinstance(t, str) for t in task_ids)):
        raise ValueError("Invalid model or task list")
    known = {case["id"]: case for case in load_cases()}
    if any(t not in known for t in task_ids):
        raise ValueError("Unknown task in pilot")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 2 * len(task_ids):
        raise ValueError("Pilot run count must equal selected tasks x two arms")
    ids = [r.get("blind_id") for r in runs if isinstance(r, dict)]
    if (len(ids) != len(runs) or len(set(ids)) != len(ids)
            or any(not isinstance(i, str) or not ID.fullmatch(i) for i in ids)):
        raise ValueError("Invalid or duplicate blind ID")
    # Reconstruct the exact randomized assignment instead of accepting
    # modified arm labels or forged blind IDs in operator-manifest.json.
    regenerated = make_manifest(manifest["seed"], model, manifest["trial"])
    expected = {
        row["blind_id"]: row for row in regenerated["runs"]
        if row["task_id"] in task_ids
    }
    if set(expected) != set(ids):
        raise ValueError("Pilot blind IDs changed since preparation")
    for row in runs:
        if row != expected[row["blind_id"]]:
            raise ValueError("Pilot task, arm, prompt or metadata was modified")
    return runs


def audit(study_dir: Path) -> dict:
    if study_dir.is_symlink():
        raise ValueError("Study root cannot be a symlink")
    study = study_dir.expanduser().resolve(strict=True)
    if not study.is_dir():
        raise ValueError("Study must be a directory")
    manifest_file = safe_file(study, Path("operator-manifest.json"))
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    runs = validate_manifest(manifest)
    present = []
    missing = []
    deviations = []
    status_counts = {name: 0 for name in sorted(OUTCOMES)}
    for run in runs:
        blind = run["blind_id"]
        arm = run["arm"]
        response = Path("reviewer/artifacts") / (blind + ".response.md")
        logfile = Path("reviewer/artifacts") / (blind + ".run.log")
        metadata = Path("operator") / blind / "session.json"
        files = (response, logfile, metadata)
        absent = [str(f) for f in files if not (study / f).exists()]
        if absent:
            missing.append({"blind_id": blind, "missing": absent})
            continue
        paths = [safe_file(study, f) for f in files]
        data = json.loads(paths[2].read_text(encoding="utf-8"))
        if (data.get("blind_id") != blind or data.get("agent") != manifest["agent"]
                or data.get("model") != manifest["model"]):
            raise ValueError("Actual session identity mismatch: " + blind)
        if data.get("skill_commit") != manifest["skill_commit"]:
            raise ValueError("Session pinned Skill version mismatch: " + blind)
        client_version = data.get("client_version")
        if not isinstance(client_version, str) or not client_version.strip():
            raise ValueError("Missing actual client version: " + blind)
        start = utc_timestamp(data.get("started_at_utc"))
        end = utc_timestamp(data.get("finished_at_utc"))
        if end <= start:
            raise ValueError("Invalid session time order: " + blind)
        status = data.get("execution_status")
        if status not in OUTCOMES:
            raise ValueError("Invalid execution status: " + blind)
        discovery = data.get("skill_discovered")
        if discovery is not None and type(discovery) is not bool:
            raise ValueError("Invalid Skill discovery observation: " + blind)
        if status == "completed" and discovery is None:
            raise ValueError("Completed session needs an observed discovery flag: " + blind)
        category = data.get("failure_category")
        reason = data.get("failure_detail")
        if status != "completed":
            if category not in FAILURES or not isinstance(reason, str) or not reason.strip():
                raise ValueError("Failed/blocked run needs failure category and detail: " + blind)
        elif category is not None or (reason is not None and reason != ""):
            raise ValueError("Completed run cannot claim a failure category: " + blind)
        prompt_file = safe_file(study, Path("operator") / blind / "PROMPT.txt")
        if prompt_file.read_text(encoding="utf-8") != run["prompt"] + "\n":
            raise ValueError("Operator prompt was modified: " + blind)
        status_counts[status] += 1
        # A client failing to discover the Skill is a NEGATIVE observation,
        # not a reason to delete that arm from evidence coverage.
        if arm == "archvela" and discovery is not True:
            deviations.append({"blind_id": blind, "type": "treatment_skill_not_discovered",
                               "status": status})
        # Baseline with inherited Skill is contaminated and cannot be used
        # in a valid baseline/treatment comparison, but keep the raw evidence.
        if arm == "baseline" and discovery is True:
            deviations.append({"blind_id": blind, "type": "baseline_skill_contamination",
                               "status": status})
        present.append({
            "blind_id": blind,
            "execution_status": status,
            "skill_discovered": discovery,
            "failure_category": category if status != "completed" else None,
            "response_sha256": evidence_digest(paths[0]),
            "run_log_sha256": evidence_digest(paths[1]),
            "metadata_sha256": evidence_digest(paths[2]),
        })
    contamination = any(x["type"] == "baseline_skill_contamination" for x in deviations)
    return {
        "schema_version": 2,
        "audit_type": "operator_only_self_reported_evidence",
        "expected_runs": len(runs),
        "evidence_complete_runs": len(present),
        "all_evidence_present": not missing,
        "protocol_valid": not contamination,
        "execution_status_counts": status_counts,
        "discovery_deviations": deviations,
        "evidence": present,
        "missing": missing,
        "caveat": (
            "Complete evidence can include failed/blocked runs and Skill discovery failures. "
            "Fields and SHA256 only: neither client execution, redaction, scores nor model benefit is verified."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only real-agent pilot evidence inventory (operator only)")
    p.add_argument("--study", required=True, type=Path)
    args = p.parse_args()
    try:
        result = audit(args.study)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        # Failed/blocked treatment attempts are valid negative outcomes.
        # Baseline contamination is a reproducibility defect.
        return 0 if result["all_evidence_present"] and result["protocol_valid"] else 2
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
