#!/usr/bin/env python3
"""Search 62 curated Archvela V3 scenarios (stdlib only, deterministic)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "references" / "scenarios.json"

# Curated bilingual query shorthands, not model-based translation.
# Keep specific aliases before generic domain words.
ALIASES = {
    "home digital twin": ("V3-26",),
    "house digital twin": ("V3-26",),
    "smart farm": ("V3-25", "V3-35"),
    "3d house": ("V3-26", "V3-31", "V3-32"),
    "digital twin": ("domain:03",),
    "iot digital twin": ("V3-27", "V3-28", "V3-35", "V3-36"),
    "tower defense": ("V3-45", "V3-46"),
    "web game": ("domain:05",),
    "browser game": ("domain:05",),
    "company website": ("V3-01", "V3-02", "V3-13"),
    "landing page": ("V3-01", "V3-02", "V3-03"),
    "ecommerce": ("V3-06", "V3-07", "V3-08", "V3-09", "V3-24"),
    "e-commerce": ("V3-06", "V3-07", "V3-08", "V3-09", "V3-24"),
    "dashboard": ("V3-14", "V3-16", "V3-21", "V3-56"),
    "ai workflow": ("V3-15",),
    "agent workflow": ("V3-15",),
    "english practice": ("V3-37", "V3-38"),
    "english pronunciation": ("V3-37", "V3-38"),
    "online video editor": ("V3-18", "V3-24"),
    "geo visualization": ("domain:06",),
    "geospatial": ("domain:06",),
}

DOMAIN_ALIASES = {
    "01": ("website", "websites", "marketing site", "官网", "品牌", "网站", "电商"),
    "02": ("saas", "productivity", "workflow", "admin", "业务应用", "工作台"),
    "03": ("digital twin", "3d visualization", "bim", "facility", "孪生", "工业"),
    "04": ("education", "training", "medical viewer", "学习", "教育", "教学"),
    "05": ("game", "immersive", "webxr", "游戏", "娱乐", "沉浸"),
    "06": ("gis", "geospatial", "map", "mapping", "地理", "地图", "空间数据"),
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def load_scenarios() -> list[dict]:
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 62:
        raise ValueError("Expected exactly 62 scenarios")
    ids = [row.get("id") for row in rows]
    if len(set(ids)) != 62:
        raise ValueError("Duplicate scenario IDs")
    return rows


def resolve_domain(value: str) -> str | None:
    key = normalize(value)
    if key in DOMAIN_ALIASES:
        return key
    # Accept an exact domain name or exact bilingual domain alias.
    for domain, aliases in DOMAIN_ALIASES.items():
        if key in aliases:
            return domain
    names = {"网站与商业展示": "01", "业务应用与生产工具": "02",
             "空间与数字孪生": "03", "教育与专业可视化": "04",
             "互动娱乐与沉浸体验": "05", "地理数据与公共展示": "06"}
    return names.get(value.strip())


def score(row: dict, query: str) -> int:
    if not query:
        return 1
    if normalize(row["id"]) == query:
        return 100
    if normalize(row["title"]) == query:
        return 90
    alias_ids = ALIASES.get(query, ())
    if row["id"] in alias_ids:
        return 70
    if ("domain:" + row["domain_code"]) in alias_ids:
        return 35
    if query in normalize(row["title"]):
        return 50
    fields = ("task", "features", "stack", "mvp", "domain", "differentiation")
    if any(query in normalize(str(row.get(key, ""))) for key in fields):
        return 20
    if query in (normalize(alias) for alias in DOMAIN_ALIASES[row["domain_code"]]):
        return 10
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Archvela V3 scenario search (Chinese/English)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--query", help="Search titles, roles and curated English aliases")
    group.add_argument("--id", help="Exact ID, e.g. V3-26")
    group.add_argument("--list-domains", action="store_true")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--domain", help="Optional domain filter 01–06 or domain name")
    parser.add_argument("--limit", type=int, help="Limit results (1–62)")
    parser.add_argument("--json", action="store_true", help="Machine-readable result")
    args = parser.parse_args()
    rows = load_scenarios()
    if args.limit is not None and not 1 <= args.limit <= 62:
        parser.error("--limit must be 1–62")
    if args.list_domains:
        if args.domain:
            parser.error("--list-domains cannot be combined with --domain")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["domain"]] = counts.get(row["domain"], 0) + 1
        print(json.dumps(counts, ensure_ascii=False, indent=2) if args.json else
              "\n".join(f"{key}: {value}" for key, value in counts.items()))
        return 0
    if not (args.query or args.id or args.all or args.domain):
        parser.error("Specify --query, --id, --domain or --all")
    if args.domain:
        domain = resolve_domain(args.domain)
        if domain is None:
            parser.error("Unknown domain; use 01–06 or exact domain name")
        rows = [row for row in rows if row["domain_code"] == domain]
    if args.id:
        rows = [row for row in rows if normalize(row["id"]) == normalize(args.id)]
    elif args.query is not None:
        query = normalize(args.query)
        if not query:
            parser.error("--query must be non-empty")
        ranked = [(score(row, query), row) for row in rows]
        rows = [row for points, row in sorted(ranked, key=lambda p: -p[0]) if points > 0]
    if args.limit is not None:
        rows = rows[:args.limit]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print(f'{row["id"]} · {row["title"]} [{row["domain"]}]')
            print(f'  技术: {row["stack"]}')
            print(f'  用户任务: {row["task"]}')
            print(f'  功能: {row["features"]}')
            print(f'  MVP: {row["mvp"]}')
            print(f'  参考: references/{row["domain_file"]}\n')
    if not rows:
        print("No matching scenarios found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
