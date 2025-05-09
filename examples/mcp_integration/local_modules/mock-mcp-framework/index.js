/**
 * Mock simple del MCP Framework para pruebas
 */

class MCPTool {
  constructor() {
    this.name = '';
    this.description = '';
    this.schema = {};
  }
    
  async execute(params) {
    return { result: 'Método execute debe ser implementado' };
  }
}

class MCPServer {
  constructor() {
    this.tools = [];
  }
    
  registerTool(tool) {
    this.tools.push(tool);
    console.log(`Herramienta registrada: ${tool.name}`);
    return this;
  }
    
  async start() {
    console.log("Servidor MCP Mock iniciado con éxito");
    console.log("Herramientas disponibles:");
    for (const tool of this.tools) {
      console.log(` - ${tool.name}: ${tool.description}`);
    }
    return this;
  }
}

// Exportar las clases simuladas
module.exports = {
  MCPTool,
  MCPServer
}; 