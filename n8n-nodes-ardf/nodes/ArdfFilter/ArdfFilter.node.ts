import axios, { AxiosError } from 'axios';
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

type FilterMode = 'lexical' | 'semantic';

type ResourceType =
  | 'tool'
  | 'prompt'
  | 'workflow'
  | 'document'
  | 'policy'
  | 'model'
  | 'dataset'
  | 'connector'
  | 'custom'
  | string;

interface ArdfMetadata {
  domain?: string;
  tags?: string[];
  [key: string]: unknown;
}

interface ArdfResource {
  resource_id?: string;
  resourceId?: string;
  resource_type?: ResourceType;
  resourceType?: ResourceType;
  description?: string;
  when_to_use?: string;
  whenToUse?: string;
  metadata?: ArdfMetadata;
  content?: Record<string, unknown>;
  [key: string]: unknown;
}

interface SemanticRankingItem {
  id: string;
  score?: number;
}

const toArray = (value: unknown): ArdfResource[] => {
  if (Array.isArray(value)) {
    return value as ArdfResource[];
  }

  if (value && typeof value === 'object') {
    const castValue = value as { resources?: unknown };
    if (Array.isArray(castValue.resources)) {
      return castValue.resources as ArdfResource[];
    }
  }

  return [];
};

const normalizeType = (value?: ResourceType): string => value?.toString().toLowerCase() ?? '';

const buildSearchText = (resource: ArdfResource): string => {
  const parts: string[] = [];

  if (resource.description) {
    parts.push(resource.description);
  }
  if (resource.when_to_use) {
    parts.push(resource.when_to_use);
  }
  if ((resource as { whenToUse?: string }).whenToUse) {
    parts.push((resource as { whenToUse?: string }).whenToUse as string);
  }
  if (Array.isArray(resource.metadata?.tags)) {
    parts.push(resource.metadata?.tags?.join(' ') ?? '');
  }

  return parts.join(' ').toLowerCase();
};

const lexicalScore = (resource: ArdfResource, query: string): number => {
  const text = buildSearchText(resource);
  if (!query) {
    return 0;
  }

  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!tokens.length) {
    return 0;
  }

  return tokens.reduce((score, token) => (text.includes(token) ? score + 1 : score), 0);
};

const mapSemanticScores = (
  resources: ArdfResource[],
  ranking: SemanticRankingItem[],
): ArdfResource[] => {
  const scoreMap = new Map<string, number>();
  ranking.forEach((item) => {
    if (item?.id) {
      scoreMap.set(item.id, item.score ?? 0);
    }
  });

  return resources.map((resource) => {
    const id = resource.resource_id ?? resource.resourceId ?? '';
    return {
      ...resource,
      score: scoreMap.get(id) ?? 0,
    } as ArdfResource & { score: number };
  });
};

