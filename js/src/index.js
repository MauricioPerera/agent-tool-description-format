const ATDFTool = require('./ATDFTool');
const ATDFToolbox = require('./ATDFToolbox');
const MCPConverter = require('./MCPConverter');
const fs = require('fs');

/**
 * Carga una herramienta desde un archivo JSON
 * @param {string} filePath - Ruta al archivo JSON
 * @returns {ATDFTool|null} Herramienta cargada o null si hubo un error
 */
function loadToolFromFile(filePath) {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const toolData = JSON.parse(fileContent);
    return new ATDFTool(toolData);
  } catch (error) {
    console.error(
      `Error al cargar la herramienta desde ${filePath}: ${error.message}`
    );
    return null;
  }
}

/**
 * Carga un conjunto de herramientas desde un directorio
 * @param {string} dirPath - Ruta al directorio
 * @param {Object} [options] - Opciones adicionales
 * @param {boolean} [options.recursive=false] - Si debe buscar en subdirectorios
 * @returns {ATDFToolbox} Conjunto de herramientas cargadas
 */
function loadToolboxFromDirectory(dirPath, options = {}) {
  const { recursive = false } = options;
  const toolbox = new ATDFToolbox();
  toolbox.loadToolsFromDirectory(dirPath, recursive);
  return toolbox;
}

/**
 * Encuentra la mejor herramienta para un objetivo específico
 * @param {ATDFToolbox} toolbox - Conjunto de herramientas donde buscar
 * @param {string} goal - Objetivo o tarea a realizar
 * @param {Object} [options] - Opciones adicionales
 * @param {string} [options.language] - Idioma preferido
 * @returns {ATDFTool|null} La herramienta más adecuada o null si no se encuentra ninguna
 */
function findBestTool(toolbox, goal, options = {}) {
  return toolbox.findBestTool(goal, options);
}

// Exportar clases y funciones
module.exports = {
  ATDFTool,
  ATDFToolbox,
  loadToolFromFile,
  loadToolboxFromDirectory,
  findBestTool,
  // Exportar funciones del conversor MCP
  mcpToAtdf: MCPConverter.mcpToAtdf,
  convertMcpFile: MCPConverter.convertMcpFile,
  batchConvertMcp: MCPConverter.batchConvert,
};
