import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./styles.css";

export const metadata: Metadata = {
  title: "Atelier / Product Stories — Archvela Demo",
  description: "A demonstrative cinematic product storytelling website with a lazy 3D preview.",
  robots: { index: false, follow: false }
};

export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
