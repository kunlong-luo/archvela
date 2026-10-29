# GitHub repository profile & maintainer checklist

> This is a **proposed repository configuration**, not proof that settings were changed. Some settings require repository administration permissions in the GitHub web interface.

## About sidebar (suggested)

**Description** (short, ready to paste):

> Scenario-first frontend architecture Skill for AI coding agents. 62 scenarios, 3 runnable starters, reproducible evaluation and safe-by-default generators.

**Topics** (copy/paste, choose up to the GitHub limit):

```text
agent-skills, ai-coding, architecture, frontend, nextjs, react, typescript, developer-tools, code-generation, software-design, digital-twin, opensource
```

**Website:** leave empty until there is a verified, maintained public demo. A GitHub README or unlaunched product domain is not a deployed website.

**Social preview image:** optional. Use a rights-cleared, original brand image. Do not imply an official affiliation with OpenAI, Anthropic or other platform vendors.

## Settings and governance checks

- [ ] Set repository **Description** and **Topics** in the GitHub About panel.
- [ ] Enable appropriate branch protection/rulesets for `main` with required status checks; avoid requiring PR-only jobs on push events.
- [ ] Require PR reviews where collaborator availability permits, and restrict force pushes and deletion of `main`.
- [ ] Review Actions permissions; prefer least-privilege `GITHUB_TOKEN` and explicit write permissions only for necessary jobs.
- [ ] Confirm Dependabot alerts, security advisories, and secret scanning/push protection availability for this repository and plan.
- [ ] Enable automatic deletion of merged PR branches if desired; manually delete previously merged stale branches only after verifying their PRs and merged commits.
- [ ] Check that [Issue templates](../.github/ISSUE_TEMPLATE/bug_report.md) and [PR template](../.github/pull_request_template.md) appear in the GitHub UI.
- [ ] Check [SECURITY.md](../SECURITY.md), original asset provenance, license coverage, and [release gates](./RELEASE-READINESS.md).
- [ ] Create a real GitHub Release only after explicit owner approval and verifying the tag, notes, CI, documentation and third-party rights.

## Evidence claims

- CI tests currently verify installation/structure, builds and browser interactions. They do **not** prove model-backed benefits.
- The external Skills CLI is a third-party tool; references to supported agents describe installer targets, not endorsements or integrations certified by their vendors.
- Badges reflect the latest GitHub Actions runs on `main`; they are not static quality scores.
- Keep user-visible READMEs bilingual and check local links through `tests/test_documentation.py`.

## Branch cleanup command (maintainers only)

Verify branch merge status and run this from a properly authenticated clone **only after reviewing the exact branch list**:

```bash
git fetch --prune origin
git branch -r --merged origin/main
# Review the list; delete only verified stale branches:
# git push origin --delete <exact-branch-name>
```

Never delete a branch solely because its PR was closed: closed-without-merge can contain valuable work.
