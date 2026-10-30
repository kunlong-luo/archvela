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
| Non-main remote branches | **0 after verified cleanup** (10 existed at preflight) | [Cleanup #40990833067](https://github.com/kunlong-luo/archvela/actions/runs/40990833067) + fresh branch API |
| Rulesets returned by public API | `[]` | Repository rulesets API |
| Detailed branch protection | **Unknown**; integration received HTTP 403 | Requires owner Settings check |
| Auto-delete merged PR branches | **disabled** | Repository API (`delete_branch_on_merge=false`) |
| GitHub About Description | Contains accidental `复制` suffix | Repository API |
| GitHub Topics | Includes `architecture-srv` | Repository API |
| Secret scanning, alerts, repository Actions defaults | **Not independently verified** | Requires owner Settings check |

## Latest pre-Alpha candidate check (2026-10-30)

This section supersedes historical values in the 2026-10-30 cleanup snapshot **below**:
- `main` at `4b4c20d93084db1c326afbc561b60184dd69e379`; 7/7 main CI workflows passed.
- `main.protected=false` (branch API) and public Rulesets API returned `[]`. Owner must configure mandatory checks and prevent force-push/delete.
- Auto-delete on merge remains **false**; five post-cleanup merged feature branches remained as of the last audit.
- Description no longer contains the accidental `复制` suffix, but still has trailing spaces; topic `architecture-srv` remains.
- Zero GitHub Releases; no Alpha tag, no approval yet. See [Alpha sign-off](./ALPHA-RELEASE-CHECKLIST.md).

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
   write permissions. The one-time cleanup exception was removed after success.
6. **Settings → Security & analysis / Advanced Security**: verify
   Dependabot alerts, secret scanning, push protection and private
   vulnerability reporting if offered for this repository and plan.
   Existing CodeQL, npm audits and PR dependency review are separate checks.

## Verified one-time cleanup — completed on 2026-10-30

The audited [cleanup run](https://github.com/kunlong-luo/archvela/actions/runs/40990833067)
completed with **success**. GitHub's branch API was queried afterward and
listed **only `main`**: ten existing merged PR branches plus the hardening
PR's branch were deleted. Validation included expected SHA, merged PR,
branch protection, ancestry and repo identity. The code remains in
[the audit script](../scripts/prune_merged_branches.py).

- [x] Verified the workflow run succeeded.
- [x] Verified that no non-main branches remain.
- [x] Removed the temporary privileged workflow from the default branch;
  there is **no standing `contents:write` cleanup job**.
- [ ] **Owner setting still needed:** enable automatic deletion of merged PR
  branches. The installed GitHub connector cannot change this repository
  setting.

For future work, use pull requests and review actual branch merge status
before cleanup. A closed PR is not necessarily merged. Do not delete
unmerged work, protected branches, or `main`.

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
