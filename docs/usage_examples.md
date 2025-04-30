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