import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  IWebhookFunctions,
  IWebhookResponseData,
  NodeOperationError,
} from 'n8n-workflow';

export class AtdfMcpServer implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ATDF MCP Server',
    name: 'atdfMcpServer',
    icon: 'file:atdf-mcp-server.svg',
    group: ['trigger'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Expose n8n workflows as ATDF tools via MCP protocol',
    defaults: {
      name: 'ATDF MCP Server',
    },
    inputs: [],
    outputs: ['main'],
    webhooks: [
      {
        name: 'default',
        httpMethod: 'POST',
        responseMode: 'onReceived',
        path: 'atdf-mcp-server',
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        options: [
          {
            name: 'Expose as Tool',
            value: 'exposeTool',
            description: 'Expose this workflow as an ATDF tool',
            action: 'Expose workflow as ATDF tool',
          },
          {
            name: 'List Available Tools',
            value: 'listTools',
            description: 'List all available ATDF tools',
            action: 'List available tools',
          },
        ],
        default: 'exposeTool',
      },
      {
        displayName: 'Tool Configuration',
        name: 'toolConfig',
        type: 'collection',
        displayOptions: {
          show: {
            operation: ['exposeTool'],
          },
        },
        default: {},
        options: [
          {
            displayName: 'Tool Name',
            name: 'name',
            type: 'string',
            default: '',
            placeholder: 'my_custom_tool',
            description: 'Unique name for the ATDF tool',
            required: true,
          },
          {
            displayName: 'Tool Description',
            name: 'description',
            type: 'string',
            default: '',
            placeholder: 'This tool performs a specific task...',
            description: 'Description of what the tool does',
            required: true,
          },
          {
            displayName: 'When to Use',
            name: 'when_to_use',
            type: 'string',
            default: '',
            placeholder: 'Use this tool when you need to...',
            description: 'Guidelines for when to use this tool',
          },
          {
            displayName: 'Category',
            name: 'category',
            type: 'options',
            options: [
              {
                name: 'Data Processing',
                value: 'data_processing',
              },
              {
                name: 'Communication',
                value: 'communication',
              },
              {
                name: 'File Operations',
                value: 'file_operations',
              },
              {
                name: 'API Integration',
                value: 'api_integration',
              },
              {
                name: 'Automation',
                value: 'automation',
              },
              {
                name: 'Custom',
                value: 'custom',
              },
            ],
            default: 'custom',
            description: 'Category of the tool',
          },
          {
            displayName: 'Input Schema',
            name: 'input_schema',
            type: 'json',
            default: '{\n  "type": "object",\n  "properties": {},\n  "required": []\n}',
            description: 'JSON Schema defining the input parameters',
          },
          {
            displayName: 'Tags',
            name: 'tags',
            type: 'string',
            default: '',
            placeholder: 'tag1, tag2, tag3',
            description: 'Comma-separated list of tags',
          },
        ],
      },
      {
        displayName: 'Multilingual Support',
        name: 'multilingual',
        type: 'collection',
        default: {},
        options: [
          {
            displayName: 'Spanish Description',
            name: 'es_description',
            type: 'string',
            default: '',
            description: 'Tool description in Spanish',
          },
          {
            displayName: 'Spanish When to Use',
            name: 'es_when_to_use',
            type: 'string',
            default: '',
            description: 'When to use guidelines in Spanish',
          },
          {
            displayName: 'Portuguese Description',
            name: 'pt_description',
            type: 'string',
            default: '',
            description: 'Tool description in Portuguese',
          },
          {
            displayName: 'Portuguese When to Use',
            name: 'pt_when_to_use',
            type: 'string',
            default: '',
            description: 'When to use guidelines in Portuguese',
          },
        ],
      },
      {
        displayName: 'Response Configuration',
        name: 'responseConfig',
        type: 'collection',
        default: {},
        options: [
          {
            displayName: 'Success Message',
            name: 'successMessage',
            type: 'string',
            default: 'Tool executed successfully',
            description: 'Message to return on successful execution',
          },
          {
            displayName: 'Include Execution Data',
            name: 'includeExecutionData',
            type: 'boolean',
            default: true,
            description: 'Whether to include workflow execution data in response',
          },
          {
            displayName: 'Response Format',
            name: 'responseFormat',
            type: 'options',
            options: [
              {
                name: 'ATDF Standard',
                value: 'atdf',
              },
              {
                name: 'MCP Standard',
                value: 'mcp',
              },
              {
                name: 'Custom JSON',
                value: 'custom',
              },
            ],
            default: 'atdf',
            description: 'Format for the response data',
          },
        ],
      },
    ],
  };

  async webhook(this: IWebhookFunctions): Promise<IWebhookResponseData> {
    const operation = this.getNodeParameter('operation') as string;
    const req = this.getRequestObject();
    const res = this.getResponseObject();

    try {
      switch (operation) {
        case 'exposeTool':
          return await this.handleToolExecution(req, res);

        case 'listTools':
          return await this.handleListTools(req, res);

        default:
          throw new Error(`Unknown operation: ${operation}`);
      }
    } catch (error) {
      return {
        webhookResponse: {
          status: 500,
          body: {
            error: error.message,
            success: false,
            timestamp: new Date().toISOString(),
          },
        },
      };
    }
  }

  private async handleToolExecution(req: any, res: any): Promise<IWebhookResponseData> {
    const toolConfig = this.getNodeParameter('toolConfig') as any;
    const responseConfig = this.getNodeParameter('responseConfig') as any;
    const multilingual = this.getNodeParameter('multilingual') as any;

    // Extract MCP request data
    const mcpRequest = req.body;
    const toolName = mcpRequest.params?.name || toolConfig.name;
    const toolArguments = mcpRequest.params?.arguments || {};

    // Validate tool name
    if (toolName !== toolConfig.name) {
      throw new Error(`Tool '${toolName}' not found. Available: '${toolConfig.name}'`);
    }

    // Validate input against schema
    if (toolConfig.input_schema) {
      try {
        const schema = JSON.parse(toolConfig.input_schema);
        // Basic validation - in production, use a proper JSON schema validator
        if (schema.required) {
          for (const requiredField of schema.required) {
            if (!(requiredField in toolArguments)) {
              throw new Error(`Required field '${requiredField}' is missing`);
            }
          }
        }
      } catch (error) {
        throw new Error(`Schema validation failed: ${error.message}`);
      }
    }

    // Create ATDF-compliant tool definition
    const atdfTool = this.createAtdfTool(toolConfig, multilingual);

    // Prepare execution data
    const executionData = {
      tool: atdfTool,
      arguments: toolArguments,
      timestamp: new Date().toISOString(),
      requestId: mcpRequest.id || `req_${Date.now()}`,
    };

    // Format response based on configuration
    let responseData: any;
    switch (responseConfig.responseFormat) {
      case 'mcp':
        responseData = {
          jsonrpc: '2.0',
          id: mcpRequest.id,
          result: {
            content: [
              {
                type: 'text',
                text: responseConfig.successMessage || 'Tool executed successfully',
              },
            ],
            isError: false,
          },
        };
        if (responseConfig.includeExecutionData) {
          responseData.result.executionData = executionData;
        }
        break;

      case 'atdf':
        responseData = {
          success: true,
          tool: atdfTool,
          execution: executionData,
          message: responseConfig.successMessage || 'Tool executed successfully',
        };
        break;

      case 'custom':
      default:
        responseData = {
          success: true,
          data: executionData,
          message: responseConfig.successMessage || 'Tool executed successfully',
        };
        break;
    }

    return {
      webhookResponse: {
        status: 200,
        body: responseData,
      },
      workflowData: [
        [
          {
            json: executionData,
          },
        ],
      ],
    };
  }

  private async handleListTools(req: any, res: any): Promise<IWebhookResponseData> {
    const toolConfig = this.getNodeParameter('toolConfig') as any;
    const multilingual = this.getNodeParameter('multilingual') as any;

    const atdfTool = this.createAtdfTool(toolConfig, multilingual);

    const mcpResponse = {
      jsonrpc: '2.0',
      id: req.body.id,
      result: {
        tools: [
          {
            name: atdfTool.name,
            description: atdfTool.description,
            inputSchema: JSON.parse(atdfTool.input_schema || '{}'),
          },
        ],
      },
    };

    return {
      webhookResponse: {
        status: 200,
        body: mcpResponse,
      },
    };
  }

  private createAtdfTool(toolConfig: any, multilingual: any): any {
    const tags = toolConfig.tags ? toolConfig.tags.split(',').map((tag: string) => tag.trim()) : [];

    const atdfTool: any = {
      name: toolConfig.name,
      description: toolConfig.description,
      when_to_use: toolConfig.when_to_use || '',
      input_schema: toolConfig.input_schema || '{}',
      category: toolConfig.category || 'custom',
      tags,
      metadata: {
        version: '1.0.0',
        author: 'n8n-atdf-mcp',
        created_at: new Date().toISOString(),
        source: 'n8n-workflow',
      },
    };

    // Add multilingual support
    if (multilingual.es_description || multilingual.es_when_to_use) {
      atdfTool.localization = atdfTool.localization || {};
      atdfTool.localization.es = {
        description: multilingual.es_description || atdfTool.description,
        when_to_use: multilingual.es_when_to_use || atdfTool.when_to_use,
      };
    }

    if (multilingual.pt_description || multilingual.pt_when_to_use) {
      atdfTool.localization = atdfTool.localization || {};
      atdfTool.localization.pt = {
        description: multilingual.pt_description || atdfTool.description,
        when_to_use: multilingual.pt_when_to_use || atdfTool.when_to_use,
      };
    }

    return atdfTool;
  }
}