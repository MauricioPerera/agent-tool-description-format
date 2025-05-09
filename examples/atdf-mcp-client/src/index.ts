/**
 * Ejemplo de uso del cliente ATDF-MCP
 * 
 * Este archivo demuestra cómo usar el cliente ATDF-MCP
 * para interactuar con servidores MCP y trabajar con
 * herramientas en formato ATDF.
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { ATDFMCPClient } from './client/ATDFMCPClient';

/**
 * Función principal del ejemplo
 */
async function main() {
  try {
    // URL del servidor MCP
    const serverUrl = process.env.MCP_SERVER_URL || 'http://localhost:1337/mcp';
    
    // Crear cliente MCP-ATDF
    console.log(`Creando cliente MCP-ATDF para servidor: ${serverUrl}`);
    
    const client = new ATDFMCPClient(serverUrl, {
      baseUrl: serverUrl,
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    }, {
      includeWhenToUse: true,
      generateFailures: true
    });
    
    // Conexión y descubrimiento de herramientas
    console.log('Conectando al servidor MCP y descubriendo herramientas...');
    await client.connect();
    
    // Obtener herramientas ATDF ya convertidas
    const atdfTools = client.getATDFTools();
    
    console.log(`\nDescubiertas ${atdfTools.length} herramientas:`);
    atdfTools.forEach(tool => {
      console.log(`- ${tool.tool_id}: ${tool.description}`);
    });
    
    // Guardar herramientas en formato ATDF
    const outputDir = path.join(__dirname, '..', 'atdf-catalog');
    console.log(`\nGuardando herramientas ATDF en ${outputDir}...`);
    
    const filePaths = client.saveATDFToolsToDirectory(outputDir);
    console.log(`Guardadas ${filePaths.length} herramientas ATDF`);
    
    // Ejecutar una herramienta (si hay alguna disponible)
    if (atdfTools.length > 0) {
      const exampleTool = atdfTools[0];
      const requiredParams = exampleTool.how_to_use.inputs
        .filter((input) => input.required)
        .map((input) => input.name);
      
      if (requiredParams.length > 0) {
        console.log(`\nLa herramienta ${exampleTool.tool_id} requiere parámetros: ${requiredParams.join(', ')}`);
        console.log('Saltando ejecución de ejemplo');
      } else {
        console.log(`\nEjecutando herramienta de ejemplo: ${exampleTool.tool_id}`);
        
        const result = await client.executeATDFTool(exampleTool.tool_id, {});
        
        if (result.status === 'success') {
          console.log('Resultado:', result.result);
        } else {
          console.error('Error:', result.error);
        }
      }
    }
    
    console.log('\nEjemplo completado');
  } catch (error: any) {
    console.error('Error en el ejemplo:', error.message);
    process.exit(1);
  }
}

// Ejecutar la función principal
if (require.main === module) {
  main().catch(console.error);
}

// Exportar componentes principales para uso como biblioteca
export * from './client/MCPClient';
export * from './client/ATDFMCPClient';
export * from './converters/McpToAtdf';
export * from './types'; 