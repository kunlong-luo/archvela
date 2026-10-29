"use client";
import type { Incident } from "@/domain/operations";

export default function MetricsPanel({ incidents }: { incidents: Incident[] }) {
  const services = [...new Set(incidents.map(i => i.service))];
  const counts = services.map(s => ({ service: s, count: incidents.filter(i => i.service === s && i.status !== "resolved").length }));
  const max = Math.max(1, ...counts.map(c => c.count));
  return <section className="analytics-panel" aria-labelledby="analytics-heading">
    <h3 id="analytics-heading">Service distribution</h3><p>Open incidents by service · fictional data</p>
    <div className="bars">{counts.map(row => <div className="bar-row" key={row.service}>
      <span>{row.service}</span><div className="bar-track" aria-hidden><div style={{width: (row.count/max*100) + "%"}} /></div><strong>{row.count}</strong>
    </div>)}</div>
  </section>;
}
