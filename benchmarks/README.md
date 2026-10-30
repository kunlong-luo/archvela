# Archvela Agent Effectiveness Benchmark (planned, not yet run)

This repo contains a **reproducible study scaffold**, not evidence that Archvela improves AI coding results.

- **12 curated tasks**, two per domain, IDs checked against the V3 catalog.
- **Paired design**: same model, prompt, tools, time, context budget and trial number with either baseline (no Archvela Skill) or treatment (Skill available).
- **Blind scoring**: runner receives `runner-manifest.json` (which contains the arm); reviewers only receive the response files and blind IDs, plus `blank-human-grades.json`.
- Five human rubric dimensions, each **0 (unacceptable) to 4 (excellent)**: scenario fit, architecture tradeoffs, four-layer splits, fallback/safety, verification plan.
- Do not change prompts or scoring standards between arms. Run several seeds/trials to measure noise and report non-significant results honestly.
- No external API calls, credentials, paid token consumption, CLI execution of models, or simulated wins are included.
- Output score reflects **human-entered labels and artifacts only**; it does *not* run or verify code, and cannot establish agent superiority on its own.

## V0.5 candidate · Blind evaluation and version pinning hardening

**New pilot studies use V2 manifests, not the old deterministic V1 IDs.**
The 16-byte random blind identifiers do not encode the study arm. Pilot
manifests have an operator-only HMAC signed with the randomly generated
`operator/manifest.key` (0600 on POSIX). This integrity key must **never**
be included in reviewer exports, committed to git, or shared publicly.
The signature detects an altered mapping but does not prove that the
operator ran any model. The seed reproduces task order only — **not** IDs.

`pilot.py` now requires a real, clean Git checkout whose `HEAD` exactly
matches `--skill-sha`. Do not prepare experimental cards from a different
checkout, a dirty dataset, a moving branch, or an arbitrary 40-digit SHA.
The Treatment instruction uses the same pinned Skills CLI used in CI:
`npx --yes skills@1.7.4 add ...` (client login and live discovery are still
manual). The session metadata records the installer version.

The reviewer-only grade template now records a **SHA-256 of the exact
redacted response**. Do not change the response after exporting; if the
response must be re-redacted, discard and re-export the review packet,
then re-review. `summarize_pilot.py` fails on a mismatch.

The report separates a descriptive assigned-condition / intention-to-treat
score from any discovery-gated display: `full_study_human_delta` is
**null** unless every Treatment session actually reported Skill discovery.
`intention_to_treat_human_delta` remains separately labeled when every
assigned pair completed and received grades, including non-discovery
observations. Neither number is a causal claim or independently verified
model result. Failed/blocked sessions remain counted and prevent complete
graded effect estimates.

**Migration:** Do not silently reuse legacy V1 pilot directories or
their old reversible blind IDs. Reprepare with the pinned new source and
preserve any actual earlier sessions as separately versioned evidence.

## V0.3 · Real-client pilot (operator-run, no invented model results)

Before scaling to the full 12-task study, smoke-test **2 tasks x 2 conditions per client**
in Codex, Claude Code, and OpenCode: **12 real agent sessions** total across three clients.
A complete first-pass study would be **12 tasks x 2 conditions x 3 clients = 72
individual runs, or 36 paired task comparisons**.

Create isolated operator cards from a *pinned 40-character Git SHA*. Run this
outside the source checkout to prevent unintended parent-directory Skill discovery:

```bash
# Run from the Archvela source repository, but output to a fresh external directory
ARCHVELA_SHA="$(git rev-parse main)"
python3 benchmarks/pilot.py --agent codex --model EXACT-MODEL-ID \
  --skill-sha "$ARCHVELA_SHA" --output /tmp/archvela-codex-pilot

# Repeat with --agent claude-code and --agent opencode, a separate
# output directory for each, and each client's actual model ID.
```

