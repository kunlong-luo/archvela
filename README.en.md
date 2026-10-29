# Archvela — From Ideas to Architecture

Archvela is a scenario-first frontend architecture skill designed for solo builders and AI coding assistants. It includes **62 practical product scenarios in six domains**, an OpenCode-compatible `SKILL.md`, three architecture document templates, and read-only-by-default Python helper tools.

**Domains:** commercial websites and SaaS · productivity apps · 3D/GIS digital twins · education · web games and immersive experiences · geospatial/data storytelling.

## Install for OpenCode

```bash
git clone https://github.com/kunlong-luo/archvela.git
cd archvela
mkdir -p ~/.config/opencode/skills
ln -s "$(pwd)/.agents/skills/archvela-architect" ~/.config/opencode/skills/archvela-architect
```

If the destination already exists, inspect before modifying. OpenCode can also discover the Skill locally while working inside this repository. Refer to [OpenCode's official documentation](https://docs.opencode.ai/docs/skills/).

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

## Release safety and model evaluations

[Release readiness gate](./docs/RELEASE-READINESS.md) · [Agent evaluation protocol](./docs/AGENT-EVAL-PROTOCOL.md) · [12-case study harness](./benchmarks/README.md).

The repository now includes security-scanning workflows and a paired, reviewer-graded baseline-vs-Skill evaluation **harness**. No real model runs or measured effectiveness claims have been produced. Release tags, merges and deployment are manual owner-approved steps.

## Architecture discipline

Use one primary scenario and one end-to-end user journey. Make explicit ADR decisions; split the work at **package / feature / JavaScript chunk / media-asset pack** levels. Keep existing applications' framework choices unless a migration is justified by evidence. Defer WebGL/3D/video and heavy editors until their interactions require them. Never claim a model is survey-accurate, a benchmark has passed, or a release has shipped without evidence.

The project focuses on **frontend and browser rendering**, not database design, server deployment or AI autonomous execution.

See the [Chinese README](./README.md), [Skill definition](./.agents/skills/archvela-architect/SKILL.md), [scenario catalog](./.agents/skills/archvela-architect/references/07_V3_全场景蓝图与选型索引.md), and [contributing guide](./CONTRIBUTING.md).

The MIT license in this PR is proposed for repository-owner review before merging.
