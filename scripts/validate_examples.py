#!/usr/bin/env python3
"""Offline first-pass guardrails for independent Archvela demos."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SPECS = {
    "cinematic-site": ("V3-02", {"next", "react", "react-dom", "three"}),
    "saas-workspace": ("V3-14", {"next", "react", "react-dom"}),
    "home-digital-twin": ("V3-26", {"vite", "@react-three/fiber", "react", "react-dom", "three"}),
}

def check() -> list[str]:
    problems = []
    for name, (scene, expected) in SPECS.items():
        base = EXAMPLES / name
        pkg_file = base / "package.json"
        if not pkg_file.is_file():
            problems.append(name + ": missing package.json")
            continue
        pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
        deps = set(pkg.get("dependencies", {}))
        dev_deps = set(pkg.get("devDependencies", {}))
        if not pkg.get("private"):
            problems.append(name + ": starter must be private")
        if not expected <= deps | dev_deps:
            problems.append(name + ": missing required framework packages")
        if name == "saas-workspace" and ({"three", "@react-three/fiber", "cesium"} & deps):
            problems.append(name + ": SaaS incorrectly includes 3D engines")
        if name == "home-digital-twin" and ("cesium" in deps or "next" in deps):
            problems.append(name + ": house viewer incorrectly depends on GIS/Next")
        doc = base / "README.md"
        if not doc.is_file() or scene not in doc.read_text(encoding="utf-8"):
            problems.append(name + ": ADR must cite its V3 scene")
        if not {"dev", "build", "typecheck"} <= set(pkg.get("scripts", {})):
            problems.append(name + ": missing required npm scripts")
    return problems

if __name__ == "__main__":
    problems = check()
    for p in problems:
        print("FAIL", p)
    print("Example boundary review:", "PASS" if not problems else "FAIL", "|", len(SPECS), "projects")
    sys.exit(bool(problems))
