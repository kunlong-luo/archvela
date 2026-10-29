# Archvela Agent Contributor Rules

## Scope
Maintain Archvela as a **portable scenario-first Agent Skill** for frontend architecture, browser rendering, UX, loading strategies and testing. No autonomous production deployment or third-party skill/script execution.

## Documentation language policy
- **English is canonical** for root `README.md` and `docs/GETTING-STARTED.md`; full Chinese translations are `README.zh.md` and `docs/GETTING-STARTED.zh.md`.
- Keep English and Chinese entrypoints in sync whenever commands, scenario scope, install coverage or warnings change. Never reintroduce `README.en.md`.
- Validate localized links via `tests/test_documentation.py` and link the corresponding language versions in both directions.

## Before edits
1. Read this file, `README.md`, `.agents/skills/archvela-architect/SKILL.md`, and relevant reference files only.
2. Inspect existing changes and tests. Do not wipe authored V3 content or collapse 62 scenarios into a shorter list.
3. Produce a small plan that states the product task, affected files, tradeoffs and verification steps.

## Core invariants
- Skill identity: `archvela-architect`; parent directory name and frontmatter `name` must match.
- Catalog: 62 unique IDs from V3-01 to V3-62, domain counts **13/11/12/8/9/9**; all catalog domain references must exist.
- Use progressive disclosure: Skill entrypoint stays compact; documentation lives in `references/`.
- No automatic migration of existing Pagevela or Voxnelo frameworks. Respect project constraints and real test evidence.
- Keep code stdlib-only by default; generator is dry-run by default, refuses existing targets and symlinked architecture folders, and rolls back new files after a partial write failure.
- Scenario-specific output must include scene ID in all three generated documents; never replace testable recommendations with blank templates.
- Package / Feature / JS Chunk / Asset Pack are four distinct decisions.
- Use original media, designs and game artwork or licensed assets; do not clone copyrighted characters or branding.
- Do not inject unpublished project facts into public docs.

## Structured plan handoff

- Keep `--plan-json` optional: default output stays three Markdown files.
- The generated `archvela-plan.json` is a draft; reviewers must fill selected technology, repository evidence, all four boundaries, real target devices, fallback and tests.
- `plan_contract.py --level reviewed` and `--level delivered` check data and evidence **presence**, not truth. Never fabricate measurements or test runs just to pass a validator.

## Multi-agent portability
- One portable `.agents/skills/archvela-architect` source, not separate divergent Skill copies per Agent.
- 20-agent installer matrix and CLI smoke tests live in `compatibility/agents.json` and `scripts/verify_agent_installs.py`.
- Be precise about testing level: L0 schema, L1 installation, L2 native discovery, L3 model-driven end-to-end.
- Don't claim real L2/L3 unless the actual target agent executed and evidence was captured.
- Cross-agent installer CI must not use any personal API keys or target a production home directory.

## Project scaffolding rules
- Keep 62 knowledge scenes distinct from the **three** currently executable project starters.
- No writes by default; `--write` only to a new npm-safe project slug under a user-selected parent.
- Ensure copied `package.json` and `package-lock.json` names match and that generated apps pass `npm ci` + build in CI.
- Only allowlisted files can be copied; never include `.env`, local credentials, production data or `node_modules`.

## Security and empirical evidence
- Do not merge or release without repository owner approval of LICENSE, bundled reference rights and changelog.
- Security CI analyzes JS/TS/Python and dependency changes; do not silently suppress new findings.
- The 12-task evaluator is **an experiment protocol**, not evidence of model benefit. All recorded grades, tokens, durations and compiled artifacts must be reproducible, never generated as placeholders for a public win.
- Human review should be blinded to baseline/treatment assignments when possible; keep artifacts and manifest provenance.

## Verification
```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .agents/skills/archvela-architect/scripts
```
When changing references, verify IDs, links and consistent names. Changes should be submitted via PR with tested / not-tested facts clearly marked.
