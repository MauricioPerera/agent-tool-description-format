# Ejemplos de Uso de ATDF v2.0.0

Este documento proporciona ejemplos prácticos para utilizar las nuevas características implementadas en ATDF v2.0.0.

## Validación Inteligente de Herramientas

El nuevo validador inteligente puede detectar automáticamente la versión del esquema de una herramienta y aplicar el esquema correspondiente.

### Desde línea de comandos

```bash
# Validación inteligente (detecta automáticamente la versión)
python tools/validator.py schema/examples/enhanced_hole_maker.json --smart

# Validación estándar con ignorar propiedades adicionales
python tools/validator.py schema/examples/enhanced_hole_maker.json --ignore-additional
```

### Desde código Python

```python
from tools.validator import validate_tool_smart

# Validar una herramienta usando detección automática
is_valid = validate_tool_smart("path/to/my_tool.json")

# También se pueden especificar esquemas personalizados
is_valid = validate_tool_smart(
    "path/to/my_tool.json",
    schema_basic="custom_basic_schema.json",
    schema_enhanced="custom_enhanced_schema.json"
)
```

## Conversión Entre Formatos

El sistema ahora permite convertir herramientas entre formatos básico y mejorado de forma bidireccional.

### Línea de comandos (con script personalizado)

```bash
# Convierte una herramienta básica a formato mejorado 
python -c "from tools.converter import convert_to_enhanced, load_tool, save_tool; save_tool(convert_to_enhanced(load_tool('schema/examples/hole_maker.json')), 'enhanced_output.json')"

# Convierte una herramienta mejorada a formato básico
python -c "from tools.converter import convert_to_basic, load_tool, save_tool; save_tool(convert_to_basic(load_tool('schema/examples/enhanced_hole_maker.json')), 'basic_output.json')"
```

### Desde código Python

```python
from tools.converter import convert_to_enhanced, convert_to_basic, load_tool, save_tool

# Cargar una herramienta básica
basic_tool = load_tool("schema/examples/hole_maker.json")

# Convertir a formato mejorado
enhanced_tool = convert_to_enhanced(
    basic_tool,
    author="Tu Nombre",
    extract_language=True  # Intenta detectar y extraer información de idioma
)

# Guardar la versión mejorada
save_tool(enhanced_tool, "output/enhanced_tool.json")

# Convertir de mejorado a básico
basic_tool_converted = convert_to_basic(
    enhanced_tool,
    preserve_id_field=True  # Mantiene el campo id si existe
)

# Guardar la versión básica
save_tool(basic_tool_converted, "output/basic_tool.json")
```

## Selección Inteligente de Herramientas

El selector de herramientas mejorado funciona con consultas en múltiples idiomas.

```python
from improved_loader import load_tools_from_directory, select_tool_by_goal

# Cargar herramientas
tools = load_tools_from_directory("schema/examples")

# Seleccionar herramienta según consulta en español
tool_es = select_tool_by_goal(tools, "necesito hacer un agujero en la pared")

# Seleccionar herramienta según consulta en inglés
tool_en = select_tool_by_goal(tools, "I need to translate some text")

# Seleccionar herramienta según consulta en portugués
tool_pt = select_tool_by_goal(tools, "preciso fazer um furo")

# El idioma se detecta automáticamente, pero también puede especificarse
tool_forced_lang = select_tool_by_goal(tools, "quiero traducir un texto", language="es")
```

## Uso de Identificadores Alternativos

Los esquemas ahora soportan tanto `tool_id` como `id` de forma intercambiable.

```json
// Herramienta con tool_id (estilo tradicional)
{
  "schema_version": "1.0.0",
  "tool_id": "example_tool",
  "description": "Una herramienta de ejemplo",
  "when_to_use": "Cuando necesites un ejemplo",
  "how_to_use": {
    "inputs": [],
    "outputs": {
      "success": "Éxito",
      "failure": []
    }
  }
}

// Herramienta con id (estilo alternativo)
{
  "schema_version": "1.0.0",
  "id": "example_tool",
  "description": "Una herramienta de ejemplo",
  "when_to_use": "Cuando necesites un ejemplo",
  "how_to_use": {
    "inputs": [],
    "outputs": {
      "success": "Éxito",
      "failure": []
    }
  }
}
```

## Ejecución de Todas las Pruebas

Para verificar que todo funciona correctamente, puedes ejecutar el conjunto completo de pruebas:

```bash
# Ejecutar todas las pruebas
python tests/run_all_tests.py

# Ejecutar pruebas específicas
python tests/test_trilingual_agent.py
python tests/test_enhanced_features.py
```

## Convertidor MCP a ATDF

El formato ATDF ahora incluye soporte para convertir automáticamente definiciones de herramientas desde el formato MCP (Model Context Protocol) al formato ATDF estándar.

### Implementación en Python

#### Uso básico

```python
from tools.mcp_converter import mcp_to_atdf

# Definición de herramienta en formato MCP
mcp_tool = {
    "name": "fetch",
    "description": "Recupera contenido de una URL",
    "annotations": {
        "context": "Cuando necesites obtener datos de una página web"
    },
    "inputSchema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL a recuperar"
            }
        },
        "required": ["url"]
    }
}

# Convertir a formato ATDF básico
atdf_basic = mcp_to_atdf(mcp_tool)

# Convertir a formato ATDF mejorado
atdf_enhanced = mcp_to_atdf(mcp_tool, enhanced=True, author="Mi Nombre")
```

#### Conversión desde archivo

```python
from tools.mcp_converter import convert_mcp_file

# Convertir un archivo MCP a ATDF y guardarlo
convert_mcp_file(
    input_file="herramientas_mcp.json",
    output_file="herramientas_atdf.json",
    enhanced=True
)
```

#### Procesamiento por lotes

Si tienes múltiples herramientas MCP en un formato como:

```json
{
  "tools": [
    { "name": "tool1", ... },
    { "name": "tool2", ... }
  ]
}
```

Puedes procesarlas todas:

```python
import json
from tools.mcp_converter import mcp_to_atdf
from tools.converter import save_tool

# Cargar archivo con múltiples herramientas
with open("mcp_tools.json", "r") as f:
    mcp_data = json.load(f)

# Procesar cada herramienta
for tool in mcp_data["tools"]:
    atdf_tool = mcp_to_atdf(tool, enhanced=True)
    save_tool(atdf_tool, f"output/{tool['name']}.json")
```

Para un ejemplo completo de uso, consulta el archivo `examples/mcp_conversion_example.py`.

### Implementación en JavaScript

#### Uso básico

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

#### Conversión desde archivo

```javascript
const { convertMcpFile } = require('atdf-sdk');

// Convertir un archivo MCP a ATDF y guardarlo
convertMcpFile(
    'herramientas_mcp.json',
    'herramientas_atdf.json',
    { enhanced: true }
);
```

#### Procesamiento por lotes

```javascript
const { batchConvertMcp } = require('atdf-sdk');
const fs = require('fs');

// Cargar archivo con múltiples herramientas
const mcpData = JSON.parse(fs.readFileSync('mcp_tools.json', 'utf8'));

// Procesar todas las herramientas
batchConvertMcp(mcpData, './output', { enhanced: true });
```

Para un ejemplo completo, consulta el archivo `js/examples/mcp_conversion_example.js`. 