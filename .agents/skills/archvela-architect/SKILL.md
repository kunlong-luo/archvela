---
name: archvela-architect
description: Plan and audit scenario-first frontend architecture for websites, SaaS, AI workspaces, dashboards, digital twins, GIS, education and browser games. Match one of 62 documented scenarios, reason about existing React/Vue/Astro/Next.js/Vite stacks without forcing rewrites, and deliver an ADR, four-layer code and asset splitting, fallback, accessibility, performance budgets and verifiable implementation tasks. Safe read-only assessment first, with optional Python 3.10+ offline helpers.
license: MIT
compatibility: Agent Skills-capable coding agents; optional Python 3.10+ CLI helpers.
metadata:
  author: kunlong-luo
  version: "0.1.0"
---

# Archvela Architect — Scenario-first frontend architecture

Use this Skill when a developer requests frontend architecture, a product MVP, a rendering strategy or a **read-only architecture review**. It covers 62 scenarios in six domains; **only V3-02, V3-14 and V3-26 have runnable code starters**. Architecture references and generated drafts are not production-ready applications.

## Safety and scope

- **Audit first; do not change existing projects without authorization.** Inspect the available `AGENTS.md`, README, package files, lockfiles, routes, build setup, tests and user constraints. State what could not be inspected.
- Focus on frontend, UX, browser rendering, bundling, media and frontend validation. Define backend/API, payment, database and cloud boundaries without pretending to implement or certify them.
- Do not auto-install dependencies, execute untrusted scripts, expose sensitive data, delete files, migrate frameworks, pay for services or deploy without explicit approval. Generated documents are drafts.
- Do not treat architecture as engineering certification. Construction measurements, GIS coordinates, medical workflows, safety-critical claims and third-party assets need independent source/rights validation.

## Seven-step workflow

1. **Establish the product task.** Identify the primary user journey, new versus existing repo, required SEO, accessibility, minimum device/browser, offline behavior, data/privacy, runtime budget and success criteria.
2. **Find the closest scenario.** Select exactly one primary V3 ID and at most two supporting IDs. Use `scripts/scenes.py` when Python is available; otherwise inspect `references/ENGLISH-DECISION-GUIDE.md` and the Chinese V3 index. Load **only the relevant domain volume**, not all 62 scenarios at once.
3. **Decide the architecture based on evidence.** Compare incumbent stack, a smaller alternative and the proposed architecture. Prefer **preserving a functioning existing framework**. Evaluate React/Next.js/Vite, Vue/Nuxt, Astro, Svelte/SvelteKit and other maintained tools against actual SSR/SEO needs, interactivity, package maturity, contributor skills, accessibility, deployment and migration cost. **No framework or component library is categorically excluded.** If an existing project uses Vue 3 or Ant Design, audit compatibility before recommending any change. Verify version claims against the actual lockfile/official release documentation rather than assuming the latest.
4. **Specify four distinct boundaries.** (a) **Package** — source repositories/libraries and true reuse; (b) **Feature** — task/route and domain ownership; (c) **JS Chunk** — deferred routes, editors, charts, maps and game engines; (d) **Asset Pack** — pictures, video, audio, GLB/KTX2, terrain tiles or levels. Do not collapse these into a single “code splitting” recommendation.
5. **Design one recognizable vertical MVP.** Use original visual language and a working user journey. Load heavy graphics only when needed; respect reduced-motion preferences, keyboard/touch navigation and data consent. Do not copy copyrighted games, branding or art.
6. **Define trustworthy fallbacks.** Specify useful HTML or 2D/table/static-poster alternatives for unavailable WebGL/WebGPU, poor networks, missing permissions, empty/error states and low-memory devices. For GIS and digital twins, verify coordinates, scale, units, timestamps and provenance. For games, separate the deterministic simulation/game loop from view effects.
7. **Deliver and verify.** Output an ADR with adopted/rejected alternatives, module plan, four-layer split, MVP scope, loading and performance targets, fallback, privacy/licensing notes, acceptance tests and a staged PR plan. Distinguish **recommended, implemented, measured and unverified**. Typecheck, unit, build, end-to-end, accessibility and field-device metrics are proposed checks unless genuinely run.

## Scenario lookup (Python 3.10+, stdlib only)

Run these from the **Skill root** (`.agents/skills/archvela-architect`):

```bash
python3 scripts/scenes.py --list-domains
python3 scripts/scenes.py --query "company website"
python3 scripts/scenes.py --query "digital twin" --json
python3 scripts/scenes.py --query "tower defense"
python3 scripts/scenes.py --id V3-26 --json
```

An English query can identify a scenario ID, but many returned **scenario titles and descriptions are still Chinese**. Do not claim that all 62 references have English translations. English instructions and domain-level guidance are in `references/ENGLISH-DECISION-GUIDE.md`. Primary V3 source and the six detailed domain volumes remain in Chinese:

- `references/00_通用_单人产品工厂与前端架构规范.md` — cross-domain rules.
- `references/07_V3_全场景蓝图与选型索引.md` — full 62-scenario index.
- `references/01_网站与商业展示.md` through `references/06_地理数据与公共展示.md` — choose **one** domain volume.
- `references/scenarios.json` and `references/architecture_profiles.json` — structured scenario and domain facts.

If a required passage is in Chinese, interpret it carefully in the user's requested output language; **do not invent a translation or a catalog entry** if the source is unavailable.

## Optional offline draft generation (no model, dry run by default)

```bash
python3 scripts/new_project_docs.py --scene V3-26 --project home-twin --output ./example-project --plan-json
# Only after the user approves the destination and file creation:
python3 scripts/new_project_docs.py --scene V3-26 --project home-twin --output ./example-project --plan-json --write
python3 scripts/plan_contract.py ./example-project/docs/architecture/archvela-plan.json --level draft
```

The generator emits three editable Markdown drafts and optional `archvela-plan.json`; draft/reviewed/delivered structural checks do **not** prove that a build, test, deployment or field measurement occurred. Python is optional: an agent can perform a read-only architecture review from the Markdown references alone.

## Output contract

- **Scenario and evidence** — primary ID, up to two related IDs, observed repo facts, user task, unknowns and constraints.
- **Architecture decision record** — framework/library options, choice and rejected alternatives **with context-specific reasons**.
- **Four-layer plan** — Package / Feature / JS Chunk / Asset Pack with examples and isolation boundaries.
- **MVP and fallback** — one testable end-to-end user journey, mobile/low-resource path, safety/licensing constraints and measurable budgets.
- **Execution plan** — small PR slices, verification commands *as recommendations unless run*, and explicitly unverified claims.

中文使用提示：本 Skill 的英文入口与六领域英文速查表用于跨 Agent 发现；完整 V3 领域资料、62 个场景源文档仍以中文保存。先读已有仓库与用户约束，再按场景检索，只加载所需一卷。Vue、React、Astro 等根据实际需求、维护成本及现有技术栈客观取舍；未经授权不得安装、改写、部署或制造测试数据。
