#!/usr/bin/env python3
"""Fail-closed offline check of an archived pnpm CI *observation* ledger.

This checks recorded SHA identities, current lock provenance, and 15 observed
virtual-store package roots. It never downloads tarballs or approves rights.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "docs/PNPM-LICENSE-EVIDENCE-2026-11.json"
EXPECTED_LOCKS = {
    "examples/cinematic-site/pnpm-lock.yaml": ("25bda3d9f9c52419e3ab263b8914590d82679c79", 40, 6),
    "examples/saas-workspace/pnpm-lock.yaml": ("f4803522e99af6c926c2c6b846baa6233e7f7fbd", 32, 6),
    "examples/home-digital-twin/pnpm-lock.yaml": ("fa8f80f2235d1b3ac8556f9a7460eeec267168b0", 47, 3),
    "tests/browser/pnpm-lock.yaml": ("df9f0e42f81a4d310059538802f82cb46bbb0e5a", 7, 0),
}
EXPECTED_RUNS = {
    42446627590: ("33d270cbc07df37c7359694f4269dbb38b13461b", {
        "cinematic-site": (13603552271, "0f6d656487b44f5902f178bc5ce79e3759430262b445f67026655c3d50157115", "6dd9cec6683b67d9432f80bc8e3e3f378bea0ec50f78343d97af6686c869791a"),
        "saas-workspace": (13603194954, "c37fe215576108753557cf3c8a48cab4731c67fe6a2da26a1eaaa1638d9af18f", "3a4865b4dd2898c00994116f058cc1a2a091dd6a6525875e4e0b3223e5776c02"),
        "home-digital-twin": (13603976253, "e6e0d5f3d8a2886fd744bfc72a36d70b9fee6643162b71f700c444af1aec4c94", "9e9488b4f734657dd910771d712f49a43c446937c332604104090981a28f29c4"),
        "browser-tests": (13603199980, "eec23cec1b079a05dcc621c71a44939d55b3391a3fd6aad36144dbc3e95e0d1f", "6aab14186655af811b463cdbd0e98b7b02a5ba5d03abe3ebd4b503f066a4b356"),
    }),
    43869383890: ("31a04f4bf010beca66dad4042f1bd2c19a3ba82a", {
        "cinematic-site": (14227570742, "b8776113da20e0105da4b23d4df1dda93e73bf90ed94f0326f24f3dcaa42eaaa", "6dd9cec6683b67d9432f80bc8e3e3f378bea0ec50f78343d97af6686c869791a"),
        "saas-workspace": (14225764469, "2525aedff2624215c373b2105504d280a90216cc3f9b5ff26e520e4eefffcb57", "3a4865b4dd2898c00994116f058cc1a2a091dd6a6525875e4e0b3223e5776c02"),
        "home-digital-twin": (14227056292, "c08e7a6d2f8543566b9526b5c5bba01de7541be947cfe12a32de86d566e417c2", "9e9488b4f734657dd910771d712f49a43c446937c332604104090981a28f29c4"),
        "browser-tests": (14227760394, "5892232188b762f49a5bcb0b306d634fc877f19fbd2b75f129d03fa04e9a989e", "6aab14186655af811b463cdbd0e98b7b02a5ba5d03abe3ebd4b503f066a4b356"),
    }),
}
EXPECTED_GAP_PACKAGES = {
    "examples/cinematic-site": {
        ("@img/sharp-libvips-linux-x64", "1.3.4"), ("@img/sharp-libvips-linuxmusl-x64", "1.3.4"),
        ("@next/env", "16.4.3"), ("@next/swc-linux-x64-gnu", "16.4.3"),
        ("@next/swc-linux-x64-musl", "16.4.3"), ("client-only", "0.0.1"),
    },
    "examples/saas-workspace": {
        ("@img/sharp-libvips-linux-x64", "1.3.4"), ("@img/sharp-libvips-linuxmusl-x64", "1.3.4"),
        ("@next/env", "16.4.3"), ("@next/swc-linux-x64-gnu", "16.4.3"),
        ("@next/swc-linux-x64-musl", "16.4.3"), ("client-only", "0.0.1"),
    },
    "examples/home-digital-twin": {
        ("@react-three/fiber", "9.8.2"), ("@rolldown/binding-linux-x64-gnu", "1.2.15"),
        ("@rolldown/binding-linux-x64-musl", "1.2.15"),
    },
}
HASH = re.compile(r"^[a-f0-9]{64}$")


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def validate(ledger: dict, root: Path = ROOT) -> dict:
    if ledger.get("schema_version") != 1 or ledger.get("kind") != "archvela_pnpm_virtual_store_root_notice_evidence":
        raise ValueError("Unknown pnpm evidence schema")
    if ledger.get("review_status") != "pending_human" or ledger.get("rights_cleared") is not False:
        raise ValueError("Unverified evidence approved as legal rights")
    if (ledger.get("pnpm_version") != "10.22.0"
            or ledger.get("root_notice_gap_occurrences") != 15
            or ledger.get("distinct_package_versions_with_root_notice_gaps") != 9
            or ledger.get("observed_virtual_store_total") != 126
            or ledger.get("archived_npm_root_notice_occurrences") != 10
            or ledger.get("archived_npm_distinct_package_versions") != 6
            or ledger.get("archived_npm_source") != "docs/INSTALLED-LICENSE-EXCEPTIONS.json"):
        raise ValueError("Historical or pnpm CI count changed")
    lockfiles = ledger.get("reviewed_pnpm_lockfiles")
    if not isinstance(lockfiles, list) or len(lockfiles) != 4:
        raise ValueError("Expected four pnpm lock sources")
    locked_data = {}
    seen_locks = set()
    for item in lockfiles:
        path = item.get("path")
        if path not in EXPECTED_LOCKS or path in seen_locks:
            raise ValueError("Unknown or duplicate pnpm lock")
        sha, total, gaps = EXPECTED_LOCKS[path]
        if (item.get("git_blob_sha"), item.get("materialized_virtual_store_package_roots"),
                item.get("missing_root_notice_occurrences")) != (sha, total, gaps):
            raise ValueError("pnpm lock evidence count or SHA changed")
        f = root / path
        if f.is_symlink() or not f.is_file():
            raise ValueError("Missing or symlinked pnpm lock")
        content = f.read_bytes()
        if blob_sha(content) != sha or b"lockfileVersion: '9.0'" not in content:
            raise ValueError("pnpm lock changed since actual CI observations")
        locked_data[path.removesuffix("/pnpm-lock.yaml")] = content.decode("utf-8")
        seen_locks.add(path)
    if seen_locks != set(EXPECTED_LOCKS):
        raise ValueError("Missing reviewed pnpm lock")
    runs = ledger.get("historical_run_evidence")
    if not isinstance(runs, list) or len(runs) != 2:
        raise ValueError("Expected two real workflow runs")
    seen_runs, seen_artifacts = set(), set()
    for entry in runs:
        run_id = entry.get("run_id")
        if run_id in seen_runs or run_id not in EXPECTED_RUNS:
            raise ValueError("Unknown/duplicate CI run")
        source_sha, expected = EXPECTED_RUNS[run_id]
        if entry.get("commit_sha") != source_sha:
            raise ValueError("CI source commit changed")
        artifacts = entry.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != 4:
            raise ValueError("Expected four actual ZIP artifacts per run")
        names = set()
        for artifact in artifacts:
            project = artifact.get("project")
            if project not in expected or project in names:
                raise ValueError("Unknown/duplicate evidence artifact")
            id_, zip_sha, json_sha = expected[project]
            if (artifact.get("artifact_id"), artifact.get("artifact_name"),
                    artifact.get("zip_sha256"), artifact.get("json_sha256"),
                    artifact.get("zip_is_original_github_artifact")) != (
                    id_, "installed-license-evidence-" + project, zip_sha, json_sha, True):
                raise ValueError("Actual GitHub artifact identity/digest changed")
            if not HASH.fullmatch(zip_sha) or not HASH.fullmatch(json_sha):
                raise ValueError("Malformed artifact digest")
            if id_ in seen_artifacts:
                raise ValueError("Duplicate artifact id")
            seen_artifacts.add(id_)
            names.add(project)
        if names != set(expected):
            raise ValueError("Incomplete actual CI evidence")
        seen_runs.add(run_id)
    if seen_runs != set(EXPECTED_RUNS):
        raise ValueError("Missing original pnpm CI run")
    rows = ledger.get("observations")
    if not isinstance(rows, list) or len(rows) != 15:
        raise ValueError("All 15 real package-root gaps must remain visible")
    per_project = {name: set() for name in EXPECTED_GAP_PACKAGES}
    paths = set()
    unique = set()
    for row in rows:
        project, name, version, path = (row.get("project"), row.get("name"),
                                        row.get("version"), row.get("virtual_store_path"))
        if (project not in per_project or (name, version) not in EXPECTED_GAP_PACKAGES[project]
                or not isinstance(path, str) or not path.startswith("node_modules/.pnpm/")
                or "\\" in path or ".." in path.split("/")):
            raise ValueError("Unknown or unsafe pnpm package root observation")
        if not path.endswith("/node_modules/" + name):
            raise ValueError("Installed package path does not match recorded name")
        if (project, path) in paths or (name, version) in per_project[project]:
            raise ValueError("Duplicate pnpm observed package")
        if (row.get("missing_recognized_root_notice") is not True
                or row.get("registry_tarball_verified") is not False
                or row.get("runtime_linkage_verified") is not False
                or row.get("shipped_payload_verified") is not False
                or row.get("review_status") != "pending_human"
                or row.get("rights_cleared") is not False):
            raise ValueError("Unreviewed pnpm package observation silently approved")
        if f"{name}@{version}".encode("utf-8") not in locked_data[project].encode("utf-8"):
            raise ValueError("Observed package/version missing in frozen pnpm lock")
        per_project[project].add((name, version))
        paths.add((project, path))
        unique.add((name, version))
    if per_project != EXPECTED_GAP_PACKAGES or len(unique) != 9:
        raise ValueError("The 15 package observations have changed")
    archived = root / "docs/INSTALLED-LICENSE-EXCEPTIONS.json"
    if archived.is_symlink():
        raise ValueError("Historical evidence register symlink")
    previous = json.loads(archived.read_text(encoding="utf-8"))
    if previous.get("rights_cleared") is not False or len(previous.get("exceptions", [])) != 10:
        raise ValueError("Historical npm-era CI observations changed or approved")
    return {"status": "PNPM_VIRTUAL_STORE_EVIDENCE_MATCHED_NOT_LEGAL_CLEARANCE",
            "artifact_archives": len(seen_artifacts), "root_notice_gap_occurrences": len(paths),
            "distinct_package_versions": len(unique), "rights_cleared": False}


def main() -> int:
    try:
        result = validate(json.loads(FILE.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print("PNPM-LICENSE-LEDGER-FAIL: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
