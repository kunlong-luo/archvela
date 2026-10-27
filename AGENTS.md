# Archvela Agent Contributor Rules

## Scope
Maintain Archvela as a **portable scenario-first Agent Skill** for frontend architecture, browser rendering, UX, loading strategies and testing. No autonomous production deployment or third-party skill/script execution.

## Before edits
1. Read this file, `README.md`, `.agents/skills/archvela-architect/SKILL.md`, and relevant reference files only.
2. Inspect existing changes and tests. Do not wipe authored V3 content or collapse 62 scenarios into a shorter list.
3. Produce a small plan that states the product task, affected files, tradeoffs and verification steps.

## Core invariants
- Skill identity: `archvela-architect`; parent directory name and frontmatter `name` must match.
- Catalog: 62 unique IDs from V3-01 to V3-62, domain counts **13/11/12/8/9/9**; all catalog domain references must exist.
- Use progressive disclosure: Skill entrypoint stays compact; documentation lives in `references/`.
- No automatic migration of existing Pagevela or Voxnelo frameworks. Respect project constraints and real test evidence.
- Keep code stdlib-only by default; generator is dry-run by default and must never overwrite user files.
- Package / Feature / JS Chunk / Asset Pack are four distinct decisions.
- Use original media, designs and game artwork or licensed assets; do not clone copyrighted characters or branding.
- Do not inject unpublished project facts into public docs.

## Multi-agent portability
- One portable `.agents/skills/archvela-architect` source, not separate divergent Skill copies per Agent.
- 20-agent installer matrix and CLI smoke tests live in `compatibility/agents.json` and `scripts/verify_agent_installs.py`.
- Be precise about testing level: L0 schema, L1 installation, L2 native discovery, L3 model-driven end-to-end.
- Don't claim real L2/L3 unless the actual target agent executed and evidence was captured.
- Cross-agent installer CI must not use any personal API keys or target a production home directory.

## Verification
```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .agents/skills/archvela-architect/scripts
```
When changing references, verify IDs, links and consistent names. Changes should be submitted via PR with tested / not-tested facts clearly marked.
