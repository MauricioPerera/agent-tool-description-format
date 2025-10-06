import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'ARDF Manager',
  description: 'Control panel for ARDF resources',
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang='es'>
      <body className="wp-body">
        <div className="min-h-screen flex">
          <aside className="wp-sidebar border-r border-slate-800/60 p-4">
            <div className="mb-4 text-sm font-semibold">ARDF Manager</div>
            <nav className="wp-nav space-y-1" aria-label="Menú principal">
              <a href="/" className="block rounded px-3 py-2 hover:bg-slate-800/60">Dashboard</a>
              <a href="#recursos" className="block rounded px-3 py-2 hover:bg-slate-800/60">Recursos</a>
              <a href="#recomendacion" className="block rounded px-3 py-2 hover:bg-slate-800/60">Recomendación</a>
              <a href="#configuracion" className="block rounded px-3 py-2 hover:bg-slate-800/60">Configuración</a>
            </nav>
          </aside>
          <main className="flex-1">
            <Providers>{children}</Providers>
          </main>
        </div>
      </body>
    </html>
  );
}
