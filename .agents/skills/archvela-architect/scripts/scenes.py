#!/usr/bin/env python3
"""Search the 62 Archvela V3 scenarios (stdlib only; read-only)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "references" / "scenarios.json"

def load_scenarios() -> list[dict]:
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 62:
        raise ValueError("Expected exactly 62 scenarios")
    ids = [row.get("id") for row in rows]
    if len(set(ids)) != 62:
        raise ValueError("Duplicate scenario ID")
    return rows

def main() -> int:
    parser = argparse.ArgumentParser(description="Archvela V3 scenario search")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Match title, domain, tech stack and features")
    group.add_argument("--id", help="Exact ID, e.g. V3-26")
    group.add_argument("--list-domains", action="store_true")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--json", action="store_true", help="Machine-readable result")
    args = parser.parse_args()
    rows = load_scenarios()
    if args.list_domains:
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["domain"]] = counts.get(row["domain"], 0) + 1
        print(json.dumps(counts, ensure_ascii=False, indent=2) if args.json else
              "\n".join(f"{key}: {value}" for key, value in counts.items()))
        return 0
    if args.id:
        matches = [row for row in rows if row["id"].casefold() == args.id.casefold()]
    elif args.query:
        query = args.query.strip().casefold()
        if not query:
            parser.error("--query must be non-empty")
        keys = ("id", "title", "domain", "stack", "task", "features", "mvp")
        matches = [row for row in rows if query in " ".join(str(row.get(key, "")) for key in keys).casefold()]
    else:
        matches = rows
    if args.json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
    else:
        for row in matches:
            print(f'{row["id"]} · {row["title"]} [{row["domain"]}]')
            print(f'  技术: {row["stack"]}')
            print(f'  用户任务: {row["task"]}')
            print(f'  功能: {row["features"]}')
            print(f'  MVP: {row["mvp"]}')
            print(f'  参考: references/{row["domain_file"]}\n')
    if not matches:
        print("No matching scenarios found", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
