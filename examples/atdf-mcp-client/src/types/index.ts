/**
 * Interfaces y tipos para el cliente MCP-ATDF
 */

/**
 * Tipo básico para una herramienta MCP
 */
export interface MCPTool {
  name: string;
  description?: string;
  schema: Record<string, MCPParameter>;
}

/**
 * Definición de un parámetro en una herramienta MCP
 */
export interface MCPParameter {
  type: any; // Normalmente un tipo Zod
  description?: string;
  required?: boolean;
}

/**
 * Estructura simplificada de una herramienta ATDF
 */
export interface ATDFTool {
  schema_version: string;
  tool_id: string;
  description: string;
  when_to_use?: string;
  how_to_use: {
    inputs: ATDFParameter[];
    outputs: {
      success: string;
      failure?: Array<{
        code: string;
        description: string;
      }>;
    };
  };
}

/**
 * Definición de un parámetro en una herramienta ATDF
 */
export interface ATDFParameter {
  name: string;
  type: string;
  description: string;
  required?: boolean;
}

/**
 * Opciones para la conexión al servidor MCP
 */
export interface MCPClientOptions {
  baseUrl: string;
  headers?: Record<string, string>;
  timeout?: number;
}

/**
 * Respuesta de una llamada a herramienta MCP
 */
export interface MCPToolCallResponse {
  result: any;
  status: 'success' | 'error';
  error?: string;
  toolName?: string;
}

/**
 * Opciones para la conversión MCP a ATDF
 */
export interface McpToAtdfOptions {
  includeWhenToUse?: boolean;
  defaultWhenToUse?: string;
  generateFailures?: boolean;
} 