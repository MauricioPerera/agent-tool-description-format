'use client';

import { useQuery } from '@tanstack/react-query';

const fetchResources = async () => {
  const res = await fetch('http://localhost:4000/api/catalog/resources');
  if (!res.ok) {
    throw new Error('Failed to load resources');
  }
  return res.json();
};

export default function HomePage() {
  const { data, isLoading, error } = useQuery({ queryKey: ['resources'], queryFn: fetchResources });

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <section className="max-w-4xl mx-auto space-y-6">
        <header>
          <h1 className="text-3xl font-semibold">ARDF Manager</h1>
          <p className="text-slate-300">Panel inicial para explorar recursos sincronizados desde servidores MCP.</p>
        </header>
        {isLoading && <p>Cargando recursos...</p>}
        {error && <p className="text-red-400">{(error as Error).message}</p>}
        {data && (
          <div className="space-y-2">
            <p className="text-sm text-slate-400">Recursos sincronizados: {data.total ?? data.resources?.length ?? 0}</p>
            <pre className="bg-slate-900 border border-slate-800 rounded p-4 text-xs overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}
      </section>
    </main>
  );
}
