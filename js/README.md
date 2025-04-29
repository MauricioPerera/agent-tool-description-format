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

## Instalación

```bash
# Desde npm (cuando esté disponible)
npm install atdf-js

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

## Ejemplos

El directorio `examples` contiene varios ejemplos que muestran cómo utilizar el SDK:

```bash
# Ejecutar el ejemplo básico
node examples/basic_usage.js
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
```

## Compatibilidad

- **Node.js**: 14.x y superior
- **Navegadores**: Chrome, Firefox, Safari, Edge (versiones modernas)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles. 