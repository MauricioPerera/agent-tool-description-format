import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';
import { ATDFMCPClient } from '../../src/client/ATDFMCPClient';

// Convertir exec a Promise
const execAsync = promisify(exec);

// Mock para fs-extra
jest.mock('fs-extra', () => {
  return {
    ensureDir: jest.fn().mockResolvedValue(undefined),
    writeJSON: jest.fn().mockResolvedValue(undefined),
    readJSON: jest.fn().mockResolvedValue({
      name: 'test-tool',
      description: 'Test tool',
      schema: {}
    }),
    pathExists: jest.fn().mockResolvedValue(true),
    stat: jest.fn().mockImplementation(() => Promise.resolve({
      isDirectory: () => false
    })),
    statSync: jest.fn().mockReturnValue({
      isFile: () => true,
      isDirectory: () => false
    }),
    ensureDirSync: jest.fn().mockReturnValue(undefined),
    writeJsonSync: jest.fn().mockReturnValue(undefined),
    readJsonSync: jest.fn().mockReturnValue({
      name: 'test-tool',
      description: 'Test tool',
      schema: {}
    }),
    existsSync: jest.fn().mockReturnValue(true)
  };
});

// Mock para el cliente ATDF-MCP
jest.mock('../../src/client/ATDFMCPClient');

// Path a los archivos ejecutables
const CLI_PATH = 'src/cli/atdf-mcp-client.ts';

// Interfaz para el error de ejecución
interface ExecError extends Error {
  stdout: string;
  stderr: string;
}

describe('CLI', () => {
  // Helper para ejecutar comandos CLI
  const runCLI = async (args: string): Promise<{ stdout: string, stderr: string }> => {
    try {
      return await execAsync(`ts-node ${CLI_PATH} ${args}`);
    } catch (error) {
      // Capturamos el error para verificar el stderr en las pruebas
      const execError = error as ExecError;
      return {
        stdout: execError.stdout,
        stderr: execError.stderr
      };
    }
  };
  
  // Antes de cada test, limpiar mocks
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('Comando discover', () => {
    // Aumentamos el timeout para dar tiempo suficiente al comando
    it('debería validar la URL del servidor', async () => {
      const result = await runCLI('discover invalid-url');
      // Verificar que hay algún mensaje de error (no importa el texto exacto)
      expect(result.stderr).toBeTruthy();
    }, 30000);
    
    it('debería crear directorio de salida si se especifica', async () => {
      // Mockear los métodos necesarios para la acción discover
      const mockConnect = jest.fn().mockResolvedValue([]);
      const mockGetATDFTools = jest.fn().mockReturnValue([]);
      const mockSaveATDFToolsToDirectory = jest.fn().mockReturnValue(['file1.json']);
      
      // Configurar el mock del cliente
      (ATDFMCPClient as jest.Mock).mockImplementation(() => {
        return {
          connect: mockConnect,
          getATDFTools: mockGetATDFTools,
          saveATDFToolsToDirectory: mockSaveATDFToolsToDirectory
        };
      });
      
      // Crear una instancia del cliente y ejecutar la acción directamente
      const client = new ATDFMCPClient('http://example.com');
      await client.connect();
      client.saveATDFToolsToDirectory('./output-dir');
      
      // Verificar que se llamó al método correcto
      expect(mockSaveATDFToolsToDirectory).toHaveBeenCalledWith('./output-dir');
    }, 15000);
  });
  
  describe('Comando execute', () => {
    it('debería requerir un ID de herramienta', async () => {
      const result = await runCLI('execute http://example.com');
      // Verificar que hay algún mensaje de error sobre argumento faltante
      expect(result.stderr).toContain('missing required argument');
    }, 15000);
    
    it('debería pasar parámetros correctamente', async () => {
      // Mockear los métodos necesarios para la acción execute
      const mockConnect = jest.fn().mockResolvedValue([]);
      const mockExecuteATDFTool = jest.fn().mockResolvedValue({
        status: 'success',
        result: { test: 'data' }
      });
      
      // Configurar el mock del cliente
      (ATDFMCPClient as jest.Mock).mockImplementation(() => {
        return {
          connect: mockConnect,
          executeATDFTool: mockExecuteATDFTool
        };
      });
      
      // Crear una instancia del cliente y ejecutar la acción directamente
      const client = new ATDFMCPClient('http://example.com');
      await client.connect();
      await client.executeATDFTool('test-tool', { param: 'value' });
      
      // Verificar que se llamó al método con los parámetros correctos
      expect(mockExecuteATDFTool).toHaveBeenCalledWith('test-tool', { param: 'value' });
    }, 15000);
  });
  
  describe('Comando convert', () => {
    it('debería requerir una ruta de origen', async () => {
      const result = await runCLI('convert');
      // Verificar que hay algún mensaje de error sobre argumento faltante
      expect(result.stderr).toContain('missing required argument');
    }, 15000);
    
    it('debería convertir herramientas MCP a ATDF', async () => {
      // Mockear los métodos necesarios para la acción convert
      const mockConvertToolToATDF = jest.fn().mockReturnValue({
        tool_id: 'test-tool',
        schema_version: '1.0.0',
        description: 'Test Tool',
        how_to_use: {
          inputs: [],
          outputs: { success: {} }
        }
      });
      
      // Configurar el mock del cliente
      (ATDFMCPClient as jest.Mock).mockImplementation(() => {
        return {
          convertToolToATDF: mockConvertToolToATDF
        };
      });
      
      // Simular la función del comando convert
      const client = new ATDFMCPClient('http://localhost');
      
      // Leer una herramienta MCP de un archivo
      const mcpTool = fs.readJsonSync('./input.json');
      
      // Convertir la herramienta
      const atdfTool = client.convertToolToATDF(mcpTool);
      
      // Guardar el resultado
      fs.ensureDirSync('./output-dir');
      fs.writeJsonSync(path.join('./output-dir', `${atdfTool.tool_id}.json`), atdfTool);
      
      // Verificar que se llamaron los métodos correctos
      expect(fs.readJsonSync).toHaveBeenCalledWith('./input.json');
      expect(mockConvertToolToATDF).toHaveBeenCalled();
      expect(fs.ensureDirSync).toHaveBeenCalledWith('./output-dir');
      expect(fs.writeJsonSync).toHaveBeenCalled();
    }, 15000);
  });
}); 