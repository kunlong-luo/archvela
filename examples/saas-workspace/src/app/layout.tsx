import type { ReactNode } from "react";
import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Orbit Desk — Archvela SaaS Example",
  description: "Offline sample dashboard for exploring accessible incident workflows.",
  robots: { index: false, follow: false }
};

export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
