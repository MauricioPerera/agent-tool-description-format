/**
 * Cliente MCP extendido con soporte para herramientas ATDF
 * 
 * Este cliente extiende el cliente MCP básico para agregar
 * funcionalidad de conversión y manejo de herramientas ATDF.
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { MCPClient } from './MCPClient';
import { mcpToAtdf, batchConvert } from '../converters/McpToAtdf';
import { ATDFTool, MCPTool, MCPClientOptions, MCPToolCallResponse, McpToAtdfOptions } from '../types';

export class ATDFMCPClient extends MCPClient {
  // Herramientas en formato ATDF
  private atdfTools: ATDFTool[] = [];
  
  // Opciones para la conversión MCP a ATDF
  private conversionOptions?: McpToAtdfOptions;
  
  /**
   * Constructor del cliente MCP-ATDF
   * 
   * @param baseUrlOrOptions URL base del servidor MCP o opciones completas
   * @param options Opciones adicionales para el cliente
   * @param conversionOptions Opciones para la conversión MCP a ATDF
   */
  constructor(
    baseUrlOrOptions: string | MCPClientOptions, 
    options?: MCPClientOptions,
    conversionOptions?: McpToAtdfOptions
  ) {
    super(baseUrlOrOptions, options);
    this.conversionOptions = conversionOptions;
  }
  
  /**
   * Conectar al servidor MCP y convertir herramientas a formato ATDF
   * 
   * @returns Lista de herramientas en formato ATDF
   */
  async connect(): Promise<MCPTool[]> {
    // Conectar al servidor MCP y obtener herramientas
    const mcpTools = await super.connect();
    
    // Convertir herramientas MCP a formato ATDF
    this.atdfTools = batchConvert(mcpTools, this.conversionOptions);
    
    console.log(`Convertidas ${this.atdfTools.length} herramientas a formato ATDF`);
    return mcpTools;
  }
  
  /**
   * Obtener las herramientas en formato ATDF
   * 
   * @returns Lista de herramientas ATDF
   */
  getATDFTools(): ATDFTool[] {
    return this.atdfTools;
  }
  
  /**
   * Buscar una herramienta ATDF por su ID
   * 
   * @param toolId ID de la herramienta ATDF
   * @returns Herramienta ATDF o undefined si no se encuentra
   */
  findATDFTool(toolId: string): ATDFTool | undefined {
    return this.atdfTools.find(tool => tool.tool_id === toolId);
  }
  
  /**
   * Convertir una herramienta MCP específica a formato ATDF
   * 
   * @param mcpTool Herramienta MCP a convertir
   * @param options Opciones específicas para esta conversión
   * @returns Herramienta en formato ATDF
   */
  convertToolToATDF(mcpTool: MCPTool, options?: McpToAtdfOptions): ATDFTool {
    return mcpToAtdf(mcpTool, options || this.conversionOptions);
  }
  
  /**
   * Guardar las herramientas ATDF en archivos JSON
   * 
   * @param directory Directorio donde guardar los archivos
   * @param pretty Si es true, formatea el JSON para mejor legibilidad
   * @returns Lista de rutas de archivos guardados
   */
  saveATDFToolsToDirectory(directory: string, pretty: boolean = true): string[] {
    // Crear directorio si no existe
    fs.ensureDirSync(directory);
    
    const filePaths: string[] = [];
    
    // Guardar cada herramienta en un archivo separado
    for (const tool of this.atdfTools) {
      const filePath = path.join(directory, `${tool.tool_id}.json`);
      fs.writeJsonSync(filePath, tool, { spaces: pretty ? 2 : 0 });
      filePaths.push(filePath);
    }
    
    console.log(`Guardadas ${filePaths.length} herramientas ATDF en ${directory}`);
    return filePaths;
  }
  
  /**
   * Ejecutar una herramienta usando su ID ATDF
   * 
   * @param toolId ID de la herramienta ATDF
   * @param params Parámetros para la herramienta
   * @returns Resultado de la ejecución
   */
  async executeATDFTool(toolId: string, params: any): Promise<MCPToolCallResponse> {
    // Buscar la herramienta por su ID ATDF
    const atdfTool = this.findATDFTool(toolId);
    
    if (!atdfTool) {
      return {
        result: null,
        status: 'error',
        error: `Herramienta ATDF no encontrada: ${toolId}`,
        toolName: toolId
      };
    }
    
    // Validar parámetros según definición ATDF
    const validationError = this.validateParams(atdfTool, params);
    if (validationError) {
      return {
        result: null,
        status: 'error',
        error: validationError,
        toolName: toolId
      };
    }
    
    // Ejecutar la herramienta MCP correspondiente
    return await super.callTool(atdfTool.tool_id, params);
  }
  
  /**
   * Validar parámetros según definición ATDF
   * 
   * @param atdfTool Herramienta ATDF
   * @param params Parámetros a validar
   * @returns Mensaje de error o null si la validación es exitosa
   */
  private validateParams(atdfTool: ATDFTool, params: any): string | null {
    // Verificar parámetros requeridos
    for (const input of atdfTool.how_to_use.inputs) {
      if (input.required && (params[input.name] === undefined || params[input.name] === null)) {
        return `Parámetro requerido faltante: ${input.name}`;
      }
    }
    
    // Verificar tipos básicos (validación simple)
    for (const input of atdfTool.how_to_use.inputs) {
      const param = params[input.name];
      if (param === undefined || param === null) continue;
      
      // Validación de tipo simple
      const paramType = typeof param;
      
      switch (input.type) {
        case 'string':
          if (paramType !== 'string') {
            return `Tipo incorrecto para ${input.name}: esperado string, recibido ${paramType}`;
          }
          break;
        case 'number':
          if (paramType !== 'number') {
            return `Tipo incorrecto para ${input.name}: esperado number, recibido ${paramType}`;
          }
          break;
        case 'boolean':
          if (paramType !== 'boolean') {
            return `Tipo incorrecto para ${input.name}: esperado boolean, recibido ${paramType}`;
          }
          break;
        case 'array':
          if (!Array.isArray(param)) {
            return `Tipo incorrecto para ${input.name}: esperado array, recibido ${paramType}`;
          }
          break;
        case 'object':
          if (paramType !== 'object' || Array.isArray(param)) {
            return `Tipo incorrecto para ${input.name}: esperado object, recibido ${paramType}`;
          }
          break;
      }
    }
    
    return null;
  }
} 