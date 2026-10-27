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
