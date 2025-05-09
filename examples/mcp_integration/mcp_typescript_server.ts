/**
 * Servidor MCP Framework con soporte para herramientas ATDF.
 * 
 * Este archivo implementa un ejemplo completo de integración bidireccional entre
 * el formato ATDF (Agent Tool Description Format) y MCP Framework, permitiendo:
 * 
 * 1. Convertir herramientas ATDF a formato MCP
 * 2. Cargar dinámicamente herramientas desde archivos JSON
 * 3. Vincular implementaciones con definiciones
 * 4. Ejecutar herramientas ATDF a través de MCP Framework
 * 
 * La arquitectura se basa en un adaptador que actúa como puente entre
 * ambos ecosistemas, con conversión automática de tipos y esquemas.
 * 
 * Dependencias:
 * - mock-mcp-framework (simulación local de MCP Framework)
 * - zod (para validación de esquemas)
 * - fs-extra (para operaciones de archivos)
 * - @atdf/js (o importación directa de los archivos de conversión)
 */

// Importar el simulador de MCP Framework
import { MCPServer, MCPTool } from 'mock-mcp-framework';
import { z } from 'zod';
import * as fs from 'fs-extra';
import * as path from 'path';

// Importaciones de ATDF
// En un entorno de producción, se usaría el paquete npm @atdf/js
// import { atdfToMcp, createMCPToolFromATDF } from '@atdf/js';

// Para este ejemplo, importamos directamente desde el código fuente
import { atdfToMcp } from '../../js/src/AtdfToMcp';

/**
 * Interfaz que define la estructura de una herramienta ATDF.
 * Esta definición se basa en el esquema oficial ATDF v1.0.0
 */
interface ATDFTool {
  schema_version: string;
  tool_id: string;
  description: string;
  when_to_use: string;
  how_to_use: {
    inputs: Array<{
      name: string;
      type: string;
      description: string;
      required?: boolean;
    }>;
    outputs: {
      success: string;
      failure: Array<{
        code: string;
        description: string;
      }>;
    };
  };
}

/**
 * Adaptador que convierte herramientas ATDF para uso en MCP Framework.
 * 
 * Esta clase extiende MCPTool y sirve como puente entre los dos formatos,
 * gestionando la conversión de tipos, validación de parámetros y 
 * delegación a la implementación subyacente.
 * 
 * @template T Tipo de parámetros que acepta la herramienta
 */
class ATDFToolAdapter<T extends Record<string, any>> extends MCPTool {
  private implementation: (params: T) => Promise<any>;
  
  /**
   * Crea un nuevo adaptador para una herramienta ATDF.
   * 
   * @param atdfDefinition Definición de la herramienta en formato ATDF
   * @param implementation Función que implementa la funcionalidad real
   */
  constructor(atdfDefinition: ATDFTool, implementation: (params: T) => Promise<any>) {
    super();
    
    // Convertir ATDF a propiedades MCP utilizando el conversor
    const mcpTool = atdfToMcp(atdfDefinition);
    
    // Asignar propiedades requeridas por MCP Framework
    this.name = mcpTool.name;
    this.description = mcpTool.description;
    
    // Guardar la implementación para su posterior invocación
    this.implementation = implementation;
    
    // Construir el esquema Zod a partir de los inputs ATDF
    this.schema = this.buildSchema(atdfDefinition.how_to_use.inputs);
  }
  
  /**
   * Construye un esquema Zod a partir de las definiciones de inputs ATDF.
   * 
   * Este método mapea los tipos de datos ATDF a validadores Zod equivalentes,
   * permitiendo una validación de parámetros tipo-segura en tiempo de ejecución.
   * 
   * @param inputs Definiciones de entradas ATDF
   * @returns Esquema compatible con MCP Framework
   */
  private buildSchema(inputs: ATDFTool['how_to_use']['inputs']): Record<string, { type: any, description: string }> {
    const schema: Record<string, { type: any, description: string }> = {};
    
    for (const input of inputs) {
      // Mapear tipos ATDF a tipos Zod equivalentes
      let zodType;
      switch (input.type.toLowerCase()) {
        case 'string':
          zodType = z.string();
          break;
        case 'number':
          zodType = z.number();
          break;
        case 'boolean':
          zodType = z.boolean();
          break;
        case 'array':
          zodType = z.array(z.any());
          break;
        case 'object':
          zodType = z.record(z.any());
          break;
        default:
          zodType = z.any();
      }
      
      schema[input.name] = {
        type: zodType,
        description: input.description
      };
    }
    
    return schema;
  }
  
  /**
   * Implementación del método execute requerido por MCPTool.
   * 
   * Recibe los parámetros validados por MCP Framework y los
   * pasa a la implementación subyacente de la herramienta.
   * 
   * @param params Parámetros validados a pasar a la implementación
   * @returns Resultado de la ejecución de la herramienta
   */
  async execute(params: T): Promise<any> {
    try {
      // Llamar a la implementación concreta de la herramienta
      return await this.implementation(params);
    } catch (error: any) {
      console.error(`Error ejecutando herramienta ${this.name}:`, error);
      throw new Error(`Error en herramienta ${this.name}: ${error.message}`);
    }
  }
}

