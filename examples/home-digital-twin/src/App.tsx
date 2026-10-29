import { lazy, Suspense, useState } from "react";
import { dimensions, disclosure, houseAreaM2, plotAreaM2 } from "./domain/geometry";
import PlanDrawing from "./components/PlanDrawing";

const HouseScene = lazy(() => import("./components/HouseScene"));

function supportsWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}
export default function App(){
  const [view,setView] = useState<"plan"|"model">("plan");
  const [floor,setFloor] = useState<1|2>(1);
  const [angle,setAngle] = useState(0);
  const [selection,setSelection] = useState("请选择主屋构件");
  const [notice,setNotice] = useState("");
  const show3D = () => {
    if (supportsWebGL()) {setView("model");setNotice("");}
    else {setNotice("该浏览器或设备未提供 WebGL，保留平面比例图供查看。");setView("plan");}
  };
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-badge">A</span><span>archvela<span className="muted">/space</span></span></div>
      <div className="side-heading">项目概念原型 <span>V3-26</span></div>
      <div className="project-mini"><div className="mini-icon">⌂</div><div><strong>家庭住宅孪生</strong><small>仅用核定尺寸做比例演示</small></div></div>
      <div className="side-section"><p>SPATIAL LAYERS</p><button className="layer active" type="button" onClick={()=>setView("plan")}><span>▣</span> 宅基地平面 <small>ON</small></button><button className="layer" type="button" onClick={show3D}><span>⬡</span> 主屋三维 <small>{view==="model"?"ON":"LOAD"}</small></button><div className="layer disabled"><span>⌗</span> 附属厨房 <small>未定位</small></div></div>
      <div className="sidebar-note"><strong>尺寸安全提示</strong><p>{disclosure}</p></div>
    </aside>
    <main className="main">
      <header className="header"><div><span>Spatial Projects</span> / House Demonstration</div><div className="pill">● CONCEPT ONLY</div></header>
      <div className="content">
        <div className="page-intro"><div><span className="eyebrow">SPATIAL EXPLORER / 2026</span><h1>住宅空间概览<span className="dot">.</span></h1><p>真实平面尺寸与可选三维结构演示。非施工图、非实测 BIM 模型。</p></div><span className="version">SCENE ID / H1</span></div>
        <div className="stats"><div><span>宅基地面积</span><strong>{plotAreaM2.toFixed(0)} <small>m²</small></strong><small>15.00 × 14.00 m</small></div><div><span>主屋占地示意</span><strong>{houseAreaM2.toFixed(2)} <small>m²</small></strong><small>11.20 × 8.40 m</small></div><div><span>图纸精度</span><strong className="status">概念</strong><small>层高和位置尚未核定</small></div></div>
        <section className="viewer">
          <div className="viewer-toolbar"><div><strong>空间查看器</strong><span>比例保持 / 未定位部分不渲染</span></div><div className="segmented" role="group" aria-label="查看模式"><button type="button" className={view==="plan"?"selected":""} onClick={()=>setView("plan")} aria-pressed={view==="plan"}>平面</button><button type="button" className={view==="model"?"selected":""} onClick={show3D} aria-pressed={view==="model"}>三维</button></div></div>
          <div className="canvas-shell">{view==="plan"?<PlanDrawing/>:<Suspense fallback={<div role="status" className="loading">正在加载三维引擎…</div>}><HouseScene floor={floor} angle={angle} onSelect={setSelection}/></Suspense>}</div>
          <div className="viewer-bottom">{view==="model"?<><div className="floor-switch" role="group" aria-label="演示楼层"><button className={floor===1?"on":""} type="button" onClick={()=>setFloor(1)}>一层</button><button className={floor===2?"on":""} type="button" onClick={()=>setFloor(2)}>二层</button></div><label className="rotation">视角旋转 <input aria-label="视角旋转角度" type="range" min={-180} max={180} value={Math.round(angle*180/Math.PI)} onChange={e=>setAngle(Number(e.target.value)*Math.PI/180)}/></label></>:<span>模型引擎不会在平面模式下载</span>}<span className="scale-note">1 unit = 1 m · 高度仅演示</span></div>
        </section>
        {notice&&<p role="status" className="notice">{notice}</p>}
        <div className="info-grid"><article className="info"><span>01 / GEOMETRY</span><h2>尺寸透明，位置不臆造。</h2><p>主屋平面尺寸来自已知数据。图中居中摆放用于展示比例，实际坐标、门窗与附属厨房位置仍需以获批图纸为准。</p></article><article className="info"><span>02 / INTERACTION</span><h2>{view==="model"?selection:"建筑模型按需载入"}</h2><p>{view==="model"?"点击墙、楼板或屋顶查看构件。模型墙高使用演示值 "+dimensions.demonstrationFloorHeightM+" 米，不能用于施工。":"点击“三维”后才会下载 React Three Fiber 和 Three.js。无 WebGL 时会继续显示平面图。"}</p></article></div>
        <footer>Archvela · V3-26 · 演示数据，无实时物联网连接，无测绘精度声明。</footer>
      </div>
    </main>
  </div>;
}
