# Archvela v0.1 · Release readiness gate

**Not approved for publication by default.** PR #1, #6, #7 and #8 were merged into `main` in order on 2026-10-29, and the post-merge commit `9b237e5` passed all seven CI workflows. No release tag, deployment or package publication has been authorized. The owner approved MIT licensing of original materials; third-party rights and other release-specific gates remain open.

## Required before v0.1 release

- [x] Repository owner approved MIT licensing for original Archvela code and documentation within their publishing rights (recorded in PR #1, 2026-10-28).
- [ ] Complete attribution, copyright provenance and bundled V3 reference rights review; owner MIT approval does not grant rights to third-party materials.
- [x] PR #1 and PR #6 were merged to `main` in order using merge commits (2026-10-29).
- [x] PR #7 and PR #8 passed PR security gates (including GitHub Dependency Review) and were merged to `main` in order on 2026-10-29.
- [x] All seven CI workflows passed on merged `main` at commit `9b237e5`: Python/Skill validation, 26 Skills CLI installation checks, three app builds, generated-project builds, browser E2E, lockfile integrity and security scanning.
- [x] [Post-merge Security scanning](https://github.com/kunlong-luo/archvela/actions/runs/40797578807) passed CodeQL Python and JavaScript/TypeScript jobs; monitor new findings continuously.
- [x] All four npm lockfiles passed the post-merge CI `npm audit --package-lock-only --include=dev --audit-level=high` (registry-side scan; vulnerabilities may change over time).
- [x] **GitHub Dependency Graph is available:** the public [Dependencies page](https://github.com/kunlong-luo/archvela/network/dependencies) displayed 216 indexed dependencies from `main` lockfiles on 2026-10-29, after merging PR #6. Public repositories normally have the graph enabled by default. Earlier SBOM API 404 did not by itself prove the setting was off; see Issue #9. Dependency Graph availability is not proof that the PR Dependency Review job succeeded.
- [x] GitHub Dependency Review executed and **passed (not skipped)** in [PR #7](https://github.com/kunlong-luo/archvela/actions/runs/40797317029) and [PR #8](https://github.com/kunlong-luo/archvela/actions/runs/40797318957). On ordinary `main` push events this PR-only job is expected to be skipped.
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
