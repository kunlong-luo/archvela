#!/usr/bin/env python3
"""Offline, paired, reviewer-scored eval harness for Archvela.

No model calls or subjective automatic scoring. Fixture results are tests ONLY.
Human grading is self-reported and must not be presented as verified benchmark
wins without artifacts and an auditable run protocol.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import secrets
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "cases.json"
RUBRIC = ("scenario_fit", "architecture_reasoning", "four_layer_split",
          "fallback_safety", "verification_plan")
ARMS = ("baseline", "archvela")


def load_cases() -> list[dict]:
    value = json.loads(DATA.read_text(encoding="utf-8"))
    cases = value["cases"]
    if len(cases) != 12 or len({c["id"] for c in cases}) != 12:
        raise ValueError("Expected 12 unique benchmark tasks")
    catalog = json.loads((HERE.parent / ".agents/skills/archvela-architect/references/scenarios.json").read_text(encoding="utf-8"))
    scene_ids = {row["id"] for row in catalog}
    expected_domain_counts = defaultdict(int)
    for c in cases:
        if c["scenario_id"] not in scene_ids:
            raise ValueError("Unknown scenario " + c["scenario_id"])
        if not isinstance(c["prompt"], str) or len(c["prompt"]) < 25:
            raise ValueError("Task prompt too short " + c["id"])
        topics = c.get("acceptance_topics")
        if not isinstance(topics, list) or len(topics) < 3 or not all(isinstance(t, str) and t for t in topics):
            raise ValueError("At least three scoring topics required for " + c["id"])
        expected_domain_counts[c["scenario_id"].split("-")[0] if False else next(
            row["domain_code"] for row in catalog if row["id"] == c["scenario_id"]
        )] += 1
    if set(expected_domain_counts) != {"01", "02", "03", "04", "05", "06"}:
        raise ValueError("All six scenario domains must be represented")
    if any(count != 2 for count in expected_domain_counts.values()):
        raise ValueError("Expected two tasks per domain")
    return cases


def make_manifest(seed: int, model: str, trial: int) -> dict:
    if not model.strip() or trial < 1:
        raise ValueError("Model ID must be nonblank and trial >= 1")
    tasks = []
    cases = load_cases()
    for c in cases:
        for arm in ARMS:
            # The shuffle seed only fixes task order, never the reviewer ID.
            # A predictable hash of seed/model/arm would unblind a reviewer.
            blind_id = secrets.token_hex(16)
            tasks.append({
                "blind_id": blind_id, "task_id": c["id"], "scenario_id": c["scenario_id"],
                "arm": arm, "prompt": c["prompt"], "acceptance_topics": c["acceptance_topics"],
                "model": model, "trial": trial,
            })
    random.Random(seed).shuffle(tasks)
    return {
        "schema_version": 1, "seed": seed, "model": model, "trial": trial,
        "note": "Runner manifest contains the study arm. Do not expose it to blind reviewers.",
        "runs": tasks,
    }


def create_grading_sheet(manifest: dict) -> dict:
    """Blank human grading records; never invent results."""
    return {
        "schema_version": 1, "seed": manifest["seed"], "model": manifest["model"],
        "trial": manifest["trial"], "records": [
            {"blind_id": entry["blind_id"], "response_artifact": "",
             "run_log_artifact": "", "grades": {key: None for key in RUBRIC},
             "reviewer": "", "review_notes": ""}
            for entry in manifest["runs"]
        ],
    }


def score(manifest: dict, grading: dict) -> dict:
    if manifest.get("schema_version") != 1 or grading.get("schema_version") != 1:
        raise ValueError("Unknown benchmark schema")
    for name in ("seed", "model", "trial"):
        if grading.get(name) != manifest.get(name):
            raise ValueError(f"Manifest and grading sheet {name} mismatch")
    runs = manifest["runs"]
    ids = [row["blind_id"] for row in runs]
    if len(set(ids)) != len(ids) or len(ids) != 24:
        raise ValueError("Expected 24 distinct trial runs (12 tasks x 2 arms)")
    record_rows = grading["records"]
    records = {row["blind_id"]: row for row in record_rows}
    if len(records) != len(record_rows) or set(records) != set(ids):
        raise ValueError("Grading sheet missing or unexpected blind IDs")
    per_task = defaultdict(dict)
    for task in runs:
        entry = records[task["blind_id"]]
        if not isinstance(entry.get("grades"), dict):
            raise ValueError("Each record needs grades")
        if any(entry["grades"].get(k) not in (0, 1, 2, 3, 4) or
               type(entry["grades"].get(k)) is not int for k in RUBRIC):
            raise ValueError("Missing/invalid human rubric grades for " + task["blind_id"])
        for evidence_key in ("response_artifact", "run_log_artifact", "reviewer"):
            if not isinstance(entry.get(evidence_key), str) or not entry[evidence_key].strip():
                raise ValueError("Missing " + evidence_key + " for " + task["blind_id"])
        if task["arm"] in per_task[task["task_id"]]:
            raise ValueError("Duplicate arm for task")
        per_task[task["task_id"]][task["arm"]] = round(
            sum(entry["grades"][key] for key in RUBRIC) / (len(RUBRIC) * 4), 4)
    if len(per_task) != 12 or any(set(row) != set(ARMS) for row in per_task.values()):
        raise ValueError("Incomplete paired task comparisons")
    baseline = sum(row["baseline"] for row in per_task.values()) / len(per_task)
    with_skill = sum(row["archvela"] for row in per_task.values()) / len(per_task)
    return {
        "schema_version": 1,
        "measurement": "human-reported five-dimension 0-4 rubric (not verified automated code tests)",
        "model": manifest["model"], "seed": manifest["seed"], "trial": manifest["trial"],
        "evaluated_pairs": len(per_task),
        "baseline_mean": round(baseline, 4),
        "archvela_mean": round(with_skill, 4),
        "paired_delta": round(with_skill - baseline, 4),
        "per_task": [{"task_id": key, **value} for key, value in sorted(per_task.items())],
        "caveat": "Reviewer grades and run logs are self-reported. Replicate with actual agents, fixed budgets and artifact inspection.",
    }


def verify_artifact_files(grading: dict, root_path: Path) -> dict:
    """Verify evidence *file presence and bytes*, never the truth of its content.

    Paths in grading records must be relative to the explicitly supplied
    directory. Symlink paths and traversal are rejected to prevent accidentally
    reading private data outside the selected experiment workspace.
    """
    if root_path.is_symlink():
        raise ValueError("Evidence root must not be a symlink")
    root = root_path.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Evidence root must be an existing directory")
    digests: dict[str, dict[str, str]] = {}
    seen: set[str] = set()
    for record in grading["records"]:
        blind_id = record["blind_id"]
        digests[blind_id] = {}
        for field in ("response_artifact", "run_log_artifact"):
            raw = record[field]
            relative = Path(raw)
            if (relative.is_absolute() or not relative.parts or
                    ".." in relative.parts or "." in relative.parts):
                raise ValueError("Unsafe evidence path for " + blind_id + ": " + field)
            key = str(relative)
            if key in seen:
                raise ValueError("Duplicate evidence file: " + key)
            seen.add(key)
            target = root
            for part in relative.parts:
                target = target / part
                if target.is_symlink():
                    raise ValueError("Symlink in evidence path: " + key)
            target = target.resolve(strict=True)
            if not target.is_relative_to(root) or not target.is_file():
                raise ValueError("Evidence is not a regular file inside root: " + key)
            size = target.stat().st_size
            if not 0 < size <= 8_000_000:
                raise ValueError("Evidence file empty or exceeds 8MB: " + key)
            digest = hashlib.sha256()
            with target.open("rb") as reader:
                for block in iter(lambda: reader.read(64 * 1024), b""):
                    digest.update(block)
            digests[blind_id][field] = digest.hexdigest()
    return {
        "file_check": "passed",
        "files_checked": len(seen),
        "hash_algorithm": "sha256",
        "fingerprints": digests,
        "caveat": "Existence and hashes verified; file content, grader accuracy and model execution are not verified.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Archvela 12-case human-reviewed, paired agent benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-cases")
    prepare = sub.add_parser("prepare", help="Generate randomized run manifest and empty blind grading sheet")
    prepare.add_argument("--model", required=True)
    prepare.add_argument("--trial", type=int, default=1)
    prepare.add_argument("--seed", type=int, default=20261028)
    prepare.add_argument("--output", type=Path, required=True,
                         help="A NEW empty directory; will not overwrite existing paths")
    s = sub.add_parser("score", help="Refuse to calculate scores from missing human evidence")
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--grades", type=Path, required=True)
    s.add_argument("--artifacts-dir", type=Path,
                   help="Verify all 48 response/log files inside an approved local directory")
    s.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate-cases":
            print("PASS: 12 unique cases, 2 per domain, scene IDs valid")
            load_cases()
        elif args.command == "prepare":
            manifest = make_manifest(args.seed, args.model, args.trial)
            out = args.output.expanduser().absolute()
            if out.exists() or out.is_symlink():
                raise ValueError("Output already exists; refuse to overwrite " + str(out))
            # Avoid partial output on write errors.
            out.mkdir(parents=True)
            try:
                for name, value in (
                    ("runner-manifest.json", manifest),
                    ("blank-human-grades.json", create_grading_sheet(manifest)),
                ):
                    with (out / name).open("x", encoding="utf-8") as writer:
                        json.dump(value, writer, ensure_ascii=False, indent=2)
                        writer.write("\n")
            except OSError:
                for file in out.iterdir():
                    if file.is_file():
                        file.unlink()
                out.rmdir()
                raise
            print(f"Created two files with {len(manifest['runs'])} unexecuted trial slots in {out}")
        elif args.command == "score":
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            grading = json.loads(args.grades.read_text(encoding="utf-8"))
            result = score(manifest, grading)
            result["evidence_files"] = (
                verify_artifact_files(grading, args.artifacts_dir)
                if args.artifacts_dir else
                {"file_check": "not_requested", "files_checked": 0,
                 "caveat": "No artifact directory supplied; only self-reported file names were checked."}
            )
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"Human-scored paired delta: {result['paired_delta']:+.4f} "
                      f"over {result['evaluated_pairs']} task pairs; not independently verified")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
