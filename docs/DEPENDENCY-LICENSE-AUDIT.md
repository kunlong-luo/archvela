# Archvela Alpha — Dependency license metadata triage

> **STATUS: AUTOMATED LOCKFILE INVENTORY COMPLETE; LEGAL / REDISTRIBUTION RIGHTS REVIEW NOT COMPLETE.** Candidate: `v0.1.0-alpha.1` (not tagged/published). Source: committed npm v3 `package-lock.json` files, checked at 2026-10-30 baseline `4c8ce65e6406e5431b89714c2cc83477eb5cd64a`. For a final release review, rerun at the **actual release candidate commit**, not the earlier baseline.

## Observed source data — 4 lockfiles / 283 installation entries

| Lockfile | Installed-package rows | Notable declared licenses requiring human review |
|---|---:|---|
| `examples/cinematic-site/package-lock.json` | 88 | LGPL family / mixed expressions (14); CC-BY-4.0 (1) |
| `examples/home-digital-twin/package-lock.json` | 89 | MPL-2.0 (12) |
| `examples/saas-workspace/package-lock.json` | 80 | LGPL family / mixed expressions (14); CC-BY-4.0 (1) |
| `tests/browser/package-lock.json` | 26 | None outside the narrow review-triage list |

**All 283 installation entries contain a non-empty license metadata string in the current lockfiles.** This is a check of npm metadata and does not verify actual `LICENSE`/`NOTICE` files or the copyright authority of any publisher.

The snapshot flags **42 entries** for attention: 28 in the LGPL family (including mixed `AND` expressions), 12 MPL-2.0, and 2 CC-BY-4.0. A package can be repeated across lockfiles and a platform-specific optional package may never be installed on the target platform; neither fact is an automatic waiver of any redistribution requirements. These are 42 **installation rows**, not 42 unique products.

- **Sharp/libvips platform packages:** `@img/sharp-libvips-*` (optional; `LGPL-3.0-or-later`) plus certain `@img/sharp-*` optional binaries with conjunctive Apache/LGPL/MIT license expressions. Verify what the actual build/deployment packages and distributes; consult applicable upstream license files and notices for each platform/binary.
- **Lightning CSS:** `lightningcss` and platform-specific packages in the Vite digital-twin lockfile declare `MPL-2.0`, predominantly development or optional packages. The actual distribution and any modifications should be reviewed against the upstream license.
- **caniuse-lite:** the cinematic site and SaaS workspace include `caniuse-lite` declaring `CC-BY-4.0`. Determine whether any licensed database/content is distributed and which attribution terms actually apply.

**No listed license is categorically classified here as forbidden or approved.** In particular, `MIT`, `Apache-2.0` and other common licenses remain subject to their license text, notice and attribution requirements. This is a triage policy, **not a legal determination of compatibility**.

## Reproduce and track changes

```bash
python3 scripts/audit_dependency_licenses.py
python3 scripts/audit_dependency_licenses.py --json
python3 scripts/check_release_candidate.py
```

The first command verifies that the four lockfiles match the checked-in [machine-readable review register](./DEPENDENCY-LICENSE-REVIEW.json), using Git blob hashes to detect **any** lockfile change and keyed per-package fields to detect shifted license expressions, versions, development/optional flags or missing reviews. Every flagged item has `review_status: pending_human_review`; the register's `rights_cleared` is `false`. Git blob SHA is a source identity, **not a cryptographic legal attestation**.

When dependencies update, regenerate the register from actual new lockfile metadata, investigate newly flagged expressions, and obtain appropriate human review. Do **not** flip approval booleans just to pass CI. Genuine legal clearance requires review of actual installed code/binaries, upstream license texts, package notices, the distribution form and the owner's rights in original reference material.

## Owner's manual release tasks

- [ ] Identify what ships to users: source-only Skill/Starter repository, npm-distributed package, website deployment, bundled binaries, or all of these. License obligations may differ.
- [ ] Obtain actual upstream license texts and required notices for applicable `@img/sharp-*`, `@img/sharp-libvips-*`, `lightningcss*`, and `caniuse-lite` packages.
- [ ] Review common MIT/Apache/BSD/ISC/etc. package conditions and preserve notices where required. Lockfile metadata alone is not legal clearance.
- [ ] Audit the original Chinese V3 text, example markup, inline SVG/3D, translated references and trademarks separately, as recorded in [the human rights register](./RIGHTS-REVIEW-REGISTER.md).
- [ ] Tie findings, exceptions, any attribution files and reviewer/owner sign-off to the **final** candidate Git SHA.

Linked gate: [Issue #5](https://github.com/kunlong-luo/archvela/issues/5), [Alpha checklist](./ALPHA-RELEASE-CHECKLIST.md). No software tag or Release is created by this audit.
