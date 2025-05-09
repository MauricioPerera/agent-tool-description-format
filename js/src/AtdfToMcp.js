/**
 * Convertidor de ATDF (Agent Tool Description Format) a MCP (Model Context Protocol).
 * 
 * Este módulo proporciona funciones para convertir herramientas desde el formato ATDF
 * a formato MCP utilizado por algunos frameworks de AI como MCP Framework.
 */

const fs = require('fs');
const path = require('path');

/**
 * Convierte una herramienta ATDF a formato MCP.
 * 
 * @param {Object} atdfTool - Objeto JSON de una herramienta ATDF.
 * @param {Object} options - Opciones de conversión.
 * @param {Object} options.annotations - Anotaciones adicionales para la herramienta MCP.
 * @returns {Object} - Objeto MCP válido.
 * @throws {Error} - Si faltan campos obligatorios o la validación falla.
 */
function atdfToMcp(atdfTool, options = {}) {
    const { annotations = {} } = options;

    // Validar campos obligatorios en ATDF
    const requiredAtdfFields = ["tool_id", "description", "how_to_use"];
    for (const field of requiredAtdfFields) {
        if (!(field in atdfTool)) {
            throw new Error(`Campo obligatorio '${field}' no encontrado en ATDF`);
        }
    }

    if (!atdfTool.how_to_use.inputs) {
        throw new Error(`Campo obligatorio 'how_to_use.inputs' no encontrado en ATDF`);
    }

    // Mapear campos ATDF → MCP
    const mcpTool = {
        name: atdfTool.tool_id,
        description: atdfTool.description,
        inputSchema: buildInputSchema(atdfTool.how_to_use.inputs),
        annotations: {
            ...annotations,
            when_to_use: atdfTool.when_to_use || ""
        }
    };

    console.log(`[✓] ${mcpTool.name} convertido exitosamente a MCP`);
    return mcpTool;
}

/**
 * Construye el esquema de entrada MCP a partir de los inputs ATDF.
 * 
 * @param {Array} inputs - Lista de definiciones de inputs de ATDF.
 * @returns {Object} - Esquema de entrada válido para MCP.
 */
function buildInputSchema(inputs) {
    const properties = {};
    const required = [];

    // Construir propiedades y lista de campos requeridos
    for (const input of inputs) {
        properties[input.name] = {
            type: input.type,
            description: input.description || `Parámetro ${input.name}`
        };

        // Añadir a la lista de requeridos si es necesario
        if (input.required) {
            required.push(input.name);
        }
    }

    return {
        type: "object",
        properties: properties,
        required: required
    };
}

/**
 * Convierte un archivo ATDF a formato MCP.
 * 
 * @param {string} inputFile - Ruta al archivo ATDF a convertir.
 * @param {string} outputFile - Ruta donde guardar el resultado. Si es null, solo retorna el resultado.
 * @param {Object} options - Opciones de conversión.
 * @returns {Object|null} - Objeto MCP o null si hay error.
 */
function convertAtdfFile(inputFile, outputFile = null, options = {}) {
    try {
        // Verificar existencia del archivo
        if (!fs.existsSync(inputFile)) {
            console.error(`Archivo no encontrado: ${inputFile}`);
            return null;
        }
        
        // Leer archivo JSON
        const atdfData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
        
        // Convertir a MCP
        const mcpResult = atdfToMcp(atdfData, options);
        
        // Guardar si se especificó archivo de salida
        if (outputFile) {
            // Crear directorio si no existe
            const outputDir = path.dirname(outputFile);
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }
            
            // Guardar el archivo
            fs.writeFileSync(outputFile, JSON.stringify(mcpResult, null, 2));
            console.log(`Herramienta guardada en ${outputFile}`);
        }
        
        return mcpResult;
    } catch (error) {
        console.error(`Error en la conversión: ${error.message}`);
        return null;
    }
}

/**
 * Procesa un lote de herramientas ATDF.
 * 
 * @param {Array} atdfTools - Array de herramientas ATDF.
 * @param {string} outputDir - Directorio donde guardar las herramientas convertidas.
 * @param {Object} options - Opciones de conversión.
 * @returns {Array} - Array de herramientas MCP convertidas.
 */
function batchConvert(atdfTools, outputDir, options = {}) {
    const results = [];
    
    // Crear directorio si no existe
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Procesar cada herramienta
    for (let i = 0; i < atdfTools.length; i++) {
        const tool = atdfTools[i];
        try {
            // Convertir a MCP
            const mcpTool = atdfToMcp(tool, options);
            
            // Guardar en archivo
            const outputFile = path.join(outputDir, `${tool.tool_id}.json`);
            fs.writeFileSync(outputFile, JSON.stringify(mcpTool, null, 2));
            
            console.log(`✅ Herramienta ${i+1}/${atdfTools.length} convertida: ${outputFile}`);
            results.push(mcpTool);
        } catch (error) {
            console.error(`❌ Error al convertir herramienta ${tool.tool_id}: ${error.message}`);
        }
    }
    
    return results;
}

// Exportar funciones
module.exports = {
    atdfToMcp,
    convertAtdfFile,
    batchConvert
}; 