The command creates an **operator-only** assignment manifest, verbatim prompt
files, paired empty workspaces, instructions for pinned Skill installation in
treatment only, and an empty blind-review area. No model or Skills CLI is run by
`pilot.py`. Do not share `operator-manifest.json` or `RUN.md` with graders.
The study *must* use genuine authorized agent sessions with consistent budgets,
fresh contexts, no inherited global Archvela skill in baseline, and evidence
redacted for secrets. If the pinned GitHub-source install fails, stop and record
the failure rather than silently installing a moving `main`.

**The pilot intentionally has no scoring subcommand.** Its purpose is to expose
installation, discovery, isolation, and evidence-capture failures before a
full paired evaluation. After piloting, prepare a full 24-slot study with the
existing `evaluate.py prepare` command and score only after collecting 24 real
outputs/logs and independent human grades. Do not present a missing or
synthetic output as measured effectiveness.

### Evidence audit for the operator-run pilot

Each generated `operator/<blind-id>/session.template.json` is deliberately
**incomplete**. After genuinely running an agent client, the operator must
fill `operator/<blind-id>/session.json` with real client/model version,
UTC start/end times, observed native Skill discovery and `completed` status.
Redact actual tool logs and response artifacts before depositing them at:

```text
<pilot>/
  operator-manifest.json                    # PRIVATE operator arm mapping
  operator/<blind-id>/PROMPT.txt            # immutable paired prompt
  operator/<blind-id>/session.json          # PRIVATE observed client evidence
  reviewer/artifacts/<blind-id>.response.md # blinded response
  reviewer/artifacts/<blind-id>.run.log     # sanitized tool / session logs
```

Then run the **read-only** audit against the external pilot directory:

```bash
python3 benchmarks/audit_pilot.py --study /tmp/archvela-codex-pilot
```

The command exits with an error for missing evidence, changed prompts,
symlinks, invalid metadata, inconsistent discovery reports and unpinned
model versions. With a complete bundle it reports SHA-256 checksums and the
number of recorded runs. **It does not invoke any AI client, assign human
grades, measure model quality or independently verify the operator's claims.**
Do not publish `operator-manifest.json`, `RUN.md`, or `session.json`
to blind reviewers or commit private session data to the repository.

Read the [pilot procedure](../docs/REAL-AGENT-PILOT.md) and
[full human evaluation protocol](../docs/AGENT-EVAL-PROTOCOL.md).


## V0.4: failure-aware pilot and response-only blind review

A **Skill-discovery failure in the Treatment arm is a negative finding**,
not missing/invalid data. A failed or blocked client run can be recorded with
`execution_status: "failed"` or `"blocked"`, `skill_discovered: false`
(or `null` when no discovery observation was possible), and a truthful
`failure_category` / `failure_detail`. Keep the sanitized failed response
and actual error log. A completed run with no discovered Skill is reported
as a treatment discovery deviation. **Baseline discovery of Archvela is
contamination**: the audit retains evidence but marks the pairing invalid.

Before starting authorized model sessions, run an offline workspace check:

```bash
python3 benchmarks/preflight.py --study /tmp/archvela-codex-pilot
```

This verifies the manifest, clean isolated workspaces and unchanged prompts;
it cannot detect your logged-in client, global Skills or account permissions.
You must check those manually.

After the operator collects **real** evidence, use the existing auditor:

```bash
python3 benchmarks/audit_pilot.py --study /tmp/archvela-codex-pilot
```

The audit reports successful, failed and blocked attempts separately. A
failed Treatment attempt may produce a **passing evidence check** without
being a successful L2/L3 outcome; keep both observations in final reports.
It never invokes agents or scores quality.

Once **every response has been manually checked for secrets and signs that
reveal the arm**, export only prompts and redacted response texts to a
new external directory:

```bash
python3 benchmarks/export_blind_review.py \
  --study /tmp/archvela-codex-pilot \
  --output /tmp/archvela-codex-review \
  --redaction-confirmed
```

The exporter requires an operator attestation, never overwrites the output,
and **does not include** the operator manifest, arm assignments, session
metadata or tool logs. It includes a blank five-dimension review sheet.
Manual inspection is still required: generated text may reveal the Skill.
Baseline contamination prevents a clean paired export. Failed/blocked
attempts are **not dropped** to inflate results. Neither this command nor
the pilot runs an AI client.

