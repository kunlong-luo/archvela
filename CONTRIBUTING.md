# Contributing to Archvela

Archvela welcomes proposals to improve frontend architecture decisions, browser rendering, accessibility, performance and independent-developer workflows.

1. Open an Issue describing the target scenario and user task; identify the corresponding `V3-xx` ID.
2. Contribute a minimal PR with a concrete decision rationale, browser/runtime assumptions, resource-loading rules and an acceptance test.
3. Preserve existing IDs; a renamed scenario should retain its ID. Add new scenarios intentionally rather than silently rewriting existing data.
4. Update `references/scenarios.json` and its matching Markdown catalog together; keep 62 entries for the V3 snapshot. A future expanded catalog should be versioned separately.
5. Run `python3 -m unittest discover -s tests -v` before opening a PR.
6. Clearly label unverified performance estimates, mock/real data, external API requirements, third-party media licenses and safety-sensitive uses.

Please do not add private credentials, customer materials, proprietary source code or executable third-party Skill scripts without provenance and review.

## Reproducible frontend examples

Changes to any `examples/*/package.json` or `tests/browser/package.json` must include the corresponding `package-lock.json`, generated with Node 24/npm. Use `npm ci` in the supported CI path. Browser E2E tests run locally built services, not published production URLs; record real-device and other-browser limitations separately.
