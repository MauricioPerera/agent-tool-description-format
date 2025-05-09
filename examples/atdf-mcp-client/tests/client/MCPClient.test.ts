import { MCPClient } from '../../src/client/MCPClient';
import fetchMock from 'jest-fetch-mock';

describe('MCPClient', () => {
  let client: MCPClient;
  const mockServerUrl = 'http://localhost:1337/mcp';
  
  beforeEach(() => {
    fetchMock.resetMocks();
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

  describe('connect', () => {
    it('debería conectarse y obtener herramientas del servidor', async () => {
      // Configuración del mock para fetch
      fetchMock.mockResponseOnce(JSON.stringify({
        tools: [
          { name: 'tool1', description: 'Tool 1', schema: {} },
          { name: 'tool2', description: 'Tool 2', schema: {} }
        ]
      }));
      
      const tools = await client.connect();
      
      expect(tools).toHaveLength(2);
      expect(tools[0].name).toBe('tool1');
      expect(tools[1].name).toBe('tool2');
      expect(fetchMock).toHaveBeenCalledWith(
        `${mockServerUrl}/tools/list`,
        expect.objectContaining({ method: 'GET' })
      );
    });
    
    it('debería manejar errores de conexión', async () => {
      // Mock de error de red
      fetchMock.mockRejectOnce(new Error('Network error'));
      
      await expect(client.connect()).rejects.toThrow('Network error');
    });
    
    it('debería manejar respuestas de error del servidor', async () => {
      // Mock de respuesta con error del servidor
      fetchMock.mockResponseOnce('{"error":"Server error"}', { status: 500 });
      
      await expect(client.connect()).rejects.toThrow('Error al conectar al servidor MCP');
    });
    
    it('debería validar el formato de la respuesta', async () => {
      // Mock de respuesta con formato incorrecto
      fetchMock.mockResponseOnce('{"data":"invalid"}');
      
      await expect(client.connect()).rejects.toThrow('Formato de respuesta inválido');
    });
  });

  describe('callTool', () => {
    it('debería llamar correctamente a una herramienta', async () => {
      // Mock de respuesta exitosa
      fetchMock.mockResponseOnce(JSON.stringify({ result: 'success' }));
      
      const result = await client.callTool('test-tool', { param: 'value' });
      
      expect(result.status).toBe('success');
      expect(result.toolName).toBe('test-tool');
      expect(fetchMock).toHaveBeenCalledWith(
        `${mockServerUrl}/tools/call`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            name: 'test-tool',
            params: { param: 'value' }
          })
        })
      );
    });
    
    it('debería manejar errores en la llamada a la herramienta', async () => {
      // Mock de error de red
      fetchMock.mockRejectOnce(new Error('Network error'));
      
      const result = await client.callTool('test-tool', {});
      
      expect(result.status).toBe('error');
      expect(result.error).toContain('Network error');
    });
    
    it('debería manejar respuestas de error del servidor', async () => {
      // Mock de respuesta con error del servidor
      fetchMock.mockResponseOnce('{"error":"Tool execution failed"}', { status: 500 });
      
      const result = await client.callTool('test-tool', {});
      
      expect(result.status).toBe('error');
    });
  });
}); 