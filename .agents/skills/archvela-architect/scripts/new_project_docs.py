#!/usr/bin/env python3
"""Generate three architecture documents (preview by default, no overwrites)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references" / "scenarios.json"
TEMPLATES = ROOT / "references" / "templates"
DOCS = (
    ("T01_新项目立项与架构决策_ADR.md", "ADR-001_frontend-architecture.md"),
    ("T02_分包策略与性能预算.md", "frontend-performance-budget.md"),
    ("T03_OpenCode_立项与交付任务卡.md", "opencode-delivery-card.md"),
)

def main() -> int:
    parser = argparse.ArgumentParser(description="Dry run by default; refuses overwriting files")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    project = args.project.strip()
    if not project or any(c in project for c in "\r\n\0"):
        parser.error("--project must be a non-empty single-line name")
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    matched = [row for row in rows if row["id"].casefold() == args.scene.casefold()]
    if len(matched) != 1:
        parser.error("Unknown scenario; use scenes.py --list-domains")
    row = matched[0]
    destination = Path(args.output).expanduser().resolve() / "docs" / "architecture"
    planned = []
    for template_name, output_name in DOCS:
        body = (TEMPLATES / template_name).read_text(encoding="utf-8")
        if template_name.startswith("T01"):
            intro = (
                "# 已选择场景（待评审，不代表已实施）\n\n"
                f"- 项目：{project}\n"
                f'- 编号：{row["id"]} · {row["title"]}\n'
                f'- 领域：{row["domain"]}\n'
                f'- 参考技术：{row["stack"]}\n'
                f'- 用户任务：{row["task"]}\n'
                f'- 主要功能：{row["features"]}\n'
                f'- 差异化：{row["differentiation"]}\n'
                f'- 初始分包：{row["splitting"]}\n'
                f'- MVP：{row["mvp"]}\n\n---\n\n'
            )
            body = intro + body.replace("<project-name>", project)
        planned.append((destination / output_name, body))
    existing = [path for path, _ in planned if path.exists() or path.is_symlink()]
    if existing:
        print("ABORT: existing architecture files:", file=sys.stderr)
        for path in existing:
            print(f"  {path}", file=sys.stderr)
        return 2
    print(f'Scene: {row["id"]} {row["title"]} | Mode: {"WRITE" if args.write else "DRY-RUN"}')
    for path, _ in planned:
        print(path)
    if not args.write:
        return 0
    destination.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    try:
        for path, body in planned:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(body)
            created.append(path)
    except OSError as exc:
        print(f"Write failed: {exc}; already created: {created}", file=sys.stderr)
        return 3
    print("Created three draft documents; review assumptions before implementation.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
