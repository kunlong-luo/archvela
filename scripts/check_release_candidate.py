#!/usr/bin/env python3
"""Static release-candidate contract check. Never creates a tag or publishes."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "docs/RELEASE-CANDIDATE.json"
TAG = "v0.1.0-alpha.1"
VERSION = "0.1.0-alpha.1"
HARD_GATES = (
    "release_owner_approved",
    "rights_review_approved",
    "main_protection_verified",
    "actual_l2_smoke_verified",
    "final_ci_verified",
)


def check() -> dict:
    manifest = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    if (manifest.get("schema_version") != 1
            or manifest.get("kind") != "archvela_unpublished_release_candidate"):
        raise ValueError("Unknown release candidate schema")
    if manifest.get("tag") != TAG or manifest.get("skill_version") != VERSION:
        raise ValueError("Alpha candidate tag/version mismatch")
    if manifest.get("state") != "draft_not_approved":
        raise ValueError("Do not mark release approved in the preparation contract")
    if manifest.get("release_sha") is not None:
        raise ValueError("Do not invent a final released commit")
    for field in (*HARD_GATES, "release_created", "tag_created"):
        if manifest.get(field) is not False:
            raise ValueError("Unverified release gate or created artifact claimed: " + field)
    if manifest.get("expected_scenarios") != 62:
        raise ValueError("Wrong catalog size")
    if manifest.get("expected_runnable_starters") != ["V3-02", "V3-14", "V3-26"]:
        raise ValueError("Wrong runnable starter set")
    if manifest.get("installer_l1_targets") != 20:
        raise ValueError("Wrong L1 installation matrix")
    skill = (ROOT / ".agents/skills/archvela-architect/SKILL.md").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1]
    if not re.search(r'(?m)^  version: "0\.1\.0-alpha\.1"$', frontmatter):
        raise ValueError("Skill frontmatter does not match candidate version")
    scenarios = json.loads(
        (ROOT / ".agents/skills/archvela-architect/references/scenarios.json").read_text(encoding="utf-8")
    )
    if len(scenarios) != 62 or len({item["id"] for item in scenarios}) != 62:
        raise ValueError("Invalid V3 catalog")
    for path_field in ("release_notes_en", "release_notes_zh", "checklist", "rights_register"):
        rel = Path(manifest[path_field])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Unsafe candidate document path: " + path_field)
        document = ROOT / rel
        if not document.is_file() or document.stat().st_size < 500:
            raise ValueError("Missing or too-short release document: " + path_field)
        body = document.read_text(encoding="utf-8")
        if TAG not in body:
            raise ValueError("Tag absent from release document: " + path_field)
    en = (ROOT / manifest["release_notes_en"]).read_text(encoding="utf-8")
    zh = (ROOT / manifest["release_notes_zh"]).read_text(encoding="utf-8")
    rights = (ROOT / manifest["rights_register"]).read_text(encoding="utf-8")
    checklist = (ROOT / manifest["checklist"]).read_text(encoding="utf-8")
    for word in ("NOT PUBLISHED", "62", "20", "L2", "PENDING"):
        if word not in en:
            raise ValueError("English release note disclaimer missing: " + word)
    for word in ("尚未发布", "62", "20", "L2", "待完成"):
        if word not in zh:
            raise ValueError("Chinese release note disclaimer missing: " + word)
    for word in ("PENDING HUMAN REVIEW", "NOT APPROVED", "license"):
        if word not in rights:
            raise ValueError("Human rights-review gate unclear: " + word)
    for word in ("NOT APPROVED FOR PUBLICATION", "owner", "PENDING"):
        if word not in checklist:
            raise ValueError("Release sign-off gate unclear: " + word)
    return {
        "schema_version": 1,
        "candidate": TAG,
        "state": "draft_not_approved",
        "structural_checks_passed": True,
        "release_created": False,
        "tag_created": False,
        "hard_gates_verified": 0,
        "hard_gates_pending": list(HARD_GATES),
        "caveat": "Structural draft check only; GitHub settings, real L2, licenses, final CI and owner approval are NOT verified.",
    }


def main() -> int:
    try:
        print(json.dumps(check(), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, IndexError) as exc:
        print("RELEASE-CANDIDATE-FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
