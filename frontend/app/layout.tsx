import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CatalogIA",
  description: "Bootstrap frontend for CatalogIA",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        <div className="page">
          <header className="header">
            <h1>CatalogIA</h1>
            <p>Precatalogacion asistida por IA</p>
          </header>
          <main className="main">{children}</main>
          <footer className="footer">
            <span>Biblioteca Nacional de Colombia</span>
          </footer>
        </div>
      </body>
    </html>
  );
}