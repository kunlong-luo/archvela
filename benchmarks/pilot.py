#!/usr/bin/env python3
"""Prepare real-agent pilot sessions without executing an agent or inventing results.

The operator-only manifest contains study arms and MUST NOT be sent to reviewers.
This tool does not access model credentials, run an AI client, or score any output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from evaluate import DATA, HERE, load_cases, make_manifest

ROOT = HERE.parent.resolve()
AGENTS = ("codex", "claude-code", "opencode")
DEFAULT_TASKS = ("AV-01", "AV-03")


def prepare_pilot(*, output: Path, agent: str, model: str, skill_sha: str,
                  tasks: list[str], seed: int, trial: int) -> dict:
    if agent not in AGENTS:
        raise ValueError("Unsupported pilot agent")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", skill_sha):
        raise ValueError("A full 40-character Git commit SHA is required")
    if not tasks or len(set(tasks)) != len(tasks):
        raise ValueError("Select at least one distinct task")
    available = {case["id"] for case in load_cases()}
    if any(task not in available for task in tasks):
        raise ValueError("Unknown benchmark task ID")
    manifest = make_manifest(seed, model, trial)
    selected = [run for run in manifest["runs"] if run["task_id"] in tasks]
    destination = output.expanduser().resolve()
    # A nested workspace could auto-discover Archvela via the parent .agents/skills,
    # contaminating baseline even when no treatment installation was performed.
    if destination.is_relative_to(ROOT):
        raise ValueError("Pilot output must be outside the Archvela source repository")
    if output.is_symlink() or destination.exists():
        raise ValueError("Pilot output already exists; refusing to overwrite")
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    study = {
        "schema_version": 1,
        "kind": "operator_only_unexecuted_pilot",
        "agent": agent, "model": model, "skill_commit": skill_sha.lower(),
        "cases_sha256": digest, "seed": seed, "trial": trial,
        "task_ids": tasks, "executed_runs": 0,
        "warning": "Operator-only: reveals study arm. Never send to blind reviewers.",
        "runs": selected,
    }
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "operator").mkdir()
    (destination / "workspace").mkdir()
    (destination / "reviewer").mkdir()
    (destination / "operator-manifest.json").write_text(
        json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    source = (
        "https://github.com/kunlong-luo/archvela/tree/"
        + skill_sha.lower() + "/.agents/skills/archvela-architect"
    )
    for run in selected:
        blind_id = run["blind_id"]
        folder = destination / "operator" / blind_id
        folder.mkdir()
        (destination / "workspace" / blind_id).mkdir()
        (folder / "PROMPT.txt").write_text(run["prompt"] + "\n", encoding="utf-8")
        setup = (
            f"# Operator only: {blind_id}\n\n"
            f"Agent: {agent}; model: {model}; task: {run['task_id']}\n"
            f"Arm: {run['arm']}; trial: {trial}; Skill commit: {skill_sha.lower()}\n\n"
            "1. Launch a **fresh** agent session in workspace/" + blind_id + ".\n"
            "2. Confirm no inherited/global Archvela Skill is visible in baseline.\n"
            "3. Keep the same model, tools, safety policy, prompt and budget in both arms.\n"
        )
        if run["arm"] == "archvela":
            setup += (
                "4. Install the pinned Skill **inside that isolated workspace** "
                "and verify native discovery before prompting:\n\n"
                f"   npx skills add {source} --skill archvela-architect "
                f"--agent {agent} --copy --yes\n\n"
                "   If pinned-source installation is unsupported by the installed "
                "CLI, stop and document the error; do not silently use latest.\n"
            )
        else:
            setup += (
                "4. Do not install Archvela. Disable inherited/global Archvela "
                "Skills and verify native discovery is absent.\n"
            )
        setup += (
            "5. Submit PROMPT.txt **verbatim**. Record actual client/model versions, "
            "session start/end, tokens/cost if exposed, and tool events.\n"
            "6. Save the real response and run log under reviewer/artifacts using "
            "blind ID filenames. Inspect and redact secrets before sharing.\n"
            "7. Only a separate reviewer should score results; this script "
            "creates neither answers nor grades.\n"
        )
        setup += (
            "8. For evidence audit, save the raw response at "
            "reviewer/artifacts/" + blind_id + ".response.md, the real tool "
            "log at reviewer/artifacts/" + blind_id + ".run.log, and fill "
            "operator/" + blind_id + "/session.json from session.template.json. "
            "The metadata and arm assignment remain OPERATOR ONLY.\\n"
            "9. Run python3 benchmarks/audit_pilot.py --study <external-pilot-dir> "
            "from the Archvela source checkout. It validates files and claims, "
            "NOT that an LLM executed or that grades are accurate.\\n"
        )
        (folder / "session.template.json").write_text(
            json.dumps({
                "blind_id": blind_id,
                "agent": agent,
                "model": model,
                "client_version": None,
                "skill_commit": skill_sha.lower(),
                "started_at_utc": None,
                "finished_at_utc": None,
                "execution_status": None,
                "skill_discovered": None,
                "note": "Fill only after a genuine client run; do not share operator metadata with reviewers.",
            }, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8"
        )
        (folder / "RUN.md").write_text(setup, encoding="utf-8")
    (destination / "reviewer" / "README.md").write_text(
        "# Blind review area\n\n"
        "Operator: copy only de-identified responses and logs here, "
        "named by blind ID. Never copy operator-manifest.json or RUN.md here.\n"
        "Do not record made-up outputs, grades, or costs. This limited pilot "
        "is NOT a full 12-case paired benchmark and cannot be scored by "
        "evaluate.py until all 24 slots of a complete study are run.\n",
        encoding="utf-8",
    )
    return study


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create isolated, unexecuted Codex/Claude Code/OpenCode pilot cards"
    )
    parser.add_argument("--agent", choices=AGENTS, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--skill-sha", required=True, help="Pin the exact Archvela Git commit")
    parser.add_argument("--task", action="append", dest="tasks", help="Repeat for task IDs")
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--trial", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        study = prepare_pilot(
            output=args.output, agent=args.agent, model=args.model,
            skill_sha=args.skill_sha, tasks=args.tasks or list(DEFAULT_TASKS),
            seed=args.seed, trial=args.trial,
        )
    except (OSError, ValueError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2
    print(
        f"Prepared {len(study['runs'])} UNEXECUTED sessions "
        f"({len(study['task_ids'])} tasks x 2 arms); "
        "no AI calls, results, scores or costs incurred."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
