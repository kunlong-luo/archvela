# Archvela · Runnable Architecture Examples

Three independent, deliberately small front-end prototypes demonstrate how the **V3 scenario → ADR → code → build → acceptance** chain works. The examples are **not** production sites, production SaaS or construction documents.

| Example | V3 scene | Stack | Complete interaction |
|---|---|---|---|
| [cinematic-site](./cinematic-site) | V3-02 | Next 16 / React 19 / lazy Three.js | SEO-ready HTML first; click to load, interact with, then unload original procedural 3D art |
| [saas-workspace](./saas-workspace) | V3-14 | Next 16 / React 19 | Search, filter, select, change status, reset; on-demand chart; fictional in-memory fixtures |
| [home-digital-twin](./home-digital-twin) | V3-26 | Vite 8 / React 19 / R3F 9 | 2D SVG plan first; load 3D on demand; select floor/geometry, rotate; WebGL fallback |

## Getting started

```bash
cd examples/cinematic-site       # or saas-workspace / home-digital-twin
npm ci
npm run dev
npm run build
```

Run `npm run test --if-present` and `npm run typecheck` in each folder. All three examples now include committed `package-lock.json` files; prefer `npm ci` for reproducible local and CI installs. Use Node 24; the CI installs and builds **each project separately**, with no forced workspace or shared packages.

## What is deliberately not done

- No backend/database/auth, real IoT data, order/payment flow or production integrations.
- No paid external API, analytics, remote fonts, image hotlinks or reused branded commercial assets.
- No shadcn/ui generated component library: the SaaS template uses authored accessible UI primitives. The framework integration remains optional and should be validated separately if adopted.
- No CesiumJS/R3F engine mixing: house-scale Three.js is isolated from geographic-scale GIS.
- No claimed measured performance, browser WebGL success or automated agent-model end-to-end accuracy until those are tested.

## Architecture separation

Each demo includes its own ADR and has a distinct theme. Do not extract `packages/ui` simply because two Next.js apps exist; first document true reuse with at least two real consumers and tests.

All demos are illustrative. H1 footprint 11.20 × 8.40 m and plot 15 × 14 m are **dimension inputs**, but actual site placement, heights and construction details have not been verified; the 3D diagram states this clearly.

## Browser E2E

[Playwright browser tests](../tests/browser/README.md) drive **desktop Chromium and a mobile-emulation viewport** through the actual production servers. They cover search, status changes, 3D viewer controls, WebGL-unavailable fallback, and selected mobile layout checks. CI captures screenshots/video/traces on failure. This is not a real-device GPU or accessibility audit.

## CI

[examples.yml](../.github/workflows/examples.yml) runs source-boundary checks, installs packages per directory, runs Node tests where present, typechecks, performs production builds and serves an HTTP smoke page. E2E browser interactivity, mobile graphics performance and production deploy remain separate acceptance tasks.
