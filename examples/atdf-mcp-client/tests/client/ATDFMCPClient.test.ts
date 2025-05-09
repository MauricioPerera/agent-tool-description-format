import { ATDFMCPClient } from '../../src/client/ATDFMCPClient';
import { MCPClient } from '../../src/client/MCPClient';
import fs from 'fs-extra';
import fetchMock from 'jest-fetch-mock';
import { ATDFTool } from '../../src/types';

// Mock para fs-extra
jest.mock('fs-extra', () => ({
  ensureDir: jest.fn(),
  writeJSON: jest.fn(),
  readJSON: jest.fn(),
  ensureDirSync: jest.fn(),
  writeJsonSync: jest.fn()
}));

describe('ATDFMCPClient', () => {
  let client: ATDFMCPClient;
  const mockServerUrl = 'http://localhost:1337/mcp';
  
  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.resetMocks();
    client = new ATDFMCPClient(mockServerUrl);
  });
  
  describe('constructor', () => {
    it('debería inicializar correctamente con URL como string', () => {
      const client = new ATDFMCPClient(mockServerUrl);
      expect(client).toBeDefined();
      expect(client).toBeInstanceOf(MCPClient);
    });
    
    it('debería inicializar correctamente con opciones personalizadas', () => {
      const client = new ATDFMCPClient({ baseUrl: mockServerUrl, timeout: 5000 });
      expect(client).toBeDefined();
    });

    it('debería inicializar correctamente con opciones de conversión', () => {
      const conversionOptions = {
        includeWhenToUse: true,
        defaultWhenToUse: 'Usar cuando necesites esta herramienta'
      };
      
      const client = new ATDFMCPClient(
        mockServerUrl, 
        { baseUrl: mockServerUrl, timeout: 5000 },
        conversionOptions
      );
      
      expect(client).toBeDefined();
      
      // Verificar que se aplican las opciones de conversión al convertir
      const mockTool = {
        name: 'test-tool',
        description: 'Test tool',
        schema: {}
      };
      
      const atdfTool = client.convertToolToATDF(mockTool);
      expect(atdfTool.when_to_use).toBe(conversionOptions.defaultWhenToUse);
    });
  });
  
  describe('getATDFTools', () => {
    it('debería devolver array vacío si no hay herramientas MCP', () => {
      const tools = client.getATDFTools();
      expect(tools).toEqual([]);
    });
    
    it('debería devolver herramientas en formato ATDF', () => {
      // Forzamos acceso a propiedades internas para pruebas
      (client as any).atdfTools = [
        {
          tool_id: 'test-tool',
          schema_version: '1.0.0',
          description: 'Test Tool',
          how_to_use: {
            inputs: [],
            outputs: {
              success: {},
              failure: []
            }
          }
        }
      ];
      
      const tools = client.getATDFTools();
      expect(tools).toHaveLength(1);
      expect(tools[0].tool_id).toBe('test-tool');
    });
  });
  
  describe('saveATDFToolsToDirectory', () => {
    it('debería guardar herramientas ATDF en archivos', async () => {
      // Mock para fs.ensureDirSync y fs.writeJsonSync
      (fs.ensureDirSync as jest.Mock).mockReturnValue(undefined);
      (fs.writeJsonSync as jest.Mock).mockReturnValue(undefined);
      
      // Forzamos acceso a propiedades internas para pruebas
      (client as any).atdfTools = [
        {
          tool_id: 'tool1',
          schema_version: '1.0.0',
          description: 'Tool 1',
          how_to_use: {
            inputs: [],
            outputs: {
              success: {},
              failure: []
            }
          }
        },
        {
          tool_id: 'tool2',
          schema_version: '1.0.0',
          description: 'Tool 2',
          how_to_use: {
            inputs: [],
            outputs: {
              success: {},
              failure: []
            }
          }
        }
      ];
      
      const result = client.saveATDFToolsToDirectory('./output-dir');
      
      expect(fs.ensureDirSync).toHaveBeenCalledWith('./output-dir');
      expect(fs.writeJsonSync).toHaveBeenCalledTimes(2);
      expect(fs.writeJsonSync).toHaveBeenCalledWith(
        expect.stringContaining('output-dir/tool1.json'),
        expect.objectContaining({ tool_id: 'tool1' }),
        { spaces: 2 }
      );
      expect(result).toHaveLength(2);
    });
    
    it('debería manejar errores al guardar archivos', async () => {
      // Mock error para fs.ensureDirSync
      (fs.ensureDirSync as jest.Mock).mockImplementation(() => {
        throw new Error('Error al crear directorio');
      });
      
      // Forzamos acceso a propiedades internas para pruebas
      (client as any).atdfTools = [{ 
        tool_id: 'test-tool',
        schema_version: '1.0.0',
        how_to_use: {
          inputs: [],
          outputs: { success: {} }
        }
      }];
      
      expect(() => {
        client.saveATDFToolsToDirectory('./output-dir');
      }).toThrow();
    });

    it('debería respetar la opción pretty=false', () => {
      // Mock para fs.ensureDirSync y fs.writeJsonSync
      (fs.ensureDirSync as jest.Mock).mockReturnValue(undefined);
      (fs.writeJsonSync as jest.Mock).mockReturnValue(undefined);
      
      // Forzamos acceso a propiedades internas para pruebas
      (client as any).atdfTools = [
        {
          tool_id: 'tool1',
          schema_version: '1.0.0',
          description: 'Tool 1',
          how_to_use: {
            inputs: [],
            outputs: { success: {} }
          }
        }
      ];
      
      const result = client.saveATDFToolsToDirectory('./output-dir', false);
      
      expect(fs.writeJsonSync).toHaveBeenCalledWith(
        expect.stringContaining('output-dir/tool1.json'),
        expect.objectContaining({ tool_id: 'tool1' }),
        { spaces: 0 }
      );
    });
  });

  describe('connect', () => {
    it('debería conectar y convertir herramientas MCP a ATDF', async () => {
      // Mock para la respuesta de herramientas MCP
      fetchMock.mockResponseOnce(JSON.stringify({
        tools: [
          { name: 'tool1', description: 'Tool 1', schema: {} },
          { name: 'tool2', description: 'Tool 2', schema: {} }
        ]
      }));
      
      await client.connect();
      
      // Verificar que se convirtieron las herramientas
      const atdfTools = client.getATDFTools();
      expect(atdfTools).toHaveLength(2);
      expect(atdfTools[0].tool_id).toBe('tool1');
      expect(atdfTools[1].tool_id).toBe('tool2');
    });
  });
  
  describe('findATDFTool', () => {
    it('debería encontrar una herramienta por su ID', () => {
      // Configurar herramientas ATDF
      (client as any).atdfTools = [
        { tool_id: 'tool1', description: 'Tool 1' },
        { tool_id: 'tool2', description: 'Tool 2' }
      ];
      
      const tool = client.findATDFTool('tool2');
      expect(tool).toBeDefined();
      expect(tool?.tool_id).toBe('tool2');
    });
    
    it('debería devolver undefined si no encuentra la herramienta', () => {
      // Configurar herramientas ATDF
      (client as any).atdfTools = [
        { tool_id: 'tool1', description: 'Tool 1' }
      ];
      
      const tool = client.findATDFTool('non-existent');
      expect(tool).toBeUndefined();
    });
  });
  
  describe('executeATDFTool', () => {
    it('debería ejecutar una herramienta ATDF correctamente', async () => {
      // Configurar herramientas ATDF
      (client as any).atdfTools = [
        {
          tool_id: 'weather',
          description: 'Weather information',
          how_to_use: {
            inputs: [
              { name: 'city', description: 'City name', type: 'string', required: true }
            ],
            outputs: { success: 'Weather data' }
          }
        }
      ];
      
      // Mock para la respuesta de la llamada a la herramienta
      fetchMock.mockResponseOnce(JSON.stringify({
        temperature: 25,
        condition: 'Sunny'
      }));
      
      const result = await client.executeATDFTool('weather', { city: 'Madrid' });
      
      expect(result.status).toBe('success');
      expect(result.toolName).toBe('weather');
      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(fetchMock).toHaveBeenCalledWith(
        `${mockServerUrl}/tools/call`,
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Madrid')
        })
      );
    });
    
    it('debería manejar herramientas que no existen', async () => {
      const result = await client.executeATDFTool('non-existent', {});
      
      expect(result.status).toBe('error');
      expect(result.error).toContain('Herramienta ATDF no encontrada');
      expect(fetchMock).not.toHaveBeenCalled();
    });
    
    it('debería validar parámetros requeridos', async () => {
      // Configurar herramientas ATDF
      (client as any).atdfTools = [
        {
          tool_id: 'weather',
          description: 'Weather information',
          how_to_use: {
            inputs: [
              { name: 'city', description: 'City name', type: 'string', required: true }
            ],
            outputs: { success: 'Weather data' }
          }
        }
      ];
      
      // Ejecutar sin parámetro requerido
      const result = await client.executeATDFTool('weather', {});
      
      expect(result.status).toBe('error');
      expect(result.error).toContain('Parámetro requerido faltante');
      expect(fetchMock).not.toHaveBeenCalled();
    });
    
    it('debería validar tipos de parámetros', async () => {
      // Configurar herramientas ATDF
      (client as any).atdfTools = [
        {
          tool_id: 'calculator',
          description: 'Calculator',
          how_to_use: {
            inputs: [
              { name: 'number', description: 'A number', type: 'number', required: true }
            ],
            outputs: { success: 'Result' }
          }
        }
      ];
      
      // Ejecutar con tipo incorrecto
      const result = await client.executeATDFTool('calculator', { number: 'not-a-number' });
      
      expect(result.status).toBe('error');
      expect(result.error).toContain('Tipo incorrecto');
      expect(fetchMock).not.toHaveBeenCalled();
    });
  });

  describe('validateParams', () => {
    // Exponer el método privado para poder probarlo
    const validateParams = (atdfTool: ATDFTool, params: any): string | null => {
      return (client as any).validateParams(atdfTool, params);
    };

    it('debería validar parámetros de tipo array correctamente', () => {
      const tool: ATDFTool = {
        tool_id: 'array-test',
        schema_version: '1.0.0',
        description: 'Test Array',
        how_to_use: {
          inputs: [
            { name: 'items', description: 'Array de items', type: 'array', required: true }
          ],
          outputs: { success: 'Resultado' }
        }
      };
      
      // Parámetro correcto
      const validResult = validateParams(tool, { items: [1, 2, 3] });
      expect(validResult).toBeNull();
      
      // Parámetro incorrecto
      const invalidResult = validateParams(tool, { items: 'no es un array' });
      expect(invalidResult).toContain('Tipo incorrecto para items');
    });

    it('debería validar parámetros de tipo object correctamente', () => {
      const tool: ATDFTool = {
        tool_id: 'object-test',
        schema_version: '1.0.0',
        description: 'Test Object',
        how_to_use: {
          inputs: [
            { name: 'config', description: 'Configuración', type: 'object', required: true }
          ],
          outputs: { success: 'Resultado' }
        }
      };
      
      // Parámetro correcto
      const validResult = validateParams(tool, { config: { key: 'value' } });
      expect(validResult).toBeNull();
      
      // Array no es un objeto válido para este caso
      const invalidResult1 = validateParams(tool, { config: [1, 2, 3] });
      expect(invalidResult1).toContain('Tipo incorrecto para config');
      
      // String no es un objeto
      const invalidResult2 = validateParams(tool, { config: 'no es un objeto' });
      expect(invalidResult2).toContain('Tipo incorrecto para config');
    });

    it('debería validar parámetros de tipo boolean correctamente', () => {
      const tool: ATDFTool = {
        tool_id: 'boolean-test',
        schema_version: '1.0.0',
        description: 'Test Boolean',
        how_to_use: {
          inputs: [
            { name: 'flag', description: 'Bandera', type: 'boolean', required: true }
          ],
          outputs: { success: 'Resultado' }
        }
      };
      
      // Parámetros correctos
      expect(validateParams(tool, { flag: true })).toBeNull();
      expect(validateParams(tool, { flag: false })).toBeNull();
      
      // Parámetros incorrectos
      expect(validateParams(tool, { flag: 'true' })).toContain('Tipo incorrecto para flag');
      expect(validateParams(tool, { flag: 1 })).toContain('Tipo incorrecto para flag');
    });

    it('debería ignorar parámetros no requeridos que son undefined o null', () => {
      const tool: ATDFTool = {
        tool_id: 'optional-test',
        schema_version: '1.0.0',
        description: 'Test Opcionales',
        how_to_use: {
          inputs: [
            { name: 'required', description: 'Requerido', type: 'string', required: true },
            { name: 'optional', description: 'Opcional', type: 'string', required: false }
          ],
          outputs: { success: 'Resultado' }
        }
      };
      
      // Sin el parámetro opcional
      expect(validateParams(tool, { required: 'valor' })).toBeNull();
      
      // Con parámetro opcional null
      expect(validateParams(tool, { required: 'valor', optional: null })).toBeNull();
      
      // Con parámetro opcional undefined
      expect(validateParams(tool, { required: 'valor', optional: undefined })).toBeNull();
      
      // Sin parámetro requerido
      expect(validateParams(tool, { optional: 'valor' })).toContain('Parámetro requerido faltante');
      
      // Con parámetro requerido null
      expect(validateParams(tool, { required: null, optional: 'valor' })).toContain('Parámetro requerido faltante');
    });

    it('debería validar tipos desconocidos como válidos', () => {
      const tool: ATDFTool = {
        tool_id: 'unknown-test',
        schema_version: '1.0.0',
        description: 'Test Desconocido',
        how_to_use: {
          inputs: [
            { name: 'data', description: 'Datos', type: 'any', required: true }
          ],
          outputs: { success: 'Resultado' }
        }
      };
      
      // Cualquier tipo debería ser válido
      expect(validateParams(tool, { data: 'string' })).toBeNull();
      expect(validateParams(tool, { data: 123 })).toBeNull();
      expect(validateParams(tool, { data: true })).toBeNull();
      expect(validateParams(tool, { data: { key: 'value' } })).toBeNull();
      expect(validateParams(tool, { data: [1, 2, 3] })).toBeNull();
    });
  });
}); 