/**
 * Adaptador para utilizar herramientas ATDF directamente en MCP Framework.
 * 
 * Este módulo proporciona clases y utilidades para integrar herramientas ATDF
 * dentro de una aplicación que utiliza MCP Framework.
 */

const { atdfToMcp } = require('./AtdfToMcp');

/**
 * Clase base para adaptar herramientas ATDF a MCP Framework.
 * Esta clase debe ser extendida para definir la implementación de execute().
 */
class ATDFToolAdapter {
    /**
     * Crea un nuevo adaptador de herramienta ATDF.
     * 
     * @param {Object} atdfDefinition - Definición de herramienta en formato ATDF.
     * @param {Function} implementation - Función de implementación para la herramienta.
     * @param {Object} options - Opciones adicionales para la conversión.
     */
    constructor(atdfDefinition, implementation, options = {}) {
        this.atdfDefinition = atdfDefinition;
        this.implementation = implementation;
        
        // Convertir ATDF a formato MCP
        this.mcpDefinition = atdfToMcp(atdfDefinition, options);
        
        // Propiedades principales que necesita MCP Framework
        this.name = this.mcpDefinition.name;
        this.description = this.mcpDefinition.description;
        
        // Configurar el esquema para MCP Framework
        this.schema = this._buildMCPSchema();
    }
    
    /**
     * Construye el esquema en formato Zod compatible con MCP Framework.
     * Nota: Esta implementación es una simulación, en un entorno real
     * se utilizarían las definiciones reales de Zod.
     * 
     * @returns {Object} Esquema compatible con MCP Framework
     */
    _buildMCPSchema() {
        const schema = {};
        const inputs = this.atdfDefinition.how_to_use.inputs;
        
        // Simular la conversión de tipos ATDF a tipos Zod
        // En un entorno real, se usaría el paquete zod importado
        for (const input of inputs) {
            schema[input.name] = {
                type: this._zodTypeFor(input.type),
                description: input.description
            };
        }
        
        return schema;
    }
    
    /**
     * Simula la conversión de tipos ATDF a tipos Zod.
     * En un entorno real, se utilizarían las definiciones reales de Zod.
     * 
     * @param {string} atdfType - Tipo de dato en formato ATDF
     * @returns {Object} Simulación de tipo Zod
     */
    _zodTypeFor(atdfType) {
        // Simulación. En código real esto sería:
        // return atdfType === 'string' ? z.string() : z.number() ...etc
        return { type: atdfType };
    }
    
    /**
     * Método para ejecutar la herramienta.
     * Esta implementación llama a la función de implementación proporcionada.
     * 
     * @param {Object} params - Parámetros de entrada para la herramienta
     * @returns {Promise<any>} Resultado de la ejecución
     */
    async execute(params) {
        // Validación básica
        this._validateRequiredParams(params);
        
        // Ejecutar la implementación proporcionada
        return this.implementation(params);
    }
    
    /**
     * Valida que los parámetros requeridos estén presentes.
     * 
     * @param {Object} params - Parámetros a validar
     * @throws {Error} Si faltan parámetros requeridos
     */
    _validateRequiredParams(params) {
        const inputs = this.atdfDefinition.how_to_use.inputs;
        const requiredInputs = inputs.filter(input => input.required);
        
        for (const input of requiredInputs) {
            if (params[input.name] === undefined) {
                throw new Error(`Falta el parámetro requerido: ${input.name}`);
            }
        }
    }
}

/**
 * Función auxiliar para crear un adaptador listo para usar en MCP Framework.
 * 
 * @param {Object} atdfDefinition - Definición de herramienta en formato ATDF
 * @param {Function} implementation - Implementación de la herramienta
 * @param {Object} options - Opciones adicionales
 * @returns {Object} Un objeto compatible con MCPTool
 */
function createMCPToolFromATDF(atdfDefinition, implementation, options = {}) {
    // Crear una clase anónima que extiende ATDFToolAdapter
    const adapter = new ATDFToolAdapter(atdfDefinition, implementation, options);
    
    // Devolver un objeto con la estructura que espera MCP Framework
    return {
        name: adapter.name,
        description: adapter.description,
        schema: adapter.schema,
        execute: adapter.execute.bind(adapter)
    };
}

/**
 * Factory para crear un adaptador MCP-Framework usando la clase ATDFToolAdapter.
 * 
 * @param {Object} atdfDefinition - Definición de herramienta en formato ATDF
 * @returns {Function} Una función factory que recibe la implementación
 */
function adaptATDFTool(atdfDefinition) {
    return function(implementation, options = {}) {
        return createMCPToolFromATDF(atdfDefinition, implementation, options);
    };
}

// Exportar las funciones y clases
module.exports = {
    ATDFToolAdapter,
    createMCPToolFromATDF,
    adaptATDFTool
}; 