export interface ArdfResourceBase {
  schema_version: string;
  resource_id: string;
  resource_type: string;
  description: string;
  when_to_use?: string;
  metadata?: Record<string, unknown>;
  localization?: Record<string, unknown>;
  prerequisites?: Record<string, unknown>;
  examples?: unknown[];
  feedback?: Record<string, unknown>;
}

export interface ArdfWorkflowResource extends ArdfResourceBase {
  resource_type: 'workflow';
  content: {
    type: string;
    data: {
      steps: Array<Record<string, unknown>>;
    };
  };
}

export type ArdfResource = ArdfResourceBase | ArdfWorkflowResource;
