"use client";

import { useEffect, useRef, useState } from "react";

type State = "poster" | "loading" | "interactive" | "unavailable";
export default function ProductShowcase() {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [state, setState] = useState<State>("poster");
  const [enabled, setEnabled] = useState(false);
  useEffect(() => {
    if (!enabled || !canvas.current) return;
    let cancelled = false;
    let dispose: (() => void) | undefined;
    import("./three-runtime").then(({ mountScene }) => {
      if (cancelled || !canvas.current) return;
      try {
        dispose = mountScene(canvas.current);
        setState("interactive");
      } catch {
        setState("unavailable");
      }
    }).catch(() => { if (!cancelled) setState("unavailable"); });
    return () => { cancelled = true; dispose?.(); };
  }, [enabled]);
  return <div className="stage">
    <div className="stage-overlay"><span>FORM STUDY — NO.01</span><span>WEBGL LOADED ON REQUEST</span></div>
    {enabled && state !== "unavailable" && <canvas ref={canvas} aria-label="Decorative rotating 3D study" className="stage-canvas"/>}
    {!enabled && <div className="stage-poster" aria-hidden="true"><div className="poster-shape"><span/></div></div>}
    {state === "unavailable" && <div className="stage-fallback" role="status">3D is unavailable on this device. The product story remains accessible.</div>}
    <div className="stage-bottom"><div><strong>Form meets clarity.</strong><span>Procedural preview · no asset download until requested</span></div>
      {enabled ? <button type="button" className="stage-button" onClick={() => { setEnabled(false); setState("poster"); }}>Close preview</button> :
        <button type="button" className="stage-button" onClick={() => { setState("loading"); setEnabled(true); }}>Explore in 3D <span aria-hidden>↗</span></button>}
      {state === "loading" && <span className="sr-only" role="status">Loading interactive scene</span>}
    </div>
  </div>;
}
