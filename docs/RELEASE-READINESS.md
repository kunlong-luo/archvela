# Archvela v0.1 · Release readiness gate

**Not approved for publication by default.** PR #1 and PR #6 are pending repository owner review; this security/eval work is a stacked PR on PR #6. No release tag, deployment, package publication or license approval is inferred.

## Required before v0.1 release

- [ ] Repository owner approves public MIT licensing, attribution and bundled V3 reference rights.
- [ ] PR #1 is reviewed and merged, then PR #6, then this PR; rebase stacked branches if necessary.
- [ ] All CI checks pass on merged `main`: 62-case source validation, Python 3.10–13, 26 Skills CLI installer checks, three app builds, browser E2E, lockfile consistency.
- [ ] CodeQL and dependency review scanning complete. Review reported warnings rather than suppressing without explanation.
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