/**
 * Carga herramientas ATDF desde un directorio.
 * 
 * Esta función explora un directorio buscando archivos JSON con definiciones ATDF
 * y luego busca las implementaciones correspondientes para crear adaptadores.
 * 
 * El proceso es:
 * 1. Buscar archivos JSON en el directorio especificado
 * 2. Parsear cada archivo como definición ATDF
 * 3. Buscar un archivo de implementación con el mismo nombre en ./implementations/
 * 4. Crear un adaptador ATDF-MCP para cada herramienta encontrada
 * 
 * @param directory Ruta al directorio que contiene las herramientas ATDF
 * @returns Lista de adaptadores ATDF-MCP listos para usar
 */
async function loadATDFTools(directory: string): Promise<ATDFToolAdapter<any>[]> {
  const tools: ATDFToolAdapter<any>[] = [];
  
  try {
    // Verificar que el directorio existe
    if (!fs.existsSync(directory)) {
      console.error(`El directorio ${directory} no existe`);
      return tools;
    }
    
    // Leer todos los archivos JSON en el directorio
    const files = fs.readdirSync(directory)
      .filter(file => file.endsWith('.json'));
    
    for (const file of files) {
      const filePath = path.join(directory, file);
      
      try {
        // Cargar definición ATDF desde el archivo JSON
        const atdfDefinition = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // Buscar implementación con el mismo nombre (sin extensión .json)
        const baseName = path.basename(file, '.json');
        const implementationPath = path.join(directory, 'implementations', `${baseName}.js`);
        
        let implementation;
        if (fs.existsSync(implementationPath)) {
          // Importar dinámicamente la implementación encontrada
          implementation = require(implementationPath);
        } else {
          // Crear una implementación simulada si no se encuentra
          implementation = async (params: any) => {
            return {
              status: 'success',
              message: `Ejecución simulada de ${baseName} con parámetros: ${JSON.stringify(params)}`,
              tool: baseName,
              params
            };
          };
        }
        
        // Crear y registrar el adaptador ATDF-MCP
        const tool = new ATDFToolAdapter(atdfDefinition, implementation);
        tools.push(tool);
        
        console.log(`✅ Herramienta ATDF cargada: ${atdfDefinition.tool_id}`);
      } catch (error: any) {
        console.error(`❌ Error al cargar herramienta ATDF desde ${file}:`, error.message);
      }
    }
  } catch (error: any) {
    console.error('Error al cargar herramientas ATDF:', error.message);
  }
  
  return tools;
}

/**
 * Función principal que inicia el servidor MCP con soporte ATDF.
 * 
 * Esta función:
 * 1. Crea una instancia de servidor MCP
 * 2. Carga todas las herramientas ATDF disponibles
 * 3. Registra las herramientas en el servidor
 * 4. Inicia el servidor para aceptar solicitudes
 */
async function main() {
  // Crear servidor MCP
  const server = new MCPServer();
  
  console.log("🔄 Inicializando servidor MCP con soporte ATDF...");
  
  // Cargar herramientas ATDF desde el directorio de herramientas
  const toolsDirectory = path.join(__dirname, 'tools');
  const tools = await loadATDFTools(toolsDirectory);
  
  // Registrar herramientas en el servidor MCP
  for (const tool of tools) {
    server.registerTool(tool);
  }
  
  // Si no hay herramientas ATDF, crear una herramienta de ejemplo
  if (tools.length === 0) {
    console.log("ℹ️ No se encontraron herramientas ATDF. Creando herramienta de ejemplo...");
    
    // Ejemplo de herramienta ATDF incrustada (greeting)
    const greetingTool: ATDFTool = {
      schema_version: "1.0.0",
      tool_id: "greeting",
      description: "Genera un saludo personalizado en diferentes idiomas",
      when_to_use: "Cuando necesites saludar a alguien de forma personalizada",
      how_to_use: {
        inputs: [
          {
            name: "name",
            type: "string",
            description: "Nombre de la persona a saludar",
            required: true
          },
          {
            name: "language",
            type: "string",
            description: "Código de idioma (en, es, fr)"
          }
        ],
        outputs: {
          success: "Saludo generado correctamente",
          failure: [
            {
              code: "invalid_language",
              description: "El idioma especificado no está soportado"
            }
          ]
        }
      }
    };
    
    // Implementación de la herramienta de ejemplo
    const greetingImplementation = async (params: { name: string, language?: string }) => {
      const { name, language = 'en' } = params;
      
      const greetings: Record<string, string> = {
        en: `Hello, ${name}!`,
        es: `¡Hola, ${name}!`,
        fr: `Bonjour, ${name}!`
      };
      
      // Verificar que el idioma esté soportado
      if (!greetings[language]) {
        throw new Error('invalid_language');
      }
      
      return {
        greeting: greetings[language],
        language
      };
    };
    
    // Crear y registrar adaptador para la herramienta de ejemplo
    const greetingAdapter = new ATDFToolAdapter(greetingTool, greetingImplementation);
    server.registerTool(greetingAdapter);
    
    console.log(`✅ Herramienta de ejemplo registrada: ${greetingTool.tool_id}`);
  }
  
  // Iniciar servidor MCP
  try {
    console.log("🚀 Iniciando servidor MCP...");
    await server.start();
    
    console.log("\n✅ Servidor MCP iniciado con éxito");
    console.log(`Herramientas disponibles: ${tools.length + (tools.length === 0 ? 1 : 0)}`);
  } catch (error: any) {
    console.error("❌ Error al iniciar servidor MCP:", error.message);
  }
}

// Ejecutar función principal
main().catch(error => {
  console.error("Error fatal:", error);
  process.exit(1);
}); 