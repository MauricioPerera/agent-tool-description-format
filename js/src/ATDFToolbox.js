const ATDFTool = require('./ATDFTool');
const fs = require('fs');
const path = require('path');

/**
 * Clase que gestiona una colección de herramientas ATDF
 */
class ATDFToolbox {
  /**
   * Crea una nueva instancia de ATDFToolbox
   */
  constructor() {
    this.tools = [];
  }

  /**
   * Añade una herramienta al conjunto
   * @param {ATDFTool|Object} tool - Herramienta a añadir (instancia de ATDFTool o objeto de descripción)
   * @returns {ATDFTool} La herramienta añadida
   */
  addTool(tool) {
    if (!(tool instanceof ATDFTool)) {
      tool = new ATDFTool(tool);
    }

    // Comprobar si ya existe una herramienta con el mismo ID
    const existingIndex = this.tools.findIndex(t => t.toolId === tool.toolId);
    if (existingIndex >= 0) {
      this.tools[existingIndex] = tool;
    } else {
      this.tools.push(tool);
    }

    return tool;
  }

  /**
   * Elimina una herramienta del conjunto
   * @param {string} toolId - ID de la herramienta a eliminar
   * @returns {boolean} true si la herramienta se eliminó correctamente
   */
  removeTool(toolId) {
    const initialLength = this.tools.length;
    this.tools = this.tools.filter(tool => tool.toolId !== toolId);
    return this.tools.length < initialLength;
  }

  /**
   * Obtiene una herramienta por su ID
   * @param {string} toolId - ID de la herramienta a obtener
   * @returns {ATDFTool|null} Herramienta encontrada o null si no existe
   */
  getTool(toolId) {
    return this.tools.find(tool => tool.toolId === toolId) || null;
  }

  /**
   * Carga una herramienta desde un archivo JSON
   * @param {string} filePath - Ruta al archivo JSON
   * @returns {ATDFTool|null} Herramienta cargada o null si hubo un error
   */
  loadToolFromFile(filePath) {
    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const toolData = JSON.parse(fileContent);
      const tool = new ATDFTool(toolData);
      this.addTool(tool);
      return tool;
    } catch (error) {
      console.error(
        `Error al cargar la herramienta desde ${filePath}: ${error.message}`
      );
      return null;
    }
  }

  /**
   * Carga todas las herramientas desde un directorio
   * @param {string} directoryPath - Ruta al directorio que contiene archivos JSON de herramientas
   * @param {boolean} [recursive=false] - Si debe buscar en subdirectorios
   * @returns {number} Número de herramientas cargadas correctamente
   */
  loadToolsFromDirectory(directoryPath, recursive = false) {
    try {
      const files = fs.readdirSync(directoryPath);
      let loadedCount = 0;

      for (const file of files) {
        const fullPath = path.join(directoryPath, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory() && recursive) {
          // Si es un directorio y recursive es true, procesar el directorio
          loadedCount += this.loadToolsFromDirectory(fullPath, recursive);
        } else if (file.endsWith('.json')) {
          // Si es un archivo JSON, intentar cargarlo
          const tool = this.loadToolFromFile(fullPath);
          if (tool) {
            loadedCount++;
          }
        }
      }

      return loadedCount;
    } catch (error) {
      console.error(
        `Error al cargar herramientas desde ${directoryPath}: ${error.message}`
      );
      return 0;
    }
  }

  /**
   * Busca herramientas que coincidan con el texto de búsqueda
   * @param {string} searchText - Texto a buscar
   * @param {Object} [options] - Opciones de búsqueda
   * @param {string} [options.language] - Idioma preferido para la búsqueda
   * @param {boolean} [options.caseSensitive=false] - Si la búsqueda distingue mayúsculas y minúsculas
   * @returns {Array<ATDFTool>} Lista de herramientas que coinciden con la búsqueda
   */
  searchTools(searchText, options = {}) {
    const { language, caseSensitive = false } = options;
    if (!searchText) return [];

    // Normalizar el texto de búsqueda
    const normalizedText = caseSensitive
      ? searchText
      : searchText.toLowerCase();

    return this.tools.filter(tool => {
      // Obtener textos a buscar en el idioma adecuado
      const description = caseSensitive
        ? tool.getDescription(language)
        : tool.getDescription(language).toLowerCase();

      const whenToUse = caseSensitive
        ? tool.getWhenToUse(language)
        : tool.getWhenToUse(language).toLowerCase();

      // Comprobar coincidencias
      return (
        description.includes(normalizedText) ||
        whenToUse.includes(normalizedText)
      );
    });
  }

  /**
   * Encuentra la mejor herramienta para un objetivo dado
   * @param {string} goal - Objetivo o tarea a realizar
   * @param {Object} [options] - Opciones adicionales
   * @param {string} [options.language] - Idioma preferido
   * @returns {ATDFTool|null} La herramienta más adecuada o null si no se encuentra ninguna
   */
  findBestTool(goal, options = {}) {
    if (!goal) return null;

    const { language } = options;
    const results = this.searchTools(goal, { language });

    if (results.length === 0) return null;
    if (results.length === 1) return results[0];

    // Si hay múltiples resultados, podríamos implementar una lógica más sofisticada
    // para elegir el mejor, por ahora simplemente devolvemos el primero
    return results[0];
  }

  /**
   * Devuelve el número de herramientas en el conjunto
   * @returns {number} Número de herramientas
   */
  get size() {
    return this.tools.length;
  }

  /**
   * Convierte el conjunto de herramientas a un array de objetos JSON
   * @returns {Array<Object>} Array de objetos JSON con las descripciones de herramientas
   */
  toJSON() {
    return this.tools.map(tool => tool.toJSON());
  }
}

module.exports = ATDFToolbox;
