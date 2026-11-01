# Alpha — installed dependency license evidence gaps (10 occurrences / 6 packages)

> **HUMAN REVIEW PENDING — NOT A COPYRIGHT INFRINGEMENT FINDING OR APPROVAL.**
> Observed from the actual successful [GitHub Security scanning workflow #41262733686](https://github.com/kunlong-luo/archvela/actions/runs/41262733686) on source commit `f15a5bd394a5e32f509b6d61887a2493cdcb13fa` (2026-11-01). All four genuine JSON artifacts were downloaded and inspected; the [immutable historical exception register](./INSTALLED-LICENSE-EXCEPTIONS.json) preserves artifact IDs, report SHA-256, exact original lockfile Git blob IDs and individual unmatched package rows. The workflow archives expire after its configured retention period; this written summary preserves the observations.

## Verified CI evidence at the historical commit

| npm project | Locked rows | Installed Linux rows | Optional platform rows not installed | Installed rows without recognized package-root notice | GitHub artifact ID |
|---|---:|---:|---:|---:|---:|
| cinematic-site | 88 | 37 | 51 | **4** | `13065628785` |
| saas-workspace | 80 | 29 | 51 | **4** | `13065519062` |
| home-digital-twin | 89 | 45 | 44 | **2** | `13065314851` |
| browser-tests | 26 | 7 | 19 | **0** | `13065549168` |
| **Total** | **283** | **118** | **165** | **10** | **Four JSON reports** |

These numbers count **lockfile installation rows**, not unique upstream repositories or legal obligations. On this one Linux installation, ten installed rows lacked a recognized **top-level** `LICENSE`, `LICENCE`, `COPYING`, `NOTICE`, `ATTRIBUTION` or `THIRD_PARTY` filename; package content may still carry licensing in other directories, parent packages, bundled text or authoritative upstream sources. Absence alone is not infringement.

## Precisely identified gaps

| Exact package/version and declared lockfile license | Where missing root notice was observed | Review priority and authoritative lead |
|---|---|---|
| `@img/sharp-libvips-linux-x64@1.3.4` — LGPL-3.0-or-later | V3-02 cinematic-site; V3-14 saas-workspace | **High:** precompiled native libvips with multiple bundled third-party library licenses; verify full notices, LGPL requirements and actual shipped binaries. [npm package 1.3.4](https://www.npmjs.com/package/%40img/sharp-libvips-linux-x64?activeTab=code) |
| `@next/env@16.4.3` — MIT | V3-02; V3-14 | Check Next.js 16.4.3 exact upstream licensing, package tarball and NOTICE attribution; [npm package](https://www.npmjs.com/package/%40next/env) |
| `@next/swc-linux-x64-gnu@16.4.3` — MIT | V3-02; V3-14 | Check exact Linux native compiler artifact, upstream Rust/source licensing and any included notice requirements; [npm package](https://www.npmjs.com/package/%40next/swc-linux-x64-gnu) |
| `client-only@0.0.1` — MIT | V3-02; V3-14 | Npm page lists MIT, but no package-root license found by this scanner. Verify authoritative version-specific license text and usage/distribution; [npm package](https://www.npmjs.com/package/client-only) |
| `@react-three/fiber@9.8.2` — MIT | V3-26 home-digital-twin | Check package tarball and authoritative upstream license/notice (parent repo has an [MIT LICENSE](https://github.com/pmndrs/react-three-fiber/blob/master/LICENSE)); do not infer that the npm tarball itself includes a copy |
| `@rolldown/binding-linux-x64-gnu@1.2.15` — MIT | V3-26 home-digital-twin | Native tooling binary, development/optional in the observed lockfile; check Rust and copied third-party notice sources ([Rolldown upstream](https://github.com/rolldown/rolldown/blob/main/README.md) describes MIT and third-party-derived code) |

These are **six distinct package versions appearing in ten installation locations**. No package is flagged as proven unauthorized. The first priority should be the libvips native binary, then compiler/tooling binaries, then common package notice attribution. Other packages with recognized LICENSE files still require normal notice and redistribution review.

## What this audit improves (and what it does not)

The new [offline consistency checker](../scripts/verify_license_exceptions.py) checks that all ten observations remain present, none are silently approved, the precise historical run SHA and four artifact sources are named, and all current lockfile bytes, package version, license declaration and dev/optional flags still match the evidence. CI **fails if lockfiles drift**; a new real CI installation run and refreshed human review is needed in that case. This is stronger than a free-form TODO but is **not independent re-execution of an expired artifact**.

The 42 flagged unusual SPDX expressions in the separate [all-lockfile metadata review](./DEPENDENCY-LICENSE-REVIEW.json) and the six missing-root-file packages here are **different audit dimensions**. They overlap for libvips, but one must not be substituted for the other. Review all actual redistribution terms and V3 textual/design copyright separately.

## Authorized reviewer actions

- [ ] Retrieve the four original artifact JSONs (or archived copies with matching `report_sha256`), and reproduce under the intended release platform(s). If unavailable, rerun `Security scanning` against a clean commit with the same reviewed lockfiles.
- [ ] For each six-package case: compare exact-version upstream LICENSE text, third-party notices, tarball entries and any embedded native binary licenses. Keep links and SHA evidence; avoid assuming all platform packages are identical.
- [ ] Determine what Archvela actually redistributes (GitHub source-only examples, generated app source, built static assets, production server bundle, or native artifacts) and document attribution needed for **that form**.
- [ ] Track decisions in [Rights Review Register](./RIGHTS-REVIEW-REGISTER.md): `keep with notice`, `replace`, `remove`, or `unresolved`, with reviewer, date, exact release SHA and evidence.
- [ ] Only authorized rights owners/reviewers may approve final redistribution. **No branch merge, passing script or release-note draft is such an approval.**

The Alpha is **not published**; owner branch protections ([#27](https://github.com/kunlong-luo/archvela/issues/27)) and actual Codex native discovery ([#31](https://github.com/kunlong-luo/archvela/issues/31)) remain separately blocked.
