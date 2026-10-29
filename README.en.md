# Archvela — From Ideas to Architecture

Archvela is a scenario-first frontend architecture skill designed for solo builders and AI coding assistants. It includes **62 practical product scenarios in six domains**, an OpenCode-compatible `SKILL.md`, three architecture document templates, and read-only-by-default Python helper tools.

**Domains:** commercial websites and SaaS · productivity apps · 3D/GIS digital twins · education · web games and immersive experiences · geospatial/data storytelling.

## One-command install for Codex, Claude Code, OpenCode and more

Run inside your target project (requires Node.js 22.20+ and GitHub access). You **do not** need to clone Archvela or create symlinks by hand:

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect
```

Select your coding agent interactively, or specify several targets with explicit copy installation:

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect \
  --agent codex --agent claude-code --agent opencode --copy --yes

# Install for the current user rather than only this project:
npx skills add kunlong-luo/archvela --skill archvela-architect \
  --agent codex --agent claude-code --agent opencode --global --copy --yes
```

Use `--agent cursor`, `--agent gemini-cli`, `--agent github-copilot` etc. for other supported clients. Manage installed skills with `npx skills list`, `npx skills check`, `npx skills update archvela-architect`, or `npx skills remove archvela-architect`.

**Evidence level:** Archvela CI covers Skills CLI **local-source** installs to 20 agent targets (L1). CI additionally runs a public GitHub-source installation for Codex, Claude Code and OpenCode, and checks pinned Git-commit installation (L1). See the [official CLI usage](https://github.com/vercel-labs/skills/blob/main/docs/commands.md). Neither form proves the agent model discovered or used the Skill in a real session.

## Quick start

```bash
SKILL=".agents/skills/archvela-architect"
python3 "$SKILL/scripts/scenes.py" --list-domains
python3 "$SKILL/scripts/scenes.py" --query "digital twin"
python3 "$SKILL/scripts/scenes.py" --query "home digital twin" --json
python3 "$SKILL/scripts/scenes.py" --domain 03 --limit 5
python3 "$SKILL/scripts/scenes.py" --id V3-26 --json
python3 "$SKILL/scripts/new_project_docs.py" --scene V3-26 --project home-twin --output ./demo
```

The project-docs generator is a **dry run by default**. Add `--write` only when the target is reviewed; it refuses to overwrite existing files. The three generated documents contain scene-specific decisions and six-domain architecture profiles; newly created files are rolled back if writing fails.

## Mainstream Agent compatibility

The CI validates **local Skills CLI installation into 20 agent targets** and global installation for six key agents. This is an *installer-level* smoke test (L1), not proof of actual model/agent execution (L2–L3). See [compatibility and installation matrix](./docs/COMPATIBILITY.md) and [live-agent acceptance prompts](./docs/L3-TEST-PROMPTS.md).

## Structured cross-agent planning contract

Add `--plan-json` to `new_project_docs.py` for an optional machine-readable `archvela-plan.json` alongside the original three Markdown artifacts. `scripts/plan_contract.py` validates the draft, reviewed or delivered evidence **structure**. These checks cannot prove the real test outcomes, performance, or AI correctness.

## Runnable project generator

`python3 scripts/archvela_create.py list` shows the **three** available runnable starters. `create --scene V3-26 --project my-new-app --output ./workspace` is a dry-run; add `--write` to generate an isolated, npm-lockfile-based project with draft architecture documents. Unsupported scenarios fail clearly. [Generator guide](./docs/PROJECT-GENERATOR.md).

## Release safety and model evaluations

[Release readiness gate](./docs/RELEASE-READINESS.md) · [Agent evaluation protocol](./docs/AGENT-EVAL-PROTOCOL.md) · [12-case study harness](./benchmarks/README.md).

The repository includes security-scanning workflows and a paired, reviewer-graded baseline-vs-Skill evaluation **harness**. All four foundational feature PRs (#1, #6, #7 and #8) have been merged. No real model runs or measured effectiveness claims have been produced. Release tags and deployments remain manual, owner-approved steps.

## Architecture discipline

Use one primary scenario and one end-to-end user journey. Make explicit ADR decisions; split the work at **package / feature / JavaScript chunk / media-asset pack** levels. Keep existing applications' framework choices unless a migration is justified by evidence. Defer WebGL/3D/video and heavy editors until their interactions require them. Never claim a model is survey-accurate, a benchmark has passed, or a release has shipped without evidence.

The project focuses on **frontend and browser rendering**, not database design, server deployment or AI autonomous execution.

See the [Chinese README](./README.md), [Skill definition](./.agents/skills/archvela-architect/SKILL.md), [scenario catalog](./.agents/skills/archvela-architect/references/07_V3_全场景蓝图与选型索引.md), and [contributing guide](./CONTRIBUTING.md).

The repository uses the [MIT License](./LICENSE) for original code and documentation the owner has the right to license. Third-party code, assets, datasets, trademarks and other material require independent rights review before redistribution.
