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

const RESOURCES_ENDPOINT = 'http://localhost:4000/api/catalog/resources';
const RECOMMEND_ENDPOINT = 'http://localhost:4000/api/recommend';

const fetchResources = async (): Promise<ResourcesResponse> => {
  const res = await fetch(RESOURCES_ENDPOINT);
  if (!res.ok) {
    throw new Error('No fue posible cargar los recursos. Intenta nuevamente.');
  }
  return res.json();
};

const recommendResources = async (payload: { query: string; type?: string; limit?: number }) => {
  const res = await fetch(RECOMMEND_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'No fue posible calcular la recomendación.');
  }
  return res.json() as Promise<{
    recommended: Array<{ resource: Resource; score: number; lexical?: number; semantic?: number }>;
    totalCandidates: number;
  }>;
};

const dateTimeFormatter = new Intl.DateTimeFormat('es-ES', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

export default function HomePage() {
  const { data, isLoading, error } = useQuery({ queryKey: ['resources'], queryFn: fetchResources });
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [limit, setLimit] = useState(5);

  const recommendMutation = useMutation({
    mutationFn: recommendResources,
  });

  const rows = useMemo(() => data?.resources ?? [], [data]);
  const uniqueTypes = useMemo(() => {
    const set = new Set(rows.map((resource) => resource.resourceType));
    return Array.from(set).sort();
  }, [rows]);
  const lastUpdated = useMemo(() => {
    if (!rows.length) return null;
    const timestamps = rows.map((resource) => new Date(resource.updatedAt).getTime());
    return new Date(Math.max(...timestamps));
  }, [rows]);

  const recommended = recommendMutation.data?.recommended ?? [];
  const totalCandidates = recommendMutation.data?.totalCandidates ?? 0;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) {
      recommendMutation.reset();
      return;
    }
    recommendMutation.mutate({ query, type: typeFilter || undefined, limit });
  };

  const handleClear = () => {
    setQuery('');
    setTypeFilter('');
    setLimit(5);
    recommendMutation.reset();
  };

  const handleLimitChange = (value: string) => {
    const parsed = Number(value);
    if (Number.isNaN(parsed)) {
      setLimit(1);
      return;
    }
    setLimit(Math.max(1, Math.min(20, parsed)));
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_#1d4ed8_0%,_transparent_55%)] opacity-40" />
      <section id="recomendacion" className="relative mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-10 lg:flex-row lg:pt-16">
        <div className="flex w-full flex-col gap-8 lg:w-2/5">
          <header className="space-y-4 rounded-2xl border border-slate-800/60 bg-slate-900/70 p-6 shadow-lg shadow-slate-900/30 backdrop-blur">
            <span className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" aria-hidden />
              Servidor ARDF activo
            </span>
            <div className="space-y-2">
              <h1 className="text-3xl font-semibold lg:text-4xl">ARDF Manager</h1>
              <p className="text-sm text-slate-300">
                Explora, filtra y encuentra rápidamente recursos ARDF sincronizados desde endpoints MCP.
                Utilizamos un ranking híbrido (léxico + semántico) alimentado por el endpoint <code className="rounded bg-slate-800 px-1.5 py-0.5 text-xs">/api/recommend</code>.
              </p>
            </div>
            <dl className="grid gap-4 rounded-xl border border-slate-800/60 bg-slate-950/70 p-4 text-sm">
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Recursos sincronizados</dt>
                <dd className="text-lg font-semibold text-slate-100">{rows.length}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Tipos detectados</dt>
                <dd className="text-sm text-slate-100">{uniqueTypes.length ? uniqueTypes.join(', ') : '-'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-slate-400">Última actualización</dt>
                <dd className="text-sm text-slate-100">{lastUpdated ? dateTimeFormatter.format(lastUpdated) : '-'}</dd>
              </div>
            </dl>
          </header>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-2xl border border-slate-800/60 bg-slate-900/70 p-6 shadow-lg shadow-slate-900/30 backdrop-blur">
            <div className="grid gap-1">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-400" htmlFor="intent">
                Intento o necesidad del cliente
              </label>
              <textarea
                id="intent"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ej. reservar cita médica"
                rows={3}
                className="resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 shadow-inner shadow-slate-950 focus:border-sky-500 focus:outline-none focus:ring focus:ring-sky-500/30"
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="grid gap-1">
                <label className="text-xs font-medium uppercase tracking-wide text-slate-400" htmlFor="type">
                  Tipo de recurso
                </label>
                <select
                  id="type"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none focus:ring focus:ring-sky-500/30"
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
                <label className="text-xs font-medium uppercase tracking-wide text-slate-400" htmlFor="limit">
                  Top N resultados
                </label>
                <input
                  id="limit"
                  type="number"
                  min={1}
                  max={20}
                  value={limit}
                  onChange={(e) => handleLimitChange(e.target.value)}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none focus:ring focus:ring-sky-500/30"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                className="inline-flex items-center gap-2 rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-500 focus:outline-none focus:ring focus:ring-sky-500/40"
              >
                {recommendMutation.isPending ? 'Calculando...' : 'Calcular recomendación'}
              </button>
              <button
                type="button"
                onClick={handleClear}
                className="text-sm text-slate-400 transition hover:text-slate-200"
              >
                Limpiar campos
              </button>
            </div>

            {recommendMutation.isError && (
              <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300" role="alert">
                {(recommendMutation.error as Error).message}
              </p>
            )}

            {recommended.length > 0 && (
              <div className="space-y-4 rounded-xl border border-slate-800/70 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-slate-100">Ranking sugerido</h2>
                  <span className="text-xs uppercase tracking-wide text-slate-400">{totalCandidates} candidatos</span>
                </div>
                <ul className="space-y-3">
                  {recommended.map((entry, index) => (
                    <li key={entry.resource.resourceId} className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div className="space-y-1">
                          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                            <span className="flex h-5 w-5 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-[11px] font-bold text-slate-200">
                              {index + 1}
                            </span>
                            {entry.resource.resourceId}
                          </p>
                          <p className="text-sm text-slate-100">{entry.resource.description}</p>
                          <div className="flex flex-wrap gap-2 text-xs text-slate-400">
                            <span className="rounded-full border border-slate-700 px-2 py-0.5 text-slate-300">
                              {entry.resource.resourceType}
                            </span>
                            {entry.resource.tags?.map((tag) => (
                              <span key={tag} className="rounded-full border border-slate-800 px-2 py-0.5 text-slate-400">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        </div>
                        <dl className="grid w-full max-w-[180px] grid-cols-2 gap-2 text-xs text-slate-300">
                          <div className="rounded border border-slate-800/70 bg-slate-950/60 px-2 py-1.5 text-center">
                            <dt className="text-[10px] uppercase tracking-wide text-slate-500">Score</dt>
                            <dd className="text-sm font-semibold text-slate-100">{entry.score.toFixed(2)}</dd>
                          </div>
                          <div className="rounded border border-slate-800/70 bg-slate-950/60 px-2 py-1.5 text-center">
                            <dt className="text-[10px] uppercase tracking-wide text-slate-500">Léxico</dt>
                            <dd className="text-sm font-semibold text-slate-100">{(entry.lexical ?? 0).toFixed(2)}</dd>
                          </div>
                          <div className="rounded border border-slate-800/70 bg-slate-950/60 px-2 py-1.5 text-center">
                            <dt className="text-[10px] uppercase tracking-wide text-slate-500">Semántico</dt>
                            <dd className="text-sm font-semibold text-slate-100">{(entry.semantic ?? 0).toFixed(2)}</dd>
                          </div>
                          <div className="rounded border border-slate-800/70 bg-slate-950/60 px-2 py-1.5 text-center">
                            <dt className="text-[10px] uppercase tracking-wide text-slate-500">Candidatos</dt>
                            <dd className="text-sm font-semibold text-slate-100">{totalCandidates}</dd>
                          </div>
                        </dl>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </form>
        </div>

        <section id="recursos" className="flex w-full flex-1 flex-col gap-6 rounded-2xl border border-slate-800/60 bg-slate-900/70 p-6 shadow-lg shadow-slate-900/30 backdrop-blur">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold text-slate-100">Recursos sincronizados</h2>
              <p className="text-sm text-slate-400">Listado en tiempo real desde la base local SQLite.</p>
            </div>
            <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
              {rows.length} registros
            </span>
          </header>

          {isLoading && <p className="text-sm text-slate-300">Cargando recursos...</p>}
          {error && <p className="rounded border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300">{(error as Error).message}</p>}

          {!isLoading && rows.length === 0 && !error && (
            <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-300">
              No hay recursos registrados. Ejecuta <code className="rounded bg-slate-800 px-1.5 py-0.5">npm run seed</code> o sincroniza un servidor MCP.
            </div>
          )}

          {rows.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-slate-800/60">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-800 text-sm">
                  <thead className="bg-slate-900 text-left text-slate-300">
                    <tr>
                      <th scope="col" className="px-4 py-3 font-semibold">Recurso</th>
                      <th scope="col" className="px-4 py-3 font-semibold">Descripción</th>
                      <th scope="col" className="px-4 py-3 font-semibold">Etiquetas</th>
                      <th scope="col" className="px-4 py-3 font-semibold">Estado</th>
                      <th scope="col" className="px-4 py-3 font-semibold">Actualizado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900 bg-slate-950/60">
                    {rows.map((resource) => (
                      <tr key={resource.id} className="transition hover:bg-slate-900/60">
                        <td className="px-4 py-3 align-top text-xs">
                          <div className="font-mono text-slate-200">{resource.resourceId}</div>
                          <div className="text-slate-500">{resource.resourceType}</div>
                        </td>
                        <td className="px-4 py-3 align-top text-sm text-slate-200">{resource.description}</td>
                        <td className="px-4 py-3 align-top text-xs text-slate-300">
                          {resource.tags?.length ? resource.tags.join(', ') : '-'}
                        </td>
                        <td className="px-4 py-3 align-top">
                          <span className="inline-flex rounded-full border border-slate-700 bg-slate-900 px-2 py-0.5 text-[11px] uppercase tracking-wide text-slate-200">
                            {resource.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 align-top text-xs text-slate-400">
                          {dateTimeFormatter.format(new Date(resource.updatedAt))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

