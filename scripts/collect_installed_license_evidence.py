#!/usr/bin/env python3
"""Collect evidence of installed npm LICENSE/NOTICE files, without legal approval.

The lockfile audit checks declared license metadata; this script observes what
actually arrived in one isolated npm install. Missing license files are
recorded as unresolved human-review findings, not silently accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

TEXT_NAMES = ("LICENSE", "LICENCE", "COPYING", "NOTICE", "ATTRIBUTION", "THIRD_PARTY")
MAX_BYTES = 2 * 1024 * 1024


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def is_license_filename(name: str) -> bool:
    upper = name.upper()
    return any(upper == token or upper.startswith(token + ".")
               or upper.startswith(token + "-") or upper.startswith(token + "_")
               for token in TEXT_NAMES)


def inventory(directory: Path) -> dict:
    directory = directory.resolve()
    lock_path = directory / "package-lock.json"
    if lock_path.is_symlink() or not lock_path.is_file():
        raise ValueError("Expected non-symlink package-lock.json in " + str(directory))
    lock_bytes = lock_path.read_bytes()
    lock = json.loads(lock_bytes)
    if lock.get("lockfileVersion") != 3 or not isinstance(lock.get("packages"), dict):
        raise ValueError("Expected npm v3 packages lockfile")
    if not (directory / "node_modules").is_dir():
        raise ValueError("node_modules is missing; run npm ci --ignore-scripts first")
    rows = []
    missing_required = 0
    installed = 0
    missing_text = 0
    optional_skipped = 0
    for package_path, expected in sorted(lock["packages"].items()):
        if package_path == "":
            continue
        if (not package_path.startswith("node_modules/")
                or ".." in package_path.split("/") or "\\" in package_path):
            raise ValueError("Invalid npm package path: " + package_path)
        if not isinstance(expected, dict) or not isinstance(expected.get("version"), str):
            raise ValueError("Invalid lockfile entry: " + package_path)
        pkg = directory / package_path
        row = {
            "path": package_path,
            "name": package_path.rsplit("node_modules/", 1)[-1],
            "version": expected["version"],
            "lockfile_license": expected.get("license"),
            "development": expected.get("dev") is True,
            "optional": expected.get("optional") is True,
            "installed": False,
            "license_notice_files": [],
            "review_state": "not_approved",
        }
        if not pkg.exists():
            if not row["optional"]:
                missing_required += 1
            else:
                optional_skipped += 1
            rows.append(row)
            continue
        if pkg.is_symlink() or not pkg.is_dir() or not pkg.resolve().is_relative_to(directory):
            raise ValueError("Unsafe installed package directory: " + package_path)
        manifest = pkg / "package.json"
        if manifest.is_symlink() or not manifest.is_file():
            raise ValueError("Installed package.json missing or symlink: " + package_path)
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        if meta.get("version") != expected["version"]:
            raise ValueError("Installed package version differs from lockfile: " + package_path)
        row["installed"] = True
        row["installed_license_metadata"] = meta.get("license")
        installed += 1
        for candidate in sorted(pkg.iterdir()):
            if not is_license_filename(candidate.name):
                continue
            if candidate.is_symlink():
                raise ValueError("Untrusted license/NOTICE symlink: " + str(candidate))
            if not candidate.is_file():
                continue
            if candidate.stat().st_size > MAX_BYTES:
                raise ValueError("License/NOTICE file exceeds evidence size cap: " + str(candidate))
            raw = candidate.read_bytes()
            row["license_notice_files"].append({
                "name": candidate.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            })
        if not row["license_notice_files"]:
            missing_text += 1
        rows.append(row)
    if missing_required:
        raise ValueError(f"{missing_required} required lockfile packages missing from node_modules")
    return {
        "schema_version": 1,
        "kind": "installed_npm_license_file_evidence",
        "rights_cleared": False,
        "review_state": "evidence_only_not_approved",
        "lockfile_git_blob_sha": git_blob_id(lock_bytes),
        "lockfile_package_rows": len(rows),
        "installed_package_rows": installed,
        "optional_platform_rows_not_installed": optional_skipped,
        "installed_rows_without_top_level_license_or_notice": missing_text,
        "rows": rows,
        "caveat": (
            "Package-root LICENSE/NOTICE file names and SHA-256 hashes are "
            "evidence, not proof of license authenticity, completeness, "
            "legal redistribution approval, deployable binary contents or "
            "third-party source rights. Absence does not prove infringement."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Observe installed npm license file evidence; no legal clearance")
    ap.add_argument("--directory", type=Path, required=True, help="npm project after npm ci --ignore-scripts")
    ap.add_argument("--output", type=Path, required=True, help="JSON report path outside installed source")
    args = ap.parse_args()
    try:
        report = inventory(args.directory)
        target = args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
        print("INSTALLED-LICENSE-EVIDENCE-FAIL: " + str(exc), file=sys.stderr)
        return 2
    print(
        f"INSTALLED-LICENSE-EVIDENCE: {report['installed_package_rows']} installed/"
        f"{report['lockfile_package_rows']} locked; "
        f"{report['installed_rows_without_top_level_license_or_notice']} "
        "without top-level LICENSE/NOTICE. RIGHTS NOT CLEARED."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
