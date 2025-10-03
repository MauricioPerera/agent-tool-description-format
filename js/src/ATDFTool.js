/**
 * Representa una herramienta individual en formato ATDF (Agent Tool Description Format)
 */
class ATDFTool {
  /**
   * Crea una nueva instancia de ATDFTool a partir de un objeto de descripción
   * @param {Object} toolData - Objeto con la descripción de la herramienta en formato ATDF
   */
  constructor(toolData) {
    // Comprobar que tenemos los campos obligatorios
    const requiredFields = [
      'tool_id',
      'description',
      'when_to_use',
      'how_to_use',
    ];
    for (const field of requiredFields) {
      if (!toolData[field]) {
        throw new Error(
          `Campo obligatorio '${field}' no encontrado en la descripción de la herramienta`
        );
      }
    }

    // Almacenar los datos completos de la herramienta
    this.data = toolData;
  }

  /**
   * Obtiene el ID de la herramienta
   * @returns {string} ID de la herramienta
   */
  get toolId() {
    return this.data.tool_id;
  }

  /**
   * Obtiene la descripción de la herramienta
   * @param {string} [language] - Código de idioma opcional (por ejemplo, 'es', 'en')
   * @returns {string} Descripción de la herramienta
   */
  getDescription(language) {
    if (
      language &&
      this.data.localization &&
      this.data.localization[language]
    ) {
      return (
        this.data.localization[language].description || this.data.description
      );
    }
    return this.data.description;
  }

  /**
   * Obtiene cuándo usar la herramienta
   * @param {string} [language] - Código de idioma opcional (por ejemplo, 'es', 'en')
   * @returns {string} Descripción de cuándo usar la herramienta
   */
  getWhenToUse(language) {
    if (
      language &&
      this.data.localization &&
      this.data.localization[language]
    ) {
      return (
        this.data.localization[language].when_to_use || this.data.when_to_use
      );
    }
    return this.data.when_to_use;
  }

  /**
   * Obtiene los parámetros de entrada requeridos para la herramienta
   * @returns {Array} Lista de parámetros de entrada
   */
  get inputs() {
    return this.data.how_to_use.inputs || [];
  }

  /**
   * Obtiene la información de salida de la herramienta
   * @returns {Object} Información de salida
   */
  get outputs() {
    return this.data.how_to_use.outputs || {};
  }

  /**
   * Obtiene los mensajes de éxito de la herramienta
   * @returns {string} Mensaje de éxito
   */
  get successMessage() {
    return this.data.how_to_use.outputs.success || '';
  }

  /**
   * Obtiene los posibles mensajes de error de la herramienta
   * @returns {Array} Lista de posibles errores
   */
  get possibleErrors() {
    return this.data.how_to_use.outputs.failure || [];
  }

  /**
   * Comprueba si la herramienta tiene soporte para un idioma determinado
   * @param {string} language - Código de idioma (por ejemplo, 'es', 'en')
   * @returns {boolean} true si la herramienta tiene soporte para el idioma
   */
  supportsLanguage(language) {
    return !!(
      language &&
      this.data.localization &&
      this.data.localization[language]
    );
  }

  /**
   * Obtiene la lista de idiomas soportados por la herramienta
   * @returns {Array<string>} Lista de códigos de idioma soportados
   */
  get supportedLanguages() {
    const languages = ['default'];
    if (this.data.localization) {
      return [...languages, ...Object.keys(this.data.localization)];
    }
    return languages;
  }

  /**
   * Obtiene los prerrequisitos de la herramienta (si existen)
   * @returns {Object|null} Prerrequisitos de la herramienta
   */
  get prerequisites() {
    return this.data.prerequisites || null;
  }

  /**
   * Obtiene los ejemplos de uso de la herramienta (si existen)
   * @returns {Array|null} Ejemplos de uso
   */
  get examples() {
    return this.data.examples || null;
  }

  /**
   * Obtiene los metadatos de la herramienta (si existen)
   * @returns {Object|null} Metadatos de la herramienta
   */
  get metadata() {
    return this.data.metadata || null;
  }

  /**
   * Convierte la herramienta a un objeto JSON
   * @returns {Object} Representación JSON de la herramienta
   */
  toJSON() {
    return this.data;
  }

  /**
   * Genera un esquema JSON para validar las entradas de la herramienta
   * @returns {Object} Esquema JSON para validación
   */
  getInputSchema() {
    const schema = {
      type: 'object',
      properties: {},
      required: [],
    };

    for (const input of this.inputs) {
      if (input.type === 'object' && input.schema) {
        schema.properties[input.name] = input.schema;
      } else {
        schema.properties[input.name] = {
          type: input.type,
          description: input.description,
        };
      }

      if (input.required !== false) {
        schema.required.push(input.name);
      }
    }

    return schema;
  }
}

module.exports = ATDFTool;
