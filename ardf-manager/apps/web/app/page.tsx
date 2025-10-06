'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

type Resource = {
  id: string;
  resourceId: string;
  resourceType: string;
  description: string;
  tags: string[];
  status: string;
  updatedAt: string;
};

type ResourcesResponse = {
  resources: Resource[];
  total: number;
};

const fetchResources = async (): Promise<ResourcesResponse> => {
  const res = await fetch('http://localhost:4000/api/catalog/resources');
  if (!res.ok) {
    throw new Error('Failed to load resources');
  }
  return res.json();
};

const recommendResources = async (payload: { query: string; type?: string; limit?: number }) => {
  const res = await fetch('http://localhost:4000/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to get recommendation');
  }
  return res.json() as Promise<{ recommended: Array<{ resource: Resource; score: number; lexical?: number; semantic?: number }>; totalCandidates: number }>;
};

export default function HomePage() {
  const { data, isLoading, error } = useQuery({ queryKey: ['resources'], queryFn: fetchResources });
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [limit, setLimit] = useState(5);

  const recommendMutation = useMutation({
    mutationFn: recommendResources,
  });

  const rows = useMemo(() => data?.resources ?? [], [data]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) {
      recommendMutation.reset();
      return;
    }
    recommendMutation.mutate({ query, type: typeFilter || undefined, limit });
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <section className="max-w-5xl mx-auto space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold">ARDF Manager</h1>
          <p className="text-slate-300">
            Recursos almacenados localmente y ranking híbrido usando el endpoint <code>/api/recommend</code>.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="grid gap-3 rounded border border-slate-800 bg-slate-900/60 p-4">
          <div className="grid gap-1">
            <label className="text-sm text-slate-400" htmlFor="intent">
              Intento o necesidad del cliente
            </label>
            <input
              id="intent"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ej. reservar cita médica"
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:outline-none focus:ring"
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="grid gap-1">
              <label className="text-sm text-slate-400" htmlFor="type">
                Tipo de recurso
              </label>
              <select
                id="type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:outline-none focus:ring"
              >
                <option value="">Todos</option>
                <option value="tool">tool</option>
                <option value="prompt">prompt</option>
                <option value="workflow">workflow</option>
                <option value="document">document</option>
                <option value="policy">policy</option>
                <option value="model">model</option>
              </select>
            </div>
            <div className="grid gap-1">
              <label className="text-sm text-slate-400" htmlFor="limit">
                Top N resultados
              </label>
              <input
                id="limit"
                type="number"
                min={1}
                max={20}
                value={limit}
                onChange={(e) => setLimit(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}
                className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:outline-none focus:ring"
              />
            </div>
          </div>

          <button
            type="submit"
            className="inline-flex w-fit items-center justify-center rounded bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500"
          >
            {recommendMutation.isPending ? 'Calculando…' : 'Calcular recomendación'}
          </button>

          {recommendMutation.isError && (
            <p className="text-sm text-red-400">{(recommendMutation.error as Error).message}</p>
          )}

          {recommendMutation.data && (
            <div className="space-y-2">
              <h2 className="text-lg font-semibold text-slate-200">Ranking sugerido</h2>
              <ul className="space-y-2">
                {recommendMutation.data.recommended.map((entry, index) => (
                  <li key={entry.resource.resourceId} className="rounded border border-slate-800 bg-slate-950 p-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-mono text-xs text-slate-300">
                          #{index + 1} — {entry.resource.resourceId}
                        </p>
                        <p className="text-slate-100">{entry.resource.description}</p>
                      </div>
                      <div className="text-right text-sm text-slate-400">
                        <div>Puntaje: {entry.score.toFixed(2)}</div>
                        {entry.lexical !== undefined && <div>Léxico: {entry.lexical.toFixed(2)}</div>}
                        {entry.semantic !== undefined && <div>Semántico: {entry.semantic.toFixed(2)}</div>}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </form>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-200">Recursos sincronizados ({rows.length})</h2>
          {isLoading && <p>Cargando recursos…</p>}
          {error && <p className="text-red-400">{(error as Error).message}</p>}
          {!isLoading && rows.length === 0 && (
            <p className="text-slate-400">No hay recursos registrados. Ejecuta <code>npm run seed</code> o sincroniza un servidor MCP.</p>
          )}
          {rows.length > 0 && (
            <div className="overflow-hidden rounded border border-slate-800">
              <table className="min-w-full divide-y divide-slate-800 text-sm">
                <thead className="bg-slate-900 text-left text-slate-300">
                  <tr>
                    <th className="px-4 py-3">Recurso</th>
                    <th className="px-4 py-3">Descripción</th>
                    <th className="px-4 py-3">Etiquetas</th>
                    <th className="px-4 py-3">Estado</th>
                    <th className="px-4 py-3">Actualizado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900 bg-slate-950">
                  {rows.map((resource) => (
                    <tr key={resource.id}>
                      <td className="px-4 py-3 font-mono text-xs text-slate-200">
                        <div>{resource.resourceId}</div>
                        <div className="text-slate-500">{resource.resourceType}</div>
                      </td>
                      <td className="px-4 py-3 text-slate-200">{resource.description}</td>
                      <td className="px-4 py-3 text-slate-300">{resource.tags?.join(', ') ?? '-'}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex rounded bg-slate-800 px-2 py-1 text-xs uppercase tracking-wide text-slate-200">
                          {resource.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">
                        {new Date(resource.updatedAt).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
