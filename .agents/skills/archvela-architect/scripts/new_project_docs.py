#!/usr/bin/env python3
"""Generate scenario-specific architecture drafts safely (stdlib only).

No files are written unless --write is provided. Existing files are never
overwritten; created files are cleaned up if any write fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references" / "scenarios.json"
PROFILES = ROOT / "references" / "architecture_profiles.json"
TEMPLATES = ROOT / "references" / "templates"
DOCS = (
    ("T01_新项目立项与架构决策_ADR.md", "ADR-001_frontend-architecture.md"),
    ("T02_分包策略与性能预算.md", "frontend-performance-budget.md"),
    ("T03_OpenCode_立项与交付任务卡.md", "agent-delivery-card.md"),
)


def load_scene(scene_id: str) -> tuple[dict, dict]:
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    matches = [row for row in rows if row["id"].casefold() == scene_id.casefold()]
    if len(matches) != 1:
        raise ValueError("Unknown scenario; use scripts/scenes.py --list-domains")
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    row = matches[0]
    profile = profiles.get(row["domain_code"])
    if profile is None:
        raise ValueError("Missing architecture profile for " + row["domain_code"])
    return row, profile


def render_documents(project: str, scene: dict, domain: dict) -> list[tuple[str, str]]:
    """Pure rendering; never creates files."""
    origin = (f'{scene["id"]} · {scene["title"]} / {scene["domain"]}')
    caveat = "以下为待审核的场景推荐，尚未实施、测量或选择最终依赖版本。"
    context = (
        f"- 项目：{project}\n"
        f"- 主场景：{origin}\n"
        f'- 用户任务：{scene["task"]}\n'
        f'- MVP：{scene["mvp"]}\n'
        f'- 候选技术（需与已有仓库核对）：{scene["stack"]}\n'
    )
    package_rows = [
        ("Package / 代码复用", domain["package"]),
        ("Feature / 用户任务", domain["feature"]),
        ("JS Chunk / 动态加载", domain["chunk"]),
        ("Asset Pack / 资源分级", domain["assets"]),
    ]
    four_layers = "\n".join(f"| {label} | {detail} |" for label, detail in package_rows)
    intro_adr = (
        "# Archvela · 场景化架构决策草案\n\n"
        f"> {caveat}\n\n"
        + context
        + f'- 场景分包提醒：{scene["splitting"]}\n'
        + f'- 产品独特性：{scene["differentiation"]}\n'
        + f'- 核心验收：{scene["acceptance"]}\n\n'
        "## 前置约束和待确认决策\n\n"
        f'- 首要风险：{domain["risk"]}\n'
        "- 是否是已有项目，现有框架、锁文件和构建器是什么：**待只读审计**\n"
        "- SEO、最低设备、联网/离线与真实用户任务：**待确认**\n"
        "- 采用/不采用的技术与原因：**待 ADR 审核，不因流行而迁移**\n"
        "- 业务边界、数据所有权、许可证与隐私：**待确认**\n\n"
        "## 四层分包初稿（可更改）\n\n"
        "| 分包层次 | 建议决策 |\n|---|---|\n"
        + four_layers
        + "\n\n## 主要回退策略\n\n"
        f'{domain["fallback"]}\n\n'
        "## 分阶段切片\n\n"
        f'- 第 1 个 PR：{domain["m1"]}\n'
        f'- 第 2 个 PR：{domain["m2"]}\n'
        f'- 第 3 个 PR：{domain["m3"]}\n\n'
        "---\n\n"
    )
    intro_perf = (
        "# Archvela · 场景化分包与性能预算草案\n\n"
        f"> {caveat} 指标必须在真实设备、网络与用户任务中量测。\n\n"
        + context
        + "\n## 本场景推荐加载路径\n\n"
        f'- S0 静态/轻量反馈：{domain["fallback"]}\n'
        f'- S1 主要功能：{domain["feature"]}\n'
        f'- S2 重型 JS / Canvas：{domain["chunk"]}\n'
        f'- S3–S4 资源包：{domain["assets"]}\n\n'
        "## 四层预算和降级门禁\n\n"
        "| 层次 | 需要验证的目标 | 实测和目标设备 |\n|---|---|---|\n"
        + "\n".join(f"| {label} | {detail} | 待采集 |" for label, detail in package_rows)
        + "\n\n## 基于真实设备的验收重点\n\n"
        f'{domain["quality"]}\n\n'
        "- 浏览器版本/设备/网络：待确定\n"
        "- LCP、INP、CLS：只对适用的网页用户旅程测量，不为游戏帧率捏造统一标准\n"
        "- JS 分包报告、资源体积与 3D/媒体内存：需要构建产物和实测证据\n"
        "- WebGL/WebGPU、弱网、reduced-motion、键盘与触屏：按场景检查\n\n"
        "---\n\n"
    )
    intro_task = (
        "# Archvela · AI 编程代理可执行任务草案\n\n"
        f"> {caveat} 先审计后执行；未经用户许可，不运行部署、覆盖、删除或付费操作。\n\n"
        + context
        + "\n## 推荐 PR 切片（每个都必须有测试/回退证据）\n\n"
        f'1. **建立真实用户旅程**：{domain["m1"]}。\n'
        f'2. **异常状态与领域验证**：{domain["m2"]}。\n'
        f'3. **性能与视觉打磨**：{domain["m3"]}。\n\n'
        "## 开始前的只读核对\n\n"
        f'- 项目特有最大风险：{domain["risk"]}\n'
        f'- 主要功能模块：{scene["features"]}\n'
        f'- 加载计划：{domain["chunk"]}\n'
        f'- 资源边界：{domain["assets"]}\n'
        f'- 验收提示：{domain["quality"]}\n'
        "- 对既有工程只读审计 package.json / lockfile / AGENTS.md / 现有测试。\n"
        "- 将缺少的实时数据、3D 资产或外部权限明确标为未验证。\n\n"
        "---\n\n"
    )
    intros = (intro_adr, intro_perf, intro_task)
    output = []
    for (source_name, output_name), intro in zip(DOCS, intros):
        template = (TEMPLATES / source_name).read_text(encoding="utf-8")
        template = template.replace("<project-name>", project)
        output.append((output_name, intro + template + "\n"))
    return output


def reject_unsafe_dirs(output: Path) -> None:
    """Don't follow symlinked docs folders into another unrelated directory."""
    docs = output / "docs"
    dest = docs / "architecture"
    for path in (docs, dest):
        if path.is_symlink():
            raise ValueError(f"Refusing symlinked architecture directory: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Not a directory: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scene-specific drafts; dry-run unless --write")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true", help="JSON result for automation (no file bodies)")
    args = parser.parse_args()

    project = args.project.strip()
    if (not project or len(project) > 120 or
            any(ord(ch) < 32 or ch in "<>`" for ch in project)):
        parser.error("--project must be 1–120 single-line printable chars, no HTML/code delimiters")
    try:
        scene, profile = load_scene(args.scene)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    output = Path(args.output).expanduser().absolute()
    dest = output / "docs" / "architecture"
    try:
        reject_unsafe_dirs(output)
    except ValueError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2
    planned = [(dest / name, body) for name, body in render_documents(project, scene, profile)]
    existing = [path for path, _ in planned if path.exists() or path.is_symlink()]
    if existing:
        print("ABORT: architecture files already exist:", file=sys.stderr)
        for path in existing:
            print(f"  {path}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "mode": "write" if args.write else "dry-run",
            "scene": scene["id"], "project": project, "paths": [str(p) for p, _ in planned],
        }, ensure_ascii=False, indent=2))
    else:
        print(f'Scene: {scene["id"]} {scene["title"]} | Mode: {"WRITE" if args.write else "DRY-RUN"}')
        for path, _ in planned:
            print(path)
    if not args.write:
        return 0

    created_files: list[Path] = []
    preexisting_dirs = {path: path.exists() for path in (output, output / "docs", dest)}
    try:
        dest.mkdir(parents=True, exist_ok=True)
        reject_unsafe_dirs(output)
        for path, body in planned:
            # Exclusive creation is the final race-aware no-overwrite guard.
            with path.open("x", encoding="utf-8") as handle:
                created_files.append(path)
                handle.write(body)
    except (OSError, ValueError) as exc:
        # Clean up ONLY files this invocation created. Never remove user files.
        for path in reversed(created_files):
            try:
                path.unlink()
            except OSError:
                pass
        for path in (dest, output / "docs", output):
            if not preexisting_dirs[path]:
                try:
                    path.rmdir()  # Removes empty dirs only.
                except OSError:
                    pass
        print(f"ABORT: write failed and generated files rolled back: {exc}", file=sys.stderr)
        return 3
    print("Created three scenario-specific drafts; review all assumptions before implementation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
