/**
 * Convertidor de MCP (Model Context Protocol) a ATDF (Agent Tool Description Format).
 *
 * Este módulo proporciona funciones para convertir herramientas desde el formato MCP
 * utilizado por algunos modelos de lenguaje, al formato ATDF estándar.
 */

const fs = require('fs');
const path = require('path');

/**
 * Convierte una herramienta MCP a formato ATDF.
 *
 * @param {Object} mcpTool - Objeto JSON de una herramienta MCP.
 * @param {Object} options - Opciones de conversión.
 * @param {boolean} options.enhanced - Si es true, añade campos adicionales del formato mejorado.
 * @param {string} options.author - Autor para los metadatos en formato mejorado.
 * @returns {Object} - Objeto ATDF válido.
 * @throws {Error} - Si faltan campos obligatorios.
 */
function mcpToAtdf(mcpTool, options = {}) {
  const { enhanced = false, author = 'MCP Converter' } = options;

  // Validar campos obligatorios en MCP
  const requiredMcpFields = ['name', 'inputSchema'];
  for (const field of requiredMcpFields) {
    if (!(field in mcpTool)) {
      throw new Error(`Campo obligatorio '${field}' no encontrado en MCP`);
    }
  }

  // Mapear campos MCP → ATDF
  const atdfTool = {
    schema_version: '1.0.0',
    tool_id: mcpTool.name,
    description: mcpTool.description || 'Sin descripción proporcionada',
    when_to_use: extractWhenToUse(mcpTool),
    how_to_use: {
      inputs: parseInputs(mcpTool.inputSchema),
      outputs: defaultOutputs(),
    },
  };

  // Añadir campos del formato mejorado si se solicita
  if (enhanced) {
    atdfTool.schema_version = '2.0.0';

    // Añadir sección de metadatos
    atdfTool.metadata = {
      version: '1.0.0',
      author: author,
      tags: ['converted', 'mcp'],
      category: 'auto_converted',
      created_at: new Date().toISOString().split('T')[0],
      updated_at: new Date().toISOString().split('T')[0],
    };

    // Añadir sección de prerequisitos
    atdfTool.prerequisites = {
      tools: [],
      conditions: [],
      permissions: [],
    };

    // Añadir sección de feedback
    atdfTool.feedback = {
      progress_indicators: ['Operation in progress'],
      completion_signals: ['Operation completed'],
    };

    // Añadir sección de ejemplos
    atdfTool.examples = [
      {
        goal: `Example use of ${mcpTool.name}`,
        input_values: {},
        expected_result: 'Success',
      },
    ];
  }

  console.log(`[✓] ${atdfTool.tool_id} validado exitosamente como ATDF`);
  return atdfTool;
}

/**
 * Extrae o genera contexto de uso desde MCP.
 *
 * @param {Object} mcpTool - Objeto JSON de la herramienta MCP.
 * @returns {string} - String con el contexto de uso para ATDF.
 */
function extractWhenToUse(mcpTool) {
  // Priorizar anotaciones MCP si existen
  if (mcpTool.annotations) {
    const contextKeys = ['context', 'usage', 'purpose'];
    const contextHints = [];

    for (const key of contextKeys) {
      if (mcpTool.annotations[key]) {
        contextHints.push(`Uso: ${mcpTool.annotations[key]}`);
      }
    }

    if (contextHints.length > 0) {
      return contextHints.join(' ');
    }
  }

  // Generar mensaje por defecto
  const description = mcpTool.description || '';
  return `Usar cuando se requiera ${description.toLowerCase().replace(/\.$/, '')}`.substring(
    0,
    200
  );
}

/**
 * Convierte JSON Schema de MCP a formato inputs de ATDF.
 *
 * @param {Object} inputSchema - Esquema de entrada MCP.
 * @returns {Array} - Lista de parámetros en formato ATDF.
 */
