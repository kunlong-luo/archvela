# Alpha: Owner GitHub protection and live governance

> **Not approved for publication.** The draft `v0.1.0-alpha.1` is not a GitHub Release or tag. Current GitHub connector exposes no owner-only repository-settings writes.

## Verified baseline (2026-11-01)

- `main` at `9bd225f49d9d234e72bb4e371c1e203cdb9b1f90` passed 7/7 main-push workflow groups.
- `main.protected=false`, public Rulesets API returned `[]`.
- `delete_branch_on_merge=false`. Zero public GitHub Releases.
- No rights owner has approved the V3 source text or third-party dependencies; no actual Codex L2/L3 evaluation is recorded.

## Actions required from repository owner

1. Open [repository Settings](https://github.com/kunlong-luo/archvela/settings) → **Branches** → **Add branch protection rule**, targeting exactly `main`. A **Rules → Rulesets → New branch ruleset** targeting the default branch is an alternative; avoid overlapping contradictory rules.
2. Enable **Require a pull request before merging**. If you are the only maintainer, do not require a review you cannot obtain; require an independent approval once a second reviewer is available.
3. Enable **Require status checks to pass before merging**. Choose **real recently observed PR job names**, not only workflow names:
   - `validate (3.10)`, `validate (3.12)`, `validate (3.13)`
   - `cross-agent-install` and `lockfiles`
   - `generated (V3-02)`, `generated (V3-14)` and `generated (V3-26)`
   - `chromium`
   - `CodeQL static analysis (python)` and `CodeQL static analysis (javascript-typescript)`.
   These are recommended checks: double-check exact names under [PR #37 Checks](https://github.com/kunlong-luo/archvela/pull/37/checks). Do not require a check that does not run on PRs.
4. Keep **Allow force pushes** and **Allow deletions** disabled; review admin and app bypasses. Consider strict up-to-date checks only after confirming your normal PR workflow can comply.
5. Open **Settings → General → Pull Requests** and enable **Automatically delete head branches**.
6. Tidy **About → Edit**: remove stale `architecture-srv` Topic and trailing spaces in Description. This is recommended hygiene, not a hard release gate.
7. Review **Settings → Actions** default token permissions and **Security & analysis** for Dependabot alerts, secret scanning/push protection and private vulnerability reporting. CI passing does not establish that these settings are enabled.
8. Verify `main.protected=true` with a new GitHub API read and inspect the **actual rule requirements, bypass conditions and status checks** in owner UI. Attach a sanitized screenshot or written settings evidence to [Issue #27](https://github.com/kunlong-luo/archvela/issues/27); never attach secrets.

GitHub documents public repository branch protection on Free plans: [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches); [Branch rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## Read-only live preflight (no tag, no release, no writes)

From a checked-out Archvela source repository with Python 3.10+:

```bash
python3 scripts/audit_release_governance.py --json
python3 scripts/audit_release_governance.py \
  --expected-sha 9bd225f49d9d234e72bb4e371c1e203cdb9b1f90 --json
```

The expected SHA prevents inadvertently accepting a moving `main`. This script reads GitHub repository details, branch status, seven source-SHA-specific main-push workflows, public rulesets and Releases. Failed/403 reads are **unknown**, not a pass. The `--require-ready` mode is deliberately nonzero while actual human authorization, copyright approval or native client evidence remains outstanding.

A separate **manual-only** `Alpha release governance audit` GitHub Actions workflow produces a read-only report; a successful workflow means the audit executed, **not** that it approved publication.

## Remaining hard gates

[Rights review #5](https://github.com/kunlong-luo/archvela/issues/5) requires actual third-party LICENSE/NOTICE texts and author permissions. [Codex native smoke](./CODEX-NATIVE-SMOKE.md) needs a real authenticated operator and is separate from the four-session paired study in [Issue #31](https://github.com/kunlong-luo/archvela/issues/31). Finally, the owner must **explicitly approve the exact Git SHA, tag and release text**, not merely say to continue preparing.