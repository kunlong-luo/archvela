#!/usr/bin/env python3
"""Export manually redacted RESPONSE-ONLY pilot materials for blind review.

Never exports study arms, operator metadata or tool logs. Human redaction is
explicitly required; copying does not prove successful anonymization.
No AI clients, paid requests, scoring or network access are involved.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from audit_pilot import audit, safe_file, validate_manifest


def export(study_dir: Path, output: Path, *, redaction_confirmed: bool) -> dict:
    if not redaction_confirmed:
        raise ValueError("Operator must manually confirm redaction before exporting")
    result = audit(study_dir)
    if not result["all_evidence_present"]:
        raise ValueError("Complete response/log/metadata evidence is required")
    if not result["protocol_valid"]:
        raise ValueError("Baseline contamination prevents a clean paired comparison")
    study = study_dir.expanduser().resolve(strict=True)
    if study.is_symlink():
        raise ValueError("Study root must not be symlinked")
    destination = output.expanduser().resolve()
    if output.exists() or output.is_symlink():
        raise ValueError("Output already exists; refusing to overwrite")
    if destination.is_relative_to(study) or study.is_relative_to(destination):
        raise ValueError("Review output cannot be nested in or contain the study directory")
    if destination.is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("Review output must not be placed inside the source repository")
    manifest = json.loads(safe_file(study, Path("operator-manifest.json")).read_text(encoding="utf-8"))
    runs = validate_manifest(manifest, study)
    # Source is a pre-redacted reviewer area. Revalidate each file and prompt.
    sources = {}
    for run in runs:
        blind = run["blind_id"]
        sources[blind] = (
            safe_file(study, Path("reviewer/artifacts") / (blind + ".response.md")),
            safe_file(study, Path("operator") / blind / "PROMPT.txt"),
        )
    destination.mkdir(parents=True, exist_ok=False)
    try:
        (destination / "submissions").mkdir()
        for blind, (response, prompt) in sorted(sources.items()):
            target = destination / "submissions" / blind
            target.mkdir()
            shutil.copyfile(response, target / "RESPONSE.md")
            shutil.copyfile(prompt, target / "PROMPT.txt")
        (destination / "README.md").write_text(
            "# Blind review packet (operator-prepared; not independently anonymous)\n\n"
            "This packet contains only prompts and **manually redacted responses**, "
            "indexed by opaque blind IDs. No treatment/baseline mapping, operator "
            "manifest, session metadata, grades or tool logs were exported.\n\n"
            "A human must inspect every response again: answer text may itself "
            "mention Archvela, installation, client, or private data and unblind "
            "the study. Do not assume filenames alone guarantee blindness.\n\n"
            "Score the five human dimensions (0–4) separately: scenario fit, "
            "architecture reasoning, four-layer split, fallback/safety, "
            "verification plan. Missing real responses or failures must be "
            "reported; do not invent success, grades or execution evidence.\n",
            encoding="utf-8",
        )
        (destination / "blank-review.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "kind": "blind_response_only_ungraded",
                    "records": [
                        {
                            "blind_id": blind,
                            "grades": {
                                "scenario_fit": None, "architecture_reasoning": None,
                                "four_layer_split": None, "fallback_safety": None,
                                "verification_plan": None,
                            },
                            "reviewer": None,
                            "notes": None,
                        }
                        for blind in sorted(sources)
                    ],
                },
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    except OSError:
        shutil.rmtree(destination)
        raise
    return {
        "packet_created": True,
        "blinded_responses": len(sources),
        "scores_generated": 0,
        "model_calls": 0,
        "caveat": "No automatic redaction, blinding guarantee or review was performed.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Copy manually redacted pilot responses into a blind-review-only folder")
    p.add_argument("--study", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--redaction-confirmed", action="store_true",
                   help="Operator attests to manual privacy and arm-leak review; no automated redaction")
    args = p.parse_args()
    try:
        print(json.dumps(export(args.study, args.output,
                                redaction_confirmed=args.redaction_confirmed), indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
