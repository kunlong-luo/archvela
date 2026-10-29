#!/usr/bin/env python3
"""Integration-test Skills CLI installation into isolated per-agent projects.

This is an installer test, NOT proof that a logged-in/model-backed agent
read and followed Archvela. No user home directories are modified.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MANIFEST = HERE / "compatibility" / "agents.json"
SKILL = "archvela-architect"
GLOBAL_SMOKE = {"opencode", "codex", "claude-code", "cursor", "gemini-cli", "github-copilot"}

def run_install(binary: Path, source: Path, root: Path, spec: dict,
                scope: str, timeout: int) -> dict:
    agent = spec["id"]
    cwd = root / agent / scope / "workspace"
    home = root / agent / scope / "home"
    cwd.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["DO_NOT_TRACK"] = "1"
    env["DISABLE_TELEMETRY"] = "1"
    args = [
        str(binary), "add", str(source), "--skill", SKILL,
        "--agent", agent, "--copy", "--yes",
    ]
    if scope == "global":
        args.append("--global")
    try:
        result = subprocess.run(args, cwd=cwd, env=env, timeout=timeout,
                                text=True, capture_output=True, check=False)
    except subprocess.TimeoutExpired:
        return {"agent": agent, "scope": scope, "ok": False, "error": "installer timeout"}
    relative = spec["project_path"] if scope == "project" else spec["global_path"]
    candidates = [(home / relative.removeprefix("~/")) if scope == "global" else (cwd / relative)]
    # Skills CLI 1.7.4 may choose the shared ~/.agents/skills canonical
    # location for agents that natively support this alias (OpenCode,
    # Cursor, Gemini CLI, GitHub Copilot). This is a valid discovery path,
    # not a failed install. Never claim the dedicated path was used.
    if scope == "global" and agent in {"opencode", "cursor", "gemini-cli", "github-copilot"}:
        candidates.append(home / ".agents" / "skills")
    installed = [base / SKILL for base in candidates if (base / SKILL / "SKILL.md").is_file()]
    entry = installed[0] if installed else (candidates[0] / SKILL)
    expected = entry / "SKILL.md"
    notes = []
    if result.returncode:
        notes.append(f"skills CLI exited {result.returncode}")
    if not installed:
        notes.append("Skill not installed at any supported path: " +
                     ", ".join(str(base / SKILL / "SKILL.md") for base in candidates))
    else:
        text = expected.read_text(encoding="utf-8")
        if not text.startswith("---\nname: archvela-architect\n"):
            notes.append("unexpected SKILL.md frontmatter")
        catalog = entry / "references" / "scenarios.json"
        if not catalog.is_file():
            notes.append("missing scenarios.json")
        else:
            try:
                scenarios = json.loads(catalog.read_text(encoding="utf-8"))
                if len(scenarios) != 62:
                    notes.append(f"unexpected catalog count: {len(scenarios)}")
            except (ValueError, OSError) as err:
                notes.append(f"invalid catalog: {err}")
        if not (entry / "scripts" / "scenes.py").is_file():
            notes.append("missing bundled CLI")
        if not (entry / "references" / "03_空间与数字孪生.md").is_file():
            notes.append("missing digital twin reference")
        if not (entry / "references" / "architecture_profiles.json").is_file():
            notes.append("missing bundled domain architecture profiles")
        # Actually execute both offline CLIs from the copied Skill rather than
        # asserting files are present. No network/API keys or file writes.
        if not notes:
            scenes_run = subprocess.run(
                [sys.executable, str(entry / "scripts" / "scenes.py"),
                 "--query", "home digital twin", "--json"],
                cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout,
                check=False,
            )
            if scenes_run.returncode or "V3-26" not in scenes_run.stdout:
                notes.append("installed scenario lookup failed")
            docs_out = cwd / "preview-only"
            docs_run = subprocess.run(
                [sys.executable, str(entry / "scripts" / "new_project_docs.py"),
                 "--scene", "V3-26", "--project", "ci-test",
                 "--output", str(docs_out), "--plan-json", "--json"],
                cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout,
                check=False,
            )
            if docs_run.returncode or docs_out.exists():
                notes.append("installed generator dry-run failed or wrote files")
            else:
                try:
                    payload = json.loads(docs_run.stdout)
                    if payload.get("mode") != "dry-run" or len(payload.get("paths", [])) != 4:
                        notes.append("unexpected generator preview JSON")
                except json.JSONDecodeError:
                    notes.append("invalid generator preview JSON")
            # Write only into the disposable runner workspace and validate the
            # copied Skill's new cross-agent machine-readable contract.
            if not notes:
                artifact_out = cwd / "write-smoke"
                write_run = subprocess.run(
                    [sys.executable, str(entry / "scripts" / "new_project_docs.py"),
                     "--scene", "V3-26", "--project", "ci-sample",
                     "--output", str(artifact_out), "--plan-json", "--write", "--json"],
                    cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout,
                    check=False,
                )
                plan_path = artifact_out / "docs/architecture/archvela-plan.json"
                if write_run.returncode != 0 or not plan_path.is_file():
                    notes.append("installed generator could not write isolated plan fixture")
                else:
                    try:
                        outcome = json.loads(write_run.stdout)
                        if outcome.get("status") != "created":
                            notes.append("installed generator JSON output is not a creation receipt")
                    except json.JSONDecodeError:
                        notes.append("installed generator --json --write response is invalid JSON")
                    validator = subprocess.run(
                        [sys.executable, str(entry / "scripts" / "plan_contract.py"),
                         str(plan_path), "--level", "draft", "--json"],
                        cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout,
                        check=False,
                    )
                    if validator.returncode != 0:
                        notes.append("installed plan-contract draft validation failed")
    return {
        "agent": agent, "scope": scope, "ok": not notes,
        "destination": str(expected.relative_to(root)) if expected.is_relative_to(root) else str(expected),
        "used_shared_global_alias": scope == "global" and ".agents/skills/" in str(expected),
        "cli_exit_code": result.returncode, "issues": notes,
        "stdout_tail": result.stdout[-1200:], "stderr_tail": result.stderr[-1200:],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills-cli", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=HERE)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--global-smoke", action="store_true")
    parser.add_argument("--agents", nargs="*", help="Optional agent subset")
    args = parser.parse_args()

    binary, source = args.skills_cli.resolve(), args.source.resolve()
    if not binary.is_file():
        parser.error("Skills CLI binary does not exist")
    if not (source / ".agents/skills" / SKILL / "SKILL.md").is_file():
        parser.error("No Archvela skill in source repository")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    specs = manifest["agents"]
    if args.agents:
        unknown = set(args.agents) - {row["id"] for row in specs}
        if unknown:
            parser.error(f"Unknown agent IDs: {sorted(unknown)}")
        specs = [row for row in specs if row["id"] in args.agents]
    results = []
    with tempfile.TemporaryDirectory(prefix="archvela-agent-ci-") as temp:
        root = Path(temp)
        for spec in specs:
            results.append(run_install(binary, source, root, spec, "project", args.timeout))
            print(f'{"PASS" if results[-1]["ok"] else "FAIL"} project {spec["id"]}', flush=True)
            if args.global_smoke and spec["id"] in GLOBAL_SMOKE:
                results.append(run_install(binary, source, root, spec, "global", args.timeout))
                print(f'{"PASS" if results[-1]["ok"] else "FAIL"} global  {spec["id"]}', flush=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = [row for row in results if not row["ok"]]
    for row in failures:
        print(json.dumps(row, ensure_ascii=False, indent=2), file=sys.stderr)
    print(f"Installer validation: {len(results) - len(failures)}/{len(results)} passed")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
