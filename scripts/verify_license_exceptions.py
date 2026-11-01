#!/usr/bin/env python3
"""Validate a *historical* four-artifact npm LICENSE/NOTICE exception snapshot.

No legal rights approval, model call, network request or GitHub mutation.
The report is tied to one known workflow run and immutable lockfile blobs.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "docs/INSTALLED-LICENSE-EXCEPTIONS.json"
SOURCE_SHA = "f15a5bd394a5e32f509b6d61887a2493cdcb13fa"
RUN_ID = 41262733686
EXPECTED_ARTIFACTS = {
    "examples/cinematic-site/package-lock.json": (88, 37, 51, 4),
    "examples/saas-workspace/package-lock.json": (80, 29, 51, 4),
    "examples/home-digital-twin/package-lock.json": (89, 45, 44, 2),
    "tests/browser/package-lock.json": (26, 7, 19, 0),
}

# Original artifact IDs and SHA-256 of the extracted JSON bytes (downloaded
# from the successful run, not independently legal/provenance approval).
EXPECTED_REPORTS = {
    "examples/cinematic-site/package-lock.json": (
        13065628785, "installed-license-evidence-cinematic-site",
        "7840f1cb1d123166ad023b1d59f39c9883a076da5cae2e45564cf58da0c2a826"),
    "examples/saas-workspace/package-lock.json": (
        13065519062, "installed-license-evidence-saas-workspace",
        "08da4e763621ea57f0099b39cdd5e49fadef068a26352029432ee67c9f0749b3"),
    "examples/home-digital-twin/package-lock.json": (
        13065314851, "installed-license-evidence-home-digital-twin",
        "f608d5c504678e4c40e29125daf38658e15090b2a0a384daba4ebc50bc68f9e6"),
    "tests/browser/package-lock.json": (
        13065549168, "installed-license-evidence-browser-tests",
        "f21704710105884916c97d71429d852b9d5572b61553ec13ef8fa04535d68353"),
}
# Frozen observation from the downloaded CI reports, NOT an allowed-license list.
EXPECTED_GAPS = {
    ("examples/cinematic-site/package-lock.json", "node_modules/@img/sharp-libvips-linux-x64"),
    ("examples/cinematic-site/package-lock.json", "node_modules/@next/env"),
    ("examples/cinematic-site/package-lock.json", "node_modules/@next/swc-linux-x64-gnu"),
    ("examples/cinematic-site/package-lock.json", "node_modules/client-only"),
    ("examples/home-digital-twin/package-lock.json", "node_modules/@react-three/fiber"),
    ("examples/home-digital-twin/package-lock.json", "node_modules/@rolldown/binding-linux-x64-gnu"),
    ("examples/saas-workspace/package-lock.json", "node_modules/@img/sharp-libvips-linux-x64"),
    ("examples/saas-workspace/package-lock.json", "node_modules/@next/env"),
    ("examples/saas-workspace/package-lock.json", "node_modules/@next/swc-linux-x64-gnu"),
    ("examples/saas-workspace/package-lock.json", "node_modules/client-only"),
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def validate(manifest: dict, root: Path = ROOT) -> dict:
    if manifest.get("schema_version") != 1 or (
        manifest.get("kind") != "historical_installed_license_evidence_exceptions"
    ):
        raise ValueError("Unexpected exception manifest schema")
    if manifest.get("source_commit") != SOURCE_SHA or manifest.get("security_workflow_run_id") != RUN_ID:
        raise ValueError("Unverified original GitHub source commit/run")
    if manifest.get("review_status") != "pending_human" or manifest.get("rights_cleared") is not False:
        raise ValueError("No human licensing or redistribution approval has been granted")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(EXPECTED_ARTIFACTS):
        raise ValueError("Expected exactly four actual CI reports")
    names, ids = set(), set()
    metadata = {}
    for a in artifacts:
        path = a.get("lockfile")
        if path not in EXPECTED_ARTIFACTS or path in metadata:
            raise ValueError("Unknown or duplicate lockfile artifact")
        if (a.get("locked"), a.get("installed"),
            a.get("optional_skipped"), a.get("missing_root_notice")) != EXPECTED_ARTIFACTS[path]:
            raise ValueError("CI installation counts do not match actual archived observation: " + path)
        if not isinstance(a.get("id"), int) or a["id"] <= 0 or a["id"] in ids:
            raise ValueError("Invalid/duplicate historical GitHub artifact ID")
        if not isinstance(a.get("name"), str) or not a["name"].startswith("installed-license-evidence-") or a["name"] in names:
            raise ValueError("Invalid/duplicate artifact name")
        if not isinstance(a.get("report_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", a["report_sha256"]):
            raise ValueError("Missing original CI report digest")
        if (a["id"], a["name"], a["report_sha256"]) != EXPECTED_REPORTS[path]:
            raise ValueError("Historical artifact ID/name/report digest changed")
        # Prefer immutable npm-era archive; retain fixture fallback for tests.
        archived = root / "docs/historical/npm-lockfiles" / path
        f = archived if archived.is_file() or archived.is_symlink() else root / path
        if f.is_symlink() or not f.is_file():
            raise ValueError("Missing/symlinked reviewed npm lockfile: " + path)
        raw = f.read_bytes()
        if a.get("lockfile_git_blob_sha") != git_blob_sha(raw):
            raise ValueError("Locked source has changed since original CI evidence: " + path)
        parsed = json.loads(raw)
        if parsed.get("lockfileVersion") != 3 or not isinstance(parsed.get("packages"), dict):
            raise ValueError("Unrecognized npm lockfile format")
        metadata[path] = parsed["packages"]
        names.add(a["name"])
        ids.add(a["id"])
    if set(metadata) != set(EXPECTED_ARTIFACTS):
        raise ValueError("A reviewed project has no evidence")
    entries = manifest.get("exceptions")
    if not isinstance(entries, list) or len(entries) != 10:
        raise ValueError("10 observed package-root gaps must remain visible")
    actual = set()
    unique = set()
    for entry in entries:
        key = (entry.get("lockfile"), entry.get("package_path"))
        if key in actual or key not in EXPECTED_GAPS:
            raise ValueError("Unexpected, duplicate or missing historical package-root exception")
        actual.add(key)
        package = metadata[key[0]].get(key[1])
        if not isinstance(package, dict):
            raise ValueError("Exception references absent lockfile dependency: " + str(key))
        fields = (
            ("version", "version"),
            ("declared_license", "license"),
        )
        for field, lock_field in fields:
            if entry.get(field) != package.get(lock_field):
                raise ValueError("Package changed since actual evidence: " + str(key))
        if entry.get("development") is not (package.get("dev") is True) or (
                entry.get("optional") is not (package.get("optional") is True)):
            raise ValueError("Dependency optional/development flags changed: " + str(key))
        if entry.get("review_status") != "pending_human":
            raise ValueError("An exception was silently approved or omitted")
        if entry.get("observation") != "no recognized package-root LICENSE/NOTICE file in CI install":
            raise ValueError("Exception observation tampered")
        unique.add((key[1], entry["version"]))
    if actual != EXPECTED_GAPS or len(unique) != 6:
        raise ValueError("Historical 10 occurrence / 6 unique package observation changed")
    if sum(x[0] for x in EXPECTED_ARTIFACTS.values()) != 283:
        raise ValueError("Unexpected source lockfile count")
    return {
        "status": "HISTORICAL_EVIDENCE_MATCHED_NOT_LEGAL_CLEARANCE",
        "source_sha": SOURCE_SHA,
        "security_run_id": RUN_ID,
        "lockfile_package_rows": 283,
        "installed_package_rows": 118,
        "uninstalled_optional_platform_rows": 165,
        "root_notice_gaps": len(actual),
        "distinct_affected_package_versions": len(unique),
        "human_review_approved": False,
        "note": "Historical CI source and lockfile checks only. Actual license texts, redistribution rights and current-platform outputs require an authorized human.",
    }


def main() -> int:
    try:
        result = validate(json.loads(FILE.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("LICENSE-EXCEPTIONS-FAIL: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
