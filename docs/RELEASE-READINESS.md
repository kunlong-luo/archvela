# Release Readiness — Archvela first Alpha candidate

> **Status: PRE-RELEASE / NOT APPROVED FOR PUBLICATION.**
> **2026-10-30 pre-candidate baseline:** `main` commit
> `4b4c20d93084db1c326afbc561b60184dd69e379`, with seven GitHub Actions
> workflow groups passing. **That earlier commit is NOT the Alpha release SHA.**
> GitHub Releases observed: **0**. Actual candidate CI and final release SHA
> must be rechecked after candidate PR merge. A PR merge is not publication.
>
> **Proposed tag:** `v0.1.0-alpha.1` (**not created**).
> [English draft](./releases/v0.1.0-alpha.1.md) ·
> [中文草案](./releases/v0.1.0-alpha.1.zh.md) ·
> [Alpha sign-off checklist](./ALPHA-RELEASE-CHECKLIST.md) ·
> [Rights review register](./RIGHTS-REVIEW-REGISTER.md) ·
> [Machine-checked candidate contract](./RELEASE-CANDIDATE.json).

## Preliminary npm dependency license review — automated metadata only

- [x] Added an offline, reproducible audit of **4 lockfiles / 283 package installation rows**, with zero missing reported license metadata and **42 flagged rows** (LGPL-family / MPL / CC-BY). CI checks lockfile Git blob IDs and the full flagged review register. [Details](./DEPENDENCY-LICENSE-AUDIT.md).
- [ ] Actual third-party **license texts, NOTICE obligations, distributed binary contents and owner rights** remain unreviewed. The triage report intentionally says `rights_cleared=false`; a successful automated check is not legal sign-off.

## Alpha candidate release gates (2026-10-30)

- [x] First-Alpha bilingual release notes and a no-publication candidate contract prepared.
- [x] V0.1.0-alpha.1 candidate Skill metadata aligned; **not an official release**.
- [ ] **Third-party content/source/notice rights sign-off** by the authorized owner, including V3 text and npm packages; see [Issue #5](https://github.com/kunlong-luo/archvela/issues/5).
- [ ] **GitHub admin protection:** public branch API currently returns `main.protected=false`; public Rulesets API `[]`. Owner must enable and confirm. Auto-delete branches is also off.
- [ ] **Authentic Codex L2/L3 smoke:** see [Issue #31](https://github.com/kunlong-luo/archvela/issues/31); no fake scores, timestamps or model logs.
- [ ] Freeze the final Alpha SHA, check 7/7 CI against that commit, verify package/license notices and scan for secrets.
- [ ] Obtain **explicit owner approval for the exact version, final SHA and wording** before creating a tag or Release.



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
- [ ] GitHub About **Description** no longer has the former `复制` suffix
  (2026-10-30 API), but still contains trailing whitespace. Tidy in Settings.
- [ ] Change the misleading `architecture-srv` Topic to
  `software-architecture` or `software-design`; verify the public About panel.
- [ ] Enable `Automatically delete head branches`; it was disabled on
  2026-10-30. This requires repository Settings access.
- [ ] Add an appropriate **main branch ruleset / branch protection**.
  Fresh GitHub branch API returned `main.protected=false` and public rulesets
  API returned `[]` (2026-10-30). Detailed branch protection returned 403 for
  the integration, and owner-only settings remain unverified.
- [ ] Inspect Dependabot alerts, secret scanning, private vulnerability
  reporting and Actions token defaults in Settings; these require settings
  access not available through the current connector. Existing CodeQL and npm
  audits **do not prove** these GitHub settings are enabled.

## Evidence and provenance tooling (not release approvals)

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

## Release blockers independent of branch cleanup

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

## V0.5 pilot integrity gates (still no model trials)

- [x] CSPRNG-generated opaque blind IDs and signed, operator-only pilot
  assignment manifests replace derivable reviewer IDs in fresh V2 studies;
  integrity checks cannot certify a truthful operator.
- [x] Strict clean local checkout vs pinned SHA checks and
  `skills@1.7.4` installer version pinning in Treatment instructions.
- [x] Independent review response SHA-256 binding, and explicit separation
  of assigned-condition / intention-to-treat descriptive differences
  from Skill discovery-gated observations.
- [ ] Real-agent sessions remain 0/12. Future published claims require
  actual recorded sessions, independently inspected outputs, original
  failure rates, third-party rights clearance and explicit owner sign-off.
- [ ] GitHub `main` branch protection and other owner-admin controls
  remain incomplete; see [#27](https://github.com/kunlong-luo/archvela/issues/27).

## V0.4.1 pilot reporting gate (no live model data)

- [x] Added per-client offline evidence and human-grade summary tooling
  that enforces all planned attempts and preserves failed/blocked
  sessions in denominators.
- [x] Strict review-sheet validation, no scoring for failed sessions,
  no incomplete-pair delta, no cross-model pooled score, and regression
  tests using **fixtures only**.
- [ ] Capture 12 actually authorized client runs, independent blinded
  human scores, real build results and permission-checked transcripts
  before making *any* model-effectiveness statement.

## V0.6 English-first Skill usability (does NOT establish L2/L3)

- [x] English discovery metadata and native entrypoint guidance without blanket exclusions of Vue or any frontend/component framework.
- [x] Six-domain English decision guide and explicit disclosure that most long-form V3 sources and scenario descriptions remain Chinese.
- [x] Offline tests for bilingual entrypoint, guide references and neutral technology selection.
- [ ] Independent English-speaking human review of all 62 source scenarios remains incomplete; this is not a full translation.
- [ ] Real Codex/Claude Code/OpenCode Skill discovery and outcomes remain unverified; see [#21](https://github.com/kunlong-luo/archvela/issues/21).
- [ ] GitHub `main` branch protection, rights provenance and owner release approval remain outstanding.

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
