import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';

// Convertir exec a Promise
const execAsync = promisify(exec);

// Mock para fs-extra
jest.mock('fs-extra', () => ({
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
  }))
}));

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
      expect(result.stderr).toContain('Error');
    }, 15000);
    
    it('debería crear directorio de salida si se especifica', async () => {
      // Simulamos una respuesta del servidor
      (fs.ensureDir as jest.Mock).mockResolvedValue(undefined);
      (fs.writeJSON as jest.Mock).mockResolvedValue(undefined);
      
      await runCLI('discover http://example.com -o ./output-dir');
      
      // El comando fallará porque no hay un servidor real, pero podemos
      // verificar que se intentó crear el directorio
      expect(fs.ensureDir).toHaveBeenCalledWith('./output-dir');
    }, 15000);
  });
  
  describe('Comando execute', () => {
    it('debería requerir un ID de herramienta', async () => {
      const result = await runCLI('execute http://example.com');
      expect(result.stderr).toContain('Error');
    }, 15000);
    
    it('debería validar los parámetros', async () => {
      const result = await runCLI('execute http://example.com fetch --param invalid');
      expect(result.stderr).toContain('Error');
    }, 15000);
  });
  
  describe('Comando convert', () => {
    it('debería requerir una ruta de origen', async () => {
      const result = await runCLI('convert');
      expect(result.stderr).toContain('Error');
    }, 15000);
    
    it('debería crear el directorio de destino', async () => {
      // Mock de herramienta MCP para convertir
      const mockTool = {
        name: 'test-tool',
        description: 'Test tool',
        schema: {}
      };
      
      (fs.readJSON as jest.Mock).mockResolvedValue(mockTool);
      
      await runCLI('convert ./input.json -o ./output-dir');
      
      expect(fs.ensureDir).toHaveBeenCalledWith('./output-dir');
      expect(fs.readJSON).toHaveBeenCalledWith('./input.json');
    }, 15000);
  });
}); 