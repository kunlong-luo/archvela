# Archvela v0.1.0-alpha.1 — Release candidate sign-off checklist

> **Do not create a Git tag / GitHub Release / package / deployment until all hard gates are verified and the owner explicitly authorizes publication.** This is a **draft checklist**, not a signing record. See [English notes](./releases/v0.1.0-alpha.1.md) and [中文说明](./releases/v0.1.0-alpha.1.zh.md).

## Candidate scope (frozen for review)

- Candidate tag **proposed only**: `v0.1.0-alpha.1`.
- Skill metadata **candidate**: `0.1.0-alpha.1`; not published merely because this file exists.
- Published GitHub Releases observed at start of preparation: **0 (2026-10-30)**. Recheck before tagging.
- 62 architecture references, six domains, only 3 runnable generated starters and 20 agent **installer** targets.
- Current CI green means tested source/scripts, not independent legal rights or any AI model performance.

## Hard gates — all required before a public Alpha

| Gate | Current evidence and work remaining | Verified by / link |
|---|---|---|
| Repository owner authorization | **PENDING** — explicitly approve exact tag, release commit, release text and public scope after the remaining checks. Do not infer from prior approval to *prepare* an Alpha. | Owner, date and link: pending |
| Source and third-party rights | **PENDING** — review V3 texts, snippets, inline SVG/CSS/3D, trademarks, npm dependency redistribution and license obligations. Complete [rights register](./RIGHTS-REVIEW-REGISTER.md); MIT only covers owned content. | [Issue #5](https://github.com/kunlong-luo/archvela/issues/5) |
| `main` GitHub protection | **PENDING** — API reported `protected=false`, rulesets `[]` on 2026-10-30. Require PR-based checks, block force-push/delete, verify rule by API & owner UI. | [Issue #27](https://github.com/kunlong-luo/archvela/issues/27) |
| Real L2/L3 smoke | **PENDING** — run at least one authenticated Codex native Skill discovery and a real scenario-to-ADR task; record sanitized client/model/time, source SHA, actual references read and output. Do not fabricate. | [Issues #31](https://github.com/kunlong-luo/archvela/issues/31) and [#21](https://github.com/kunlong-luo/archvela/issues/21) |
| Release candidate commit | **PENDING** — freeze an exact 40-char SHA **after** final PR merge, not prior `main`; ensure clean source checkout and version consistency. | SHA: pending |
| CI verification | **PENDING** for candidate SHA — verify all 7 workflow groups passed **on exact candidate commit**: Skill Python tests, installer L1, npm lock, example build, generated build, CodeQL/npm/PR dependency review, Chromium E2E. | GitHub Actions run URLs: pending |
| Docs and truthful promises | **DRAFTED** — verify English/Chinese notes, README, Skill frontmatter, `CHANGELOG.md`, installed paths, known 62/3/20 limitations, and no claimed L2/L3 win. | Owner review: pending |
| Secret/privacy and security | **PENDING** — check security alerts/secret scanning, source files, no credentials/private study logs in published assets, release artifact manifest and dependency license obligations. | Owner settings and review: pending |

## Important distinction: Alpha versus stable

- A **public Alpha** may disclose limited coverage, unoptimized graphics, partial translations and **missing statistically significant comparative benchmarks**. Do **not** claim improved coding results without a real study.
- It still requires **clear rights to redistribute content, a truthful release description, security governance, exact release provenance and owner authorization**.
- The study protocol itself proposes 12 real pilot sessions and 72 full trial sessions; **none are claimed complete**. For a narrowly described Alpha, do not present those research-scale trials as measured product outcomes. At minimum, actual L2/L3 smoke is expected by this project release policy.

## Reproducible manual verification, not automatic publication

From an independently reviewed, clean clone at the **final candidate SHA**:

```bash
git rev-parse HEAD
git status --porcelain
python3 -m unittest discover -s tests -v
python3 scripts/check_asset_provenance.py
python3 scripts/check_release_candidate.py
```

Run `npm ci`, package builds, generated smoke and Playwright as documented in existing CI; compare GitHub workflow results for the **same commit**. Verify `SKILL.md` metadata and both release-note files refer to exactly the proposed tag.

**Only after each gate is true and separately documented**, the repository owner may approve creating a **GitHub pre-release** with tag `v0.1.0-alpha.1`, pointing to the reviewed SHA, with notes copied from the reviewed draft. A future stable `v1.0.0` is a different decision.

## Final sign-off record — intentionally blank

- Exact reviewed commit SHA: **PENDING**
- Owner / date / approval artifact: **PENDING**
- Rights review owner / evidence link: **PENDING**
- Native Codex L2/L3 sanitized evidence: **PENDING**
- CI checks / URLs on exact release commit: **PENDING**
- GitHub `main` protection verification: **PENDING**
- Result: **NOT APPROVED FOR PUBLICATION**

The checklist does not perform an authorized release itself.
