# ATDF Examples

[Inicio](index.md) | [Especificación](specification.md) | [Ejemplos](examples.md) | [Contribuir](contributing.md) | [Multilingüe](multilingual.md) | [Historial de Cambios](changelog.md) | [Licencia](license.md)

**Idiomas:** [English (en)](../en/examples.md) | [Español (es)](examples.md) | [Português (pt)](../pt/examples.md)

This page showcases examples of ATDF tool descriptions in different languages.

## Hole Maker Tool

### English Version
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Creates holes in solid surfaces",
  "when_to_use": "Use when you need to make a hole in a wall or other drillable surface",
  "how_to_use": {
    "inputs": [
      {
        "name": "location",
        "type": "string",
        "description": "Location of the hole (e.g., 'x:10,y:20' or textual description)"
      },
      {
        "name": "bit_id",
        "type": "string",
        "description": "Identifier of the drill bit to use (e.g., 'BIT_5MM')"
      }
    ],
    "outputs": {
      "success": "Hole created successfully",
      "failure": [
        {
          "code": "invalid_bit",
          "description": "The selected drill bit is not compatible with the surface"
        },
        {
          "code": "invalid_surface",
          "description": "The surface is not drillable (e.g., unsupported glass)"
        }
      ]
    }
  }
}
```

### Spanish Version
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  "when_to_use": "Usar cuando necesites generar un agujero en una pared u otra superficie perforable",
  "how_to_use": {
    "inputs": [
      {
        "name": "location",
        "type": "string",
        "description": "Ubicación del agujero (e.g., 'x:10,y:20' o descripción textual)"
      },
      {
        "name": "bit_id",
        "type": "string",
        "description": "Identificador de la broca a usar (e.g., 'BIT_5MM')"
      }
    ],
    "outputs": {
      "success": "Agujero creado con éxito",
      "failure": [
        {
          "code": "invalid_bit",
          "description": "La broca seleccionada no es compatible con la superficie"
        },
        {
          "code": "invalid_surface",
          "description": "La superficie no es perforable (e.g., vidrio no soportado)"
        }
      ]
    }
  }
}
```

### Portuguese Version
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Permite criar furos em superfícies sólidas",
  "when_to_use": "Usar quando precisar fazer um furo em uma parede ou outra superfície perfurável",
  "how_to_use": {
    "inputs": [
      {
        "name": "location",
        "type": "string",
        "description": "Localização do furo (ex.: 'x:10,y:20' ou descrição textual)"
      },
      {
        "name": "bit_id",
        "type": "string",
        "description": "Identificador da broca a ser usada (ex.: 'BIT_5MM')"
      }
    ],
    "outputs": {
      "success": "Furo criado com sucesso",
      "failure": [
        {
          "code": "invalid_bit",
          "description": "A broca selecionada não é compatível com a superfície"
        },
        {
          "code": "invalid_surface",
          "description": "A superfície não é perfurável (ex.: vidro não suportado)"
        }
      ]
    }
  }
}
```

## Text Translator Tool

### English Version
```json
{
  "tool_id": "text_translator_v1",
  "description": "Translates text between languages",
  "when_to_use": "Use when you need to convert text from one language to another",
  "how_to_use": {
    "inputs": [
      {
        "name": "text",
        "type": "string",
        "description": "Text to translate"
      },
      {
        "name": "source_lang",
        "type": "string",
        "description": "Source language code (e.g., 'es', 'en')"
      },
      {
        "name": "target_lang",
        "type": "string",
        "description": "Target language code (e.g., 'fr', 'de')"
      }
    ],
    "outputs": {
      "success": "Text successfully translated",
      "failure": [
        {
          "code": "unsupported_language",
          "description": "The source or target language is not supported"
        },
        {
          "code": "invalid_text",
          "description": "The input text is invalid or empty"
        }
      ]
    }
  }
}
```

### Spanish Version
```json
{
  "tool_id": "text_translator_v1",
  "description": "Permite traducir texto entre idiomas",
  "when_to_use": "Usar cuando necesites convertir texto de un idioma a otro",
  "how_to_use": {
    "inputs": [
      {
        "name": "text",
        "type": "string",
        "description": "Texto a traducir"
      },
      {
        "name": "source_lang",
        "type": "string",
        "description": "Código del idioma de origen (e.g., 'es', 'en')"
      },
      {
        "name": "target_lang",
        "type": "string",
        "description": "Código del idioma de destino (e.g., 'fr', 'de')"
      }
    ],
    "outputs": {
      "success": "Texto traducido con éxito",
      "failure": [
        {
          "code": "unsupported_language",
          "description": "El idioma de origen o destino no está soportado"
        },
        {
          "code": "invalid_text",
          "description": "El texto de entrada es inválido o está vacío"
        }
      ]
    }
  }
}
```

### Portuguese Version
```json
{
  "tool_id": "text_translator_v1",
  "description": "Permite traduzir texto entre idiomas",
  "when_to_use": "Usar quando precisar converter texto de um idioma para outro",
  "how_to_use": {
    "inputs": [
      {
        "name": "text",
        "type": "string",
        "description": "Texto a ser traduzido"
      },
      {
        "name": "source_lang",
        "type": "string",
        "description": "Código do idioma de origem (ex.: 'pt', 'en')"
      },
      {
        "name": "target_lang",
        "type": "string",
        "description": "Código do idioma de destino (ex.: 'fr', 'de')"
      }
    ],
    "outputs": {
      "success": "Texto traduzido com sucesso",
      "failure": [
        {
          "code": "unsupported_language",
          "description": "O idioma de origem ou destino não é suportado"
        },
        {
          "code": "invalid_text",
          "description": "O texto de entrada é inválido ou está vazio"
        }
      ]
    }
  }
}
```

## Validation

All examples in this page are valid against the ATDF schema. You can validate them using the validator script:

```bash
python tools/validator.py schema/examples/hole_maker_en.json
python tools/validator.py schema/examples/hole_maker_es.json
python tools/validator.py schema/examples/hole_maker_pt.json
```

[View More Examples on GitHub](https://github.com/MauricioPerera/agent-tool-description-format/tree/main/schema/examples) 