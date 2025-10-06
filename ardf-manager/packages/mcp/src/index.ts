import type { McpCatalogResult, McpSource, McpSyncResult } from './types';

export * from './types';

export interface McpEndpointConfig {
  id: string;
  baseUrl: string;
  apiKey?: string;
  label?: string;
}

export class McpManager {
  constructor(private readonly config: McpEndpointConfig) {}

  private async fetchJson(path: string): Promise<any> {
    const url = new URL(path, this.config.baseUrl).toString();
    const res = await fetch(url, {
      headers: this.config.apiKey ? { Authorization: `Bearer ${this.config.apiKey}` } : undefined,
    });
    if (!res.ok) {
      throw new Error(`MCP request failed ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async syncCatalog(): Promise<McpSyncResult> {
    const [tools, prompts, resources] = await Promise.all([
      this.fetchOptional('/tools').then((data) => data?.tools ?? data ?? []).catch(() => []),
      this.fetchOptional('/prompts').then((data) => data?.prompts ?? data ?? []).catch(() => []),
      this.fetchOptional('/resources').then((data) => data?.resources ?? data ?? []).catch(() => []),
    ]);

    return { tools, prompts, resources };
  }

  async listResources(type?: string): Promise<McpCatalogResult> {
    const query = type ? `?type=${encodeURIComponent(type)}` : '';
    const resources = await this.fetchOptional(`/resources${query}`).then((data) => data?.resources ?? data ?? []);
    return { resources };
  }

  private async fetchOptional(path: string): Promise<any> {
    try {
      return await this.fetchJson(path);
    } catch {
      return [];
    }
  }

  get source(): McpSource {
    return {
      id: this.config.id,
      baseUrl: this.config.baseUrl,
      label: this.config.label ?? this.config.baseUrl,
      lastSyncAt: new Date().toISOString(),
    };
  }
}
