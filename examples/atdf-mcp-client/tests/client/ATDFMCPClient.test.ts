import { ATDFMCPClient } from '../../src/client/ATDFMCPClient';
import { MCPClient } from '../../src/client/MCPClient';
import fs from 'fs-extra';

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
  });
}); 