import { MCPClient } from '../../src/client/MCPClient';

describe('MCPClient', () => {
  let client: MCPClient;
  const mockServerUrl = 'http://localhost:1337/mcp';
  
  beforeEach(() => {
    client = new MCPClient(mockServerUrl);
  });
  
  describe('constructor', () => {
    it('debería inicializar correctamente con URL como string', () => {
      const client = new MCPClient(mockServerUrl);
      expect(client).toBeDefined();
    });
    
    it('debería inicializar correctamente con opciones', () => {
      const client = new MCPClient({ baseUrl: mockServerUrl, timeout: 5000 });
      expect(client).toBeDefined();
    });
  });
  
  describe('getTools', () => {
    it('debería devolver array vacío si no se ha conectado', () => {
      const tools = client.getTools();
      expect(tools).toEqual([]);
    });
  });
  
  describe('findTool', () => {
    it('debería devolver undefined si no hay herramientas', () => {
      const tool = client.findTool('non-existent');
      expect(tool).toBeUndefined();
    });
    
    it('debería encontrar una herramienta por nombre', () => {
      // Forzamos el acceso a la propiedad tools para simular que hay herramientas
      // Esto es solo para pruebas
      (client as any).tools = [
        { name: 'test-tool', description: 'Test tool' }
      ];
      
      const tool = client.findTool('test-tool');
      expect(tool).toBeDefined();
      expect(tool?.name).toBe('test-tool');
    });
  });
}); 