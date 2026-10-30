# Changelog

All notable changes to Archvela are documented here. This project follows the
principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

**Release status:** No GitHub Release has been published as of 2026-10-30.
The version in `.agents/skills/archvela-architect/SKILL.md` is **candidate
metadata**, not proof of a published Git tag or release. Dates below describe
repository development, not official release dates.

## [Unreleased]

### Changed
- 2026-10-30: Hardened repository maintenance with a preflight-only-by-default,
  one-time merged-branch cleanup that validates PR merge state, pinned commit
  SHA, ancestry, branch protection and repository identity before any deletion.
  **Execution outcome must be verified in the corresponding Actions run**;
  merging a PR alone is not evidence that branches were removed.
- 2026-10-30: Reconciled release gates and issue descriptions against merged
  PRs and current CI evidence; kept unverified configuration and real-agent
  evaluation explicitly pending.

### Documentation
- 2026-10-29: Made English the GitHub default in `README.md`, moved the full
  Chinese translation to `README.zh.md`, and maintained English/Chinese
  `docs/GETTING-STARTED.md` / `docs/GETTING-STARTED.zh.md`.
- 2026-10-29: Redesigned the README landing with an architecture workflow,
  install instructions, starter boundaries, badges and evidence disclaimers;
  introduced issue/PR templates, expanded contributing guidance and offline
  documentation integrity tests.
- 2026-10-29: Corrected out-of-date GitHub-source install instructions.

### Agent Skill and tooling
- Added a scenario-first Skill with **62 stable V3 references** in six domains,
  deterministic bilingual search and six domain-specific architecture profiles.
- Added safe, dry-run-first architecture document generation, optional
  `archvela-plan.json` handoff, and structural draft/reviewed/delivered checks.
  Structural checks **do not** verify actual test or performance claims.
- Added the independent `archvela_create.py` generator for **three** runnable
  starters. The other 59 scenarios have architecture references/docs only.
- Added an offline 12-task paired agent evaluation harness and a pinned
  Codex/Claude Code/OpenCode pilot preparation tool. **No model-backed
  evaluation results have been collected.**

### Testing and security
- Added 20 Skills CLI project-target checks and six global installation
  targets, plus public GitHub-source and pinned-commit installation smoke
  checks for Codex, Claude Code and OpenCode (**L1, not L2/L3**).
- Added three isolated reference applications: a Next.js cinematic site,
  Next.js SaaS workspace and Vite/React Three Fiber home concept viewer,
  with separate lockfiles and builds.
- Added Chromium desktop/mobile-*viewport* E2E tests, generated-project
  smoke builds, lockfile verification, Python regression tests,
  CodeQL (Python/JS-TS), four npm audits and pull-request dependency review.
- Updated supported GitHub Actions and fixed TypeScript 7 compatibility
  regressions; prevented `@types/node` major upgrades while CI uses Node 24.

## Repository baseline: 2026-10-27 (unreleased 0.1.0 candidate)

- Established the `archvela-architect` Skill identity, V3 architecture
  references, 62 scenario catalog, initial helpers, tests and MIT license for
  original materials within the rights of the copyright holder.
- Archived six domain guidelines and the architecture templates.
- The `0.1.0` label is **not a published version**. No official tag, package,
  live demo or model benchmark is implied.

## Before publishing

Complete third-party intellectual-property and asset provenance review,
GitHub security/governance settings, an actual client discovery acceptance,
a reproducible end-to-end example, and [Release Readiness](./docs/RELEASE-READINESS.md).
A tag, release, package publication or deployment requires separate owner
approval.
