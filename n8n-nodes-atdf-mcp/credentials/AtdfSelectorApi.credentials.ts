import {
  IAuthenticateGeneric,
  ICredentialTestRequest,
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

export class AtdfSelectorApi implements ICredentialType {
  name = 'atdfSelectorApi';
  displayName = 'ATDF Selector API';
  documentationUrl = 'https://github.com/your-org/n8n-nodes-atdf-mcp';
  properties: INodeProperties[] = [
    {
      displayName: 'Selector URL',
      name: 'serverUrl',
      type: 'string',
      default: 'http://localhost:8050',
      placeholder: 'http://localhost:8050',
      description: 'Base URL of the ATDF tool selector service',
      required: true,
    },
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: {
        password: true,
      },
      default: '',
      description: 'API key if the selector requires authentication',
    },
    {
      displayName: 'Timeout (ms)',
      name: 'timeout',
      type: 'number',
      default: 20000,
      description: 'Request timeout when calling the selector API',
    },
  ];

  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: {
      headers: {
        Authorization: '= {{$credentials.apiKey ? `Bearer ${$credentials.apiKey}` : undefined}}',
        'Content-Type': 'application/json',
      },
    },
  };

  test: ICredentialTestRequest = {
    request: {
      baseURL: '={{$credentials.serverUrl}}',
      url: '/health',
      method: 'GET',
    },
  };
}
