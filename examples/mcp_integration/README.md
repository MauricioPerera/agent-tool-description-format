# Integración ATDF con MCP Framework

Este proyecto proporciona un ejemplo completo y funcional de la integración bidireccional entre el formato ATDF (Agent Tool Description Format) y MCP Framework, permitiendo usar herramientas ATDF en aplicaciones basadas en MCP.

## Arquitectura de la Integración

La integración se basa en estos componentes principales:

```
┌─────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│ Definición ATDF │─────>│ Convertidor ATDF  │─────>│ Herramienta MCP   │
│ (JSON)          │      │ (atdfToMcp)       │      │ (MCPTool)         │
└─────────────────┘      └───────────────────┘      └───────────────────┘
        │                                                    ▲
        │                                                    │
        │                ┌───────────────────┐              │
        └───────────────>│ Adaptador ATDF    │──────────────┘
                         │ (ATDFToolAdapter)  │
                         └───────────────────┘
                                   ▲
                                   │
                         ┌───────────────────┐
                         │ Implementación JS │
                         │ (módulo Node.js)  │
                         └───────────────────┘
```

## Contenido del ejemplo

```
├── tools/                  # Directorio de herramientas ATDF
│   ├── fetch.json          # Definición de herramienta ATDF
│   └── implementations/    # Implementaciones de herramientas
│       └── fetch.js        # Implementación de la herramienta fetch
├── local_modules/          # Módulos locales para simulación
│   └── mock-mcp-framework/ # Simulación de MCP Framework
├── mcp_typescript_server.ts # Servidor MCP en TypeScript con soporte ATDF
├── package.json            # Configuración de dependencias
├── tsconfig.json           # Configuración de TypeScript
└── README.md               # Este archivo
```

## Requisitos

- Node.js v16 o superior
- npm o yarn
- TypeScript 4.5 o superior

## Instalación

```bash
# Instalar dependencias
npm install

# O con yarn
yarn install
```

## Ejecución

```bash
# Ejecutar con ts-node (recomendado para desarrollo)
npm run dev

# O compilar y ejecutar
npm run build
npm run start
```

## Componentes principales

### 1. `ATDFToolAdapter` - Adaptador principal

Este adaptador es una clase que extiende `MCPTool` y sirve como puente entre los dos formatos:

```typescript
class ATDFToolAdapter<T extends Record<string, any>> extends MCPTool {
  // Propiedades heredadas de MCPTool
  name: string;
  description: string;
  schema: Record<string, { type: any, description: string }>;
  
  // Propiedades propias del adaptador
  private implementation: (params: T) => Promise<any>;
  
  constructor(atdfDefinition: ATDFTool, implementation: (params: T) => Promise<any>) {
    super();
    
    // Convertir ATDF a formato MCP
    const mcpTool = atdfToMcp(atdfDefinition);
    
    // Configurar propiedades
    this.name = mcpTool.name;
    this.description = mcpTool.description;
    this.implementation = implementation;
    this.schema = this.buildSchema(atdfDefinition.how_to_use.inputs);
  }
  
  // Método execute requerido por MCPTool
  async execute(params: T): Promise<any> {
    // Delegación a la implementación real
    return await this.implementation(params);
  }
}
```

### 2. Función `atdfToMcp` - Conversor de formatos

Esta función convierte definiciones ATDF al formato que espera MCP Framework:

```typescript
// Importar la función desde la biblioteca ATDF
import { atdfToMcp } from '@atdf/js';

// Ejemplo de uso
const mcpTool = atdfToMcp(atdfDefinition);
```

### 3. Función `loadATDFTools` - Cargador dinámico

Esta función escanea un directorio buscando archivos JSON con definiciones ATDF:

```typescript
async function loadATDFTools(directory: string): Promise<ATDFToolAdapter<any>[]> {
  // Buscar archivos JSON
  // Cargar definiciones
  // Encontrar implementaciones
  // Crear adaptadores
  // Devolver lista de herramientas listas para usar
}
```

## Ejemplo práctico de herramienta ATDF

### Definición (fetch.json)

```json
{
  "schema_version": "1.0.0",
  "tool_id": "fetch",
  "description": "Recupera contenido de una URL",
  "when_to_use": "Usar cuando necesites obtener datos de una página web",
  "how_to_use": {
    "inputs": [
      {
        "name": "url",
        "type": "string",
        "description": "URL a recuperar",
        "required": true
      },
      {
        "name": "raw",
        "type": "boolean",
        "description": "Devolver HTML crudo (opcional)"
      }
    ],
    "outputs": {
      "success": "Contenido web recuperado con éxito",
      "failure": [
        {
          "code": "invalid_url",
          "description": "La URL proporcionada es inválida o inaccesible"
        },
        {
          "code": "fetch_error",
          "description": "Error al recuperar el contenido"
        }
      ]
    }
  }
}
```

