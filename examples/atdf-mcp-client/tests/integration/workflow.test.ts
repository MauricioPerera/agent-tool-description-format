import { ATDFMCPClient } from '../../src/client/ATDFMCPClient';
import { MCPClient } from '../../src/client/MCPClient';
import nock from 'nock';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';

// Mock para fs-extra
jest.mock('fs-extra');

describe('Flujos de trabajo de integración', () => {
  // Configuración para servidor mock
  const mockServerUrl = 'http://localhost:1337';
  const mockServerPath = '/mcp';
  
  // Directorio temporal para pruebas
  let tempDir: string;
  
  beforeAll(() => {
    // Crear directorio temporal
    tempDir = path.join(os.tmpdir(), 'atdf-mcp-tests');
  });
  
  beforeEach(() => {
    // Limpiar mocks y reiniciar interceptores de red
    jest.clearAllMocks();
    nock.cleanAll();
    
    // Configurar mock para operaciones de archivo
    (fs.ensureDir as jest.Mock).mockResolvedValue(undefined);
    (fs.writeJSON as jest.Mock).mockResolvedValue(undefined);
  });
  
  afterAll(() => {
    // Limpieza final
    nock.restore();
  });
  
  describe('Flujo de descubrimiento y ejecución', () => {
    it('debería descubrir herramientas, convertirlas y ejecutarlas', async () => {
      // 1. Configurar mock para servidor MCP
      const scope = nock(mockServerUrl)
        // Endpoint de descubrimiento
        .get(`${mockServerPath}/tools/list`)
        .reply(200, {
          tools: [
            {
              name: 'weather',
              description: 'Obtener información del clima',
              schema: {
                city: {
                  type: { name: 'string' },
                  description: 'Ciudad para obtener clima',
                  required: true
                }
              }
            }
          ]
        })
        // Endpoint de ejecución
        .post(`${mockServerPath}/tools/call`)
        .reply(200, {
          result: {
            temperature: 22,
            condition: 'Soleado',
            humidity: 45
          },
          status: 'success',
          toolName: 'weather'
        });
      
      // 2. Crear cliente ATDF-MCP
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // 3. Conectar y descubrir herramientas
      await client.connect();
      
      // 4. Verificar herramientas ATDF convertidas
      const atdfTools = client.getATDFTools();
      expect(atdfTools).toHaveLength(1);
      expect(atdfTools[0].tool_id).toBe('weather');
      expect(atdfTools[0].how_to_use.inputs).toHaveLength(1);
      expect(atdfTools[0].how_to_use.inputs[0].name).toBe('city');
      
      // 5. Ejecutar herramienta ATDF
      const result = await client.executeATDFTool('weather', {
        city: 'Madrid'
      });
      
      // 6. Verificar resultado
      expect(result).toEqual({
        result: {
          temperature: 22,
          condition: 'Soleado',
          humidity: 45
        },
        status: 'success',
        toolName: 'weather'
      });
      
      // 7. Guardar herramientas en archivos
      await client.saveATDFToolsToDirectory(tempDir);
      
      // 8. Verificar que se guardaron correctamente
      expect(fs.ensureDir).toHaveBeenCalledWith(tempDir);
      expect(fs.writeJSON).toHaveBeenCalledWith(
        path.join(tempDir, 'weather.json'),
        expect.objectContaining({ tool_id: 'weather' }),
        { spaces: 2 }
      );
      
      // 9. Verificar que todas las peticiones se realizaron
      scope.done();
    });
  });
  
  describe('Flujo de conversión y persistencia', () => {
    it('debería convertir herramientas MCP y guardarlas como ATDF', async () => {
      // 1. Configurar mock para servidor MCP
      const scope = nock(mockServerUrl)
        .get(`${mockServerPath}/tools/list`)
        .reply(200, {
          tools: [
            {
              name: 'fetch',
              description: 'Realizar petición HTTP',
              schema: {
                url: {
                  type: { name: 'string' },
                  description: 'URL a consultar',
                  required: true
                },
                method: {
                  type: { name: 'string' },
                  description: 'Método HTTP',
                  required: false
                }
              }
            },
            {
              name: 'calculator',
              description: 'Realizar cálculos matemáticos',
              schema: {
                expression: {
                  type: { name: 'string' },
                  description: 'Expresión a evaluar',
                  required: true
                }
              }
            }
          ]
        });
      
      // 2. Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // 3. Conectar y obtener herramientas
      await client.connect();
      
      // 4. Verificar herramientas ATDF
      const atdfTools = client.getATDFTools();
      expect(atdfTools).toHaveLength(2);
      
      // 5. Guardar en directorio
      await client.saveATDFToolsToDirectory(tempDir);
      
      // 6. Verificar operaciones de archivo
      expect(fs.ensureDir).toHaveBeenCalledWith(tempDir);
      expect(fs.writeJSON).toHaveBeenCalledTimes(2);
      
      // 7. Verificar contenido específico
      const fetchToolPath = path.join(tempDir, 'fetch.json');
      
      expect(fs.writeJSON).toHaveBeenCalledWith(
        fetchToolPath,
        expect.objectContaining({ 
          tool_id: 'fetch',
          how_to_use: expect.objectContaining({
            inputs: expect.arrayContaining([
              expect.objectContaining({ name: 'url', required: true }),
              expect.objectContaining({ name: 'method', required: false })
            ])
          })
        }),
        { spaces: 2 }
      );
      
      // Verificar que se completaron todas las peticiones
      scope.done();
    });
  });
  
  describe('Manejo de errores', () => {
    it('debería manejar errores de servidor correctamente', async () => {
      // 1. Configurar mock para servidor con error
      const scope = nock(mockServerUrl)
        .get(`${mockServerPath}/tools/list`)
        .reply(500, { error: 'Error interno del servidor' });
      
      // 2. Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // 3. Intentar conectar (debería fallar)
      await expect(client.connect()).rejects.toThrow('Error al conectar al servidor MCP');
      
      // 4. Verificar que la petición se realizó
      scope.done();
    });
    
    it('debería manejar errores de validación de parámetros', async () => {
      // 1. Configurar mock para servidor
      const scope = nock(mockServerUrl)
        // Endpoint de descubrimiento
        .get(`${mockServerPath}/tools/list`)
        .reply(200, {
          tools: [
            {
              name: 'search',
              description: 'Buscar información',
              schema: {
                query: {
                  type: { name: 'string' },
                  description: 'Término de búsqueda',
                  required: true
                }
              }
            }
          ]
        })
        // Endpoint de ejecución con error
        .post(`${mockServerPath}/tools/call`)
        .reply(200, {
          error: 'Parámetro requerido faltante: query',
          result: null,
          status: 'error',
          toolName: 'search'
        });
      
      // 2. Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // 3. Conectar
      await client.connect();
      
      // 4. Intentar ejecutar sin parámetros requeridos (devuelve el objeto de error)
      const result = await client.executeATDFTool('search', {});
      expect(result).toEqual({
        error: 'Parámetro requerido faltante: query',
        result: null,
        status: 'error',
        toolName: 'search'
      });
      
      // 5. Verificar que la petición se realizó
      scope.done();
    });
  });
}); 