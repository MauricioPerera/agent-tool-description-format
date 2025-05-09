/**
 * Convertidor de herramientas MCP a formato ATDF
 * 
 * Este módulo proporciona funciones para convertir herramientas
 * del formato MCP al formato ATDF.
 */

import { ATDFTool, ATDFParameter, MCPTool, McpToAtdfOptions } from '../types';

/**
 * Convertir una herramienta MCP a formato ATDF
 * 
 * @param mcpTool Herramienta MCP a convertir
 * @param options Opciones para la conversión
 * @returns Herramienta en formato ATDF
 */
export function mcpToAtdf(mcpTool: MCPTool, options?: McpToAtdfOptions): ATDFTool {
  const defaultOptions: McpToAtdfOptions = {
    includeWhenToUse: true,
    defaultWhenToUse: `Usar cuando necesites ${mcpTool.description?.toLowerCase() || 'esta funcionalidad'}`,
    generateFailures: true
  };
  
  const opts = { ...defaultOptions, ...options };
  
  // Convertir parámetros de MCP a ATDF
  const inputs: ATDFParameter[] = Object.entries(mcpTool.schema).map(([name, schema]) => {
    return {
      name,
      type: inferTypeFromSchema(schema.type),
      description: schema.description || `Parámetro ${name}`,
      required: schema.required !== false // Por defecto, parámetros requeridos
    };
  });
  
  // Crear estructura ATDF
  const atdfTool: ATDFTool = {
    schema_version: "1.0.0",
    tool_id: mcpTool.name,
    description: mcpTool.description || `Herramienta ${mcpTool.name}`,
    how_to_use: {
      inputs,
      outputs: {
        success: `Resultado exitoso de ${mcpTool.name}`,
        failure: opts.generateFailures ? [
          {
            code: "parameter_error",
            description: "Error en los parámetros proporcionados"
          },
          {
            code: "execution_error",
            description: "Error durante la ejecución de la herramienta"
          }
        ] : []
      }
    }
  };
  
  // Agregar when_to_use si está habilitado
  if (opts.includeWhenToUse) {
    atdfTool.when_to_use = opts.defaultWhenToUse;
  }
  
  return atdfTool;
}

/**
 * Inferir el tipo ATDF a partir de un esquema MCP/Zod
 * 
 * @param schemaType Tipo de esquema Zod o similar
 * @returns Tipo ATDF equivalente
 */
function inferTypeFromSchema(schemaType: any): string {
  // Si tenemos acceso directo al tipo
  if (schemaType?._def?.typeName) {
    const typeName = schemaType._def.typeName;
    
    // Mapeo de tipos Zod a tipos ATDF
    switch (typeName) {
      case 'ZodString': return 'string';
      case 'ZodNumber': return 'number';
      case 'ZodBoolean': return 'boolean';
      case 'ZodArray': return 'array';
      case 'ZodObject': return 'object';
      case 'ZodEnum': return 'string';
      case 'ZodUnion': return 'any';
      case 'ZodAny': return 'any';
      default: return 'any';
    }
  }
  
  // Inferir basado en la descripción o nombre si está disponible
  if (typeof schemaType === 'string') {
    if (['string', 'text', 'str'].includes(schemaType.toLowerCase())) {
      return 'string';
    } else if (['number', 'integer', 'float', 'int'].includes(schemaType.toLowerCase())) {
      return 'number';
    } else if (['boolean', 'bool'].includes(schemaType.toLowerCase())) {
      return 'boolean';
    } else if (['array', 'list'].includes(schemaType.toLowerCase())) {
      return 'array';
    } else if (['object', 'map', 'dict'].includes(schemaType.toLowerCase())) {
      return 'object';
    }
  }
  
  // Tipo por defecto
  return 'any';
}

/**
 * Convertir varias herramientas MCP a formato ATDF
 * 
 * @param mcpTools Lista de herramientas MCP a convertir
 * @param options Opciones para la conversión
 * @returns Lista de herramientas en formato ATDF
 */
export function batchConvert(mcpTools: MCPTool[], options?: McpToAtdfOptions): ATDFTool[] {
  return mcpTools.map(tool => mcpToAtdf(tool, options));
} 