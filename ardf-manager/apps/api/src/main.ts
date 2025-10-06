import express from 'express';
import cors from 'cors';
import { db } from '@ardf/database';
import { McpManager } from '@ardf/mcp';
import { HybridRanker } from '@ardf/search';
import { resolveEmbeddingProvider } from './embedding';

export const app = express();
const embeddingProvider = resolveEmbeddingProvider(process.env, { logger: console });
const ranker = new HybridRanker(embeddingProvider);
app.use(cors());
app.use(express.json());

const normalizeTags = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map((entry) => String(entry).trim()).filter(Boolean);
  }
  if (typeof value === 'string') {
    return value
      .split(',')
      .map((entry) => entry.trim())
      .filter(Boolean);
  }
  return [];
};

const toRecord = (value: unknown): Record<string, unknown> | null => {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
};

const toStringOrNull = (value: unknown): string | null => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  return null;
};

const getMetadataValue = (metadata: Record<string, unknown> | null, key: string): unknown => {
  if (!metadata) {
    return undefined;
  }
  return metadata[key];
};

app.get('/health', (_req, res) => {
  try {
    db.listSources();
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ status: 'error', message: 'database error', error: String(error) });
  }
});

app.get('/api/mcp/sources', (_req, res) => {
  res.json({ sources: db.listSources() });
});

app.get('/api/catalog/resources', (req, res) => {
  const { type, q, limit } = req.query;
  const result = db.listResources({
    type: type ? String(type) : undefined,
    query: q ? String(q) : undefined,
    limit: limit ? Number(limit) : undefined,
  });
  res.json(result);
});

app.post('/api/mcp/sync', async (req, res) => {
  const { baseUrl, apiKey, label, sourceId } = req.body ?? {};
  if (!baseUrl) {
    return res.status(400).json({ message: 'baseUrl is required' });
  }
  try {
    const manager = new McpManager({
      id: sourceId ?? baseUrl,
      baseUrl,
      apiKey,
      label,
    });
    const sync = await manager.syncCatalog();
    let resourcesSynced = 0;

    if (Array.isArray(sync.resources)) {
      for (const resource of sync.resources) {
        if (!resource || !resource.resource_id || !resource.resource_type) {
          continue;
        }
        const metadata = toRecord((resource as any).metadata);
        const content = toRecord((resource as any).content);
        const tags = normalizeTags(getMetadataValue(metadata, 'tags') ?? (resource as any)?.tags);

        db.upsertResource({
          resourceId: resource.resource_id,
          resourceType: resource.resource_type,
          description: resource.description ?? resource.title ?? resource.name ?? 'No description',
          whenToUse: resource.when_to_use ?? null,
          metadata,
          content,
          tags,
          domain: toStringOrNull(getMetadataValue(metadata, 'domain')),
          status: resource.status ?? 'published',
          version:
            toStringOrNull((resource as any)?.schema_version) ??
            toStringOrNull(getMetadataValue(metadata, 'version')) ??
            '1.0.0',
        });
        resourcesSynced += 1;
      }
    }

    db.recordSourceSync(manager.source.id, manager.source.baseUrl, manager.source.label);
    res.json({ status: 'ok', synced: { resources: resourcesSynced } });
  } catch (error) {
    res.status(500).json({ message: 'sync failed', error: String(error) });
  }
});

app.post('/api/recommend', async (req, res) => {
  const { query, type, limit = 10 } = req.body ?? {};
  if (!query || typeof query !== 'string') {
    return res.status(400).json({ message: 'query is required' });
  }

  const candidates = db.listResources({ type: type ? String(type) : undefined, query: undefined, limit: 200 });
  const ranked = await ranker.rank(query, candidates.resources, { limit });
  res.json({
    totalCandidates: candidates.total,
    recommended: ranked.map((entry) => ({
      resource: entry.item,
      score: entry.score,
      lexical: entry.lexical,
      semantic: entry.semantic,
    })),
  });
});

app.post('/api/catalog/resources', (req, res) => {
  const payload = req.body ?? {};
  if (!payload.resource_id || !payload.resource_type || !payload.description) {
    return res.status(400).json({ message: 'resource_id, resource_type and description are required' });
  }

  const metadata = toRecord(payload.metadata);
  const content = toRecord(payload.content);
  const resource = db.upsertResource({
    resourceId: payload.resource_id,
    resourceType: payload.resource_type,
    description: payload.description,
    whenToUse: payload.when_to_use,
    metadata,
    content,
    tags: Array.isArray(payload.tags)
      ? payload.tags.map((tag: unknown) => String(tag))
      : normalizeTags(getMetadataValue(metadata, 'tags')),
    domain: toStringOrNull(getMetadataValue(metadata, 'domain')) ?? toStringOrNull(payload.domain),
    status: payload.status ?? 'draft',
    version:
      toStringOrNull(payload.version) ??
      toStringOrNull(getMetadataValue(metadata, 'version')) ??
      '1.0.0',
  });

  res.status(201).json(resource);
});

const port = Number(process.env.PORT ?? 4000);

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`ARDF Manager API listening on port ${port}`);
  });
}

export default app;
