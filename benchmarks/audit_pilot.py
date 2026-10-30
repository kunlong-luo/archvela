#!/usr/bin/env python3
"""Audit *operator-supplied* pilot evidence without running or scoring models.

Only verifies files, self-reported metadata, and hashes. The operator-only
report reveals study arms and must never be given to blind reviewers.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

from evaluate import DATA, load_cases

ID = re.compile(r"^[0-9a-f]{16}$")
MAX_BYTES = 8_000_000


def safe_file(study: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
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
    timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset() != dt.timedelta():
        raise ValueError("Timestamp must specify UTC timezone")
    return timestamp


def audit(study_dir: Path) -> dict:
    if study_dir.is_symlink():
        raise ValueError("Study root cannot be a symlink")
    study = study_dir.expanduser().resolve(strict=True)
    if not study.is_dir():
        raise ValueError("Study must be a directory")
    manifest_file = safe_file(study, Path("operator-manifest.json"))
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "operator_only_unexecuted_pilot":
        raise ValueError("Unexpected operator manifest")
    if manifest.get("agent") not in ("codex", "claude-code", "opencode"):
        raise ValueError("Unexpected client in pilot manifest")
    if not re.fullmatch("[0-9a-f]{40}", str(manifest.get("skill_commit", ""))):
        raise ValueError("Study must pin a full Git commit")
    if manifest.get("executed_runs") != 0:
        raise ValueError("Pilot generator must not claim execution")
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != manifest.get("cases_sha256"):
        raise ValueError("Benchmark cases changed after pilot preparation")
    known = {case["id"]: case for case in load_cases()}
    runs = manifest.get("runs")
    if not isinstance(runs, list) or not runs or len(runs) != 2 * len(manifest.get("task_ids", [])):
        raise ValueError("Pilot run count must equal selected tasks x two arms")
    ids = [r.get("blind_id") for r in runs]
    if any(not isinstance(i, str) or not ID.fullmatch(i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Invalid or duplicate blind ID")
    tasks = {}
    complete = []
    missing = []
    for r in runs:
        task = r.get("task_id")
        arm = r.get("arm")
        if task not in known or r.get("prompt") != known[task]["prompt"] or arm not in ("baseline", "archvela"):
            raise ValueError("Pilot task or prompt has changed")
        tasks.setdefault(task, set()).add(arm)
        blind = r["blind_id"]
        response = Path("reviewer/artifacts") / (blind + ".response.md")
        logfile = Path("reviewer/artifacts") / (blind + ".run.log")
        metadata = Path("operator") / blind / "session.json"
        files = (response, logfile, metadata)
        if any(not (study / f).exists() for f in files):
            missing.append({"blind_id": blind, "missing": [str(f) for f in files if not (study / f).exists()]})
            continue
        paths = [safe_file(study, f) for f in files]
        data = json.loads(paths[2].read_text(encoding="utf-8"))
        if (data.get("blind_id") != blind or data.get("agent") != manifest["agent"]
                or data.get("model") != manifest["model"]):
            raise ValueError("Actual session identity mismatch: " + blind)
        if data.get("skill_commit") != manifest["skill_commit"]:
            raise ValueError("Session pinned Skill version mismatch: " + blind)
        if data.get("skill_discovered") is not (arm == "archvela"):
            raise ValueError("Skill discovery does not match expected pilot condition: " + blind)
        if data.get("execution_status") != "completed":
            raise ValueError("Run was not completed: " + blind)
        client_version = data.get("client_version")
        if not isinstance(client_version, str) or not client_version.strip():
            raise ValueError("Missing actual client version: " + blind)
        start = utc_timestamp(data.get("started_at_utc"))
        end = utc_timestamp(data.get("finished_at_utc"))
        if end <= start:
            raise ValueError("Invalid session time order: " + blind)
        prompt_file = safe_file(study, Path("operator") / blind / "PROMPT.txt")
        if prompt_file.read_text(encoding="utf-8") != r["prompt"] + "\n":
            raise ValueError("Operator prompt was modified: " + blind)
        complete.append({
            "blind_id": blind,
            "response_sha256": evidence_digest(paths[0]),
            "run_log_sha256": evidence_digest(paths[1]),
            "metadata_sha256": evidence_digest(paths[2]),
        })
    if set(tasks) != set(manifest["task_ids"]) or any(arms != {"baseline", "archvela"} for arms in tasks.values()):
        raise ValueError("Incomplete or duplicated task assignment")
    return {
        "schema_version": 1,
        "audit_type": "operator_only_self_reported_evidence",
        "expected_runs": len(runs),
        "evidence_complete_runs": len(complete),
        "all_evidence_present": len(missing) == 0,
        "evidence": complete,
        "missing": missing,
        "caveat": "Files, metadata fields and SHA256 were checked only. No AI client was invoked, no grades were assigned, and model execution claims cannot be independently verified.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only real-agent pilot evidence inventory (operator only)")
    p.add_argument("--study", required=True, type=Path)
    args = p.parse_args()
    try:
        result = audit(args.study)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_evidence_present"] else 2
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
