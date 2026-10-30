# Release Readiness — Archvela V0.3

> **Status: PRE-RELEASE / NOT APPROVED FOR PUBLICATION.**
> Snapshot: **2026-10-30**. Last verified `main` commit before this
> hardening PR: `c2ba1ace2fc0c587c353b390f435818c5afff4ea`.
> Its seven GitHub Actions workflows passed. **No GitHub Release was found.**
> A PR merge does not publish a release or authorize a new tag, package or
> deployment.

## What is already supported by evidence

- [x] Original Archvela code and documentation have owner-approved MIT
  licensing **within the rights held by the owner** (PR #1). No rights to
  third-party materials are implied.
- [x] The 62-scenario, six-domain V3 Skill and three runnable example starters
  were merged through PRs [#1](https://github.com/kunlong-luo/archvela/pull/1),
  [#6](https://github.com/kunlong-luo/archvela/pull/6),
  [#7](https://github.com/kunlong-luo/archvela/pull/7),
  and [#8](https://github.com/kunlong-luo/archvela/pull/8).
- [x] `main` at `c2ba1ace` passed **7/7 workflow groups**: Skill/Python
  validation, Skills CLI compatibility, example builds, generated project
  builds, browser E2E, lockfile integrity, security scanning.
  [Actions](https://github.com/kunlong-luo/archvela/actions).
- [x] PR Dependency Review actually executed and succeeded on PRs #7/#8 and
  subsequent PRs; it is expected to be **skipped on ordinary main pushes**
  because the review examines dependency changes between PR commits.
  Repository Dependency Graph was available; [Issue #9](https://github.com/kunlong-luo/archvela/issues/9)
  is closed. The separate npm audit and CodeQL run on main.
- [x] The installer ran against **20 local agent targets + six global
  installations**. PR [#23](https://github.com/kunlong-luo/archvela/pull/23)
  also verified public GitHub-source and pinned-commit install paths for
  Codex, Claude Code and OpenCode (**L1 only**).
- [x] English `README.md`, Chinese `README.zh.md` and corresponding
  bilingual getting-started guides exist. PRs
  [#24](https://github.com/kunlong-luo/archvela/pull/24) and
  [#25](https://github.com/kunlong-luo/archvela/pull/25) passed CI and merged.

## V0.3 repository hardening

- [x] Audit as of 2026-10-30: 10 **unprotected** non-main branches were
  mapped to individual **merged** PRs, all targeting main. The inventory,
  original SHA and PR number are pinned in
  [scripts/prune_merged_branches.py](../scripts/prune_merged_branches.py).
- [x] **Verified the actual cleanup run:** [Actions #40990833067](https://github.com/kunlong-luo/archvela/actions/runs/40990833067)
  completed with success, and a fresh branch API query returned **only `main`**.
  All ten old merged branches and the PR #26 work branch were removed. The
  job compared each pinned SHA, merged PR, branch protection and ancestry.
- [x] **Removed the temporary `contents:write` cleanup workflow** after
  successful deletion, keeping the audit script and safety tests in history.
  No recurring privileged cleanup job remains.
- [ ] GitHub About **Description** currently has an accidental trailing
  `复制` suffix. Edit it out in the repo settings.
- [ ] Change the misleading `architecture-srv` Topic to
  `software-architecture` or `software-design`; verify the public About panel.
- [ ] Enable `Automatically delete head branches`; it was disabled on
  2026-10-30. This requires repository Settings access.
- [ ] Add an appropriate **main branch ruleset / branch protection**.
  Public ruleset API returned an empty list at audit time. Detailed branch
  protection returned 403 for the installed GitHub integration; its complete
  configuration could **not** be verified. Check it in repository Settings.
- [ ] Inspect Dependabot alerts, secret scanning, private vulnerability
  reporting and Actions token defaults in Settings; these require settings
  access not available through the current connector. Existing CodeQL and npm
  audits **do not prove** these GitHub settings are enabled.

## Release blockers independent of branch cleanup## Evidence and provenance tooling (not release approvals)

- [x] A read-only pilot evidence audit checks self-reported client metadata,
  paired prompt integrity, sanitized response/log file presence and SHA-256
  digests. It **does not** execute or verify an LLM run.
  [Operator procedure](./REAL-AGENT-PILOT.md).
- [x] The checked-in Git source tree currently contains no separate raster,
  SVG, 3D, font, video, audio or PDF assets; a strict
  [media inventory gate](./ASSET-PROVENANCE.md) checks any future additions.
  This is **not a legal copyright or text provenance audit**.
- [ ] Human review of all V3 reference text, example source, inline graphics,
  trademarks, package licenses and rights provenance remains mandatory.



- [ ] Review source/copyright provenance of bundled V3 references, copied
  design examples, images, trademarks, icons and any third-party media; obtain
  attribution or remove content that cannot be redistributed.
  [Issue #5](https://github.com/kunlong-luo/archvela/issues/5).
- [ ] In at least one **real** logged-in client, demonstrate Skill discovery
  (L2) and an end-to-end scenario-to-ADR task; preserve a sanitized transcript.
  Installation alone does not meet this gate.
  [Issues #2](https://github.com/kunlong-luo/archvela/issues/2) and
  [#21](https://github.com/kunlong-luo/archvela/issues/21).
- [ ] Archive a reproducible V3 scenario output, dry-run, authorized write,
  built app (where applicable), browser/user-journey validation and its
  actual limitations; separate fixture data from production data.
- [ ] Verify security alerts, README install instructions, release notes and
  third-party license compliance against the *release candidate commit*.
- [ ] Obtain **explicit owner approval** before creating a Git tag,
  GitHub Release, distribution package or public deployment.

## V0.4 evaluation-integrity improvements (no live trials)

- [x] Pilot evidence validation retains failed/blocked client attempts and
  treatment Skill non-discovery as **negative observations**. A clean evidence
  bundle is not a successful agent outcome; baseline Skill contamination
  remains an invalid paired experimental setup.
- [x] Added a no-model workspace preflight and operator-attested, response-only
  blind-review export that deliberately excludes arm mappings, metadata and
  raw tool logs. Manual redaction and native client isolation checks remain
  mandatory.
- [ ] Actually execute **12 authorized, model-backed pilot sessions**
  across Codex, Claude Code and OpenCode; no model run is asserted here.
- [ ] Obtain independent human grades and reproducible code/test evidence,
  including failed trials, before publishing model-effectiveness claims.

## Separate research goal (does not block an honest experimental release)

A paired study of Archvela versus baseline agents has **not run**. The V0.3
pilot is 2 tasks × 2 arms × 3 clients = **12 live sessions**; the full
first-pass design is 12 tasks × 2 arms × 3 clients = **72 sessions**.
The existing harness prepares blank slots and validates artifact structure,
not model behavior. Never present a synthetic score, unrun command or green
L1 installer workflow as L3 evidence.

## Release authority and operational safety

The repository does **not** automatically create releases, tags or deploy
the examples. Hardening is distinct from release approval. The one-time
cleanup ran from trusted `main`, had no `pull_request` trigger, and was
removed immediately after its successful, API-verified deletion.
Future branch hygiene depends on owner-enabled automatic deletion; see the
[maintainer runbook](./GITHUB-REPOSITORY-SETTINGS.md).

The examples are reference demonstrations, not production SaaS, real-time IoT
systems or construction-ready engineering designs.
