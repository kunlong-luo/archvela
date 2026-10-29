#!/usr/bin/env python3
"""Offline architecture contract checks. This never executes generated code.

Passing a gate proves required *fields* are present. It cannot prove that
test results, device measurements or an AI agent's claims are truthful.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
CATALOG = SKILL / "references/scenarios.json"
LAYERS = ("package", "feature", "chunk", "assets")
STATES = ("draft", "reviewed", "delivered")


def draft_plan(project: str, scene: dict, profile: dict) -> dict:
    return {
        "schema_version": 1,
        "project": project,
        "scenario": {
            "id": scene["id"],
            "title": scene["title"],
            "domain_code": scene["domain_code"],
        },
        "status": "draft",
        "stack": {
            "candidate": scene["stack"],
            "selected": "",
            "rationale": "",
            "rejected_alternatives": [],
        },
        "boundaries": {
            key: {"recommendation": profile[key], "selected": ""}
            for key in LAYERS
        },
        "fallback": {"recommendation": profile["fallback"], "selected": ""},
        "repository_audit": {"completed": False, "evidence": []},
        "target_environment": {"browsers": [], "devices": []},
        "risks": {"initial": profile["risk"], "mitigations": []},
        "delivery": {
            "mvp": scene["mvp"],
            "phases": [profile["m1"], profile["m2"], profile["m3"]],
            "planned_tests": [],
            "test_evidence": [],
            "measurements": [],
        },
        "provenance": {
            "source": "Archvela V3 scenario reference snapshot",
            "implementation_verified": False,
            "notice": "Draft recommendations only; real repository, tools, "
                      "device measurements and test outcomes require verification.",
        },
    }


def filled(value: object, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def filled_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(filled(v) for v in value)


def validate(plan: object, level: str = "draft") -> list[str]:
    failures: list[str] = []
    if not isinstance(plan, dict):
        return ["root must be an object"]
    if plan.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    project = plan.get("project")
    if not filled(project) or len(project) > 120:
        failures.append("project must be a nonblank string up to 120 characters")

    by_id = {r["id"]: r for r in json.loads(CATALOG.read_text(encoding="utf-8"))}
    scenario = plan.get("scenario")
    if not isinstance(scenario, dict):
        scenario = {}
        failures.append("scenario must be an object")
    scene_id = scenario.get("id")
    source = by_id.get(scene_id) if isinstance(scene_id, str) else None
    if source is None:
        failures.append("scenario.id must match a versioned V3 scenario")
    else:
        if scenario.get("title") != source["title"]:
            failures.append("scenario.title differs from catalog")
        if scenario.get("domain_code") != source["domain_code"]:
            failures.append("scenario.domain_code differs from catalog")

    status = plan.get("status")
    if status not in STATES:
        failures.append("status must be draft, reviewed or delivered")
    stack = plan.get("stack")
    if not isinstance(stack, dict):
        stack = {}
        failures.append("stack must be an object")
    if not filled(stack.get("candidate")):
        failures.append("stack.candidate is required")
    boundaries = plan.get("boundaries")
    if not isinstance(boundaries, dict):
        boundaries = {}
        failures.append("boundaries must be an object")
    for name in LAYERS:
        layer = boundaries.get(name)
        if not isinstance(layer, dict) or not filled(layer.get("recommendation")):
            failures.append("boundaries." + name + ".recommendation is required")
    fallback = plan.get("fallback")
    if not isinstance(fallback, dict):
        fallback = {}
        failures.append("fallback must be an object")
    if not filled(fallback.get("recommendation")):
        failures.append("fallback.recommendation is required")

    audit = plan.get("repository_audit")
    if not isinstance(audit, dict):
        audit = {}
        failures.append("repository_audit must be an object")
    env = plan.get("target_environment")
    if not isinstance(env, dict):
        env = {}
        failures.append("target_environment must be an object")
    risks = plan.get("risks")
    if not isinstance(risks, dict):
        risks = {}
        failures.append("risks must be an object")
    delivery = plan.get("delivery")
    if not isinstance(delivery, dict):
        delivery = {}
        failures.append("delivery must be an object")
    if not filled(delivery.get("mvp")) or not filled_list(delivery.get("phases")):
        failures.append("delivery.mvp and delivery.phases must be populated")

    if level in ("reviewed", "delivered"):
        if status not in ("reviewed", "delivered"):
            failures.append("status must be reviewed or delivered")
        if not filled(stack.get("selected")) or not filled(stack.get("rationale"), 20):
            failures.append("stack.selected and stack.rationale (at least 20 characters) are required")
        for name in LAYERS:
            layer = boundaries.get(name)
            if not isinstance(layer, dict) or not filled(layer.get("selected")):
                failures.append("boundaries." + name + ".selected is required")
        if not filled(fallback.get("selected")):
            failures.append("fallback.selected is required")
        if audit.get("completed") is not True or not filled_list(audit.get("evidence")):
            failures.append("repository_audit requires completed=true and evidence")
        if not filled_list(env.get("browsers")) or not filled_list(env.get("devices")):
            failures.append("target_environment requires browsers and devices")
        if not filled_list(risks.get("mitigations")):
            failures.append("risks.mitigations is required")
        if not filled_list(delivery.get("planned_tests")):
            failures.append("delivery.planned_tests is required")

    if level == "delivered":
        if status != "delivered":
            failures.append("status must be delivered")
        tests = delivery.get("test_evidence")
        if not isinstance(tests, list) or not tests:
            failures.append("delivery.test_evidence needs real test records")
        else:
            for i, record in enumerate(tests):
                if not isinstance(record, dict) or not filled(record.get("check")) or not filled(record.get("evidence")) or record.get("result") not in ("passed", "failed", "skipped"):
                    failures.append("test_evidence[%d] requires check/result/evidence" % i)
        if isinstance(tests, list) and tests:
            outcomes = [record.get("result") for record in tests if isinstance(record, dict)]
            if "passed" not in outcomes:
                failures.append("delivery requires at least one passing test with evidence")
            if "failed" in outcomes:
                failures.append("delivery contains failing tests; do not mark as delivered")
        metrics = delivery.get("measurements")
        if not isinstance(metrics, list) or not metrics:
            failures.append("delivery.measurements needs real device measurements")
        else:
            for i, metric in enumerate(metrics):
                if not isinstance(metric, dict) or not all(filled(metric.get(k)) for k in ("name", "value", "environment", "evidence")):
                    failures.append("measurements[%d] requires name/value/environment/evidence" % i)
        provenance = plan.get("provenance")
        if not isinstance(provenance, dict) or provenance.get("implementation_verified") is not True:
            failures.append("provenance.implementation_verified must be explicitly confirmed")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Archvela architecture plan")
    parser.add_argument("path", type=Path, help="archvela-plan.json")
    parser.add_argument("--level", choices=STATES, default="draft")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        problems = validate(json.loads(args.path.read_text(encoding="utf-8")), args.level)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        problems = ["cannot validate plan: %s" % exc]
    payload = {"ok": not problems, "level": args.level, "issues": problems}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("%s archvela-plan %s: %d issue(s)" % ("PASS" if not problems else "FAIL", args.level, len(problems)))
        for problem in problems:
            print("  - " + problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
