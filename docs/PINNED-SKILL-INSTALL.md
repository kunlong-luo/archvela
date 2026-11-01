# Verify an Archvela Skill install at an exact Git commit (L1 only)

> **Status:** reproducibility instructions; not a claim of native model discovery. The proposed `v0.1.0-alpha.1` tag is **not yet published**. Never treat a floating `main` or nonexistent tag as a release identifier.

## What is actually tested in GitHub CI

[Cross-Agent Skill Installer Compatibility](../.github/workflows/compatibility.yml) runs Vercel `skills@1.7.4` on 20 project installation targets and 6 global target mappings (L1). For **Codex** it also installs from:

```text
https://github.com/kunlong-luo/archvela/tree/<EXACT_GITHUB_SHA>/.agents/skills/archvela-architect
```

The pinned-install job compares the installed bytes of **five** exact paths against its own checked-out Git commit: `SKILL.md`, `references/scenarios.json`, `references/architecture_profiles.json`, `scripts/scenes.py` and `scripts/new_project_docs.py`. This prevents a false positive where the installer creates the directory but silently returns a stale or unrelated Skill. It does **not** establish that every source file is identical, that the CLI is independently trustworthy, or that a real model discovered the Skill.

## Independent local check

Replace the placeholder with an **existing, verified 40-character Git commit** (not a draft release name), from a clean source checkout:

```bash
git clone https://github.com/kunlong-luo/archvela.git archvela-review
cd archvela-review
git checkout --detach REPLACE_WITH_VERIFIED_40_HEX_SHA
git rev-parse HEAD
cd ..
mkdir -p archvela-install-check
cd archvela-install-check

npx --yes skills@1.7.4 add \
  "https://github.com/kunlong-luo/archvela/tree/REPLACE_WITH_VERIFIED_40_HEX_SHA/.agents/skills/archvela-architect" \
  --skill archvela-architect --agent codex --copy --yes

for relative in SKILL.md references/scenarios.json references/architecture_profiles.json \
  scripts/scenes.py scripts/new_project_docs.py; do
  cmp -s "../archvela-review/.agents/skills/archvela-architect/$relative" \
    ".agents/skills/archvela-architect/$relative" || exit 1
done
```

Use a fresh directory that has no customized `archvela-architect` installation. **Do not** install over user-modified Skill files or run untrusted repository scripts without approval. The CI check itself is the versioned reference implementation.

For a real L2/L3 claim, the actual Codex client must be authenticated, show it can natively discover the Skill, read a relevant V3 reference, and produce a real scenario-to-ADR result with a sanitized trace. Follow [pilot instructions](./REAL-AGENT-PILOT.md) and [Issue #31](https://github.com/kunlong-luo/archvela/issues/31); **0 real experiments are claimed** by the L1 installer job.
