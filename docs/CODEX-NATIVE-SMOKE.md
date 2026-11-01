# Codex native discovery — first real-client smoke (NOT EXECUTED)

> **Status: 0 real client sessions.** This is an operator protocol, NOT a transcript, evaluation score or authorization for API spending. It is separate from the [4-session randomized paired pilot](https://github.com/kunlong-luo/archvela/issues/31) and cannot count toward that study.

## A. Exact source and Skill installation (L1)

- Reference `main` SHA as of protocol writing: `9bd225f49d9d234e72bb4e371c1e203cdb9b1f90`. If a new commit is merged, use the **newly verified exact 40-character SHA** and clearly record it; do not install floating `main` or an unpublished release tag.
- Use the real authenticated Codex client you personally control. Inspect and authorize usage costs yourself. No API/model calls are made by this document.
- Start an empty isolated project directory; inspect global/inherited Agent Skills and `AGENTS.md` so you can distinguish native discovery from leakage.

```bash
git clone https://github.com/kunlong-luo/archvela.git archvela-smoke-source
cd archvela-smoke-source
git checkout --detach 9bd225f49d9d234e72bb4e371c1e203cdb9b1f90
git rev-parse HEAD
cd ..
mkdir archvela-smoke-project
cd archvela-smoke-project
npx --yes skills@1.7.4 add \
  "https://github.com/kunlong-luo/archvela/tree/9bd225f49d9d234e72bb4e371c1e203cdb9b1f90/.agents/skills/archvela-architect" \
  --skill archvela-architect --agent codex --copy --yes
test -s .agents/skills/archvela-architect/SKILL.md
```

For byte-level L1 verification consult [pinned installation guide](./PINNED-SKILL-INSTALL.md). File presence alone proves neither native discovery nor model quality.

## B. Authenticated natural Skill discovery (L2)

Open the **actual Codex app/CLI in the fresh project** and submit the following exact prompt, **without explicitly naming Archvela**, to avoid forcing manual Skill selection:

> Design an SEO-first enterprise landing page with a cinematic hero. Prioritize mid-range mobile devices, defer 3D until needed, use a no-WebGL fallback, support reduced-motion, and budget network and CPU use. First return a read-only architecture decision record (ADR), four-layer module/asset split, rendering choices, trade-offs, risks, and testable acceptance criteria. Do not write code or install packages.

Observe directly whether the client loads the local `archvela-architect` Skill and whether it actually reads/retrieves V3-02 reference material. **No visible native discovery = not observed**, regardless of how good a generic ADR appears. If natural discovery fails, record the failure. You may run a separate **diagnostic** using “Use the installed archvela-architect Skill”, clearly labeled **explicit invocation**, never replacing or reclassifying the first observation.

Evaluate output quality as descriptive, not a comparative L3 score: inspect actual SEO plan, deferred loading, no-WebGL/reduced-motion fallback, four-layer splitting and measurable tests.

## C. Only record real, sanitized observations

```text
Source commit:
Client app/CLI version:
Actual model ID:
UTC date and time:
Fresh workspace/global Skill interference assessed: yes / no / unknown
Installed Skill bytes verified: yes / no
Natural native discovery observed: yes / no / not_observed
Actual V3-02 reference read: yes / no / not_observed
ADR output and factual limitations:
Actual tool/permission errors:
Sanitized evidence file SHA-256 or private record identifier:
Manual reviewer and date (if any):
```

Do not publish authentication tokens, raw tool logs containing credentials, personally identifiable details, private customer code or unredacted transcripts. Preserve failed/blocked cases without substituting fabricated 0-token, 0-cost or success claims.

If you have authentic evidence, record a sanitized result in [Issue #31](https://github.com/kunlong-luo/archvela/issues/31). The experimental 4-session protocol and independent blind review live in [the pilot operator procedure](./REAL-AGENT-PILOT.md). **One L2 smoke does not establish L3 effectiveness, license clearance or GitHub Release authorization.**