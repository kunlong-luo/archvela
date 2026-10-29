# Archvela v0.1 · Release readiness gate

**Not approved for publication by default.** PR #1 and PR #6 were merged into `main` on 2026-10-29. PR #7 (security/evaluation) and PR #8 (project generator) remain pending; no release tag, deployment or package publication has been authorized. The owner has approved MIT licensing of their original materials, but third-party rights and release-specific gates remain open.

## Required before v0.1 release

- [x] Repository owner approved MIT licensing for original Archvela code and documentation within their publishing rights (recorded in PR #1, 2026-10-28).
- [ ] Complete attribution, copyright provenance and bundled V3 reference rights review; owner MIT approval does not grant rights to third-party materials.
- [x] PR #1 and PR #6 were merged to `main` in order using merge commits (2026-10-29).
- [ ] Complete PR #7 security gate and review before merge; then retarget and review PR #8, preserving its generator commits.
- [ ] All CI checks pass on merged `main`: 62-case source validation, Python 3.10–13, 26 Skills CLI installer checks, three app builds, browser E2E, lockfile consistency.
- [ ] CodeQL Python and JavaScript/TypeScript scans pass without unresolved critical findings.
- [ ] All four npm lockfiles pass CI `npm audit --package-lock-only --include=dev --audit-level=high` (registry-side scan; vulnerabilities may change over time).
- [x] **GitHub Dependency Graph is available:** the public [Dependencies page](https://github.com/kunlong-luo/archvela/network/dependencies) displayed 216 indexed dependencies from `main` lockfiles on 2026-10-29, after merging PR #6. Public repositories normally have the graph enabled by default. Earlier SBOM API 404 did not by itself prove the setting was off; see Issue #9. Dependency Graph availability is not proof that the PR Dependency Review job succeeded.
- [ ] GitHub Dependency Review must execute on a **new PR CI run** and pass (not be skipped); investigate vulnerability advisories rather than suppressing them without written reason.
- [ ] Review GitHub repository settings: branch protection/ruleset, Dependabot alerts, private vulnerability reporting, secret scanning if available, Actions token permissions.
- [ ] Install Skill by cloning public `main` into a clean project. Confirm it is discoverable in at least one real Agent client, not merely via installation paths.
- [ ] Reproducibly run one V3 architecture generation end-to-end; archive input request, output documents, safe write evidence and test result.
- [ ] Check all images/media/icons/data are original or licensed for redistribution.
- [ ] Update README installation instructions and create GitHub Release notes with a **verified** tag and short migration warning; owner must authorize the actual release.

## Still separate from release

- The model-backed paired evaluation has **not yet run**; it should not block publishing a clearly described experimental v0.1 Skill if all release criteria are met. Do not describe it as proven to improve AI coding.
- External security scanning and code coverage are not guarantees of vulnerability-free production.
- The examples are reference demos, not live business applications or approved construction plans.

## No automatic release

No workflow in this repository merges PRs, creates tags, publishes NPM packages, or deploys the examples. Only the owner should approve and initiate a release.
