# Cliente ATDF-MCP

Un cliente para servidores MCP (Model Context Protocol) con soporte para el formato ATDF (Agent Tool Description Format). Permite descubrir, convertir, guardar y ejecutar herramientas entre ecosistemas MCP y ATDF.

## Características

- **Comunicación con servidores MCP**: Conecta con servidores MCP para descubrir y usar herramientas.
- **Conversión bidireccional**: Convierte herramientas entre formatos MCP y ATDF.
- **Validación de parámetros**: Valida los parámetros según las definiciones ATDF.
- **Persistencia**: Guarda herramientas ATDF en archivos JSON.
- **CLI integrada**: Interfaz de línea de comandos para operaciones comunes.
- **Tipado completo**: Desarrollado con TypeScript para mayor seguridad.

## Arquitectura

El cliente implementa una arquitectura que conecta el ecosistema MCP con el formato ATDF:

```
┌─────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│ Herramientas    │      │  Cliente ATDF-MCP │      │    Servidor MCP   │
│     ATDF        │◄────►│                   │◄────►│                   │
└─────────────────┘      └───────────────────┘      └───────────────────┘
                              ▲       ▲
                              │       │
                              ▼       ▼
                         ┌─────────────────┐
                         │   Almacenamiento│
                         │   JSON (ATDF)   │
                         └─────────────────┘
```

### Componentes principales:

1. **MCPClient**: Cliente base para comunicación con servidores MCP
2. **ATDFMCPClient**: Cliente extendido con soporte para ATDF
3. **McpToAtdf**: Convertidor de herramientas MCP a ATDF
4. **CLI**: Interfaz de línea de comandos

## Instalación

```bash
# Instalar dependencias
npm install

# Compilar el proyecto
npm run build
```

## Uso desde línea de comandos (CLI)

El cliente incluye una interfaz de línea de comandos para operaciones comunes:

### Descubrir herramientas en un servidor MCP

```bash
# Descubrir herramientas y convertirlas a ATDF
npm run cli -- discover http://localhost:1337/mcp

# Guardar las herramientas en un directorio específico
npm run cli -- discover http://localhost:1337/mcp -o ./mis-herramientas
```

### Ejecutar una herramienta ATDF

```bash
# Ejecutar una herramienta con parámetros básicos
npm run cli -- execute http://localhost:1337/mcp fetch --param url=https://example.com

# Ejecutar con parámetros en formato JSON
npm run cli -- execute http://localhost:1337/mcp fetch -p '{"url":"https://example.com"}'
```

### Convertir herramientas MCP a ATDF

```bash
# Convertir un archivo de herramienta MCP
npm run cli -- convert ./herramienta-mcp.json -o ./herramientas-atdf

# Convertir un directorio completo
npm run cli -- convert ./herramientas-mcp -o ./herramientas-atdf
```

## Uso como biblioteca

El cliente también puede usarse como biblioteca en otros proyectos:

```typescript
import { ATDFMCPClient } from 'atdf-mcp-client';

async function ejemplo() {
  // Crear cliente
  const client = new ATDFMCPClient('http://localhost:1337/mcp');
  
  // Conectar y descubrir herramientas
  await client.connect();
  const atdfTools = client.getATDFTools();
  console.log(`Descubiertas ${atdfTools.length} herramientas`);
  
  // Guardar herramientas en formato ATDF
  client.saveATDFToolsToDirectory('./mis-herramientas');
  
  // Ejecutar una herramienta
  const result = await client.executeATDFTool('fetch', {
    url: 'https://example.com'
  });
  
  console.log('Resultado:', result);
}
```

## Componentes principales

### 1. Cliente básico MCP

El `MCPClient` proporciona funcionalidad básica para comunicarse con servidores MCP:

```typescript
import { MCPClient } from 'atdf-mcp-client';

const client = new MCPClient('http://localhost:1337/mcp');
const tools = await client.connect();
const result = await client.callTool('tool-name', { param1: 'value1' });
```

