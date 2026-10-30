# Real-agent pilot — operator procedure (L2/L3 evidence)

> **Status: NO MODEL SESSIONS EXECUTED BY THIS REPOSITORY.** This page is
> an operator playbook, not an experiment report. It contains no scores.
>
> [Benchmark tooling](../benchmarks/README.md) ·
> [Human evaluation protocol](./AGENT-EVAL-PROTOCOL.md) ·
> [Release readiness](./RELEASE-READINESS.md)

## Goal and fixed scope

First verify that a real client can discover the Archvela Skill (L2) and that
operators can collect inspectable, anonymous outputs, rather than assuming
file installation is model usage (L1).

The *pilot* consists of 2 tasks × 2 arms × 3 clients = **12 actual sessions**.
The planned full study consists of 12 tasks × 2 arms × 3 clients = **72 sessions**.
Pilot results are not a statistical claim that Archvela improves performance.

## V0.5 pilot preflight integrity (before any live client session)

Prepare from a **clean, detached Git checkout of the exact experiment SHA**.
`pilot.py` rejects a mismatched HEAD or locally modified Skill/benchmark
source files. Fresh V2 operator-manifest IDs use secure randomness; the
private `operator/manifest.key` holds an integrity signing key and must
be protected alongside the arm mapping. It is not a client credential,
not a model credential, and must never be given to reviewers.

Use `npx --yes skills@1.7.4` only in authorized **Treatment** workspaces,
and record actual installer/client versions and pinned source commit.
The baseline must not inherit any global Archvela Skill. The scripts
cannot inspect login states or independently certify native discovery.

Before collecting human scores, manually redact and export responses.
The exported blank-review sheet includes each response's SHA-256; a
reviewer must grade the exact file. If you edit or re-redact a response
after grading, the operator summary rejects the changed fingerprint.

Report `intention_to_treat_human_delta` as a *descriptive randomized
assignment comparison* only when complete; it includes all assigned
conditions and **does not prove the Skill was used**. The separate
`full_study_human_delta` is suppressed unless all Treatment runs
actually discovered the Skill. Neither implies causality, and failures
or missing human reviews never disappear from denominators.

## Before beginning any run

1. Use genuine, authorized, logged-in **Codex**, **Claude Code** and
   **OpenCode** clients. Model costs, paid credits and account permissions
   remain controlled by the operator. The repository never calls models.
2. Pin the exact Archvela commit and `benchmarks/cases.json` digest; record
   exact client/model versions. Do not silently change versions mid-run.
3. Use fresh client sessions and **independent workspaces outside the Archvela
   checkout**. Audit inherited global/project Skills, cached instructions and
   local client configuration before a baseline run.
4. Keep input prompts, tool permissions, maximum effort/tokens, time windows
   and any sample repository contents identical within each task pair.
5. Review sensitivity and share only anonymized logs. Never commit API tokens,
   internal customer code, proprietary documents or private metadata.

## Prepare cards (does not launch a model)

From a trusted clone of Archvela, run:

```bash
ARCHVELA_SHA="$(git rev-parse main)"
python3 benchmarks/pilot.py \
  --agent codex --model REPLACE-WITH-ACTUAL-MODEL-ID \
  --skill-sha "$ARCHVELA_SHA" --output /tmp/archvela-codex-pilot

# Repeat for --agent claude-code and --agent opencode, using distinct
# output paths and the actual model ID offered by each client.
```

The generator produces `operator-manifest.json` containing blinded IDs,
study-arm assignment and **0 executed runs**. For each blind ID it generates:
`operator/<id>/RUN.md`, `PROMPT.txt`, `session.template.json` and an empty
`workspace/<id>`. Do not send operator metadata to reviewers.

## V0.4: preflight and failure-aware reporting

Before any real model call, check the unmodified, isolated operator workspaces:

