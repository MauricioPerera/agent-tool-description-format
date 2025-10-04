import { Client } from '@modelcontextprotocol/sdk';

export interface McpEndpointConfig {
  id: string;
  baseUrl: string;
  apiKey?: string;
  label?: string;
}

export class McpManager {
  constructor(private readonly config: McpEndpointConfig) {}

  private get client(): Client {
    return new Client({ baseUrl: this.config.baseUrl, apiKey: this.config.apiKey });
  }

  async listResources(type?: string) {
    const client = this.client;
    if (type) {
      return client.resources.list({ type });
    }
    return client.resources.list();
  }

  async getResource(resourceId: string) {
    const client = this.client;
    const { resources } = await client.resources.list();
    return resources.find((res) => res.resource_id === resourceId);
  }

  async fetchManifest() {
    const client = this.client;
    return client.manifest.get();
  }
}