export class ArdfFilter implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ARDF Filter Node',
    name: 'ardfFilter',
    icon: 'fa:filter',
    group: ['transform'],
    version: 1,
    description: 'Filter and rank ARDF resources based on user query or intent.',
    defaults: { name: 'ARDF Filter' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'User Query',
        name: 'query',
        type: 'string',
        default: '',
        required: true,
        description: 'Natural language query or user intent.',
      },
      {
        displayName: 'ARDF Source URL',
        name: 'sourceUrl',
        type: 'string',
        default: 'http://localhost:8000/resources',
        description: 'Endpoint to retrieve ARDF resources from an MCP server.',
      },
      {
        displayName: 'Filter Mode',
        name: 'filterMode',
        type: 'options',
        default: 'lexical',
        options: [
          { name: 'Lexical (fast)', value: 'lexical' },
          { name: 'External Embeddings (connector)', value: 'semantic' },
        ],
        description: 'Method used to rank candidate resources.',
      },
      {
        displayName: 'Embedding Connector URL',
        name: 'embeddingConnector',
        type: 'string',
        default: '',
        description: 'Optional endpoint used to compute semantic similarity.',
        displayOptions: {
          show: {
            filterMode: ['semantic'],
          },
        },
      },
      {
        displayName: 'Top N Results',
        name: 'topN',
        type: 'number',
        default: 5,
        description: 'Maximum number of top-ranked resources to return.',
        typeOptions: {
          minValue: 1,
          maxValue: 50,
        },
      },
      {
        displayName: 'Allowed Resource Types',
        name: 'allowedTypes',
        type: 'multiOptions',
        default: ['tool', 'prompt', 'workflow'],
        options: [
          { name: 'Tool', value: 'tool' },
          { name: 'Prompt', value: 'prompt' },
          { name: 'Workflow', value: 'workflow' },
          { name: 'Document', value: 'document' },
          { name: 'Policy', value: 'policy' },
          { name: 'Model', value: 'model' },
          { name: 'Dataset', value: 'dataset' },
          { name: 'Connector', value: 'connector' },
        ],
        description: 'Filter resources by type before ranking.',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
      const query = (this.getNodeParameter('query', itemIndex) as string).trim();
      const sourceUrl = this.getNodeParameter('sourceUrl', itemIndex) as string;
      const filterMode = this.getNodeParameter('filterMode', itemIndex) as FilterMode;
      const embeddingConnector = (this.getNodeParameter('embeddingConnector', itemIndex) as string).trim();
      const topN = this.getNodeParameter('topN', itemIndex) as number;
      const allowedTypes = (this.getNodeParameter('allowedTypes', itemIndex) as string[]).map((type) =>
        type.toLowerCase(),
      );

      let resources: ArdfResource[] = [];

      try {
        const response = await axios.get(sourceUrl);
        resources = toArray(response.data);
      } catch (error) {
        const message = error instanceof AxiosError ? error.message : 'Unknown error';
        throw new NodeOperationError(this.getNode(), Error fetching ARDF resources: , {
          itemIndex,
        });
      }

      if (!resources.length) {
        continue;
      }

      const filtered = resources.filter((resource) => {
        const type = normalizeType(resource.resource_type ?? resource.resourceType);
        if (allowedTypes.length && !allowedTypes.includes(type)) {
          return false;
        }
        return true;
      });

      let ranked: (ArdfResource & { score: number })[];

      if (filterMode === 'semantic' && embeddingConnector) {
        try {
          const payload = {
            query,
            candidates: filtered.map((resource) => ({
              id: resource.resource_id ?? resource.resourceId ?? '',
              text: buildSearchText(resource),
            })),
          };
          const response = await axios.post(${embeddingConnector.replace(/\/?$/, '')}/rank, payload);
          const ranking = Array.isArray(response.data)
            ? (response.data as SemanticRankingItem[])
            : ((response.data?.ranking ?? []) as SemanticRankingItem[]);
          const scored = mapSemanticScores(filtered, ranking);
          ranked = scored
            .map((resource) => ({
              ...resource,
              score: Number.isFinite((resource as { score?: number }).score)
                ? ((resource as { score?: number }).score as number)
                : lexicalScore(resource, query),
            }))
            .sort((a, b) => b.score - a.score);
        } catch (error) {
          const message = error instanceof AxiosError ? error.message : 'Unknown error';
          throw new NodeOperationError(this.getNode(), Semantic ranking failed: , {
            itemIndex,
          });
        }
      } else {
        ranked = filtered
          .map((resource) => ({
            ...resource,
            score: lexicalScore(resource, query),
          }))
          .sort((a, b) => b.score - a.score);
      }

      ranked.slice(0, topN).forEach((resource) => {
        returnData.push({
          json: {
            resource_id: resource.resource_id ?? resource.resourceId ?? null,
            resource_type: resource.resource_type ?? resource.resourceType ?? null,
            description: resource.description ?? null,
            score: resource.score,
            metadata: resource.metadata ?? null,
            content: resource.content ?? null,
          },
        });
      });
    }

    return [returnData];
  }
}