\`\`\`bash
python3 benchmarks/preflight.py --study /tmp/archvela-codex-pilot
\`\`\`

The check detects local parent-directory Archvela Skills and changed prompts,
but **does not check global/user Skills, installed client versions, accounts,
or model permissions**. Those remain manual checks. Do not run preflight
after installing the Treatment Skill: nonempty workspaces are then expected.

Do **not** discard failed model calls or cases in which Treatment fails to
discover Archvela. Record the observed \`execution_status\` as \`completed\`,
\`failed\` or \`blocked\`. On a failure/blocked attempt, include a
\`failure_category\` (\`skill_discovery_failure\`, \`installation_error\`,
\`client_error\`, \`model_error\`, \`budget_exceeded\`, \`safety_refusal\`,
\`environment_error\` or \`other\`) and a truthful \`failure_detail\`.
\`skill_discovered\` is an observed boolean, or \`null\` when no check was
possible. Preserve real sanitized error artifacts.

The audit keeps treatment discovery failures as **negative observations**,
and reports baseline Skill discovery as **protocol contamination** while
retaining its evidence. Evidence completeness and client success are
separate outcomes. Never change a failure into \`completed\` just to obtain
a passing audit.

## Execute only after explicit model-access authorization

For each `RUN.md`, manually confirm the native client uses that **isolated**
workspace. Baseline must have *no* Archvela discoverability; treatment installs
the **pinned** Skill. Do not treat CLI installation as native discovery:
observe Skill selection, reference retrieval or explicit invocation in the
actual client run.

Submit the exact `PROMPT.txt` without rewriting or supplementing with
arm-specific instructions. Save the full sanitized client reply and the real
tool/session log under:

```text
reviewer/artifacts/<blind-id>.response.md
reviewer/artifacts/<blind-id>.run.log
```

Copy `operator/<blind-id>/session.template.json` to `session.json` and
fill it with **actual facts only**:

- `client_version`: installed client version, not a fixture name.
- `started_at_utc`, `finished_at_utc`: ISO 8601 UTC timestamps.
- `execution_status`: `completed` only if genuinely completed.
- `skill_discovered`: `false` for baseline, `true` for treatment only
  when observed, with corroborating sanitized log evidence.
- Preserve `blind_id`, `agent`, `model`, and pinned `skill_commit`.

If the client fails to discover the Skill or tools error out, **record the
failure**. Do not mislabel an incomplete or unsuccessful run as completed merely
to satisfy the evidence validator. Fix and rerun under a new trial if needed.

## Inspect evidence without assigning scores

```bash
python3 benchmarks/audit_pilot.py --study /tmp/archvela-codex-pilot
```

This checks known IDs, unchanged prompts and dataset hash, isolation from
symlinked paths, bounded nonempty evidence, actual metadata fields and their
consistency, timestamps, and SHA-256 fingerprints. Missing files produce a
nonzero exit code. This **cannot prove** the log was generated by a real
model, validate the completeness of a transcript, or determine correctness.
Operator testimony and independently reproducible builds/tests are still
needed.

Only the blinded, redacted response and log files may be shown to reviewers.
Never hand over the operator manifest or metadata that reveals
baseline/treatment conditions. Pilot evidence does **not** feed
`evaluate.py score`, which requires the complete 24-run single-client
study and independently entered human grades.

## V0.4.1: close the loop with human review and a failure-aware summary

The observer must preserve failed and blocked attempts (including
Treatment's inability to discover the Skill). First obtain a complete
audit for each client. Then, and only after **manual privacy and
arm-leakage inspection**, export the blank reviewer packet using
`benchmarks/export_blind_review.py --redaction-confirmed`.

A **separate reviewer** reads the files in `submissions/<blind-id>`
and enters a reviewer identifier and five rubric scores in a copy of
`blank-review.json`. Incomplete scores, non-integer values, duplicate
IDs and attempts graded despite failure will be rejected. A reviewer
must never receive the operator-only manifest, run metadata or raw logs.

After review, the operator runs `benchmarks/summarize_pilot.py`
with one `--study` and one `--review` pair per client. See the
[exact three-client CLI command](../benchmarks/README.md).
The summary accounts for **all 12 planned sessions** when the full
two-task, three-client pilot is supplied, even if some sessions failed.
It never outputs a study-level human score if any task pair is missing,
failed, blocked or ungraded. It calculates within-client scores only,
and deliberately does not pool across different models.

Because all inputs are self-reported, a complete packet is **not proof**
that an Agent executed, that evidence is free of private data, or that
Archvela had a causal benefit. Publish only independently inspected,
sanitized, consented results and clearly include negative outcomes.

## Stop conditions and publication rules

Stop when a model/client version changes, a global Skill contaminates baseline,
a pinned install fails, a repository or secret may be disclosed, or conditions
cannot be reproduced. Publish negative findings alongside successful runs.
Record missing token/cost metrics as `N/A`, not invented zeros. A passing
evidence audit **never** authorizes release, external deployment, paid trials
or marketing claims.

For a comprehensive pilot, also preserve reproducible build and browser
acceptance logs where the requested task actually produces code.
