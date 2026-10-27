# Home Digital Twin · V3-26 (concept demo)

A real runnable React 19 + Vite 8 + React Three Fiber 9 example. Static SVG plan ships first; WebGL engine downloads only when the visitor explicitly requests **三维**. Floor selection, view rotation and geometry selection operate on real components.

## Critical source-of-truth boundary

**Confirmed inputs only:** 15 × 14 m plot (210 m²), H1 house footprint 11.20 × 8.40 m (94.08 m²).

**Not confirmed:** H1 placement within plot, exact floor/wall heights, internal walls, doors/windows, material specifications and separate heavy kitchen location. The plan **centers the house solely for scale demonstration**, and the 3D uses **2.8 m illustrative floor height**. **Neither is a survey, architectural drawing, construction plan, BIM nor real device integration**.

The separate kitchen is deliberately *not* drawn in the yard because its required 1.5 m separation plus rectangular dimension cannot be safely fit without authoritative site geometry.

## Run

```bash
npm install
npm run dev
npm run test
npm run typecheck
npm run build
```

Visit the Vite URL, usually `http://localhost:5173`. Node 24 recommended.

## ADR and loading boundaries

- **Chosen:** Vite + React for a viewer app, R3F + Three for precise geometry primitives. An authoritative BIM/glTF import must await survey verification.
- **Alternative:** CesiumJS is appropriate for larger georeferenced farm/GIS visualizations, not necessary inside this one-house Canvas. Babylon.js is unnecessary for this viewer.
- **Package:** standalone app; no forced cross-app shared package.
- **Feature:** fixed-size 2D proportional plan vs lazy 3D viewer, and a pure geometry domain.
- **Chunk:** `React.lazy(import('./components/HouseScene'))`, so R3F/Three are isolated from the initial SVG view.
- **Asset Pack:** no GLB/tiles/video; purely generated geometry, no license ambiguity.
- **Fallback:** static SVG persists even on WebGL-disabled browsers; no continuous animation; focus/labels provided.
- **Quality:** typecheck, pure geometry tests, production build, HTTP smoke in CI. Actual FPS/memory/mobile GPU checks remain unverified.

Official docs: https://r3f.docs.pmnd.rs/getting-started/installation ; https://vite.dev/guide/
