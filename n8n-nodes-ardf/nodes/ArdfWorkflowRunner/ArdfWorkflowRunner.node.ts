import axios, { AxiosError } from 'axios';
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

type ExecutionMode = 'sequential' | 'parallel';

type StepResult = {
  status: 'success' | 'error' | 'skipped';
  step: string;
  output?: unknown;
  error?: string;
};

type WorkflowStep = {
  step: string;
  description?: string;
  tool_id?: string;
  prompt_id?: string;
  workflow_id?: string;
  [key: string]: unknown;
};

const normaliseBaseUrl = (baseUrl: string): string => baseUrl.replace(/\/$/, '');

const fetchWorkflowDescriptor = async (
  baseUrl: string,
  workflowId: string,
): Promise<{ steps: WorkflowStep[]; descriptor: Record<string, unknown> }> => {
  try {
    const response = await axios.get(${normaliseBaseUrl(baseUrl)}/workflows);
    const resources = Array.isArray(response.data?.resources) ? response.data.resources : [];
    const workflow = resources.find((resource: Record<string, unknown>) => resource.resource_id === workflowId);

    if (!workflow) {
      throw new Error(Workflow '' not found.);
    }

    const steps = Array.isArray(workflow?.content?.data?.steps)
      ? (workflow.content.data.steps as WorkflowStep[])
      : [];

    return { steps, descriptor: workflow };
  } catch (error) {
    const message = error instanceof AxiosError ? error.message : 'Unknown error';
    throw new Error(Failed to fetch workflow descriptor: );
  }
};

const determineStepType = (step: WorkflowStep): 'tool' | 'prompt' | 'workflow' | 'unknown' => {
  if (step.tool_id) return 'tool';
  if (step.prompt_id) return 'prompt';
  if (step.workflow_id) return 'workflow';
  return 'unknown';
};

const buildExecutionEndpoint = (baseUrl: string, stepType: 'tool' | 'prompt' | 'workflow') => {
  const normalised = normaliseBaseUrl(baseUrl);
  switch (stepType) {
    case 'tool':
      return ${normalised}/tools/call;
    case 'prompt':
      return ${normalised}/prompts/call;
    case 'workflow':
      return ${normalised}/workflows/call;
    default:
      throw new Error(Unsupported step type ''.);
  }
};

const executeStep = async (
  baseUrl: string,
  step: WorkflowStep,
  context: Record<string, unknown>,
  timeout: number,
): Promise<StepResult> => {
  const stepType = determineStepType(step);

  if (stepType === 'unknown') {
    return { status: 'skipped', step: step.step, error: 'Unsupported step type.' };
  }

  if (stepType === 'workflow') {
    // Nested workflows can be supported recursively in the future.
    return { status: 'skipped', step: step.step, error: 'Nested workflows are not supported yet.' };
  }

  const resourceId = step.tool_id ?? step.prompt_id ?? '';

  if (!resourceId) {
    return { status: 'error', step: step.step, error: 'Missing resource identifier.' };
  }

  const endpoint = buildExecutionEndpoint(baseUrl, stepType);

  const payload = {
    resource_id: resourceId,
    inputs: context,
    mode: 'auto',
  };

  try {
    const response = await axios.post(endpoint, payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout,
    });

    return {
      status: 'success',
      step: step.step,
      output: response.data ?? null,
    };
  } catch (error) {
    const message = error instanceof AxiosError ? error.message : 'Unknown error';
    return {
      status: 'error',
      step: step.step,
      error: message,
    };
  }
};

export class ArdfWorkflowRunner implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ARDF Workflow Runner',
    name: 'ardfWorkflowRunner',
    icon: 'fa:project-diagram',
    group: ['transform'],
    version: 1,
    description: 'Executes ARDF workflows sequentially, calling each resource step via MCP endpoints.',
    defaults: { name: 'ARDF Workflow Runner' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'MCP Base URL',
        name: 'mcpBaseUrl',
        type: 'string',
        default: 'http://localhost:8000',
        required: true,
        description: 'Base URL of the ARDF MCP server.',
      },
      {
        displayName: 'Workflow Resource ID',
        name: 'workflowId',
        type: 'string',
        default: '',
        description: 'Identifier of the ARDF workflow to execute. Leave empty to use the incoming item value.',
      },
      {
        displayName: 'Execution Mode',
        name: 'execMode',
        type: 'options',
        default: 'sequential',
        options: [
          { name: 'Sequential', value: 'sequential' },
          { name: 'Parallel (best-effort)', value: 'parallel' },
        ],
        description: 'Defines how workflow steps are executed.',
      },
      {
        displayName: 'Input Context (JSON)',
        name: 'context',
        type: 'json',
        default: {},
        description: 'Initial shared context available to all workflow steps.',
      },
      {
        displayName: 'Stop on Error',
        name: 'stopOnError',
        type: 'boolean',
        default: true,
        description: 'Stop execution when a step fails.',
      },
      {
        displayName: 'Request Timeout (ms)',
        name: 'timeout',
        type: 'number',
        default: 20000,
        description: 'Timeout in milliseconds for each step execution request.',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
      const mcpBaseUrl = (this.getNodeParameter('mcpBaseUrl', itemIndex) as string).trim();
      const configuredWorkflowId = (this.getNodeParameter('workflowId', itemIndex) as string).trim();
      const execMode = this.getNodeParameter('execMode', itemIndex) as ExecutionMode;
      const stopOnError = this.getNodeParameter('stopOnError', itemIndex) as boolean;
      const timeout = Number(this.getNodeParameter('timeout', itemIndex)) || 20000;
      const initialContext = this.getNodeParameter('context', itemIndex, {}) as Record<string, unknown>;

      const incoming = items[itemIndex].json as Record<string, unknown>;
      const workflowId = configuredWorkflowId || (incoming.resource_id as string) || (incoming.workflow_id as string);

      if (!workflowId) {
        throw new NodeOperationError(
          this.getNode(),
          'Workflow identifier is required but was not provided or inferred from the input.',
          { itemIndex },
        );
      }

      const { steps, descriptor } = await fetchWorkflowDescriptor(mcpBaseUrl, workflowId);

      if (!steps.length) {
        throw new NodeOperationError(
          this.getNode(),
          Workflow '' does not contain any steps to execute.,
          { itemIndex },
        );
      }

      const stepResults: Record<string, StepResult> = {};
      let context: Record<string, unknown> = { ...initialContext, ...incoming };

      const runSequential = async () => {
        for (const step of steps) {
          const result = await executeStep(mcpBaseUrl, step, context, timeout);
          stepResults[step.step] = result;

          if (result.status === 'success' && result.output && typeof result.output === 'object') {
            context = {
              ...context,
              ...((result.output as Record<string, unknown>) ?? {}),
            };
          }

          if (result.status === 'error' && stopOnError) {
            break;
          }
        }
      };

      const runParallel = async () => {
        const executions = await Promise.all(
          steps.map((step) => executeStep(mcpBaseUrl, step, context, timeout)),
        );

        executions.forEach((result, index) => {
          const step = steps[index];
          stepResults[step.step] = result;

          if (result.status === 'success' && result.output && typeof result.output === 'object') {
            context = {
              ...context,
              ...((result.output as Record<string, unknown>) ?? {}),
            };
          }
        });
      };

      if (execMode === 'parallel') {
        await runParallel();
      } else {
        await runSequential();
      }

      returnData.push({
        json: {
          workflow_id: workflowId,
          descriptor,
          steps: stepResults,
          final_context: context,
        },
      });
    }

    return [returnData];
  }
}
