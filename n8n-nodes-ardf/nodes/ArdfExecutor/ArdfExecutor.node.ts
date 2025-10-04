import axios, { AxiosError } from 'axios';
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

type ResourceType = 'tool' | 'prompt' | 'workflow' | 'model' | 'document' | 'policy' | 'dataset' | 'connector' | 'custom';
type ExecutionMode = 'auto' | 'sync' | 'async';

type SupportedExecutionType = 'tool' | 'prompt' | 'workflow' | 'model';

const SUPPORTED_TYPES: SupportedExecutionType[] = ['tool', 'prompt', 'workflow', 'model'];

const resolveResourceType = (preferred: string, fallback?: string): SupportedExecutionType => {
  const normalizedPreferred = preferred.trim().toLowerCase();
  const normalizedFallback = fallback?.trim().toLowerCase();

  if (normalizedPreferred && normalizedPreferred !== 'auto') {
    if (SUPPORTED_TYPES.includes(normalizedPreferred as SupportedExecutionType)) {
      return normalizedPreferred as SupportedExecutionType;
    }
    throw new Error(Unsupported resource type: );
  }

  if (normalizedFallback && SUPPORTED_TYPES.includes(normalizedFallback as SupportedExecutionType)) {
    return normalizedFallback as SupportedExecutionType;
  }

  // Default to tool if nothing else is provided.
  return 'tool';
};

const normaliseBaseUrl = (baseUrl: string): string => baseUrl.replace(/\/$/, '');

const buildEndpoint = (baseUrl: string, type: SupportedExecutionType): string => {
  const normalised = normaliseBaseUrl(baseUrl);
  switch (type) {
    case 'tool':
      return ${normalised}/tools/call;
    case 'prompt':
      return ${normalised}/prompts/call;
    case 'workflow':
      return ${normalised}/workflows/call;
    case 'model':
      return ${normalised}/models/call;
    default:
      throw new Error(Unsupported execution type: );
  }
};

export class ArdfExecutor implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ARDF Executor Node',
    name: 'ardfExecutor',
    icon: 'fa:rocket',
    group: ['transform'],
    version: 1,
    description: 'Executes ARDF resources (tools, prompts, workflows, models) via MCP server endpoints.',
    defaults: { name: 'ARDF Executor' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'MCP Base URL',
        name: 'mcpBaseUrl',
        type: 'string',
        default: 'http://localhost:8000',
        description: 'Base URL of the ARDF MCP server.',
        required: true,
      },
      {
        displayName: 'Resource ID',
        name: 'resourceId',
        type: 'string',
        default: '',
        description: 'ID of the resource to execute. Leave empty to use the incoming item value.',
      },
      {
        displayName: 'Resource Type',
        name: 'resourceType',
        type: 'options',
        default: 'auto',
        options: [
          { name: 'Auto (from input)', value: 'auto' },
          { name: 'Tool', value: 'tool' },
          { name: 'Prompt', value: 'prompt' },
          { name: 'Workflow', value: 'workflow' },
          { name: 'Model', value: 'model' },
        ],
        description: 'Type of the resource to execute. When set to Auto, the node will infer it from the incoming item.',
      },
      {
        displayName: 'Execution Mode',
        name: 'execMode',
        type: 'options',
        default: 'auto',
        options: [
          { name: 'Auto-detect', value: 'auto' },
          { name: 'Force synchronous', value: 'sync' },
          { name: 'Force asynchronous', value: 'async' },
        ],
        description: 'Hint for how the MCP server should run the resource.',
      },
      {
        displayName: 'Input Parameters (JSON)',
        name: 'inputs',
        type: 'json',
        default: {},
        description: 'Inputs or context required by the resource (depends on its schema).',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
      const mcpBaseUrl = (this.getNodeParameter('mcpBaseUrl', itemIndex) as string).trim();
      let resourceId = (this.getNodeParameter('resourceId', itemIndex) as string).trim();
      const configuredType = this.getNodeParameter('resourceType', itemIndex) as string;
      const execMode = this.getNodeParameter('execMode', itemIndex) as ExecutionMode;
      const rawInputs = this.getNodeParameter('inputs', itemIndex, {}) as unknown;

      const incoming = items[itemIndex].json as Record<string, unknown>;

      if (!resourceId) {
        const incomingId = incoming.resource_id ?? incoming.resourceId;
        if (typeof incomingId === 'string' && incomingId.trim()) {
          resourceId = incomingId.trim();
        }
      }

      if (!resourceId) {
        throw new NodeOperationError(this.getNode(), 'Resource ID is required but could not be determined from input.', {
          itemIndex,
        });
      }

      const incomingType = typeof incoming.resource_type === 'string'
        ? incoming.resource_type
        : typeof incoming.resourceType === 'string'
        ? incoming.resourceType
        : undefined;

      let executionType: SupportedExecutionType;
      try {
        executionType = resolveResourceType(configuredType, incomingType);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        throw new NodeOperationError(this.getNode(), message, { itemIndex });
      }

      const endpoint = buildEndpoint(mcpBaseUrl, executionType);

      const inputs = ((): Record<string, unknown> => {
        if (rawInputs && typeof rawInputs === 'object' && !Array.isArray(rawInputs)) {
          return rawInputs as Record<string, unknown>;
        }
        if (incoming && typeof incoming === 'object') {
          return incoming;
        }
        return {};
      })();

      const payload: Record<string, unknown> = {
        resource_id: resourceId,
        inputs,
        mode: execMode,
      };

      try {
        const response = await axios.post(endpoint, payload, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 30_000,
        });

        returnData.push({
          json: {
            resource_id: resourceId,
            resource_type: executionType,
            endpoint,
            result: response.data ?? null,
          },
        });
      } catch (error) {
        const message = error instanceof AxiosError ? error.message : 'Unknown error';
        throw new NodeOperationError(
          this.getNode(),
          Execution failed for resource '' (): ,
          { itemIndex },
        );
      }
    }

    return [returnData];
  }
}
