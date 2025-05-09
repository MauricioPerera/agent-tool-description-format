#!/usr/bin/env node
/**
 * Ejemplo de uso del convertidor MCP a ATDF en JavaScript.
 * 
 * Este script demuestra cómo utilizar el módulo MCPConverter.js para transformar
 * herramientas desde el formato MCP al formato ATDF.
 */

const path = require('path');
const fs = require('fs');
const { mcpToAtdf, batchConvert } = require('../src/MCPConverter');

// Crear directorio para los resultados
const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

console.log('🔄 Iniciando ejemplo de conversión MCP a ATDF en JavaScript...');

// Ejemplo 1: Herramienta simple convertida programáticamente
console.log('\n==== Ejemplo 1: Conversión programática simple ====');

const mcpToolExample = {
    name: 'fetch',
    description: 'Recupera contenido de una URL',
    annotations: {
        context: 'Cuando necesites obtener datos de una página web'
    },
    inputSchema: {
        type: 'object',
        properties: {
            url: {
                type: 'string',
                description: 'URL a recuperar'
            },
            raw: {
                type: 'boolean',
                description: 'Devolver HTML crudo (opcional)'
            }
        },
        required: ['url']
    }
};

try {
    // Convertir a formato básico
    const basicResult = mcpToAtdf(mcpToolExample);
    const basicOutputPath = path.join(outputDir, 'fetch_basic.json');
    fs.writeFileSync(basicOutputPath, JSON.stringify(basicResult, null, 2));
    console.log(`✅ Herramienta básica guardada en: ${basicOutputPath}`);
    
    // Convertir a formato mejorado
    const enhancedResult = mcpToAtdf(mcpToolExample, { 
        enhanced: true, 
        author: 'MCP Example JS' 
    });
    const enhancedOutputPath = path.join(outputDir, 'fetch_enhanced.json');
    fs.writeFileSync(enhancedOutputPath, JSON.stringify(enhancedResult, null, 2));
    console.log(`✅ Herramienta mejorada guardada en: ${enhancedOutputPath}`);
    
    // Mostrar resultado
    console.log('\nContenido del archivo ATDF generado:');
    console.log('-'.repeat(50));
    console.log(JSON.stringify(basicResult, null, 2));
    console.log('-'.repeat(50));
} catch (error) {
    console.error(`❌ Error: ${error.message}`);
}

// Ejemplo 2: Procesamiento por lotes
console.log('\n==== Ejemplo 2: Procesamiento por lotes ====');

// Crear múltiples herramientas para el ejemplo
const mcpTools = {
    tools: [
        {
            name: 'search',
            description: 'Busca información en la web',
            annotations: {
                purpose: 'Obtener resultados de búsqueda de un término'
            },
            inputSchema: {
                type: 'object',
                properties: {
                    query: { type: 'string', description: 'Término de búsqueda' },
                    limit: { type: 'number', description: 'Número máximo de resultados' }
                },
                required: ['query']
            }
        },
        {
            name: 'weather',
            description: 'Obtiene información meteorológica',
            annotations: {
                context: 'Para conocer las condiciones climáticas de una ubicación'
            },
            inputSchema: {
                type: 'object',
                properties: {
                    location: { type: 'string', description: 'Ciudad o coordenadas' },
                    units: { type: 'string', description: 'Unidades (metric/imperial)' }
                },
                required: ['location']
            }
        }
    ]
};

// Guardar herramientas MCP en un archivo temporal
const mcpFilePath = path.join(outputDir, 'mcp_tools.json');
fs.writeFileSync(mcpFilePath, JSON.stringify(mcpTools, null, 2));

// Procesar por lotes
const batchOutputDir = path.join(outputDir, 'batch');
try {
    // Convertir todas las herramientas
    const results = batchConvert(mcpTools, batchOutputDir, { enhanced: true });
    console.log(`\n🎉 Conversión por lotes completada. Se convirtieron ${results.length} herramientas.`);
} catch (error) {
    console.error(`❌ Error en el procesamiento por lotes: ${error.message}`);
}

console.log(`\n🎉 Conversión completa. Resultados guardados en: ${outputDir}`); 