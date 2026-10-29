# Cinematic Product Site · V3-02

A runnable high-end marketing homepage with editorial layout, SSR content, and a **user-triggered, lazy-loaded Three.js procedural study**. The product narrative is explicitly fictional; no fake contact form, real customer outcomes, tracking, third-party images or credentials.

## Run

```bash
npm install
npm run dev
npm run build
npm run typecheck
```

Node 24 recommended. Browse `http://localhost:3000`. Production: `npm run start` after a build.

## ADR

- **Chosen:** Next.js 16 App Router / React 19 for SEO content and isolated interactive UI; handcrafted CSS for a coherent original visual signature.
- **Alternative:** Astro is more appropriate for a primarily static brochure site; here Next.js is intentional to show a heavier interactive 3D product-view route.
- **Package:** standalone example; no shared app package.
- **Feature:** editorial story / 3D showcase.
- **Chunk:** `three-runtime.ts` downloads only after user selects Explore in 3D.
- **Asset Pack:** no remote images/models/videos; procedural demo geometry and a CSS static poster.
- **Fallback:** browser without WebGL sees a readable poster/status; reduced-motion stops automatic rotation; text and navigation work without canvas.
- **Quality:** build and typecheck in CI, HTTP HTML smoke; validate WebGL, mobile, keyboard and real LCP/INP/CLS manually before production.
- **Safety:** robots noindex; demo is not a production commerce site.

Official docs: https://nextjs.org/docs ; https://threejs.org/docs/
