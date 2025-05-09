# ATDF JavaScript SDK

Una implementación en JavaScript del formato ATDF (Agent Tool Description Format), que permite a los agentes de IA descubrir, seleccionar y utilizar herramientas de forma estandarizada.

## Características

- Carga de descripciones de herramientas desde archivos JSON
- Gestión de colecciones de herramientas
- Búsqueda de herramientas basada en texto
- Selección automática de herramientas basada en objetivos
- Soporte completo para herramientas multilingües
- Validación de entradas mediante esquemas JSON
- Funciona tanto en Node.js como en navegadores
- Búsqueda semántica/vectorial de herramientas (opcional)

## Instalación

```bash
# Desde npm (cuando esté disponible)
npm install atdf-js

# Para usar la búsqueda vectorial (opcional)
npm install lancedb @xenova/transformers

# O clonar el repositorio
git clone https://github.com/MauricioPerera/agent-tool-description-format.git
cd agent-tool-description-format/js
npm install
```

## Uso básico

```javascript
const { loadToolboxFromDirectory, findBestTool } = require('atdf-js');

// Cargar herramientas desde un directorio
const toolbox = loadToolboxFromDirectory('./schema/examples');

// Buscar la herramienta adecuada para un objetivo
const goal = 'Necesito traducir texto de español a inglés';
const tool = findBestTool(toolbox, goal);

if (tool) {
  console.log(`Herramienta encontrada: ${tool.toolId}`);
  console.log(`Descripción: ${tool.getDescription()}`);
  
  // Acceder a los parámetros de entrada requeridos
  console.log('Parámetros requeridos:');
  tool.inputs.forEach(input => {
    console.log(`- ${input.name}: ${input.description}`);
  });
  
  // Mostrar mensajes de éxito/error
  console.log(`Mensaje de éxito: ${tool.successMessage}`);
}
```

## Compatibilidad multilingüe

El SDK soporta herramientas con descripciones en múltiples idiomas:

```javascript
// Obtener la descripción en español
const descripcionEs = tool.getDescription('es');

// Obtener la descripción en inglés
const descripcionEn = tool.getDescription('en');

// Verificar si la herramienta soporta un idioma específico
if (tool.supportsLanguage('pt')) {
  const descripcionPt = tool.getDescription('pt');
}

// Obtener la lista de idiomas soportados
const idiomas = tool.supportedLanguages;
```

## Búsqueda vectorial (opcional)

El SDK ofrece soporte opcional para búsqueda semántica avanzada utilizando bases de datos vectoriales:

```javascript
const { ATDFToolbox, ATDFVectorStore } = require('atdf-js');

async function main() {
  // Crear e inicializar el almacén vectorial
  const vectorStore = new ATDFVectorStore();
  await vectorStore.initialize();
  
  // Crear un toolbox con soporte vectorial
  const toolbox = new ATDFToolbox({ vectorStore });
  
  // Cargar herramientas
  toolbox.loadToolsFromDirectory('./tools');
  
  // Realizar búsqueda vectorial (captura similitud semántica)
  const results = await toolbox.searchTools('comunicarme con alguien', { 
    useVectorSearch: true,
    language: 'es'
  });
  
  console.log(results);
}

main().catch(console.error);
```

Esta funcionalidad requiere dependencias adicionales:
```bash
npm install lancedb @xenova/transformers
```

La búsqueda vectorial ofrece varias ventajas:
- Encuentra herramientas semánticamente similares aunque usen términos diferentes
- Funciona mejor en escenarios multilingües
- Mejora los resultados con consultas ambiguas o incompletas

## Ejemplos

El directorio `examples` contiene varios ejemplos que muestran cómo utilizar el SDK:

```bash
# Ejecutar el ejemplo básico
node examples/basic_usage.js

# Ejecutar el ejemplo de búsqueda vectorial
node examples/vector_search.js
```

## Desarrollo

### Requisitos previos

- Node.js 14.x o superior
- npm 7.x o superior

### Scripts disponibles

```bash
# Instalar dependencias
npm install

# Ejecutar pruebas
npm test

# Lint
npm run lint

# Construir para producción
npm run build

# Desarrollo con recarga automática
npm run dev

# Ejecutar el ejemplo de búsqueda vectorial
npm run example:vector
```

## Compatibilidad

- **Node.js**: 14.x y superior
- **Navegadores**: Chrome, Firefox, Safari, Edge (versiones modernas)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## Conversor MCP a ATDF

El SDK incluye un convertidor de herramientas desde el formato MCP (Model Context Protocol) al formato ATDF.

### Uso básico

```javascript
const { mcpToAtdf } = require('atdf-sdk');

// Definición de herramienta en formato MCP
const mcpTool = {
    name: 'fetch',
    description: 'Recupera contenido de una URL',
    annotations: {
        context: 'Cuando necesites obtener datos de una página web'
    },
    inputSchema: {
        type: 'object',
        properties: {
            url: {
                type: 'string',
                description: 'URL a recuperar'
            }
        },
        required: ['url']
    }
};

// Convertir a formato ATDF básico
const atdfBasic = mcpToAtdf(mcpTool);

// Convertir a formato ATDF mejorado
const atdfEnhanced = mcpToAtdf(mcpTool, { 
    enhanced: true, 
    author: 'Mi Nombre' 
});
```

### Conversión desde archivo

```javascript
const { convertMcpFile } = require('atdf-sdk');

// Convertir un archivo MCP a ATDF y guardarlo
convertMcpFile(
    'herramientas_mcp.json',
    'herramientas_atdf.json',
    { enhanced: true }
);
```

### Procesamiento por lotes

```javascript
const { batchConvertMcp } = require('atdf-sdk');
const fs = require('fs');

// Cargar archivo con múltiples herramientas
const mcpData = JSON.parse(fs.readFileSync('mcp_tools.json', 'utf8'));

// Procesar todas las herramientas
batchConvertMcp(mcpData, './output', { enhanced: true });
```

Para ver un ejemplo completo, consulte el archivo `examples/mcp_conversion_example.js`. 