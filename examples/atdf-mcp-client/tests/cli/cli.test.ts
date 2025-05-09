import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';

// Convertir exec a Promise
const execAsync = promisify(exec);

// Mock para fs-extra
jest.mock('fs-extra', () => ({
  ensureDir: jest.fn(),
  writeJSON: jest.fn(),
  readJSON: jest.fn(),
  pathExists: jest.fn(),
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
    return execAsync(`ts-node ${CLI_PATH} ${args}`);
  };
  
  // Antes de cada test, limpiar mocks
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('Comando discover', () => {
    it('debería validar la URL del servidor', async () => {
      try {
        await runCLI('discover invalid-url');
        fail('Debería fallar con URL inválida');
      } catch (error) {
        const execError = error as ExecError;
        expect(execError.stderr).toContain('Error');
      }
    });
    
    it('debería crear directorio de salida si se especifica', async () => {
      // Mockear las operaciones de archivo
      (fs.ensureDir as jest.Mock).mockResolvedValue(undefined);
      (fs.writeJSON as jest.Mock).mockResolvedValue(undefined);
      
      try {
        await runCLI('discover http://localhost:1337/mcp -o ./output-dir');
      } catch (error) {
        // La prueba fallará porque no hay un servidor real, pero podemos
        // verificar que al menos se intentó crear el directorio
        expect(fs.ensureDir).toHaveBeenCalledWith('./output-dir');
      }
    });
  });
  
  describe('Comando execute', () => {
    it('debería requerir un ID de herramienta', async () => {
      try {
        await runCLI('execute http://localhost:1337/mcp');
        fail('Debería fallar sin ID de herramienta');
      } catch (error) {
        const execError = error as ExecError;
        expect(execError.stderr).toContain('Error');
      }
    });
    
    it('debería validar los parámetros', async () => {
      try {
        await runCLI('execute http://localhost:1337/mcp fetch --param invalid');
        fail('Debería fallar con parámetros inválidos');
      } catch (error) {
        const execError = error as ExecError;
        expect(execError.stderr).toContain('Error');
      }
    });
  });
  
  describe('Comando convert', () => {
    it('debería requerir una ruta de origen', async () => {
      try {
        await runCLI('convert');
        fail('Debería fallar sin ruta de origen');
      } catch (error) {
        const execError = error as ExecError;
        expect(execError.stderr).toContain('Error');
      }
    });
    
    it('debería crear el directorio de destino', async () => {
      // Mockear las operaciones de archivo
      (fs.ensureDir as jest.Mock).mockResolvedValue(undefined);
      (fs.writeJSON as jest.Mock).mockResolvedValue(undefined);
      (fs.readJSON as jest.Mock).mockResolvedValue({
        name: 'test-tool',
        description: 'Test tool',
        schema: {}
      });
      (fs.pathExists as jest.Mock).mockResolvedValue(true);
      
      try {
        await runCLI('convert ./input.json -o ./output-dir');
        
        expect(fs.ensureDir).toHaveBeenCalledWith('./output-dir');
        expect(fs.readJSON).toHaveBeenCalledWith('./input.json');
        expect(fs.writeJSON).toHaveBeenCalled();
      } catch (error) {
        const execError = error as ExecError;
        fail(`No debería fallar: ${execError.message}`);
      }
    });
  });
}); 