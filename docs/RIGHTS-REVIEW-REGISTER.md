# Archvela first Alpha — third-party rights and source review register

> Intended candidate: `v0.1.0-alpha.1` — **NOT PUBLISHED**; review must be tied to the final candidate SHA before any approval.

> **Status: UNREVIEWED — NO REDISTRIBUTION APPROVAL INFERRED.** This human sign-off register supplements the [machine-checkable standalone media inventory](./ASSET-PROVENANCE.md), which reported zero separately committed media files at its earlier source-tree snapshot. Zero media files **does not** mean zero copyrighted material.

Complete this register against the **actual proposed release commit**, not merely an older snapshot. Where ownership/redistribution cannot be established, obtain permission, rewrite/remove the material, or hold the release. Do not copy private identity documents or license keys into the repository.

## Inventory and manual decisions

| Content class | Sources to examine | Evidence required | Status |
|---|---|---|---|
| 62 V3 scenario references | `references/scenarios.json`, V3 index and six Chinese volumes in `.agents/skills/archvela-architect/references/` | For original/adapted passages, origin and author; quotes, tables, diagrams and translation rights; explicit permission for substantial third-party material | **PENDING HUMAN REVIEW** |
| Templates and architecture profiles | `references/templates/T01–T03`, `references/architecture_profiles.json`, generated text | Authorship and origins of adapted document structures, code excerpts and borrowed checklists | **PENDING HUMAN REVIEW** |
| Python scripts and benchmarks | `scripts/`, Skill `scripts/`, `benchmarks/` and tests | Confirm contributor rights and source attribution for any imported snippets or fixtures; no customer transcripts | **PENDING HUMAN REVIEW** |
| 3 web/3D Starters | `examples/cinematic-site`, `examples/saas-workspace`, `examples/home-digital-twin` | Inline SVG/JSX/CSS, sample data and procedural 3D originality; no recreated third-party trademarks or product screenshots | **PENDING HUMAN REVIEW** |
| Third-party JavaScript/npm dependencies | All **four committed lockfiles**, npm licenses and packages included with generated starters | Record dependency name/version/license, link to authoritative license and any notices/redistribution conditions; a vulnerability audit is **not** a license audit | **PENDING HUMAN REVIEW** |
| Product names, icons and vendor references | README, guides, logos, client names and compatibility links | Descriptive nominative references only; avoid endorsement implication; verify permissions for any embedded graphic/logo | **PENDING HUMAN REVIEW** |
| Standalone graphics/media/fonts/PDF | Git tracked files and `docs/ASSET-PROVENANCE.json` | Exact media inventory and source rights; current manifest is empty, must be rechecked at candidate commit | **PENDING HUMAN REVIEW** |
| English translated/derived content | English Skill entrypoint and `ENGLISH-DECISION-GUIDE.md` | Check any adapted translated work and confirm rights in the original material | **PENDING HUMAN REVIEW** |

## Required reviewer record — each exception

Fill only from genuine review evidence:

```text
Relative path and line range:
Original rights holder / author:
Original source URL or repository:
Original / adapted / third-party / unknown:
License or permission (exact SPDX expression/terms):
Redistribution allowed under intended MIT distribution?:
Required NOTICE / attribution text:
Action taken: keep / attribute / rewrite / remove / unresolved
Reviewer and review date:
Evidence URL or offline record identifier:
```

**Do not mark a row approved solely because it has no standalone images, because the GitHub repository has a MIT LICENSE file, or because CodeQL and npm audit passed.** Software dependency notice obligations may differ from source-code reuse permissions.

## Review decision / approval

- Final candidate SHA: **PENDING**
- Inventory completeness and dependency license report: **PENDING**
- Unresolved third-party rights issues: **UNKNOWN**
- Reviewer/owner name, date, approval evidence: **PENDING**
- Clearance decision: **NOT APPROVED**

Track [Issue #5](https://github.com/kunlong-luo/archvela/issues/5). Only the actual rights holder or authorized reviewer can grant approval; this file is deliberately an unfilled register.
