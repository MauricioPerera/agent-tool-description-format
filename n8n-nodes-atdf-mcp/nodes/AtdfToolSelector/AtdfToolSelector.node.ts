import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

import axios, { AxiosRequestConfig } from 'axios';

export class AtdfToolSelector implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ATDF Tool Selector',
    name: 'atdfToolSelector',
    icon: 'fa:filter',
    group: ['transform'],
    version: 1,
    description: 'Recommend ATDF tools using the selector service',
    defaults: {
      name: 'ATDF Tool Selector',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'atdfSelectorApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Query',
        name: 'query',
        type: 'string',
        default: '',
        description: 'Natural language description of the task',
        required: true,
      },
      {
        displayName: 'Preferred Language',
        name: 'language',
        type: 'options',
        options: [
          {
            name: 'Auto',
            value: '',
          },
          {
            name: 'English',
            value: 'en',
          },
          {
            name: 'Spanish',
            value: 'es',
          },
          {
            name: 'Portuguese',
            value: 'pt',
          },
        ],
        default: '',
      },
      {
        displayName: 'Top Results',
        name: 'topN',
        type: 'number',
        typeOptions: {
          minValue: 1,
          maxValue: 50,
        },
        default: 5,
        description: 'Number of tools to return',
      },
      {
        displayName: 'Allowed Servers',
        name: 'servers',
        type: 'string',
        default: '',
        description: 'JSON array or comma-separated list of selector server URLs to include',
      },
      {
        displayName: 'Allowed Tool IDs',
        name: 'allowedTools',
        type: 'string',
        default: '',
        description: 'JSON array or comma-separated list of tool IDs to restrict the search to',
      },
      {
        displayName: 'Include Raw Descriptor',
        name: 'includeRaw',
        type: 'boolean',
        default: false,
        description: 'Whether to include the full ATDF descriptor in the output',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    const credentials = await this.getCredentials('atdfSelectorApi');
    const baseUrl = credentials.serverUrl as string;
    const apiKey = credentials.apiKey as string;
    const timeout = (credentials.timeout as number) || 20000;

    const axiosConfig: AxiosRequestConfig = {
      baseURL: baseUrl,
      timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (apiKey) {
      axiosConfig.headers = {
        ...axiosConfig.headers,
        Authorization: `Bearer ${apiKey}`,
      };
    }

    for (let i = 0; i < items.length; i++) {
      try {
        const query = this.getNodeParameter('query', i) as string;
        const topN = this.getNodeParameter('topN', i) as number;
        const includeRaw = this.getNodeParameter('includeRaw', i) as boolean;
        let language = this.getNodeParameter('language', i) as string;
        language = language || undefined;

        const serversParam = this.getNodeParameter('servers', i) as string;
        const allowedToolsParam = this.getNodeParameter('allowedTools', i) as string;

        const body: any = {
          query,
          top_n: topN,
          include_raw: includeRaw,
        };

        if (language) {
          body.language = language;
        }

        const parsedServers = this.parseList(serversParam);
        if (parsedServers) {
          body.servers = parsedServers;
        }

        const parsedTools = this.parseList(allowedToolsParam);
        if (parsedTools) {
          body.allowed_tools = parsedTools;
        }

        const response = await axios.post('/recommend', body, axiosConfig);
        returnData.push({
          json: response.data,
        });
      } catch (error: any) {
        throw new NodeOperationError(this.getNode(), error, { itemIndex: i });
      }
    }

    return [returnData];
  }

  private parseList(value: string): string[] | undefined {
    if (!value) {
      return undefined;
    }

    const trimmed = value.trim();
    if (!trimmed) {
      return undefined;
    }

    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        return parsed.map((entry) => String(entry));
      }
    } catch (error) {
      // fall back to comma-separated parsing
    }

    return trimmed
      .split(',')
      .map((entry) => entry.trim())
      .filter((entry) => entry.length > 0);
  }
}
