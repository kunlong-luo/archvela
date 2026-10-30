# Archvela — English architecture decision guide

> **Scope:** An English-language navigation and decision aid for Archvela's six Chinese-source V3 domain volumes. It does **not** translate all 62 scenario descriptions or replace their original source. The original catalog and references are the authority for exact task IDs and domain-specific facts. No real coding-agent effectiveness tests have been performed.

## Before selecting a stack

Ask what the project must **actually do** and what is already implemented. A working application's framework, tests, lockfile and team capabilities are evidence; a fashionable library is not.

| Constraint | What to investigate | Possible choices (not mandates) |
|---|---|---|
| Content-first, discoverable pages | SEO, caching, localization, no-JS access | Astro, Next.js, Nuxt, SvelteKit, static HTML |
| Interactive workspace | Existing stack, auth, forms, state, data volume | React/Vite, Next.js, Vue/Nuxt, SvelteKit |
| Interactive 3D / CAD | Coordinates, real dimensions, GPU capability, 2D fallback | Three.js/R3F, Babylon.js, PlayCanvas, domain-specific viewers |
| Geospatial extent | Coordinate systems, tile data, license, provenance | MapLibre, Leaflet, CesiumJS, deck.gl, server-side tiling |
| Audio/video or learning | Permission models, accessibility, loading and privacy | Browser media APIs, domain viewers, incremental workers |
| Game / immersive | Determinism, render loop, FPS, loading, original assets | Phaser, PixiJS, Babylon.js, Three.js, PlayCanvas |

Framework names above are **candidate families**. A known Vue 3 or Ant Design installation is not a reason to rewrite. Choose based on audited constraints, supported versions and the smallest safe change. For every choice, record one rejected alternative and why.

## Domain routing and risk gates

These are *original English summaries of the domain profiles*; check the linked Chinese source for details, and use the exact catalog ID before citing a scenario.

| Domain | Detailed V3 source | Main decisions | Minimum fallback and verification |
|---|---|---|---|
| 01 · Websites and commercial presentation (13 scenarios) | [01](./01_网站与商业展示.md) | SEO-first static content, forms, interactive product visualization, media deferred until needed | Accessible content/contact CTA without WebGL or heavy animation; consent and asset rights; LCP/CLS/INP measured on target devices |
| 02 · Business apps and productivity (11) | [02](./02_业务应用与生产工具.md) | Feature/task boundaries, editing/query/approval, access and persistence, heavy editor/table chunking | Empty/error/no-permission/retry states; export correctness, data recovery, E2E of a real workflow |
| 03 · Digital twins and built environments (12) | [03](./03_空间与数字孪生.md) | Site vs detailed geometry, coordinate systems, building/IoT data mapping, layer/floor and LOD boundaries | Scaled 2D plan or equipment list; unverified locations/heights clearly labeled; test frame rate, memory and source measurements |
| 04 · Education and professional visualization (8) | [04](./04_教育与专业可视化.md) | Course/tasks, audio/video/medical or engineering viewers, permissions and progressive loading | Text and 2D alternatives when permission/GPU unavailable; health/education limits, privacy and feedback correctness |
| 05 · Games and immersive experiences (9) | [05](./05_互动娱乐与沉浸体验.md) | Separate rendering, deterministic state/game loop, level chunks and licensed asset packs | Clear unsupported-device state, user-gesture audio, FPS and repeatable gameplay tests |
| 06 · Geographic data and public information (9) | [06](./06_地理数据与公共展示.md) | Map layers and queries, temporal data, data provenance, geographic tiles/PMTiles/GeoJSON and server budgets | Searchable table, legend and timestamps if maps fail; accuracy, mapping license and low-end mobile test |

Start with [cross-domain guidance](./00_通用_单人产品工厂与前端架构规范.md) and [62-scenario V3 index](./07_V3_全场景蓝图与选型索引.md), then **one** selected domain volume. The [structured catalog](./scenarios.json) maps each `V3-NN` ID to its `domain_file`; the [profiles](./architecture_profiles.json) give the 4-way split and rollout plans. Keep scenario content and original language provenance unchanged.

## How to find an ID without reading every volume

From the installed Skill root (requires optional Python 3.10+):

```bash
python3 scripts/scenes.py --query "company website" --json
python3 scripts/scenes.py --query "dashboard" --json
python3 scripts/scenes.py --query "smart farm" --json
python3 scripts/scenes.py --query "home digital twin" --json
python3 scripts/scenes.py --query "english pronunciation" --json
python3 scripts/scenes.py --query "tower defense" --json
python3 scripts/scenes.py --query "geospatial" --json
python3 scripts/scenes.py --id V3-26 --json
```

If Python is absent, read the 62-scenario index and locate the relevant `V3-NN` section manually. Some queries return **Chinese titles and descriptions** even when the search words are English; carefully interpret the actual reference and answer in the user's requested language.

Three verified **code starters** exist: `V3-02` cinematic website, `V3-14` SaaS workspace, `V3-26` concept digital twin. The other **59** are architectural references, not installed project templates.

## Keep four boundaries separate

| Boundary | Example for a dashboard | Why it matters |
|---|---|---|
| Package | App repository and shared types with real consumers | Ownership, independent changes, avoid premature monorepos |
| Feature | Device alarms, search, incident resolution | User-task cohesion and test scope |
| JS Chunk | Lazy-load incident charts, large editor or maps | Initial bundle size and async failure handling |
| Asset Pack | Screenshots, report templates, charts or GLB assets | Bandwidth, license, cache eviction, memory |

For a static marketing site, the four boundaries look different: one app package, feature sections, optional contact/3D chunks, and responsive posters/videos/model assets. Avoid abstract reuse that has no real consumers.

## Required review record

1. User journey and source evidence (what was inspected vs not available).
2. Selected primary ID; at most two related IDs; data and domain source links.
3. Architecture Decision Record with at least two credible alternatives and rationale.
4. Separate Package, Feature, JS Chunk, Asset Pack boundaries.
5. A vertical MVP, smallest acceptance test, errors/privacy/permissions and fallback.
6. Target-device performance measurements **to be collected**, without invented values.
7. Implementation slices and permission gate before writes/installs.

Use `scripts/new_project_docs.py` only as a dry-run generator unless the user has explicitly authorized writing. Output files and `archvela-plan.json` are drafts; passing structural validation is **not evidence of successful implementation**.

## Source and maintenance boundaries

The Chinese V3 reference collection is a historical baseline, **not current official framework documentation**. For implementation, verify package versions, browser support, dependencies, third-party licenses and API compatibility using actual lockfiles and upstream project documentation. Explicitly label uncertainty and mark any unverified source date. English discovery/decision guidance is available now; a complete human-reviewed bilingual translation of all 62 scenarios remains outstanding.
