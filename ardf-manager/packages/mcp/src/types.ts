export interface McpCatalogResult {
  tools?: any[];
  prompts?: any[];
  resources?: any[];
}

export interface McpSyncResult {
  tools: any[];
  prompts: any[];
  resources: any[];
}

export interface McpSource {
  id: string;
  baseUrl: string;
  label?: string;
  lastSyncAt?: string;
}
