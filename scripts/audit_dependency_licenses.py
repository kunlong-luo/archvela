#!/usr/bin/env python3
"""Audit lockfile license *metadata* offline; NEVER grant legal clearance.

A checked-in review register tracks package/version/license declarations from
npm package-lock v3. This is not a package license-file or rights audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/DEPENDENCY-LICENSE-REVIEW.json"
LOCKFILES = (
    "examples/cinematic-site/package-lock.json",
    "examples/home-digital-twin/package-lock.json",
    "examples/saas-workspace/package-lock.json",
    "tests/browser/package-lock.json",
)
# This is only a *review triage* allowlist, NOT a legal allowlist: even MIT
# packages need authorship, license-text and NOTICE verification by a human.
SIMPLE_METADATA_EXPRESSIONS = frozenset((
    "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause",
    "ISC", "0BSD", "Unlicense",
))


def git_blob_id(raw: bytes) -> str:
    """Git's file blob object ID, useful for detecting any lockfile change."""
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def collect(root: Path = ROOT) -> dict:
    flagged = []
    all_rows = 0
    missing = 0
    licenses = Counter()
    blobs = {}
    by_lock = {}
    for relative in LOCKFILES:
        path = root / relative
        if path.is_symlink():
            raise ValueError("Refusing to read a symlink lockfile: " + relative)
        raw = path.read_bytes()
        blobs[relative] = git_blob_id(raw)
        data = json.loads(raw)
        if data.get("lockfileVersion") != 3:
            raise ValueError("Expected npm lockfile v3: " + relative)
        packages = data.get("packages")
        if not isinstance(packages, dict) or not packages:
            raise ValueError("Missing lockfile package map: " + relative)
        count = 0
        for package_path, pkg in packages.items():
            if package_path == "":  # npm's root project metadata, not a dependency
                continue
            if (not isinstance(package_path, str)
                    or not package_path.startswith("node_modules/")
                    or ".." in package_path.split("/")):
                raise ValueError("Unexpected installed package path: " + str(package_path))
            if not isinstance(pkg, dict):
                raise ValueError("Malformed installed package entry: " + package_path)
            name = package_path.rsplit("node_modules/", 1)[-1]
            version = pkg.get("version")
            license_id = pkg.get("license")
            if not isinstance(version, str) or not version.strip():
                raise ValueError("Missing installed dependency version: " + name)
            if not isinstance(license_id, str) or not license_id.strip():
                license_id = None
                missing += 1
            licenses[license_id or "<missing metadata>"] += 1
            all_rows += 1
            count += 1
            if license_id not in SIMPLE_METADATA_EXPRESSIONS:
                flagged.append({
                    "lockfile": relative, "package_path": package_path,
                    "name": name, "version": version, "license": license_id,
                    "development": pkg.get("dev") is True,
                    "optional": pkg.get("optional") is True,
                    "review_status": "pending_human_review",
                })
        by_lock[relative] = count
    flagged.sort(key=lambda v: (v["lockfile"], v["package_path"]))
    return {
        "lockfile_git_blob_sha": blobs,
        "expected_package_rows": all_rows,
        "expected_flagged_rows": len(flagged),
        "flagged_dependencies": flagged,
        "missing_declared_license": missing,
        "license_metadata_counts": dict(sorted(licenses.items())),
        "by_lockfile": by_lock,
    }


def verify_register(register: dict, observed: dict) -> None:
    if register.get("schema_version") != 1 or register.get("kind") != (
            "archvela_dependency_license_metadata_review"):
        raise ValueError("Unexpected dependency rights register schema")
    if (register.get("status") != "pending_human_review"
            or register.get("rights_cleared") is not False):
        raise ValueError("Unverified third-party dependency rights approval claimed")
    for key in ("lockfile_git_blob_sha", "expected_package_rows", "expected_flagged_rows"):
        if register.get(key) != observed[key]:
            raise ValueError("Stale/changed lockfile or license review list: " + key)
    def index(records: object) -> dict:
        if not isinstance(records, list):
            raise ValueError("Invalid reviewed dependency list")
        items = {}
        for entry in records:
            if not isinstance(entry, dict):
                raise ValueError("Invalid dependency review record")
            identity = (entry.get("lockfile"), entry.get("package_path"))
            if identity in items:
                raise ValueError("Duplicate dependency review record")
            items[identity] = entry
        return items
    if index(register.get("flagged_dependencies")) != index(observed["flagged_dependencies"]):
        raise ValueError("Stale/changed lockfile or license review list: flagged_dependencies")
    if observed["missing_declared_license"]:
        raise ValueError("Lockfile dependencies have missing license metadata")
    # Even all metadata present and zero flag rows would NOT be rights clearance.


def audit(root: Path = ROOT, register_path: Path | None = None) -> dict:
    observed = collect(root)
    path = register_path or root / "docs/DEPENDENCY-LICENSE-REVIEW.json"
    if path.is_symlink():
        raise ValueError("Refusing symlink rights register")
    register = json.loads(path.read_text(encoding="utf-8"))
    verify_register(register, observed)
    return {
        "schema_version": 1,
        "kind": "lockfile_license_metadata_only",
        "lockfile_count": len(LOCKFILES),
        "dependency_install_rows": observed["expected_package_rows"],
        "manual_review_rows": observed["expected_flagged_rows"],
        "missing_declared_license": observed["missing_declared_license"],
        "reviewed_and_cleared": False,
        "rights_register_state": "pending_human_review",
        "licenses": observed["license_metadata_counts"],
        "by_lockfile": observed["by_lockfile"],
        "caveat": "npm lockfile license strings are self-reported metadata, not verified license texts, legally sufficient notices, installed artifact contents, permission or distributability.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline npm lockfile metadata inventory, NOT copyright clearance")
    parser.add_argument("--json", action="store_true", help="Emit full metadata-only audit summary as JSON")
    args = parser.parse_args()
    try:
        result = audit()
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print("DEPENDENCY-LICENSE-AUDIT-FAIL: " + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("DEPENDENCY-LICENSE-METADATA-OK: {} locks, {} installation rows, "
              "{} flagged for human review, {} missing metadata; RIGHTS NOT CLEARED".format(
                  result["lockfile_count"], result["dependency_install_rows"],
                  result["manual_review_rows"], result["missing_declared_license"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
