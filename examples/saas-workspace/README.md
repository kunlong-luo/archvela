# Orbit Desk · V3-14 (runnable demo)

Next.js 16 + React 19 operational dashboard, with fully functional **client-only sample workflow** (filter/search/select, update status, reset) and a **lazy-loaded** SVG service breakdown. **No backend, auth, telemetry or live data is connected.**

## Run

```bash
npm install
npm run dev
npm run test
npm run typecheck
npm run build
```

Visit `http://localhost:3000`. Node 24 recommended.

## ADR

- **Chosen:** Next.js App Router for a prospective authenticated SaaS platform, React client components for browser-only demo state. This starter deliberately does *not* implement authentication, database access, payments, or server actions.
- **UI:** authored UI with accessible semantic controls; no claim that shadcn CLI was run. shadcn/ui could be adopted in a real app after evaluating components and design tokens.
- **Package:** standalone app, no premature shared UI workspace.
- **Feature:** operational incidents and on-demand insights are separate components.
- **Chunk:** `MetricsPanel` only mounts and imports after the user selects Load breakdown.
- **Assets:** no external icons, images, or media.
- **Fallback:** semantically meaningful table, search empty state, labels and keyboard focus.
- **Testing:** Node tests for pure filter/aggregation, TypeScript, production build and HTTP smoke in CI.
- **Performance:** measure LCP/INP/CLS and chunk sizes on a real deployment before committing to numerical budgets.

Official docs: https://nextjs.org/docs ; https://ui.shadcn.com/docs
