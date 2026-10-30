#!/usr/bin/env python3
"""Check redistribution provenance records for committed-style media assets.

This is an inventory/documentation guard, not a legal opinion or proof that
the claimed rights are genuine. It performs no network calls.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

ASSET_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg", ".ico",
    ".glb", ".gltf", ".obj", ".fbx", ".stl", ".hdr", ".exr",
    ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".mov",
    ".woff", ".woff2", ".ttf", ".otf",
    ".pdf",  # Bundled documents can also carry redistribution rights.
}
SKIP_DIRS = {
    ".git", ".next", "node_modules", "dist", "build", "coverage",
    "__pycache__", ".venv", ".pytest_cache", "test-results",
    "playwright-report", ".turbo",
}
MANIFEST = Path("docs/ASSET-PROVENANCE.json")


def discover(root: Path) -> list[str]:
    assets = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        directory = Path(current)
        for name in sorted(files):
            path = directory / name
            if path.suffix.lower() not in ASSET_SUFFIXES:
                continue
            if path.is_symlink():
                raise ValueError("Media symlink is not permitted: " + str(path.relative_to(root)))
            if not path.is_file():
                raise ValueError("Media is not a regular file: " + str(path.relative_to(root)))
            assets.append(path.relative_to(root).as_posix())
    return sorted(assets)


def verify(root: Path) -> dict:
    path = root / MANIFEST
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or symlinked provenance manifest: " + str(MANIFEST))
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("Unsupported provenance manifest schema")
    items = manifest.get("assets")
    if not isinstance(items, list):
        raise ValueError("Provenance manifest assets must be an array")

    found = discover(root)
    records: dict[str, dict] = {}
    for row in items:
        if not isinstance(row, dict):
            raise ValueError("Provenance row must be an object")
        name = row.get("path")
        if not isinstance(name, str) or not name:
            raise ValueError("Provenance record missing path")
        normalized = Path(name)
        if (normalized.is_absolute() or ".." in normalized.parts or
                normalized.as_posix() != name or name in records):
            raise ValueError("Unsafe or duplicate provenance path: " + name)
        for key in ("origin", "rights_holder", "license", "source", "attribution", "reviewed_on"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing {key} for {name}")
        if row["origin"] not in ("original", "third_party"):
            raise ValueError("origin must be original or third_party: " + name)
        if row.get("redistribution_approved") is not True:
            raise ValueError("Asset must be explicitly approved for redistribution: " + name)
        try:
            dt.date.fromisoformat(row["reviewed_on"])
        except ValueError as exc:
            raise ValueError("Invalid reviewed_on for " + name) from exc
        records[name] = row
    missing = sorted(set(found) - set(records))
    stale = sorted(set(records) - set(found))
    if missing or stale:
        raise ValueError(f"Asset provenance mismatch: unrecorded={missing}, stale={stale}")
    return {
        "inventory_check": "passed",
        "media_files": len(found),
        "manifest_entries": len(records),
        "caveat": "Metadata presence validated, not authorship, license accuracy or redistribution rights.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Offline media provenance inventory gate")
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Repository root is not a directory")
        result = verify(root)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
