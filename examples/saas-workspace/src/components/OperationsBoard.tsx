"use client";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { filterIncidents, seedIncidents, summarizeIncidents, type Incident, type Status } from "@/domain/operations";

const MetricsPanel = dynamic(() => import("./MetricsPanel"), { loading: () => <p role="status">Loading insight view…</p> });
const statusLabel: Record<Status, string> = { new: "New", investigating: "Investigating", resolved: "Resolved" };

export default function OperationsBoard() {
  const [items, setItems] = useState<Incident[]>(seedIncidents);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<Status | "all">("all");
  const [selected, setSelected] = useState<string | null>("OPS-1042");
  const [insights, setInsights] = useState(false);
  const stats = useMemo(() => summarizeIncidents(items), [items]);
  const visible = useMemo(() => filterIncidents(items, query, status), [items, query, status]);
  const focus = items.find(x => x.id === selected) ?? null;
  const progress = (id: string) => setItems(old => old.map(item => item.id === id ?
    { ...item, status: item.status === "new" ? "investigating" : "resolved" } : item));
  return <>
    <div className="cards" aria-label="Key indicators">
      <div className="stat-card"><span>Total incidents</span><strong>{stats.total.toString().padStart(2, "0")}</strong><small>Local fixture rows</small><div className="stat-mark">↗</div></div>
      <div className="stat-card"><span>Open issues</span><strong>{stats.open.toString().padStart(2, "0")}</strong><small>New + investigating</small><div className="stat-mark">⌁</div></div>
      <div className="stat-card accent"><span>Critical open</span><strong>{stats.critical.toString().padStart(2, "0")}</strong><small>Sample only · not live</small><div className="stat-mark">!</div></div>
      <div className="stat-card"><span>Resolved</span><strong>{stats.resolved.toString().padStart(2, "0")}</strong><small>Browser-memory state</small><div className="stat-mark">✓</div></div>
    </div>
    <section className="section incidents-section" id="incidents" aria-labelledby="incident-title">
      <div className="section-head"><div><span className="label">MONITOR / 01</span><h2 id="incident-title">Recent incidents</h2></div><button className="ghost-button" onClick={() => {setItems(seedIncidents);setQuery("");setStatus("all");setSelected(null)}} type="button">↻ Reset sample</button></div>
      <div className="filters"><label><span className="sr-only">Search incident records</span><input type="search" placeholder="Search incidents, owners or services" value={query} onChange={e => setQuery(e.target.value)}/></label>
        <label className="filter-label">Status <select value={status} onChange={e => setStatus(e.target.value as Status | "all")}><option value="all">All statuses</option><option value="new">New</option><option value="investigating">Investigating</option><option value="resolved">Resolved</option></select></label>
        <span className="result-count" role="status">{visible.length} result{visible.length===1?"":"s"}</span>
      </div>
      <div className="table-scroll"><table><thead><tr><th>INCIDENT</th><th>SERVICE</th><th>SEVERITY</th><th>STATUS</th><th>OWNER</th><th>ACTION</th></tr></thead>
        <tbody>{visible.map(row => <tr key={row.id} className={selected===row.id?"selected":""}>
          <td><button className="incident-link" onClick={() => setSelected(row.id)} aria-label={"Inspect "+row.id}>{row.id}</button><div className="title-cell">{row.title}</div></td>
          <td>{row.service}</td><td><span className={"sev "+row.severity}>{row.severity}</span></td><td><span className={"status "+row.status}><span aria-hidden>●</span> {statusLabel[row.status]}</span></td><td>{row.owner}</td><td>{row.status === "resolved" ? <span className="done">Done</span> : <button className="table-action" type="button" onClick={() => progress(row.id)}>{row.status === "new" ? "Start" : "Resolve"}</button>}</td>
        </tr>)}</tbody></table>
        {visible.length === 0 && <div className="empty" role="status"><strong>No matching incidents</strong><span>Adjust your search or status filter to see sample records.</span></div>}
      </div>
      <div className="record-detail" aria-live="polite">{focus ? <><span>SELECTED / {focus.id}</span><p><strong>{focus.title}</strong> · {focus.service} · {statusLabel[focus.status]} · {focus.minutesAgo} min ago (fixture timestamp)</p></> : <p>Select an incident ID to inspect its details.</p>}</div>
    </section>
    <section className="section insights-section" id="insights"><div className="section-head"><div><span className="label">ANALYZE / 02</span><h2>On-demand insights</h2></div><button className="solid-button" type="button" aria-expanded={insights} onClick={() => setInsights(v => !v)}>{insights ? "Hide breakdown" : "Load breakdown"} <span aria-hidden>↗</span></button></div>
      {insights ? <MetricsPanel incidents={items}/> : <p className="insight-preview">Detailed breakdown is a separate JS chunk. It loads only when requested.</p>}
    </section>
  </>;
}
