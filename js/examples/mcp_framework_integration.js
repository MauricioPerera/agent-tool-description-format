/**
 * Ejemplo de integración con MCP Framework usando herramientas ATDF.
 * 
 * Este ejemplo muestra cómo:
 * 1. Convertir herramientas ATDF a formato MCP
 * 2. Crear adaptadores para usar herramientas ATDF en MCP Framework
 * 3. Utilizar estos adaptadores en un servidor MCP
 * 
 * Nota: Para ejecutar este ejemplo, necesitarás instalar primero:
 * npm install mcp-framework zod
 */

// Módulos necesarios
const fs = require('fs');
const path = require('path');

// Importar nuestros módulos de conversión y adaptación
const { atdfToMcp } = require('../src/AtdfToMcp');
const { createMCPToolFromATDF, adaptATDFTool } = require('../src/ATDFToolAdapter');

// Simular el módulo MCP Framework (En un proyecto real, importarías desde mcp-framework)
const MCPFrameworkMock = {
    MCPTool: class {
        constructor() {
            this.name = '';
            this.description = '';
            this.schema = {};
        }
        
        async execute(params) {
            return { result: 'Método execute debe ser implementado' };
        }
    },
    MCPServer: class {
        constructor() {
            this.tools = [];
        }
        
        registerTool(tool) {
            this.tools.push(tool);
            console.log(`Herramienta registrada: ${tool.name}`);
        }
        
        async start() {
            console.log("Servidor MCP iniciado con las siguientes herramientas:");
            for (const tool of this.tools) {
                console.log(` - ${tool.name}: ${tool.description}`);
            }
        }
    }
};

// Definición de ejemplo de una herramienta ATDF
const fetchToolATDF = {
    "schema_version": "1.0.0",
    "tool_id": "fetch",
    "description": "Recupera contenido de una URL",
    "when_to_use": "Usar cuando necesites obtener datos de una página web",
    "how_to_use": {
        "inputs": [
            {
                "name": "url",
                "type": "string",
                "description": "URL a recuperar",
                "required": true
            },
            {
                "name": "raw",
                "type": "boolean",
                "description": "Devolver HTML crudo (opcional)"
            }
        ],
        "outputs": {
            "success": "Contenido web recuperado con éxito",
            "failure": [
                {
                    "code": "invalid_url",
                    "description": "La URL proporcionada es inválida o inaccesible"
                },
                {
                    "code": "fetch_error",
                    "description": "Error al recuperar el contenido"
                }
            ]
        }
    }
};

// Definición de ejemplo de otra herramienta ATDF
const weatherToolATDF = {
    "schema_version": "1.0.0",
    "tool_id": "weather",
    "description": "Obtiene información meteorológica",
    "when_to_use": "Cuando necesites conocer las condiciones climáticas de una ubicación",
    "how_to_use": {
        "inputs": [
            {
                "name": "location",
                "type": "string",
                "description": "Ciudad o coordenadas",
                "required": true
            },
            {
                "name": "units",
                "type": "string",
                "description": "Unidades (metric/imperial)",
                "required": false
            }
        ],
        "outputs": {
            "success": "Información meteorológica recuperada con éxito",
            "failure": [
                {
                    "code": "location_not_found",
                    "description": "Ubicación no encontrada"
                },
                {
                    "code": "service_error",
                    "description": "Error en el servicio meteorológico"
                }
            ]
        }
    }
};

// Implementación de la función fetch
async function fetchImplementation(params) {
    const { url, raw = false } = params;
    
    console.log(`Simulando fetch a: ${url} (raw: ${raw})`);
    
    // Simular una respuesta
    return {
        status: 200,
        content: raw 
            ? '<html><body><h1>Contenido de ejemplo</h1></body></html>'
            : { title: 'Contenido procesado', text: 'Ejemplo de texto extraído' }
    };
}

// Implementación de la función weather
async function weatherImplementation(params) {
    const { location, units = 'metric' } = params;
    
    console.log(`Obteniendo clima para: ${location} (unidades: ${units})`);
    
    // Simular respuesta del clima
    return {
        location,
        temperature: units === 'metric' ? 22 : 72,
        condition: 'Soleado',
        humidity: 45,
        units
    };
}

// Función principal
async function main() {
    console.log("🚀 Iniciando ejemplo de integración ATDF con MCP Framework");
    
    // Crear directorio para guardar resultados
    const outputDir = path.join(__dirname, 'output');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 1. Convertir herramientas ATDF a MCP y guardar los resultados
    console.log("\n📝 Convirtiendo herramientas ATDF a formato MCP...");
    
    const fetchMCP = atdfToMcp(fetchToolATDF);
    fs.writeFileSync(
        path.join(outputDir, 'fetch_mcp.json'), 
        JSON.stringify(fetchMCP, null, 2)
    );
    
    const weatherMCP = atdfToMcp(weatherToolATDF);
    fs.writeFileSync(
        path.join(outputDir, 'weather_mcp.json'),
        JSON.stringify(weatherMCP, null, 2)
    );
    
    // 2. Crear adaptadores para MCP Framework
    console.log("\n🔄 Creando adaptadores para MCP Framework...");
    
    // Método 1: Usando createMCPToolFromATDF
    const fetchTool = createMCPToolFromATDF(
        fetchToolATDF,
        fetchImplementation
    );
    
    // Método 2: Usando adaptATDFTool (factory pattern)
    const weatherToolFactory = adaptATDFTool(weatherToolATDF);
    const weatherTool = weatherToolFactory(weatherImplementation);
    
    // 3. Crear y configurar servidor MCP
    console.log("\n🖥️ Configurando servidor MCP...");
    
    const { MCPServer } = MCPFrameworkMock;
    const server = new MCPServer();
    
    // Registrar herramientas
    server.registerTool(fetchTool);
    server.registerTool(weatherTool);
    
    // 4. Iniciar servidor
    console.log("\n✅ Iniciando servidor MCP con herramientas ATDF...");
    await server.start();
    
    // 5. Simulación de llamadas a herramientas
    console.log("\n🧪 Simulando llamadas a herramientas...");
    
    try {
        // Llamar a fetch
        console.log("\n➡️ Llamando a fetch...");
        const fetchResult = await fetchTool.execute({ url: "https://example.com" });
        console.log("Resultado:", fetchResult);
        
        // Llamar a weather
        console.log("\n➡️ Llamando a weather...");
        const weatherResult = await weatherTool.execute({ location: "Madrid" });
        console.log("Resultado:", weatherResult);
        
    } catch (error) {
        console.error("❌ Error al ejecutar herramientas:", error.message);
    }
    
    console.log("\n🎉 Integración completada con éxito!");
    console.log(`📁 Archivos generados en: ${outputDir}`);
}

// Ejecutar ejemplo
main().catch(error => {
    console.error("Error en el ejemplo:", error);
}); 