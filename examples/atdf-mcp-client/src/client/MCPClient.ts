/**
 * Cliente básico para servidores MCP (Model Context Protocol)
 * 
 * Este cliente permite conectarse a un servidor MCP,
 * descubrir herramientas disponibles y ejecutarlas.
 */

import fetch from 'node-fetch';
import { MCPClientOptions, MCPTool, MCPToolCallResponse } from '../types';

export class MCPClient {
  // URL base del servidor MCP
  protected baseUrl: string;
  
  // Opciones del cliente
  protected options: MCPClientOptions;
  
  // Herramientas disponibles en el servidor
  protected tools: MCPTool[] = [];
  
  /**
   * Constructor del cliente MCP
   * 
   * @param baseUrl URL base del servidor MCP o opciones completas
   * @param options Opciones adicionales para el cliente (opcional)
   */
  constructor(baseUrlOrOptions: string | MCPClientOptions, options?: MCPClientOptions) {
    if (typeof baseUrlOrOptions === 'string') {
      this.baseUrl = baseUrlOrOptions;
      this.options = options || {
        baseUrl: baseUrlOrOptions,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 segundos
      };
    } else {
      this.baseUrl = baseUrlOrOptions.baseUrl;
      this.options = baseUrlOrOptions;
    }
    
    // Asegurarse de que la URL no termine con barra
    this.baseUrl = this.baseUrl.endsWith('/') 
      ? this.baseUrl.slice(0, -1)
      : this.baseUrl;
    
    // Valores por defecto
    if (!this.options.headers) {
      this.options.headers = { 'Content-Type': 'application/json' };
    }
  }
  
  /**
   * Conectar al servidor MCP y descubrir herramientas disponibles
   * 
   * @returns Lista de herramientas disponibles en el servidor
   */
  async connect(): Promise<MCPTool[]> {
    try {
      console.log(`Conectando al servidor MCP: ${this.baseUrl}`);
      
      const response = await fetch(`${this.baseUrl}/tools/list`, {
        method: 'GET',
        headers: this.options.headers
      });
      
      if (!response.ok) {
        throw new Error(`Error al conectar al servidor MCP: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (!data.tools || !Array.isArray(data.tools)) {
        throw new Error('Formato de respuesta inválido: no se encontró lista de herramientas');
      }
      
      this.tools = data.tools;
      console.log(`Descubiertas ${this.tools.length} herramientas en el servidor MCP`);
      
      return this.tools;
    } catch (error: any) {
      console.error('Error al conectar al servidor MCP:', error.message);
      throw error;
    }
  }
  
  /**
   * Obtener la lista de herramientas disponibles
   * 
   * @returns Lista de herramientas disponibles
   */
  getTools(): MCPTool[] {
    return this.tools;
  }
  
  /**
   * Buscar una herramienta por nombre
   * 
   * @param name Nombre de la herramienta a buscar
   * @returns Herramienta encontrada o undefined
   */
  findTool(name: string): MCPTool | undefined {
    return this.tools.find(tool => tool.name === name);
  }
  
  /**
   * Llamar a una herramienta en el servidor MCP
   * 
   * @param toolName Nombre de la herramienta a ejecutar
   * @param params Parámetros para la herramienta
   * @returns Resultado de la ejecución de la herramienta
   */
  async callTool(toolName: string, params: any): Promise<MCPToolCallResponse> {
    try {
      console.log(`Llamando a herramienta ${toolName} con parámetros:`, params);
      
      const response = await fetch(`${this.baseUrl}/tools/call`, {
        method: 'POST',
        headers: this.options.headers,
        body: JSON.stringify({
          name: toolName,
          params: params
        }),
        timeout: this.options.timeout
      });
      
      if (!response.ok) {
        throw new Error(`Error al llamar a herramienta: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      return {
        result,
        status: 'success',
        toolName
      };
    } catch (error: any) {
      console.error(`Error al llamar a herramienta ${toolName}:`, error.message);
      
      return {
        result: null,
        status: 'error',
        error: error.message,
        toolName
      };
    }
  }
} 