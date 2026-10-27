import OperationsBoard from "@/components/OperationsBoard";

export default function Home() {
  return <div className="app">
    <aside className="sidebar">
      <a className="brand" href="#overview"><span className="brand-icon">◈</span><span>orbit<span className="brand-light">desk</span></span></a>
      <div className="workspace-title">WORKSPACE <span>↗</span></div>
      <nav aria-label="Workspace navigation">
        <a className="active" href="#overview"><span aria-hidden>▦</span> Overview</a>
        <a href="#incidents"><span aria-hidden>◉</span> Incidents</a>
        <a href="#insights"><span aria-hidden>⌁</span> Insights</a>
      </nav>
      <div className="sidebar-bottom"><div className="avatar">AD</div><div><strong>Archvela demo</strong><small>Local, simulated data</small></div></div>
    </aside>
    <div className="main">
      <header className="toolbar"><div>Workspace / <strong>Overview</strong></div><span className="demo-mode">● DEMO DATA · NO BACKEND</span></header>
      <main id="overview" className="content">
        <div className="page-intro"><div className="tag">OPERATIONAL OVERVIEW / 2026</div><h1>Good afternoon <span className="hand" aria-hidden>✳</span></h1><p>Your operational picture, clearly organized. All items below are fictional and stay in browser memory.</p></div>
        <OperationsBoard />
        <footer className="app-footer">Archvela · V3-14 / no production systems, authentication or data transfer connected.</footer>
      </main>
    </div>
  </div>;
}
