# Contributing to Archvela / 参与贡献

Thank you for helping independent developers build maintainable frontend products. Contributions can improve the Skill, the 62-scenario reference catalog, generators, runnable examples, tests and documentation.

[English README](./README.md) · [中文 README](./README.zh.md) · [Getting Started](./docs/GETTING-STARTED.md) · [中文入门](./docs/GETTING-STARTED.zh.md) · [Security](./SECURITY.md)

## Documentation language convention

**English is the default language** for the GitHub landing and canonical entrypoint documentation: `README.md` and `docs/GETTING-STARTED.md`. Their maintained Chinese translations live at `README.zh.md` and `docs/GETTING-STARTED.zh.md`. Link back to the corresponding language from both versions, and update both when instructions, capabilities or safety claims change. Keep repo-relative links valid; run the documentation regression tests before opening a PR. Domain-specific V3 reference documents may remain in Chinese, but English-facing navigation should explain those limitations rather than mislabeling them as English.

## Before opening an issue or PR

1. Search [open and closed issues](https://github.com/kunlong-luo/archvela/issues) for duplicates.
2. Describe a **real user task** and reference the applicable `V3-xx` scenario. For a new scenario, propose the user journey, domain and why existing IDs do not fit.
3. State the smallest desired change, alternatives rejected, compatibility assumptions and acceptance evidence.
4. Use the [bug report](./.github/ISSUE_TEMPLATE/bug_report.md) or [feature proposal](./.github/ISSUE_TEMPLATE/feature_request.md) template. File security vulnerabilities privately according to `SECURITY.md`, not as public defects.

**Scope:** frontend/UX, browser rendering, performance, architecture planning and agent-assisted development. Backends, production deployments, payments and regulated engineering designs are outside the core Skill.

## Local development / 本地开发

Requirements: **Python 3.10+** for stdlib-only scripts, **Node.js 24/npm** for tested examples. Create a focused branch off `main` and avoid mixing unrelated refactors.

```bash
git clone https://github.com/kunlong-luo/archvela.git
cd archvela
python3 -m unittest discover -s tests -v
python3 -m compileall -q .agents/skills/archvela-architect/scripts
python3 benchmarks/evaluate.py validate-cases
```

For changes to a runnable starter, test the **specific** independent project:

```bash
cd examples/saas-workspace  # or examples/cinematic-site or examples/home-digital-twin
npm ci
npm run test --if-present
npm run typecheck
npm run build
```

For browser E2E or generated projects, check the respective workflows and [test guide](./tests/browser/README.md). Do not describe an unrun command as having passed.

## Preserve project invariants

- The Skill entrypoint is `.agents/skills/archvela-architect/SKILL.md` and must remain portable across Skills-capable clients.
- V3 keeps **62 distinct scene IDs**, six domains with counts **13 / 11 / 12 / 8 / 9 / 9**. Do not renumber old scenarios or casually change the V3 snapshot; update `scenarios.json` and the Markdown reference in sync.
- Reuse the four independent architecture layers: **Package / Feature / JS Chunk / Asset Pack**.
- Keep Python generators **dry-run by default**, refusing existing files and symlink traversal. Preserve failure rollback and add regression tests for unsafe inputs.
- Only **V3-02 / V3-14 / V3-26** have runnable starter projects. Do not claim the other 59 provide code.
- If changing `package.json` in any of the three examples or `tests/browser`, update the matching `package-lock.json` with Node 24/npm and verify `npm ci`.
- For Skill compatibility, distinguish **L0/L1 file and installer tests** from **L2/L3 real-model discovery and task outcomes**. Synthetic grading fixtures are never published model benchmarks.
- Use licensed/original media and document copyright provenance; do not introduce API keys, real customer data, private source, misleading metrics or production credentials.

## Pull request quality bar

A good PR answers **what changed, why this design, what was actually tested, what remains unknown**. Use the [PR template](./.github/pull_request_template.md), include a small reproducible example when possible, and link the related issue. Where relevant, add tests for failure paths, usability/accessibility, browser fallbacks and performance-sensitive loading.

CI runs Skill validation, installer path and public GitHub-source checks, lockfile integrity, independent starter builds, generated-project builds, Chromium browser journeys and security scanning. Checks may be skipped when event conditions do not apply; **a green workflow is not evidence of model-backed improvement**.

## Maintainer and release boundaries

Maintainers review design, provenance and test evidence before merging. Public tags, releases, deployments or package publication require **separate authorization**, independent of merge permission. See [Release Readiness](./docs/RELEASE-READINESS.md).

---

中文简述：先开 Issue 说明具体用户任务和场景编号；分支保持小而专一；同步更新数据、文档、锁文件与测试；提交 PR 时说明实际执行了哪些验证、哪些尚未验证。不要将“Agent 安装成功”写成“模型效果提升”，也不要提交未经授权的素材和隐私数据。
