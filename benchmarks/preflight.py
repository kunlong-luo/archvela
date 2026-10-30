#!/usr/bin/env python3
"""Read-only static pilot preflight. No AI process, install, or token access.

This checks study-generated workspace boundaries, NEVER users' private global
agent settings. Manual native-client/global-Skill isolation checks remain vital.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audit_pilot import safe_file, validate_manifest

AGENT_PATHS = (
    ".agents/skills/archvela-architect",
    ".claude/skills/archvela-architect",
    ".opencode/skills/archvela-architect",
)


def inspect(study_dir: Path) -> dict:
    if study_dir.is_symlink():
        raise ValueError("Study root must not be a symlink")
    study = study_dir.expanduser().resolve(strict=True)
    if not study.is_dir():
        raise ValueError("Study must be a directory")
    manifest = json.loads(safe_file(study, Path("operator-manifest.json")).read_text(encoding="utf-8"))
    runs = validate_manifest(manifest, study)
    defects = []
    root = study / "workspace"
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Workspace root missing or symlinked")
    expected = {run["blind_id"] for run in runs}
    actual = {entry.name for entry in root.iterdir()}
    if actual != expected:
        defects.append("Workspace IDs do not match pinned manifest")
    for run in runs:
        blind = run["blind_id"]
        workspace = root / blind
        if workspace.is_symlink() or not workspace.is_dir():
            defects.append("Missing or symlinked workspace: " + blind)
            continue
        if any(workspace.iterdir()):
            defects.append("Workspace is not empty before pilot: " + blind)
        prompt = safe_file(study, Path("operator") / blind / "PROMPT.txt")
        if prompt.read_text(encoding="utf-8") != run["prompt"] + "\n":
            defects.append("Paired prompt changed: " + blind)
        # Detect local inherited Skill trees in workspace parents; a global
        # user installation is NOT accessible/certified by this static check.
        for parent in (workspace, *workspace.parents):
            if parent == parent.parent:
                break
            if parent == Path.home():
                break  # Do not traverse user-controlled global Skill folders.
            for rel in AGENT_PATHS:
                if (parent / rel).exists():
                    defects.append("Potential inherited Skill at: " + str(parent / rel))
    return {
        "schema_version": 1,
        "kind": "static_unexecuted_pilot_preflight",
        "expected_runs": len(runs),
        "passed": not defects,
        "defects": sorted(set(defects)),
        "manual_checks_required": [
            "Confirm no inherited global Archvela Skills in actual agent client",
            "Confirm actual login, model ID, version, runtime tools and permission budget",
            "Confirm treatment pinned install and native discovery in the live client",
            "Confirm no model sessions are run without operator authorization",
        ],
        "caveat": "Static filesystem inspection only; this does not authenticate a client, inspect global Skills, or execute an agent.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect empty isolated pilot workspaces before real client access")
    parser.add_argument("--study", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.study)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 2
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
