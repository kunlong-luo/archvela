#!/usr/bin/env python3
"""Inventory actual pnpm virtual-store package notices, never legal clearance.

A frozen pnpm install must precede collection. Only real package roots under
node_modules/.pnpm are inspected; pnpm's dependency symlinks are not followed.
The snapshot reports installed packages, NOT optional-platform packages skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

TEXT_NAMES = ("LICENSE", "LICENCE", "COPYING", "NOTICE", "ATTRIBUTION", "THIRD_PARTY")
MAX_BYTES = 2 * 1024 * 1024


def git_blob_id(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def is_license_filename(name: str) -> bool:
    name = name.upper()
    return any(name == token or name.startswith(token + ".")
               or name.startswith(token + "_") or name.startswith(token + "-")
               for token in TEXT_NAMES)


def real_packages(virtual_store: Path):
    """Yield non-symlinked real package roots, excluding dependency links."""
    if virtual_store.is_symlink() or not virtual_store.is_dir():
        raise ValueError("Missing or linked pnpm virtual store")
    for item in sorted(virtual_store.iterdir()):
        if item.is_symlink():
            raise ValueError("Unexpected pnpm virtual-store symlink")
        if not item.is_dir():
            continue
        nm = item / "node_modules"
        if nm.is_symlink() or not nm.is_dir():
            raise ValueError("Malformed pnpm virtual-store node_modules")
        for child in sorted(nm.iterdir()):
            if child.is_symlink():
                continue  # ordinary pnpm dependency link, not a package root
            if not child.is_dir():
                continue
            if child.name.startswith("@"):
                if child.is_symlink():
                    raise ValueError("Unsafe scope symlink")
                roots = sorted(child.iterdir())
            else:
                roots = (child,)
            for pkg in roots:
                if pkg.is_symlink():
                    continue
                if pkg.is_dir() and (pkg / "package.json").is_file():
                    yield pkg


def inventory(directory: Path) -> dict:
    directory = directory.resolve()
    lock = directory / "pnpm-lock.yaml"
    if lock.is_symlink() or not lock.is_file():
        raise ValueError("Expected pnpm-lock.yaml")
    lock_bytes = lock.read_bytes()
    if b"lockfileVersion: '9.0'" not in lock_bytes or b"importers:" not in lock_bytes:
        raise ValueError("Unexpected pnpm lockfile format")
    manifest = directory / "package.json"
    if manifest.is_symlink():
        raise ValueError("Linked project package.json")
    project = json.loads(manifest.read_text(encoding="utf-8"))
    if project.get("packageManager") != "pnpm@10.22.0":
        raise ValueError("Unexpected pnpm version pin")
    store = directory / "node_modules" / ".pnpm"
    rows = []
    seen_paths = set()
    missing_notices = 0
    names = set()
    for pkg in real_packages(store):
        if not pkg.resolve().is_relative_to(store.resolve()):
            raise ValueError("Package escapes pnpm virtual store")
        pmanifest = pkg / "package.json"
        if pmanifest.is_symlink():
            raise ValueError("Unsafe package manifest symlink")
        meta = json.loads(pmanifest.read_text(encoding="utf-8"))
        name, version = meta.get("name"), meta.get("version")
        if not isinstance(name, str) or not name or not isinstance(version, str) or not version:
            raise ValueError("Invalid installed package metadata")
        relative = pkg.relative_to(directory).as_posix()
        if relative in seen_paths:
            raise ValueError("Duplicate package installation path")
        seen_paths.add(relative)
        names.add(name)
        notices = []
        for candidate in sorted(pkg.iterdir()):
            if not is_license_filename(candidate.name):
                continue
            if candidate.is_symlink():
                raise ValueError("Unsafe license symlink " + str(candidate))
            if not candidate.is_file():
                continue
            if candidate.stat().st_size > MAX_BYTES:
                raise ValueError("License file exceeds evidence size cap")
            raw = candidate.read_bytes()
            notices.append({"name": candidate.name,
                            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        missing_notices += not bool(notices)
        rows.append({"path": relative, "name": name, "version": version,
                     "installed_license_metadata": meta.get("license"),
                     "license_notice_files": notices, "review_state": "not_approved"})
    required = set(project.get("dependencies") or {}) | set(project.get("devDependencies") or {})
    missing_direct = sorted(required - names)
    if missing_direct:
        raise ValueError("Required direct pnpm package absent: " + ", ".join(missing_direct))
    if not rows:
        raise ValueError("No installed package roots found")
    return {"schema_version": 1, "kind": "installed_pnpm_license_file_evidence",
            "package_manager": project["packageManager"], "rights_cleared": False,
            "review_state": "evidence_only_not_approved",
            "lockfile_git_blob_sha": git_blob_id(lock_bytes),
            "installed_package_rows": len(rows),
            "installed_rows_without_top_level_license_or_notice": missing_notices,
            "uninstalled_optional_platform_rows": "not_measured",
            "rows": rows,
            "caveat": ("pnpm virtual-store installed package roots only. Missing optional OS/CPU "
                       "dependencies are unmeasured; root-file absence is not infringement. "
                       "These hashes do not establish legally sufficient notices or redistribution rights.")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Installed pnpm package-root evidence only")
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = inventory(args.directory)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print("PNPM-LICENSE-EVIDENCE-FAIL: " + str(exc), file=sys.stderr)
        return 2
    print("PNPM-LICENSE-EVIDENCE: installed={}, missing_root_notice={}, RIGHTS NOT CLEARED".format(
        report["installed_package_rows"],
        report["installed_rows_without_top_level_license_or_notice"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