### Implementación (fetch.js)

```javascript
module.exports = async function fetchImplementation(params) {
  const { url, raw = false } = params;
  
  // Validar URL
  if (!url || !url.startsWith('http')) {
    throw new Error('invalid_url');
  }
  
  try {
    // En una implementación real, aquí se realizaría una petición HTTP
    // Ejemplo con fetch API:
    // const response = await fetch(url);
    // const content = raw ? await response.text() : await response.json();
    
    // Aquí simulamos una respuesta
    return {
      status: 200,
      url: url,
      content: raw ? '<!DOCTYPE html>...' : { title: 'Página simulada', text: '...' }
    };
  } catch (error) {
    throw new Error('fetch_error');
  }
};
```

## Flujo de ejecución

1. **Definición**: Se lee el archivo JSON con la definición ATDF de la herramienta.
2. **Conversión**: Se convierte la definición al formato MCP usando `atdfToMcp`.
3. **Implementación**: Se localiza el archivo de implementación correspondiente.
4. **Adaptación**: Se crea un adaptador que conecta la definición con la implementación.
5. **Registro**: Se registra la herramienta adaptada en el servidor MCP.
6. **Ejecución**: Cuando se invoca la herramienta, el adaptador:
   - Valida los parámetros usando el esquema Zod
   - Llama a la implementación con los parámetros validados
   - Captura y gestiona posibles errores
   - Devuelve el resultado al cliente MCP

## Mapeo entre ATDF y MCP

| Propiedad ATDF         | Propiedad MCP          | Notas                               |
|------------------------|------------------------|-------------------------------------|
| `tool_id`              | `name`                 | Identificador principal             |
| `description`          | `description`          | Descripción corta                   |
| `how_to_use.inputs`    | `schema`               | Convertido a esquema Zod            |
| `how_to_use.outputs`   | (no hay equivalente)   | Gestionado por el adaptador         |
| (no hay equivalente)   | `execute()`            | Implementado por el adaptador       |

## Extensiones posibles

Puedes ampliar este ejemplo de varias formas:

1. **Agregar más herramientas ATDF**:
   - Crea nuevos archivos JSON en `tools/`
   - Implementa sus funciones en `implementations/`

2. **Integrar con API reales**:
   - Modifica las implementaciones para usar APIs reales
   - Añade manejo de autenticación y errores

3. **Crear un plugin MCP formalizado**:
   - Desarrolla un plugin reutilizable para cargar herramientas ATDF
   - Publícalo como paquete npm separado

4. **Mejoras de escalabilidad**:
   - Añade caché de resultados
   - Implementa límites de tasa y cuotas
   - Añade telemetría y monitorización

## Integración con proyectos MCP existentes

Para integrar herramientas ATDF en un proyecto MCP Framework existente:

```typescript
import { MCPServer } from 'mcp-framework';
import { ATDFToolAdapter } from './adapters/ATDFToolAdapter';
import { loadATDFTools } from './utilities/loader';

async function main() {
  // Crear servidor MCP
  const server = new MCPServer();
  
  // Cargar herramientas ATDF
  const tools = await loadATDFTools('./atdf-tools');
  
  // Registrar herramientas
  for (const tool of tools) {
    server.registerTool(tool);
  }
  
  // Iniciar servidor
  await server.start();
}
```

## Solución de problemas

### Error: Herramienta no encontrada

Si recibes un error indicando que una herramienta no se pudo cargar:

1. Verifica que el archivo JSON esté en el directorio `tools/`
2. Comprueba que la sintaxis JSON es válida
3. Asegúrate de que hay un archivo de implementación correspondiente en `tools/implementations/`

### Error: Conversión de tipos

Si encuentras errores relacionados con la conversión de tipos:

1. Verifica que los tipos en la definición ATDF son compatibles con Zod
2. Revisa la función `buildSchema` para asegurarte de que maneja todos los tipos necesarios

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu función (`git checkout -b feature/amazing-feature`)
3. Realiza tus cambios
4. Ejecuta las pruebas (`npm test`)
5. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
6. Push a la rama (`git push origin feature/amazing-feature`)
7. Abre un Pull Request

## Licencia

Este ejemplo está disponible bajo la misma licencia MIT que el proyecto ATDF principal. 