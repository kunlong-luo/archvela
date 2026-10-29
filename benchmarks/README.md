# Archvela Agent Effectiveness Benchmark (planned, not yet run)

This repo contains a **reproducible study scaffold**, not evidence that Archvela improves AI coding results.

- **12 curated tasks**, two per domain, IDs checked against the V3 catalog.
- **Paired design**: same model, prompt, tools, time, context budget and trial number with either baseline (no Archvela Skill) or treatment (Skill available).
- **Blind scoring**: runner receives `runner-manifest.json` (which contains the arm); reviewers only receive the response files and blind IDs, plus `blank-human-grades.json`.
- Five human rubric dimensions, each **0 (unacceptable) to 4 (excellent)**: scenario fit, architecture tradeoffs, four-layer splits, fallback/safety, verification plan.
- Do not change prompts or scoring standards between arms. Run several seeds/trials to measure noise and report non-significant results honestly.
- No external API calls, credentials, paid token consumption, CLI execution of models, or simulated wins are included.
- Output score reflects **human-entered labels and artifacts only**; it does *not* run or verify code, and cannot establish agent superiority on its own.

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
