import { dimensions, disclosure } from "../domain/geometry";

export default function PlanDrawing() {
  const w = dimensions.houseWidthM * 24;
  const h = dimensions.houseDepthM * 24;
  const plotW = dimensions.plotWidthM * 24;
  const plotH = dimensions.plotDepthM * 24;
  return <div className="plan-canvas">
    <svg viewBox="0 0 470 450" role="img" aria-labelledby="plan-title plan-desc" preserveAspectRatio="xMidYMid meet">
      <title id="plan-title">宅基地与主屋平面比例示意</title>
      <desc id="plan-desc">宅基地15米乘14米，主屋11.2米乘8.4米。房屋居中仅为比例展示，并非实际总平位置。</desc>
      <rect x={50} y={54} width={plotW} height={plotH} rx="3" fill="#d5e2d6" stroke="#8aa794" strokeWidth="2"/>
      <g stroke="#9fbaab" strokeDasharray="2 9" opacity=".58">{Array.from({length:7},(_,i)=><line key={i} x1={50+i*54} y1="54" x2={50+i*54} y2={54+plotH}/>)}</g>
      <rect x={50+(plotW-w)/2} y={54+(plotH-h)/2} width={w} height={h} fill="#6d8e85" stroke="#2c514b" strokeWidth="3"/>
      <rect x={50+(plotW-w)/2+9} y={54+(plotH-h)/2+9} width={w-18} height={h-18} fill="none" stroke="#c8d6ce" strokeWidth="2" strokeDasharray="7 8"/>
      <text x="230" y="220" textAnchor="middle" fill="#f6faf5" fontSize="15" fontWeight="700">H1 MAIN HOUSE</text>
      <text x="230" y="242" textAnchor="middle" fill="#f3faf4" fontSize="12">11.20 × 8.40 m</text>
      <text x="230" y="41" textAnchor="middle" fill="#537568" fontSize="12">SITE WIDTH 15.00 m</text>
      <text x="424" y="219" textAnchor="middle" transform="rotate(90 424 219)" fill="#537568" fontSize="12">14.00 m</text>
      <text x="230" y="418" textAnchor="middle" fill="#78918a" fontSize="10">CENTERED FOR SCALE ONLY · NOT AN APPROVED LAYOUT</text>
    </svg>
    <p className="sr-only">{disclosure}</p>
  </div>;
}