### 2. Cliente extendido ATDF-MCP

El `ATDFMCPClient` extiende el cliente básico con funcionalidad ATDF:

```typescript
import { ATDFMCPClient } from 'atdf-mcp-client';

const client = new ATDFMCPClient('http://localhost:1337/mcp');
await client.connect();

// Convertir herramientas MCP a ATDF
const atdfTools = client.getATDFTools();

// Guardar en archivos
client.saveATDFToolsToDirectory('./atdf-tools');

// Ejecutar herramienta por ID ATDF
const result = await client.executeATDFTool('fetch', { url: 'https://example.com' });
```

### 3. Convertidor MCP a ATDF

El módulo `McpToAtdf` permite convertir herramientas entre formatos:

```typescript
import { mcpToAtdf, batchConvert } from 'atdf-mcp-client';

// Convertir una herramienta individual
const atdfTool = mcpToAtdf(mcpTool);

// Convertir múltiples herramientas
const atdfTools = batchConvert(mcpTools);
```

## Formatos de datos

### Formato de herramienta MCP (entrada)

El formato MCP para herramientas que este cliente puede procesar:

```json
{
  "name": "example-tool",
  "description": "Herramienta de ejemplo",
  "schema": {
    "param1": {
      "type": "string",
      "description": "Parámetro 1",
      "required": true
    },
    "param2": {
      "type": "number",
      "description": "Parámetro 2",
      "required": false
    }
  }
}
```

### Formato de herramienta ATDF (salida)

El formato ATDF generado para las herramientas:

```json
{
  "schema_version": "1.0.0",
  "tool_id": "example-tool",
  "description": "Herramienta de ejemplo",
  "when_to_use": "Usar cuando necesites esta herramienta de ejemplo",
  "how_to_use": {
    "inputs": [
      {
        "name": "param1",
        "type": "string",
        "description": "Parámetro 1",
        "required": true
      },
      {
        "name": "param2",
        "type": "number",
        "description": "Parámetro 2",
        "required": false
      }
    ],
    "outputs": {
      "success": "Resultado exitoso de example-tool",
      "failure": [
        {
          "code": "parameter_error",
          "description": "Error en los parámetros proporcionados"
        },
        {
          "code": "execution_error",
          "description": "Error durante la ejecución de la herramienta"
        }
      ]
    }
  }
}
```

## Solución de problemas

### Problemas comunes

#### Error de conexión al servidor MCP

**Error**: `Error al conectar al servidor MCP: 404 Not Found`

**Solución**: 
- Verifica que la URL del servidor MCP sea correcta
- Confirma que el servidor MCP esté en funcionamiento
- Asegúrate que la ruta incluya `/tools/list` para la API MCP

#### Error al convertir herramientas

**Error**: `Formato de respuesta inválido: no se encontró lista de herramientas`

**Solución**:
- Confirma que el servidor devuelve una respuesta en el formato esperado
- Verifica que la respuesta contenga una propiedad `tools` que sea un array

#### Error al validar parámetros

**Error**: `Parámetro requerido faltante: url`

**Solución**:
- Proporciona todos los parámetros marcados como requeridos
- Verifica el tipo de los parámetros (string, number, boolean, etc.)

### Diagnóstico

Para diagnosticar problemas, puedes:

1. Activar logs detallados con la variable de entorno `DEBUG=atdf-mcp:*`
2. Verificar el formato de las respuestas del servidor MCP
3. Validar el formato de los archivos JSON de herramientas ATDF

## Requisitos

- Node.js 14 o superior
- TypeScript 4.5 o superior

## Desarrollo

```bash
# Ejecutar en modo desarrollo
npm run dev

# Ejecutar la CLI en desarrollo
npm run cli -- [comandos]
```

## Licencia

Este proyecto está licenciado bajo MIT.

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu característica
3. Committing tus cambios
4. Abre un Pull Request 