See [real-client operator SOP](../docs/REAL-AGENT-PILOT.md).

## V0.4.1 · Evidence-gated pilot summary across three clients

The blind reviewer fills a **separate copy** of each exported
`blank-review.json` after reading and grading authentic, manually redacted
responses. Record an independent reviewer identifier, and enter all five
rubric scores (integers from 0 through 4) for a completed session. Leave
all grades null for failed or blocked attempts; do not fabricate answers
or score failures as completed model work.

After the operator receives the reviewed files, use the **private operator
workspaces** together with reviewer scores:

```bash
python3 benchmarks/summarize_pilot.py \
  --study /tmp/archvela-codex-pilot \
  --review /tmp/archvela-codex-review/blank-review.json \
  --study /tmp/archvela-claude-pilot \
  --review /tmp/archvela-claude-review/blank-review.json \
  --study /tmp/archvela-opencode-pilot \
  --review /tmp/archvela-opencode-review/blank-review.json
```

The script requires all three clients to use the same two tasks, pinned
Skill commit, task dataset, seed and trial, while allowing each client
to specify its own actual model ID. It also supports one client for
exploratory diagnosis. Without `--review`, it reports evidence and
outcome counts **without any scores**.

**Interpretation rules:**

- All 12 scheduled attempts remain in the denominators, including
  failed, blocked and Treatment Skill-not-discovered sessions.
- Human score comparisons are **per client** and only emitted when
  *all* its task pairs were completed and fully graded. Partial
  positive-only scores never produce a study-level delta.
- Baseline Skill contamination invalidates the paired comparison; the
  tool still produces an operator-only diagnostic JSON report but exits
  with a failure code.
- The script **does not pool scores across different clients/models**,
  calculate statistical significance, execute any model or prove
  the uploaded evidence was produced by a model. Human rubric scores
  are exploratory, not verified code acceptance or causal impact.
- Keep the JSON output **operator-only** until the reviewer has finished
  and privacy plus arm-leakage checks have been performed. It includes
  treatment/discovery information and is not a blinded review input.
- The CI tests use explicitly synthetic fixtures only. Never publish
  their numbers as experimental outcomes.

See [real-agent pilot protocol](../docs/REAL-AGENT-PILOT.md)
and [tracking issue #21](https://github.com/kunlong-luo/archvela/issues/21).

## Start an evaluation study

```bash
python3 benchmarks/evaluate.py validate-cases
python3 benchmarks/evaluate.py prepare --model MODEL-NAME --trial 1 --seed 20261028 --output ./study-001
```

The output folder must not exist. These are **empty study slots**, not completed evaluations. An operator must execute each task in an approved local agent session, capture response/transcript/build logs, and commission a reviewer.

After filling the 24 rows of `blank-human-grades.json`, set artifact references and reviewer per row, then score:

```bash
python3 benchmarks/evaluate.py score --manifest ./study-001/runner-manifest.json \
  --grades ./study-001/blank-human-grades.json --json
```

For an **auditable local evidence bundle**, place each trial's output and tool transcript in an approved local evidence folder, and put **relative filenames** in `response_artifact` and `run_log_artifact`. Then score with:

```bash
python3 benchmarks/evaluate.py score --manifest ./study-001/runner-manifest.json \
  --grades ./study-001/blank-human-grades.json \
  --artifacts-dir ./study-001/artifacts --json
```

This verifies **48 existing, nonempty, non-symlinked files**, forbids directory traversal/duplicate file reuse and records their SHA-256 digests. It does not read private files outside the selected evidence directory, upload any logs, or establish that a real model was called. Reports without `--artifacts-dir` explicitly say that only self-reported filenames were checked.

The scorer **refuses incomplete sheets**. Never use the synthetic test fixtures in `tests/test_agent_benchmark.py` as results. Human review should be calibrated across multiple graders and practical code build/E2E evidence; see [evaluation protocol](../docs/AGENT-EVAL-PROTOCOL.md).

Note: model trials may create data or cost money. The harness does **not** run models without user-managed credentials/authorization.
