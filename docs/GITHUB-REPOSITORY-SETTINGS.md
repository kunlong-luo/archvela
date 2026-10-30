# GitHub Repository Hardening — Maintainer Runbook

[Release readiness](./RELEASE-READINESS.md) · [Security policy](../SECURITY.md) · [Contributing](../CONTRIBUTING.md)

This runbook separates **verified GitHub API observations** from
**settings that require owner action**. An unchecked box is not complete,
even if CI is green.

## Verified repository snapshot — 2026-10-30

| Setting or artifact | Observation | Verification |
|---|---|---|
| Default branch | `main` | GitHub repository API |
| Main baseline | `c2ba1ace` | Seven CI workflow groups passed |
| Open PRs | 0 | Pull request API |
| Published GitHub Releases | 0 observed | Releases API |
| Non-main remote branches | 10, all unprotected and linked to merged PRs | Branch + PR APIs |
| Rulesets returned by public API | `[]` | Repository rulesets API |
| Detailed branch protection | **Unknown**; integration received HTTP 403 | Requires owner Settings check |
| Auto-delete merged PR branches | **disabled** | Repository API (`delete_branch_on_merge=false`) |
| GitHub About Description | Contains accidental `复制` suffix | Repository API |
| GitHub Topics | Includes `architecture-srv` | Repository API |
| Secret scanning, alerts, repository Actions defaults | **Not independently verified** | Requires owner Settings check |

## Owner actions in GitHub Settings

1. **About → Edit**: remove the trailing `复制` from Description.
   Suggested text:

   > Scenario-first frontend architecture Skill for AI coding agents. 62 scenarios, 3 runnable starters, safe generators.

2. Replace the `architecture-srv` Topic with `software-architecture`.
   Other useful Topics: `agent-skills`, `ai-coding`, `frontend`,
   `developer-tools`, `react`, `nextjs`, `code-generation`, `digital-twin`.
   No product website should be set until a real site has been deployed.
3. **Settings → General → Pull Requests**: enable
   **Automatically delete head branches** to avoid repeated cleanup.
4. **Settings → Rules → Rulesets** (or Branches / Branch protection):
   protect `main` against direct force push and deletion; require PRs and
   the appropriate successful CI checks. Choose exact required check names
   from a completed PR; consider external Dependabot PR behavior and
   `pull_request`-only dependency reviews before marking checks mandatory.
5. **Settings → Actions → General**: review default `GITHUB_TOKEN`
   permissions; prefer read-only by default and narrow explicit job-level
   write permissions. The temporary one-time cleanup job is the sole
   exception in this hardening PR.
6. **Settings → Security & analysis / Advanced Security**: verify
   Dependabot alerts, secret scanning, push protection and private
   vulnerability reporting if offered for this repository and plan.
   Existing CodeQL, npm audits and PR dependency review are separate checks.

## One-time deletion of verified merged branches

An audited [one-time workflow](../.github/workflows/cleanup-merged-branches.yml)
and [safe preflight script](../scripts/prune_merged_branches.py)
are proposed in the V0.3 hardening PR. They run automatically **only when
that specific workflow file is added/changed by a trusted push to `main`**.
They never execute on `pull_request`; the only write permission is
`contents: write` on the cleanup job. Every deletion is preceded by a
GitHub PR merge check, fixed SHA check, branch-protection check and ancestry
check. The current maintenance PR branch itself is also audited after merge,
so the cleanup does not leave a new stale branch.

**Required follow-up:**
- [ ] The cleanup workflow has completed **successfully**, with deletion logs.
- [ ] A fresh GitHub branch API query confirms only `main` remains.
- [ ] Remove the privileged one-off cleanup workflow using a new reviewed PR
  once successful; preserve the read-only/auditable script if useful.
- [ ] Enable automatic merged-branch deletion in Settings.

If GitHub refuses the write operation, **do not mark cleanup complete**.
A repository maintainer may instead run:

```bash
git fetch --prune origin
git branch -r --merged origin/main
# Verify every named branch is merged and contains no unique commits
# before issuing explicit commands:
git push origin --delete <verified-merged-branch>
git fetch --prune origin
```

Never delete `main`, protected branches, unmerged PR work or arbitrary refs
from a wildcard list. PR closure alone does not mean a branch was merged.

## Release and trust claims

- Passing installer tests proves only L0/L1, not real-agent L2 discovery
  or L3 improvement.
- CI builds and Chromium mobile *viewport* tests do not certify physical
  mobile hardware, WebGL GPUs or all browsers.
- English canonical docs: `README.md` and `docs/GETTING-STARTED.md`.
  Full Chinese translations: `README.zh.md` and
  `docs/GETTING-STARTED.zh.md`. Run `tests/test_documentation.py`
  to check internal links.
- Creating a Git tag, GitHub Release, package or public deployment requires
  separate owner approval and copyright/license verification.

A dedicated hosted website, social preview and marketing assets remain
optional; avoid claiming they exist until independently verified.
