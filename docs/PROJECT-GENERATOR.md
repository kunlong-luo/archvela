# Archvela · Project Generator v0.1 candidate

**Scope matters:** Archvela has 62 architecture references but only **three runnable project templates** today. This generator deliberately refuses to claim a runnable scaffold for the other 59 scenarios.

## CLI

```bash
python3 scripts/archvela_create.py list --json

# No side effects: returns planned file count and path only
python3 scripts/archvela_create.py create \
  --scene V3-26 --project village-house --output ./workspace --json

# Requires an explicit output parent and creation flag
python3 scripts/archvela_create.py create \
  --scene V3-26 --project village-house --output ./workspace --write

cd ./workspace/village-house
npm ci
npm run dev
```

Currently supported projects: `V3-02` cinematic high-end site, `V3-14` SaaS operations workspace, and `V3-26` home digital-twin demonstration.

Each generated project includes:

1. The original **independently buildable** React/Next/Vite source with no server credentials.
2. A copied and renamed `package.json`/`package-lock.json` pair for reproducible `npm ci`.
3. An ADR, performance budget, Agent delivery task card and structured **draft** `archvela-plan.json`.
4. A README preserving the original starter ADR and explicit limitations, including fictional operational data and non-construction geometry.

## Safety properties

- Default dry-run; `--write` required.
- Validates npm-safe project slug; project is created under explicit `--output`.
- Refuses destination collision and symlinked output paths.
- Copies only allowlisted source paths and extensions; never copies `node_modules`, `.env`, build artifacts or arbitrary nested executable scripts.
- Each generated file is created exclusively. On failure, removes only the invocation's own files and empty directories.
- Does not install dependencies, run untrusted code, open browsers or deploy without the developer's separate action.
- Generated architecture docs are **drafts**; `reviewed` / `delivered` remain evidence checks, not proof of code correctness.

## CI

[generated-starters.yml](../.github/workflows/generated-starters.yml) invokes each supported scene in an isolated runner output directory, performs `npm ci`, typechecks and builds the generated project itself. It is separate from source-example tests.

## Next extension

A fourth template (e.g. Astro brochure or Babylon.js one-level game) should pass the same rules before being enabled. Avoid overfitting the scene-to-template mapping or reusing libraries outside their natural scope.
