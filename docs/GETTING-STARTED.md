# Getting started with Archvela

**English (default)** · [简体中文](./GETTING-STARTED.zh.md) · [Project overview](../README.md) · [Agent compatibility](./COMPATIBILITY.md)

Archvela supports two workflows:

- **Use the Skill with a coding agent** to plan and review frontend architecture in your existing project.
- **Use the local tooling** to search the 62 scenario references, create draft architecture documents, or scaffold one of three runnable examples.

Archvela is a *pre-release toolkit*: installing its Skill is not proof that an AI model will correctly discover or follow it. Generated architecture documents are drafts requiring review.

## Requirements

| Workflow | Requirements |
|---|---|
| Install the Skill | Node.js 22.20+, npm, GitHub access, and your own installed coding-agent client |
| Browse scenarios / generate documents | Python 3.10+; the core helper scripts use the standard library |
| Build standalone examples | Node.js 24, npm and the committed `package-lock.json` files |

### English-language architecture references

The [Skill's English-first entrypoint](../.agents/skills/archvela-architect/SKILL.md) provides framework-neutral review steps and a [six-domain English guide](../.agents/skills/archvela-architect/references/ENGLISH-DECISION-GUIDE.md). An English query can resolve a V3 scenario ID, but detailed scenario titles/descriptions and long-form source volumes remain largely Chinese. Do not imply the full catalog is translated. Preserve the user's existing stack unless an audited constraint justifies migration.

## Option A — Install in your project

Open a terminal **inside the target project**, then use the interactive installer:

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect
```

To select Codex, Claude Code and OpenCode explicitly:

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect \
  --agent codex --agent claude-code --agent opencode --copy --yes
```

This is a **project-local** install by default. Add `--global` only if you intend to install to your user-level Skills directories. The `--copy` option avoids requiring a symlink back to the original repository. Inspect an existing `archvela-architect` installation before replacing any customized local copy.

### Confirm installation

Check the actual installer output and project files. Common project paths include:

| Agent | Expected project-level Skill entrypoint |
|---|---|
| Codex / OpenCode | `.agents/skills/archvela-architect/SKILL.md` |
| Claude Code | `.claude/skills/archvela-architect/SKILL.md` |
| Other agents | See the [compatibility matrix](./COMPATIBILITY.md) |

Actual destinations can vary with the Skills CLI version and shared-directory support. You can also inspect installed Skills with:

```bash
npx skills list
```

**Test discovery in a real, fresh agent session.** Try this prompt:

> Use the `archvela-architect` Skill to audit my existing React project. First inspect its main user journeys, routing, dependencies and build configuration. Return the closest V3 scenario, an architecture decision record (ADR), a four-layer splitting plan, a performance budget and verifiable acceptance criteria. **Read-only analysis: do not edit files or deploy.**

For a valid L2 discovery claim, observe that the *actual client* loads the Skill and retrieves an appropriate scenario. File presence alone establishes only L1 installer behavior.

To manage an installation, read the CLI prompts before confirming updates or removal:

```bash
npx skills list
npx skills check
npx skills update archvela-architect
npx skills remove archvela-architect
```

See [Skills CLI command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## Option B — Search and generate without an AI agent

### 1. Clone the repository

```bash
git clone https://github.com/kunlong-luo/archvela.git
cd archvela
```

### 2. Browse the catalog

```bash
python3 .agents/skills/archvela-architect/scripts/scenes.py --list-domains
python3 .agents/skills/archvela-architect/scripts/scenes.py --query "digital twin"
python3 .agents/skills/archvela-architect/scripts/scenes.py --id V3-26 --json
```

These commands search the checked-in 62-scenario catalog; they do not call an AI model.

### 3. Preview architecture documents

A preview is **read-only**:

```bash
python3 .agents/skills/archvela-architect/scripts/new_project_docs.py \
  --scene V3-26 --project my-home --output ./scratch/my-home --plan-json
```

After inspecting the destination and preview, add `--write` to create the draft files:

```bash
python3 .agents/skills/archvela-architect/scripts/new_project_docs.py \
  --scene V3-26 --project my-home --output ./scratch/my-home --plan-json --write

python3 .agents/skills/archvela-architect/scripts/plan_contract.py \
  ./scratch/my-home/docs/architecture/archvela-plan.json --level draft
```

The outputs include an ADR, performance/splitting budget, agent delivery card and optional `archvela-plan.json`. Contract validation checks required fields and evidence structure; it cannot verify whether user-supplied test results or performance metrics are genuine.

### 4. Scaffold a runnable example

**Only** V3-02 (cinematic site), V3-14 (SaaS workspace) and V3-26 (home digital twin) currently ship runnable source templates. The other 59 scenarios provide architecture reference material and document generation, **not** complete code projects.

```bash
python3 scripts/archvela_create.py list
python3 scripts/archvela_create.py create --scene V3-02 --project brand-demo --output ./workspace
# Inspect the dry-run output and intended directory, then:
python3 scripts/archvela_create.py create --scene V3-02 --project brand-demo --output ./workspace --write
cd workspace/brand-demo
npm ci
npm run build
npm run dev
```

No deployment, model invocation, or package install happens from the dry-run itself.

## Troubleshooting

| Symptom | What to check |
|---|---|
| `npx` or install fails | `node --version`, `npm --version`, access to GitHub and the npm registry, proxy settings, and installer diagnostics |
| Agent cannot see the Skill | Reopen the client in the correct project, inspect the actual Skill directory and client-specific discovery rules |
| Python script not found | Run from the Archvela repository root or the correct installed Skill directory |
| The output path already exists | This is intentional overwrite protection. Choose a new destination rather than bypassing the guard |
| Need to establish model effectiveness | Use the [real-agent evaluation protocol](./AGENT-EVAL-PROTOCOL.md), not the installer CI result |

## Next steps

Explore the [scenario catalog](../.agents/skills/archvela-architect/references/07_V3_全场景蓝图与选型索引.md), [runnable examples](../examples/README.md), [structured plan contract](./PLAN-CONTRACT.md), [evaluation harness](../benchmarks/README.md) and [contribution guide](../CONTRIBUTING.md).

**Security:** review third-party installers and generated code. Do not send secrets, proprietary customer files, or unauthorized data to an unknown agent or plugin.
