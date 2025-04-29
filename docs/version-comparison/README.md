# ATDF Version Comparison

This document provides a detailed comparison between different versions of the Agent Tool Description Format (ATDF).

## Version 0.1.0 vs 0.2.0

| Feature | Version 0.1.0 (Basic) | Version 0.2.0 (Enhanced) |
|---------|-------------------|----------------------|
| **Core Structure** | ✅ Basic structure with essential fields | ✅ Same core structure with additional optional fields |
| **Required Fields** | ✅ `tool_id`, `description`, `when_to_use`, `how_to_use` | ✅ Same required fields |
| **Metadata** | ❌ Not supported | ✅ Optional `metadata` field with version, author, tags, etc. |
| **Multilingual Support** | ⚠️ Limited (separate files for each language) | ✅ Built-in through `localization` field |
| **Prerequisites** | ❌ Not supported | ✅ Optional `prerequisites` field |
| **Feedback Mechanisms** | ❌ Not supported | ✅ Optional `feedback` field with progress and completion signals |
| **Usage Examples** | ❌ Not supported | ✅ Optional `examples` field with full examples |
| **Complex Input Types** | ⚠️ Limited (basic types only) | ✅ Complex object schemas with nested properties |
| **Backward Compatibility** | ✅ N/A (first version) | ✅ Fully compatible with 0.1.0 |
| **Schema Validation** | ✅ Basic validation | ✅ Enhanced validation with additional fields |
| **Tool Selection** | ✅ Basic matching by description and usage | ✅ Enhanced matching with context awareness |
| **Language Detection** | ❌ Not supported | ✅ Automatic language detection |

## Key Improvements in Version 0.2.0

1. **Enhanced Organization**: The addition of metadata fields makes it easier to organize and categorize tools in larger collections.

2. **Improved Multilingual Support**: Instead of requiring separate files for each language, version 0.2.0 allows defining multiple language variants within a single file.

3. **Safety Enhancements**: Prerequisites allow agents to check if necessary conditions are met before using a tool.

4. **Better Learning**: Usage examples provide concrete scenarios that help agents understand how to use tools effectively.

5. **Progress Monitoring**: Feedback mechanisms allow agents to track progress and determine when operations are complete.

6. **Complex Parameters**: Support for nested object schemas enables more sophisticated tool interfaces.

## Example Comparison

### Basic Tool (v0.1.0)

```json
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  "when_to_use": "Usar cuando necesites generar un agujero en una pared",
  "how_to_use": {
    "inputs": [
      { "name": "location", "type": "string", "description": "Ubicación del agujero" },
      { "name": "bit_id", "type": "string", "description": "ID de la broca" }
    ],
    "outputs": {
      "success": "Agujero creado con éxito",
      "failure": [
        { "code": "invalid_bit", "description": "Broca no compatible" }
      ]
    }
  }
}
```

### Enhanced Tool (v0.2.0)

```json
{
  "tool_id": "enhanced_hole_maker_v1",
  "metadata": {
    "version": "1.0.0",
    "author": "ATDF Development Team",
    "tags": ["física", "perforación", "construcción"],
    "category": "herramientas_físicas",
    "created_at": "2024-06-15",
    "updated_at": "2024-06-15"
  },
  "localization": {
    "es": {
      "description": "Permite crear agujeros en diversos tipos de superficies",
      "when_to_use": "Usar cuando necesites realizar perforaciones precisas"
    },
    "en": {
      "description": "Creates holes in various types of surfaces",
      "when_to_use": "Use when you need to make precise holes"
    }
  },
  "description": "Permite crear agujeros en diversos tipos de superficies",
  "when_to_use": "Usar cuando necesites realizar perforaciones precisas",
  "prerequisites": {
    "tools": ["superficie_marcada_v1", "nivel_burbuja_v2"],
    "conditions": ["superficie_seca", "no_circulacion_electrica"],
    "permissions": ["manipulacion_estructural"]
  },
  "how_to_use": {
    "inputs": [
      { "name": "location", "type": "string", "description": "Ubicación del agujero" },
      {
        "name": "configuration",
        "type": "object",
        "schema": {
          "properties": {
            "depth": {"type": "number", "description": "Profundidad en mm"},
            "diameter": {"type": "number", "description": "Diámetro en mm"}
          },
          "required": ["depth", "diameter"]
        },
        "description": "Configuración del agujero"
      }
    ],
    "outputs": {
      "success": "Agujero creado con éxito",
      "failure": [
        { "code": "invalid_configuration", "description": "Configuración no compatible" }
      ]
    }
  },
  "feedback": {
    "progress_indicators": ["vibracion", "temperatura"],
    "completion_signals": ["profundidad_alcanzada"]
  },
  "examples": [
    {
      "title": "Perforar pared de yeso",
      "description": "Ejemplo básico de perforación",
      "inputs": {
        "location": "x:120,y:85",
        "configuration": {
          "depth": 35,
          "diameter": 8
        }
      },
      "expected_output": "Agujero creado con éxito"
    }
  ]
}
```

## Migration Guide

To upgrade from v0.1.0 to v0.2.0:

1. Keep all existing required fields from v0.1.0.
2. Add optional enhanced fields as needed:
   - `metadata` for organizational information
   - `localization` for multilingual support
   - `prerequisites` for dependency information
   - `feedback` for progress monitoring
   - `examples` for usage examples
3. Consider enhancing input parameters with complex schemas where appropriate.

The SDK provides automatic conversion through the `convert_to_enhanced()` function:

```python
from tools.converter import convert_to_enhanced, load_tool, save_tool

# Load a basic tool
basic_tool = load_tool("path/to/basic_tool.json")

# Convert to enhanced format
enhanced_tool = convert_to_enhanced(
    basic_tool,
    author="Your Name",
    extract_language=True
)

# Save the enhanced tool
save_tool(enhanced_tool, "path/to/enhanced_tool.json")
``` 