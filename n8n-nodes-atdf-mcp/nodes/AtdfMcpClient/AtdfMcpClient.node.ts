import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

import axios, { AxiosResponse } from 'axios';

export class AtdfMcpClient implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ATDF MCP Client',
    name: 'atdfMcpClient',
    icon: 'file:atdf-mcp-client.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"] + ": " + $parameter["toolName"]}}',
    description: 'Connect to ATDF servers via MCP protocol',
    defaults: {
      name: 'ATDF MCP Client',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'atdfMcpApi',
        required: true,
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
            name: 'List Tools',
            value: 'listTools',
            description: 'Get available ATDF tools from the server',
            action: 'List available ATDF tools',
          },
          {
            name: 'Execute Tool',
            value: 'executeTool',
            description: 'Execute a specific ATDF tool',
            action: 'Execute an ATDF tool',
          },
          {
            name: 'Get Tool Schema',
            value: 'getToolSchema',
            description: 'Get the schema for a specific tool',
            action: 'Get tool schema',
          },
        ],
        default: 'listTools',
      },
      {
        displayName: 'Tool Name',
        name: 'toolName',
        type: 'string',
        displayOptions: {
          show: {
            operation: ['executeTool', 'getToolSchema'],
          },
        },
        default: '',
        placeholder: 'file_operations',
        description: 'Name of the ATDF tool to execute or get schema for',
        required: true,
      },
      {
        displayName: 'Tool Parameters',
        name: 'toolParameters',
        type: 'json',
        displayOptions: {
          show: {
            operation: ['executeTool'],
          },
        },
        default: '{}',
        description: 'Parameters to pass to the ATDF tool (JSON format)',
      },
      {
        displayName: 'Language',
        name: 'language',
        type: 'options',
        options: [
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
        default: 'en',
        description: 'Language for tool descriptions and responses',
      },
      {
        displayName: 'Include Metadata',
        name: 'includeMetadata',
        type: 'boolean',
        default: true,
        description: 'Whether to include ATDF metadata in the response',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];
    const credentials = await this.getCredentials('atdfMcpApi');

    const serverUrl = credentials.serverUrl as string;
    const apiKey = credentials.apiKey as string;
    const timeout = credentials.timeout as number;

    for (let i = 0; i < items.length; i++) {
      try {
        const operation = this.getNodeParameter('operation', i) as string;
        const language = this.getNodeParameter('language', i) as string;
        const includeMetadata = this.getNodeParameter('includeMetadata', i) as boolean;

        const headers: any = {
          'Content-Type': 'application/json',
          'Accept-Language': language,
        };

        if (apiKey) {
          headers['Authorization'] = `Bearer ${apiKey}`;
        }

        let responseData: any;

        switch (operation) {
          case 'listTools':
            responseData = await this.listTools(serverUrl, headers, timeout);
            break;

          case 'executeTool':
            const toolName = this.getNodeParameter('toolName', i) as string;
            const toolParameters = this.getNodeParameter('toolParameters', i) as string;
            
            let parameters: any = {};
            try {
              parameters = JSON.parse(toolParameters);
            } catch (error) {
              throw new NodeOperationError(
                this.getNode(),
                `Invalid JSON in tool parameters: ${error.message}`,
                { itemIndex: i }
              );
            }

            responseData = await this.executeTool(
              serverUrl,
              headers,
              timeout,
              toolName,
              parameters
            );
            break;

          case 'getToolSchema':
            const schemaToolName = this.getNodeParameter('toolName', i) as string;
            responseData = await this.getToolSchema(
              serverUrl,
              headers,
              timeout,
              schemaToolName
            );
            break;

          default:
            throw new NodeOperationError(
              this.getNode(),
              `Unknown operation: ${operation}`,
              { itemIndex: i }
            );
        }

        // Process response based on includeMetadata setting
        if (!includeMetadata && responseData.data) {
          responseData = responseData.data;
        }

        returnData.push({
          json: {
            operation,
            success: true,
            data: responseData,
            timestamp: new Date().toISOString(),
          },
        });

      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: {
              error: error.message,
              success: false,
              timestamp: new Date().toISOString(),
            },
          });
          continue;
        }
        throw error;
      }
    }

    return [returnData];
  }

  private async listTools(
    serverUrl: string,
    headers: any,
    timeout: number
  ): Promise<any> {
    const response: AxiosResponse = await axios({
      method: 'GET',
      url: `${serverUrl}/mcp/tools/list`,
      headers,
      timeout,
    });

    return response.data;
  }

  private async executeTool(
    serverUrl: string,
    headers: any,
    timeout: number,
    toolName: string,
    parameters: any
  ): Promise<any> {
    const response: AxiosResponse = await axios({
      method: 'POST',
      url: `${serverUrl}/mcp/tools/call`,
      headers,
      timeout,
      data: {
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: parameters,
        },
      },
    });

    return response.data;
  }

  private async getToolSchema(
    serverUrl: string,
    headers: any,
    timeout: number,
    toolName: string
  ): Promise<any> {
    const response: AxiosResponse = await axios({
      method: 'GET',
      url: `${serverUrl}/mcp/tools/${toolName}/schema`,
      headers,
      timeout,
    });

    return response.data;
  }
}