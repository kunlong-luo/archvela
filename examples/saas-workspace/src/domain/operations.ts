export type Status = "new" | "investigating" | "resolved";
export type Severity = "critical" | "warning" | "info";
export type Incident = {
  id: string; title: string; service: string; status: Status; severity: Severity;
  minutesAgo: number; owner: string;
};

export const seedIncidents: Incident[] = [
  { id: "OPS-1042", title: "Telemetry backlog increased", service: "Stream Hub", status: "new", severity: "critical", minutesAgo: 12, owner: "M. Chen" },
  { id: "OPS-1041", title: "Edge node reconnecting", service: "Edge Network", status: "investigating", severity: "warning", minutesAgo: 28, owner: "S. Lin" },
  { id: "OPS-1040", title: "Export queue recovered", service: "Reports API", status: "resolved", severity: "info", minutesAgo: 44, owner: "A. Zhou" },
  { id: "OPS-1039", title: "High memory on worker", service: "Compute", status: "new", severity: "warning", minutesAgo: 67, owner: "M. Chen" },
  { id: "OPS-1038", title: "Connection retry storm", service: "Stream Hub", status: "investigating", severity: "critical", minutesAgo: 108, owner: "S. Lin" },
  { id: "OPS-1037", title: "Scheduled backup complete", service: "Storage", status: "resolved", severity: "info", minutesAgo: 165, owner: "A. Zhou" }
];

export function filterIncidents(items: readonly Incident[], query: string, status: Status | "all"): Incident[] {
  const text = query.trim().toLocaleLowerCase();
  return items.filter(item =>
    (status === "all" || item.status === status) &&
    (!text || [item.id, item.title, item.service, item.owner].some(s => s.toLocaleLowerCase().includes(text))));
}

export function summarizeIncidents(items: readonly Incident[]) {
  return {
    total: items.length,
    open: items.filter(x => x.status !== "resolved").length,
    critical: items.filter(x => x.severity === "critical" && x.status !== "resolved").length,
    resolved: items.filter(x => x.status === "resolved").length
  };
}
