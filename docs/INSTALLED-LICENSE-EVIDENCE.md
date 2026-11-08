# Alpha release: installed dependency LICENSE/NOTICE evidence (not legal approval)

> **Historical data, not current pnpm results:** The original 283 locked / 118 installed / 165 skipped / 10 missing-root notice observations were collected using npm on an earlier commit. Their exact npm lock bytes now live under [historical evidence](./historical/npm-lockfiles/); current CI instead installs with pinned pnpm 10.22.0 and uses the [pnpm virtual-store inventory](../scripts/collect_pnpm_license_evidence.py). Current evidence does not claim to count uninstalled optional-platform packages.


> **Status: evidence collection implemented; redistribution review remains OPEN.** Intended version `v0.1.0-alpha.1` is **not** published. This is an engineering aid to [human review](./RIGHTS-REVIEW-REGISTER.md), not a legal opinion.

## What the repository already checks

The [lockfile license metadata audit](./DEPENDENCY-LICENSE-AUDIT.md) covers four npm v3 lockfiles and 283 dependency installation rows, with 42 specially flagged license expressions. A lockfile license field can differ from what actually ships.

The [new installed-license evidence tool](../scripts/collect_installed_license_evidence.py) examines **actual packages after an isolated `npm ci`**: for each lockfile entry, it records package name/version, optional/development flags, whether installed on the CI runner, any package-root `LICENSE`/`LICENCE`/`COPYING`/`NOTICE`/`ATTRIBUTION` file names, and SHA-256 hashes and sizes (not the license text itself).

Historically, four independent jobs in [Security scanning](../.github/workflows/security.yml) run on Linux / Node.js 24. That historical run used `npm ci --ignore-scripts --include=dev --no-audit --no-fund` to install locked dependencies **without executing third-party lifecycle hooks**. Each job uploads a JSON artifact named `installed-license-evidence-<package>` with a short retention period. An artifact is evidence **for the particular job OS, tool versions and commit only**.

The script **fails** if a required locked package is absent, its installed version differs, or inspected license/NOTICE paths are unsafe. It **does not automatically fail** merely because a package lacks a top-level LICENSE file; that gap is recorded for human review rather than interpreted as conclusive infringement or permission.

## How to inspect real CI evidence

After a successful PR or main run, visit [Security scanning workflow](https://github.com/kunlong-luo/archvela/actions/workflows/security.yml), choose the **exact tested commit**, then download the four `installed-license-evidence-*` artifacts from that run. Inspect `rows`, `installed_package_rows`, `optional_platform_rows_not_installed` and `installed_rows_without_top_level_license_or_notice`. Reviewers must verify any upstream license URLs, notices, and the actual distributed product or build artifact separately.

To reproduce locally in a disposable checkout:

```bash
pnpm --dir examples/home-digital-twin install --frozen-lockfile --ignore-scripts
python3 scripts/collect_pnpm_license_evidence.py \
  --directory examples/home-digital-twin \
  --output /tmp/archvela-home-installed-license-evidence.json
```

Do not run the install on a production host or treat generated reports as proof of rights. `--ignore-scripts` may prevent some native binaries from being usable; this job only inventories installation contents, it does not replace the existing build/E2E jobs.

## Residual limits

- npm lockfiles can include platform-specific optional packages that are **not installed** on Linux. The report records them as absent rather than as inspected; Windows/macOS redistribution needs separate review.
- Licenses may live in nonstandard locations or be inherited from a parent package. A package-root filename scanner will not find every applicable notice. Hashes demonstrate file bytes in one environment but cannot certify authenticity or legal sufficiency.
- `MIT`/`Apache-2.0` declarations still require valid license texts/notices where applicable. LGPL-family, MPL and CC-BY cases require special attention; see the [42-entry review register](./DEPENDENCY-LICENSE-REVIEW.json).
- The original V3 reference text, examples, inline UI, procedural 3D geometry, trademarks and generated source remain subject to the independent [source rights checklist](./RIGHTS-REVIEW-REGISTER.md).
- **This run does not involve a real Codex/Claude Code/OpenCode client, does not grant owner sign-off and does not create a GitHub Release.**

After the final candidate commit and relevant build artifacts are frozen, the rights owner can attach a sanitized reviewer record to [Issue #5](https://github.com/kunlong-luo/archvela/issues/5). The candidate [sign-off checklist](./ALPHA-RELEASE-CHECKLIST.md) remains unchecked until then.
