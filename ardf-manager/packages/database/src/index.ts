import Database from 'better-sqlite3';
import path from 'path';

export interface CreateResourceInput {
  resourceId: string;
  resourceType: string;
  description: string;
  whenToUse?: string | null;
  metadata?: Record<string, unknown> | null;
  content?: Record<string, unknown> | null;
  tags?: string[];
  domain?: string | null;
  status?: string;
  version?: string;
}

export interface SourceRecord {
  id: string;
  baseUrl: string;
  label: string;
  lastSyncAt: string | null;
}

export interface ResourceRecord {
  id: string;
  resourceId: string;
  resourceType: string;
  description: string;
  whenToUse?: string | null;
  metadata?: Record<string, unknown> | null;
  content?: Record<string, unknown> | null;
  tags: string[];
  domain?: string | null;
  status: string;
  version: string;
  createdAt: string;
  updatedAt: string;
}

const rootDir = path.resolve(__dirname, '..', '..', '..');

const resolveDatabasePath = (): string => {
  const raw = process.env.DATABASE_URL?.trim();
  if (!raw) {
    return path.join(rootDir, 'dev.db');
  }

  if (raw.startsWith('file:')) {
    const filePath = raw.slice('file:'.length);
    return path.isAbsolute(filePath) ? filePath : path.resolve(rootDir, filePath);
  }

  return raw;
};

const dbPath = resolveDatabasePath();
const connection = new Database(dbPath);

connection.pragma('journal_mode = WAL');
connection.exec(`
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  base_url TEXT NOT NULL,
  label TEXT,
  last_sync_at TEXT
);
`);

connection.exec(`
CREATE TABLE IF NOT EXISTS resources (
  id TEXT PRIMARY KEY,
  resource_id TEXT UNIQUE NOT NULL,
  resource_type TEXT NOT NULL,
  description TEXT NOT NULL,
  when_to_use TEXT,
  metadata TEXT,
  content TEXT,
  tags TEXT,
  domain TEXT,
  status TEXT DEFAULT 'draft',
  version TEXT DEFAULT '1.0.0',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
`);

connection.exec(`
CREATE TRIGGER IF NOT EXISTS trg_resources_updated
AFTER UPDATE ON resources
BEGIN
  UPDATE resources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
`);

const serialise = (value: Record<string, unknown> | null): string | null => {
  if (!value || Object.keys(value).length === 0) {
    return null;
  }
  return JSON.stringify(value);
};

const parseJSON = <T>(value: string | null): T | null => {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
};

const serialiseTags = (tags?: string[] | null): string => {
  if (!tags || tags.length === 0) {
    return '';
  }
  return tags.map((tag) => tag.trim()).filter(Boolean).join(',');
};

const parseTags = (value: string | null): string[] => {
  if (!value) {
    return [];
  }
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
};

const selectResourcesStmt = connection.prepare(`
SELECT * FROM resources
WHERE (@type IS NULL OR resource_type = @type)
  AND (
    @query IS NULL
    OR description LIKE @pattern
    OR IFNULL(when_to_use, '') LIKE @pattern
    OR IFNULL(tags, '') LIKE @pattern
  )
ORDER BY updated_at DESC
LIMIT @limit;
`);

const countResourcesStmt = connection.prepare(`
SELECT COUNT(*) as total FROM resources
WHERE (@type IS NULL OR resource_type = @type)
  AND (
    @query IS NULL
    OR description LIKE @pattern
    OR IFNULL(when_to_use, '') LIKE @pattern
    OR IFNULL(tags, '') LIKE @pattern
  );
`);

const listSourcesStmt = connection.prepare('SELECT * FROM sources ORDER BY label ASC');
const insertResourceStmt = connection.prepare(`
INSERT INTO resources (
  id,
  resource_id,
  resource_type,
  description,
  when_to_use,
  metadata,
  content,
  tags,
  domain,
  status,
  version
) VALUES (
  @id,
  @resourceId,
  @resourceType,
  @description,
  @whenToUse,
  @metadata,
  @content,
  @tags,
  @domain,
  @status,
  @version
) ON CONFLICT(resource_id) DO UPDATE SET
  resource_type=excluded.resource_type,
  description=excluded.description,
  when_to_use=excluded.when_to_use,
  metadata=excluded.metadata,
  content=excluded.content,
  tags=excluded.tags,
  domain=excluded.domain,
  status=excluded.status,
  version=excluded.version;
`);

const upsertSourceStmt = connection.prepare(`
INSERT INTO sources (id, base_url, label, last_sync_at)
VALUES (@id, @baseUrl, @label, @lastSyncAt)
ON CONFLICT(id) DO UPDATE SET
  base_url=excluded.base_url,
  label=excluded.label,
  last_sync_at=excluded.last_sync_at;
`);

export const db = {
  upsertResource(input: CreateResourceInput): ResourceRecord {
    const record = {
      id: input.resourceId,
      resourceId: input.resourceId,
      resourceType: input.resourceType,
      description: input.description,
      whenToUse: input.whenToUse ?? null,
      metadata: serialise(input.metadata ?? null),
      content: serialise(input.content ?? null),
      tags: serialiseTags(input.tags ?? null),
      domain: input.domain ?? null,
      status: input.status ?? 'draft',
      version: input.version ?? '1.0.0',
    };

    insertResourceStmt.run(record);
    return this.findByResourceId(input.resourceId)!;
  },

  findByResourceId(resourceId: string): ResourceRecord | null {
    const row = connection.prepare('SELECT * FROM resources WHERE resource_id = ?').get(resourceId);
    return row ? mapRow(row) : null;
  },

  listResources(params: { type?: string | null; query?: string | null; limit?: number }): { resources: ResourceRecord[]; total: number } {
    const limit = Math.min(params.limit ?? 25, 100);
    const pattern = params.query ? `%${params.query}%` : null;

    const resources = selectResourcesStmt.all({
      type: params.type ?? null,
      query: params.query ?? null,
      pattern,
      limit,
    }) as any[];

    const totalRow = countResourcesStmt.get({ type: params.type ?? null, query: params.query ?? null, pattern }) as any;

    return {
      resources: resources.map(mapRow),
      total: Number(totalRow?.total ?? 0),
    };
  },

  recordSourceSync(sourceId: string, baseUrl: string, label?: string) {
    upsertSourceStmt.run({
      id: sourceId,
      baseUrl,
      label: label ?? baseUrl,
      lastSyncAt: new Date().toISOString(),
    });
  },

  listSources() {
    return listSourcesStmt.all().map(mapSource);
  },
};

function mapRow(row: any): ResourceRecord {
  return {
    id: row.id,
    resourceId: row.resource_id,
    resourceType: row.resource_type,
    description: row.description,
    whenToUse: row.when_to_use,
    metadata: parseJSON<Record<string, unknown>>(row.metadata),
    content: parseJSON<Record<string, unknown>>(row.content),
    tags: parseTags(row.tags),
    domain: row.domain,
    status: row.status,
    version: row.version,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function mapSource(row: any): SourceRecord {
  return {
    id: row.id,
    baseUrl: row.base_url,
    label: row.label ?? row.base_url,
    lastSyncAt: row.last_sync_at ?? null,
  };
}