function parseInputs(inputSchema) {
  const inputs = [];

  // Procesar las propiedades del esquema
  const properties = inputSchema.properties || {};
  for (const [paramName, paramDef] of Object.entries(properties)) {
    const inputParam = {
      name: paramName,
      type: paramDef.type || 'unknown',
      description: paramDef.description || `Parámetro ${paramName}`,
    };

    // Marcar como requerido si está en la lista required
    if (inputSchema.required && inputSchema.required.includes(paramName)) {
      inputParam.required = true;
    }

    inputs.push(inputParam);
  }

  return inputs;
}

/**
 * Genera estructura de salidas para ATDF.
 *
 * @param {string} successMsg - Mensaje personalizado de éxito.
 * @param {Array} failureCodes - Lista de códigos y descripciones de error.
 * @returns {Object} - Estructura de outputs válida para ATDF.
 */
function defaultOutputs(successMsg = null, failureCodes = null) {
  // Mensaje de éxito por defecto o personalizado
  if (!successMsg) {
    successMsg = 'Operación completada exitosamente';
  }

  // Códigos de error por defecto o personalizados
  if (!failureCodes) {
    failureCodes = [
      { code: 'invalid_input', description: 'Entrada inválida o incompleta' },
      { code: 'tool_error', description: 'Error interno de la herramienta' },
    ];
  }

  return {
    success: successMsg,
    failure: failureCodes,
  };
}

/**
 * Convierte un archivo MCP a formato ATDF.
 *
 * @param {string} inputFile - Ruta al archivo MCP a convertir.
 * @param {string} outputFile - Ruta donde guardar el resultado. Si es null, solo retorna el resultado.
 * @param {Object} options - Opciones de conversión.
 * @param {boolean} options.enhanced - Si es true, convierte al formato mejorado.
 * @param {string} options.author - Autor para los metadatos en formato mejorado.
 * @returns {Object|null} - Objeto ATDF o null si hay error.
 */
function convertMcpFile(inputFile, outputFile = null, options = {}) {
  try {
    // Verificar existencia del archivo
    if (!fs.existsSync(inputFile)) {
      console.error(`Archivo no encontrado: ${inputFile}`);
      return null;
    }

    // Leer archivo JSON
    const mcpData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

    // Convertir a ATDF
    const atdfResult = mcpToAtdf(mcpData, options);

    // Guardar si se especificó archivo de salida
    if (outputFile) {
      // Crear directorio si no existe
      const outputDir = path.dirname(outputFile);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // Guardar el archivo
      fs.writeFileSync(outputFile, JSON.stringify(atdfResult, null, 2));
      console.log(`Herramienta guardada en ${outputFile}`);
    }

    return atdfResult;
  } catch (error) {
    console.error(`Error en la conversión: ${error.message}`);
    return null;
  }
}

/**
 * Procesa un lote de herramientas MCP.
 *
 * @param {Array|Object} mcpTools - Array de herramientas o objeto con propiedad 'tools'.
 * @param {string} outputDir - Directorio donde guardar las herramientas convertidas.
 * @param {Object} options - Opciones de conversión.
 * @returns {Array} - Array de herramientas ATDF convertidas.
 */
function batchConvert(mcpTools, outputDir, options = {}) {
  const results = [];

  // Normalizar entrada: puede ser un array o un objeto con propiedad 'tools'
  const toolsArray = Array.isArray(mcpTools) ? mcpTools : mcpTools.tools || [];

  // Crear directorio si no existe
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Procesar cada herramienta
  for (let i = 0; i < toolsArray.length; i++) {
    const tool = toolsArray[i];
    try {
      // Convertir a ATDF
      const atdfTool = mcpToAtdf(tool, options);

      // Guardar en archivo
      const outputFile = path.join(outputDir, `${tool.name}.json`);
      fs.writeFileSync(outputFile, JSON.stringify(atdfTool, null, 2));

      console.log(
        `✅ Herramienta ${i + 1}/${toolsArray.length} convertida: ${outputFile}`
      );
      results.push(atdfTool);
    } catch (error) {
      console.error(
        `❌ Error al convertir herramienta ${tool.name}: ${error.message}`
      );
    }
  }

  return results;
}

// Exportar funciones
module.exports = {
  mcpToAtdf,
  convertMcpFile,
  batchConvert,
};
