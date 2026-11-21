# pnpm installed-file evidence: nine distinct package versions, fifteen observations

> **Status: original CI archives downloaded and hashed; source/tarball/deployment rights remain NOT APPROVED.**
> Evidence inspected on 2026-11-21. This is an engineering observation ledger, **not** a third-party license opinion, compliance pass, permission to redistribute, or authority to tag an Alpha release.

## Provenance and reproducibility

Two complete four-artifact [Security scanning](../.github/workflows/security.yml) workflow runs were independently downloaded and inspected:

- [PR #43 Security run 42446627590](https://github.com/kunlong-luo/archvela/actions/runs/42446627590), source SHA `33d270cbc07df37c7359694f4269dbb38b13461b`, 2026-11-08.
- [main Security run 43869383890](https://github.com/kunlong-luo/archvela/actions/runs/43869383890), source SHA `31a04f4bf010beca66dad4042f1bd2c19a3ba82a`, 2026-11-16.

All eight original artifact ZIPs were downloaded. Their SHA-256 hashes matched the GitHub artifact digests; each contained a single named JSON report. The decompressed JSON SHA-256 is recorded separately in [the machine-readable ledger](./PNPM-LICENSE-EVIDENCE-2026-11.json), together with all eight artifact IDs. For each of the four projects, the decompressed JSON was **byte-identical across both runs**, although the outer GitHub ZIP digests differed. All reported `lockfile_git_blob_sha` values exactly matched the four real committed `pnpm-lock.yaml` Git blobs.

**Artifact lifecycle:** GitHub's retained evidence ZIPs expire. Their digest metadata is an auditable record of files actually read, but a digest is **not** a substitute for retaining and inspecting the original ZIP/JSON bytes or a newly captured installation.

## Exact observed gaps

| Project | pnpm virtual-store package roots | Root-file gap observations |
| --- | ---: | ---: |
| `examples/cinematic-site` | 40 | 6 |
| `examples/saas-workspace` | 32 | 6 |
| `examples/home-digital-twin` | 47 | 3 |
| `tests/browser` | 7 | 0 |
| **Total** | **126** | **15** |

Nine distinct exact package versions account for the 15 occurrences. The two Next.js projects each have the same six; the Vite/R3F project has three:

| Exact package/version | CI projects | Root observations | Relationship to archived npm-era six |
| --- | --- | ---: | --- |
| `@img/sharp-libvips-linux-x64@1.3.4` | Cinematic, SaaS | 2 | Previously recorded; LGPL-family bundled native libraries require special scrutiny |
| `@img/sharp-libvips-linuxmusl-x64@1.3.4` | Cinematic, SaaS | 2 | **New musl-named variant** |
| `@next/env@16.4.3` | Cinematic, SaaS | 2 | Previously recorded; upstream MIT source lead |
| `@next/swc-linux-x64-gnu@16.4.3` | Cinematic, SaaS | 2 | Previously recorded; upstream MIT source lead |
| `@next/swc-linux-x64-musl@16.4.3` | Cinematic, SaaS | 2 | **New musl-named variant** |
| `client-only@0.0.1` | Cinematic, SaaS | 2 | Previously recorded; authoritative copyright line not verified |
| `@react-three/fiber@9.8.2` | Home Digital Twin | 1 | Previously recorded; upstream tag/manifest mismatch remains open |
| `@rolldown/binding-linux-x64-gnu@1.2.15` | Home Digital Twin | 1 | Previously recorded; upstream MIT/third-party source lead |
| `@rolldown/binding-linux-x64-musl@1.2.15` | Home Digital Twin | 1 | **New musl-named variant** |

These names describe directories materialized under `node_modules/.pnpm/` by the audited CI installs. They do **not** establish which binaries are actually linked into the application dependency graph, run on a glibc or musl host, or are copied into a distributed server/container/web build. In particular, the three new variants must **not** be asserted to be active or shipped merely because a virtual-store directory exists. The evidence collector does not establish uninstalled optional-platform counts. Compare the [six-package tagged upstream source triage](./UPSTREAM-LICENSE-SOURCE-TRIAGE.md) for **source leads only**, not verified published npm tarballs.

## Historic comparison: different measurement units

The earlier [npm-era report](./INSTALLED-LICENSE-EXCEPTIONS.json), using four npm v3 locks and a separate installation layout, recorded 283 lock package rows, 118 Linux installed rows, 165 uninstalled optional-platform rows and 10 gaps from 6 exact versions. Those immutable archived `package-lock.json` files remain under `docs/historical/npm-lockfiles/`. Comparing `10` and `15` as an increase in legal risk would be unsupported: pnpm's virtual-store layout/optional materialization differs, and package-root file presence is only a narrow proxy.

## Offline guard and remaining work

```bash
python3 scripts/verify_pnpm_license_ledger.py
python3 -m unittest discover -s tests -p 'test_pnpm_license_ledger.py' -v
```

The verifier checks lockfile Git blob identities, original workflow source SHAs, eight original archive and JSON digests, the complete 15-observation / nine-version list, and preserves `rights_cleared=false`. It runs alongside existing older npm-era evidence validations in the Skill CI. **It does not re-download artifacts, parse native binaries or verify rights.** If the active pnpm lockfile changes, the evidence check intentionally fails closed until its new source graph and evidence are reviewed; the original observation ledger must not be rewritten to falsely represent a new dependency graph.

Still required:

1. Independently retrieve and inspect the **nine exact registry tarballs**, including any nested LICENSE/NOTICE, binary components and the six-package source-lead provenance caveats; record registry-integrity hashes and tarball contents.
2. Determine the actual **linked dependency graph** and eligible native package variants for each intended Linux libc/CPU environment; capture absent optional targets separately. Then inspect Next.js server/container and Vite client `dist/` outputs for actual shipped code/binaries.
3. Validate applicable LGPL, MPL, MIT and other third-party conditions and complete the separate 42 flagged metadata cases.
4. Obtain written **authorized human** source/NOTICE/redistribution sign-off for the final release SHA and for the V3 scenario texts, images, renderings and examples.

**Release: HOLD.** Continue [Issue #46](https://github.com/kunlong-luo/archvela/issues/46) and the [Rights Review Register](./RIGHTS-REVIEW-REGISTER.md); green CI never clears copyright or binary redistribution obligations.
