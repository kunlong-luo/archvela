#!/usr/bin/env python3
"""Archvela starter CLI: scene-driven, offline and no-overwrite by default.

Three *verified example templates* only. Other 59 scenes remain architecture
references, not falsely advertised as runnable scaffolds.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO / ".agents" / "skills" / "archvela-architect" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from new_project_docs import load_scene, render_documents  # noqa: E402
from plan_contract import draft_plan  # noqa: E402

STARTERS = {
    "V3-02": ("cinematic-site", "Next.js 16 + lazy Three.js marketing site"),
    "V3-14": ("saas-workspace", "Next.js 16 interactive SaaS workspace"),
    "V3-26": ("home-digital-twin", "Vite 8 + R3F 9 proportional concept viewer"),
}
ROOT_FILES = {
    "package.json", "package-lock.json", "README.md",
    "tsconfig.json", "next.config.ts", "next-env.d.ts",
    "vite.config.ts", "index.html",
}
DIRS = {"src", "tests", "public"}
SUFFIXES = {".ts", ".tsx", ".mjs", ".js", ".css", ".json", ".html",
            ".md", ".svg", ".webp", ".png", ".jpg", ".jpeg", ".glb"}


def safe_sources(template: str) -> list[tuple[Path, bytes]]:
    source = REPO / "examples" / template
    if not source.is_dir() or source.is_symlink():
        raise ValueError("Starter source unavailable or symlinked")
    files = []
    total = 0
    ignored = {".next", "dist", "node_modules", ".git", "coverage",
               "playwright-report", "test-results", ".vite"}
    for folder, dirnames, filenames in os.walk(source, followlinks=False):
        directory = Path(folder)
        # Prune build outputs BEFORE walking them: locally installed starter
        # node_modules can contain thousands of files and symlinks.
        for name in list(dirnames):
            if name in ignored:
                dirnames.remove(name)
            elif (directory / name).is_symlink():
                raise ValueError("Symlink in starter source: " +
                                 str((directory / name).relative_to(source)))
        for filename in sorted(filenames):
            path = directory / filename
            rel = path.relative_to(source)
            if path.is_symlink():
                raise ValueError("Symlink in starter source: " + str(rel))
            if len(rel.parts) == 1:
                allowed = rel.name in ROOT_FILES
            else:
                allowed = rel.parts[0] in DIRS and path.suffix.lower() in SUFFIXES
            if not allowed:
                if rel.parts[0] in ignored:
                    continue
                raise ValueError("Unexpected starter file (inspect manually): " + str(rel))
            if not path.is_file() or path.stat().st_size > 5_000_000:
                raise ValueError("File missing or exceeds 5MB single-file guard: " + str(rel))
            content = path.read_bytes()
            total += len(content)
            if total > 20_000_000:
                raise ValueError("Starter exceeds 20MB maximum")
            files.append((rel, content))
    if not any(p == Path("package.json") for p, _ in files):
        raise ValueError("Starter lacks package.json")
    if not any(p == Path("package-lock.json") for p, _ in files):
        raise ValueError("Starter lacks package-lock.json")
    return files


def make_project_files(scene_id: str, project: str) -> list[tuple[Path, bytes]]:
    template, _ = STARTERS[scene_id]
    raw = dict(safe_sources(template))
    package = json.loads(raw[Path("package.json")])
    lock = json.loads(raw[Path("package-lock.json")])
    if not package.get("private") or lock.get("lockfileVersion") != 3:
        raise ValueError("Starter is not a private locked npm project")
    package["name"] = project
    lock["name"] = project
    lock["packages"][""]["name"] = project
    raw[Path("package.json")] = (json.dumps(package, ensure_ascii=False, indent=2) + "\n").encode()
    raw[Path("package-lock.json")] = (json.dumps(lock, ensure_ascii=False, indent=2) + "\n").encode()
    old_readme = raw[Path("README.md")].decode("utf-8")
    raw[Path("README.md")] = (
        f"# {project}\n\n"
        f"> Generated locally from Archvela {scene_id} / {template}. "
        "Demo data and unverified design assumptions must be reviewed before production.\n\n"
        "## Original starter explanation and ADR\n\n" + old_readme
    ).encode()
    scene, profile = load_scene(scene_id)
    for filename, content in render_documents(project, scene, profile):
        raw[Path("docs") / "architecture" / filename] = content.encode()
    plan = draft_plan(project, scene, profile)
    raw[Path("docs/architecture/archvela-plan.json")] = (
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    return sorted(raw.items(), key=lambda pair: str(pair[0]))


def check_target(parent: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise ValueError("Refusing to overwrite existing project: " + str(destination))
    # Refuse symlinked path components; do not silently redirect outside
    # the requested destination (including relative symlinked parents).
    path = parent
    while True:
        if path.is_symlink():
            raise ValueError("Refusing symlinked output parent: " + str(path))
        if path == path.parent:
            break
        path = path.parent


def create(parent: Path, destination: Path, items: list[tuple[Path, bytes]]) -> None:
    check_target(parent, destination)
    # Parent is an explicit user choice, may be created for the first run.
    parent.mkdir(parents=True, exist_ok=True)
    check_target(parent, destination)
    created_files: list[Path] = []
    created_dirs: list[Path] = []
    destination.mkdir(exist_ok=False)
    created_dirs.append(destination)
    try:
        for relative, blob in items:
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe starter path " + str(relative))
            full = destination / relative
            todo = []
            current = full.parent
            while current != destination and not current.exists():
                todo.append(current)
                current = current.parent
            for directory in reversed(todo):
                directory.mkdir(exist_ok=False)
                created_dirs.append(directory)
            with full.open("xb") as handle:
                created_files.append(full)
                handle.write(blob)
    except Exception:
        # Remove only this invocation's files and its now-empty directories;
        # never delete a pre-existing user file or an entire project tree.
        for file in reversed(created_files):
            try:
                file.unlink()
            except OSError:
                pass
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Archvela — safe scenario-to-project starter CLI")
    command = parser.add_subparsers(dest="command", required=True)
    show = command.add_parser("list", help="Show which scenarios have runnable starters")
    show.add_argument("--json", action="store_true")
    generate = command.add_parser("create", help="Preview/create a new project from a verified starter")
    generate.add_argument("--scene", required=True)
    generate.add_argument("--project", required=True, help="Lowercase npm package slug")
    generate.add_argument("--output", type=Path, required=True, help="Parent folder of new project")
    generate.add_argument("--write", action="store_true", help="Actually create new project")
    generate.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "list":
            entries = [{"scene": sid, "template": name, "description": desc}
                       for sid, (name, desc) in STARTERS.items()]
            print(json.dumps(entries, ensure_ascii=False, indent=2) if args.json else
                  "\n".join(f"{entry['scene']}: {entry['template']} — {entry['description']}" for entry in entries))
            return 0
        scene = args.scene.upper()
        if scene not in STARTERS:
            raise ValueError("No runnable template for " + scene +
                             "; use new_project_docs.py for architecture-only V3 scenes")
        slug = args.project
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,62}[a-z0-9]", slug):
            raise ValueError("Project name must be a lowercase npm-safe slug (3–64 chars)")
        parent = args.output.expanduser().absolute()
        dest = parent / slug
        check_target(parent, dest)
        items = make_project_files(scene, slug)
        if args.write:
            create(parent, dest, items)
        report = {"mode": "write" if args.write else "dry-run",
                  "status": "created" if args.write else "preview",
                  "scene": scene, "project": slug, "destination": str(dest),
                  "files": len(items), "includes_lockfile": True,
                  "includes_architecture_plan": True}
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"{report['status'].upper()}: {slug} from {scene} ({len(items)} files) at {dest}")
            if not args.write:
                print("No files written. Add --write after reviewing the target directory.")
            else:
                print(f"Next: cd {dest} && npm ci && npm run build")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("ABORT: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
