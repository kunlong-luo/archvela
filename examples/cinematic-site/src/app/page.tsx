import ProductShowcase from "@/components/ProductShowcase";

const features = [
  { id: "01", title: "Editorial hierarchy", description: "A clear message renders before optional interaction." },
  { id: "02", title: "Progressive immersion", description: "The 3D runtime is downloaded only when someone opens it." },
  { id: "03", title: "Accessible fallback", description: "Static copy and the product story remain available without WebGL." }
];

export default function Home() {
  return <main>
    <header className="topbar shell">
      <a className="wordmark" href="#top" aria-label="Atelier home">ATELIER<span className="wordmark-dot">.</span></a>
      <nav aria-label="Primary navigation"><a href="#approach">Approach</a><a href="#work">Experience</a><a href="#about">About</a></nav>
      <a className="nav-cta" href="#work">See the study <span aria-hidden>↗</span></a>
    </header>
    <section className="hero shell" id="top">
      <div className="eyebrow"><span className="status-dot"/> Architecture by Archvela · Demo 01</div>
      <div className="hero-row">
        <h1>Design that<br/><span>moves with</span><br/>purpose.</h1>
        <div className="hero-aside"><p>A fictional product narrative, built to demonstrate intentional motion, thoughtful loading, and a memorable first impression.</p><a href="#work" className="text-link">Explore the interactive study <span aria-hidden>↘</span></a></div>
      </div>
      <div className="hero-footer"><span>FEATURED STUDY / 2026</span><span>01 — 03</span><span>SCROLL TO EXPLORE ↓</span></div>
    </section>
    <section className="statement" id="approach"><div className="shell statement-inner"><p className="section-index">01 / POINT OF VIEW</p><h2>Built for the first <em>meaningful</em> interaction, not the first megabyte downloaded.</h2><p>Content first. Rich media on demand. A distinct design language without an oversized default bundle.</p></div></section>
    <section className="showcase shell" id="work">
      <div className="section-title"><span>02 / SELECTED EXPERIENCE</span><span>ONE PRODUCT, ONE PURPOSE</span></div>
      <div className="showcase-heading"><h2>The object<br/>of attention.</h2><p>Inspect a procedural sculpture built from simple geometry. This is an original demonstration, not a real commercial product.</p></div>
      <ProductShowcase/>
      <div className="feature-grid">{features.map(feature=><article key={feature.id}><span>{feature.id}</span><h3>{feature.title}</h3><p>{feature.description}</p></article>)}</div>
    </section>
    <footer className="footer shell" id="about"><div><strong>Make the<br/>essential vivid.</strong><p>An architecture reference, not a live sales funnel.</p></div><div className="footer-meta"><span>Archvela / V3-02</span><span>No analytics · No external images · No tracking</span><a href="#top">Back to top ↑</a></div></footer>
  </main>;
}
