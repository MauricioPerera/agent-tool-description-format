import { ATDFMCPClient } from '../../src/client/ATDFMCPClient';
import { MCPClient } from '../../src/client/MCPClient';
import nock from 'nock';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import fetchMock from 'jest-fetch-mock';

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
    fetchMock.resetMocks();
    
    // Configurar mock para operaciones de archivo
    (fs.ensureDir as jest.Mock).mockResolvedValue(undefined);
    (fs.writeJSON as jest.Mock).mockResolvedValue(undefined);
    (fs.ensureDirSync as jest.Mock).mockReturnValue(undefined);
    (fs.writeJsonSync as jest.Mock).mockReturnValue(undefined);
  });
  
  afterAll(() => {
    // Limpieza final
    nock.restore();
  });
  
  describe('Flujo de descubrimiento y ejecución', () => {
    it('debería descubrir herramientas, convertirlas y ejecutarlas', async () => {
      // Usamos fetchMock en lugar de nock para mayor compatibilidad
      fetchMock.mockResponseOnce(JSON.stringify({
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
      }));
      
      fetchMock.mockResponseOnce(JSON.stringify({
        temperature: 22,
        condition: 'Soleado',
        humidity: 45
      }));
      
      // Crear cliente ATDF-MCP
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // Conectar y descubrir herramientas
      await client.connect();
      
      // Verificar herramientas ATDF convertidas
      const atdfTools = client.getATDFTools();
      expect(atdfTools).toHaveLength(1);
      expect(atdfTools[0].tool_id).toBe('weather');
      expect(atdfTools[0].how_to_use.inputs).toHaveLength(1);
      expect(atdfTools[0].how_to_use.inputs[0].name).toBe('city');
      
      // Ejecutar herramienta ATDF
      const result = await client.executeATDFTool('weather', {
        city: 'Madrid'
      });
      
      // Verificar resultado
      expect(result.status).toBe('success');
      expect(result.result).toEqual({
        temperature: 22,
        condition: 'Soleado',
        humidity: 45
      });
      
      // Guardar herramientas en archivos
      client.saveATDFToolsToDirectory(tempDir);
      
      // Verificar que se guardaron correctamente
      expect(fs.ensureDirSync).toHaveBeenCalledWith(tempDir);
      expect(fs.writeJsonSync).toHaveBeenCalledWith(
        path.join(tempDir, 'weather.json'),
        expect.objectContaining({ tool_id: 'weather' }),
        { spaces: 2 }
      );
    });
  });
  
  describe('Flujo de conversión y persistencia', () => {
    it('debería convertir herramientas MCP y guardarlas como ATDF', async () => {
      // Usar fetchMock en lugar de nock
      fetchMock.mockResponseOnce(JSON.stringify({
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
      }));
      
      // Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // Conectar y obtener herramientas
      await client.connect();
      
      // Verificar herramientas ATDF
      const atdfTools = client.getATDFTools();
      expect(atdfTools).toHaveLength(2);
      
      // Guardar en directorio
      client.saveATDFToolsToDirectory(tempDir);
      
      // Verificar operaciones de archivo
      expect(fs.ensureDirSync).toHaveBeenCalledWith(tempDir);
      expect(fs.writeJsonSync).toHaveBeenCalledTimes(2);
      
      // Verificar contenido específico
      const fetchToolPath = path.join(tempDir, 'fetch.json');
      
      expect(fs.writeJsonSync).toHaveBeenCalledWith(
        expect.stringContaining('fetch.json'),
        expect.objectContaining({ 
          tool_id: 'fetch',
          how_to_use: expect.objectContaining({
            inputs: expect.arrayContaining([
              expect.objectContaining({ name: 'url', required: true }),
              expect.objectContaining({ name: 'method', required: false })
            ])
          })
        }),
        expect.anything()
      );
    });
  });
  
  describe('Manejo de errores', () => {
    it('debería manejar errores de servidor correctamente', async () => {
      // Mock para error del servidor
      fetchMock.mockRejectOnce(new Error('Error al conectar al servidor MCP'));
      
      // Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // Intentar conectar (debería fallar)
      await expect(client.connect()).rejects.toThrow();
    });
    
    it('debería manejar errores de validación de parámetros', async () => {
      // Mock para la respuesta de herramientas
      fetchMock.mockResponseOnce(JSON.stringify({
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
      }));
      
      // Crear cliente
      const client = new ATDFMCPClient(`${mockServerUrl}${mockServerPath}`);
      
      // Conectar
      await client.connect();
      
      // Intentar ejecutar sin parámetros requeridos (devuelve el objeto de error)
      const result = await client.executeATDFTool('search', {});
      expect(result).toEqual(expect.objectContaining({
        status: 'error',
        error: expect.stringContaining('Parámetro requerido')
      }));
    });
  });
}); 