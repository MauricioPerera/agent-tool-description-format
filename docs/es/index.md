[Inicio](index.md) | [Especificación](specification.md) | [Ejemplos](examples.md) | [Guía MCP de n8n](n8n_mcp_server_guide.md) | [Contribuir](contributing.md) | [Multilingüe](multilingual.md) | [Historial de Cambios](changelog.md) | [Licencia](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](index.md) | [Português (pt)](../pt/index.md)

## 📚 Documentación Principal

- **[Especificación ATDF](../docs/ATDF_SPECIFICATION.md)** - Especificación completa del formato
- **[Conceptos Fundamentales](../docs/CONCEPTS.md)** - Explicación de conceptos clave
- **[Ejemplos de Implementación](../docs/examples.md)** - Ejemplos en múltiples lenguajes y herramientas
- **[Guía de Implementación](./IMPLEMENTATION_GUIDE.md)** - Cómo implementar ATDF
- **[Mejores Prácticas](./BEST_PRACTICES.md)** - Recomendaciones para implementación

### 📊 **Recursos Visuales**
- **[Diagramas Mermaid](../MERMAID_DIAGRAMS.md)** - Diagramas de flujo y arquitectura ATDF

# Formato de Descripción de Herramientas para Agentes (ATDF)

Bienvenido a la documentación del **Formato de Descripción de Herramientas para Agentes (ATDF)**, un protocolo abierto para describir herramientas funcionalmente para permitir que los agentes de IA las seleccionen y usen basándose en el propósito, contexto y operación, sin depender de detalles específicos de implementación.

## Versión Actual

**Versión actual: 0.2.0** - Consulta el [historial de cambios](changelog.md) para detalles sobre las últimas actualizaciones.

## Introducción

ATDF está diseñado para resolver el problema de la integración de herramientas para agentes de IA. En lugar de requerir nombres de herramientas codificados o APIs técnicas complejas, ATDF proporciona una forma estandarizada de describir herramientas basada en:

1.  **Qué** hace la herramienta
2.  **Cuándo** debe usarse
3.  **Cómo** se usa

Este enfoque funcional permite a los agentes de IA seleccionar herramientas basadas en la tarea en cuestión, en lugar de requerir conocimiento específico sobre nombres de herramientas o APIs.

## Características Clave

### Características Principales (v0.1.0)
- **Formato Simple y Legible por Humanos**: Estructura JSON/YAML fácil de entender.
- **Agnóstico al Modelo**: Funciona con cualquier modelo de agente de IA.
- **Agnóstico a la Herramienta**: Describe tanto herramientas físicas (ej., taladros) como herramientas digitales (ej., APIs).
- **Agnóstico al Prompt**: Selección de herramientas basada en la función, no en nombres específicos.
- **Validación de Esquema**: Esquema JSON para validar descripciones de herramientas.

### Características Mejoradas (v0.2.0)
- **Soporte de Metadatos**: Organiza herramientas con información de versión, autor, etiquetas y categoría.
- **Soporte Multilingüe Enriquecido**: Localización integrada para múltiples idiomas.
- **Prerrequisitos y Dependencias**: Especifica herramientas, condiciones y permisos requeridos.
- **Mecanismos de Retroalimentación**: Indicadores de progreso y señales de finalización.
- **Ejemplos de Uso**: Ejemplos del mundo real con entradas y salidas esperadas.
- **Tipos de Entrada Complejos**: Soporte para objetos anidados y esquemas avanzados.

## Enlaces Rápidos

- [Especificación](specification.md): Especificación técnica detallada del protocolo ATDF.
- [Compatibilidad de Versiones](version_compatibility.md): Tabla que relaciona etiquetas antiguas con los esquemas actuales.
- [Compatibilidad de Versiones](version_compatibility.md): Tabla que relaciona etiquetas antiguas con los esquemas actuales.
- [Ejemplos](examples.md): Descripciones de herramientas de muestra y cómo crear las tuyas.
- [Soporte Multilingüe](multilingual.md): Información sobre el uso de múltiples idiomas.
- [Contribuir](contributing.md): Directrices para contribuir a ATDF.
- [Guía de Rediseño](redesign_guidelines.md): Consideraciones clave para evolucionar el protocolo.
- [Historial de Cambios](changelog.md): Historial de versiones y cambios de ATDF.

## Primeros Pasos

1. **Elige el esquema correcto**
   - 1.x básico (`schema/atdf_schema.json`): descripciones esenciales con `tool_id`, `description`, `when_to_use` y `how_to_use`.
   - 2.x mejorado (`schema/enhanced_atdf_schema.json`): agrega `metadata`, `localization`, `prerequisites`, `examples` y `feedback`.
   Revisa [Compatibilidad de Versiones](version_compatibility.md) si tienes dudas.

2. **Redacta la descripción**

```json
{
  "schema_version": "2.0.0",
  "tool_id": "validador_fechas",
  "description": "Valida rangos de fechas y explica cómo corregir errores",
  "when_to_use": "Usa la herramienta cuando necesites verificar fechas con recomendaciones",
  "how_to_use": {
    "inputs": [
      {"name": "fecha_inicio", "type": "string", "description": "Fecha inicial ISO 8601", "required": true},
      {"name": "fecha_fin", "type": "string", "description": "Fecha final ISO 8601", "required": true}
    ],
    "outputs": {
      "success": "El rango es válido",
      "failure": [
        {"code": "INVALID_DATE_RANGE", "description": "La fecha inicial debe ser menor que la final"}
      ]
    }
  }
}
```

Para un descriptor 1.x usa `schema_version` = "1.0.0" y omite campos opcionales como `metadata` y `examples`.

3. **Valida y prueba**

```bash
python tools/validator.py tu_tool.json --schema schema/atdf_schema.json
python tools/validate_enhanced.py tu_tool.json
python tests/run_all_tests.py
```

El manejo de errores enriquecidos se explica en la [Guía de Respuestas Enriquecidas](enriched_responses_guide.md).
## Licencia

ATDF está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](license.md) para más detalles.

## Componentes Principales

- [**Especificación**](specification.md): Los detalles técnicos del formato
- [**Ejemplos**](examples.md): Ejemplos de descripciones de herramientas
- [**Ejemplos de Uso**](../usage_examples.md): Ejemplos prácticos de uso de ATDF
- [**Soporte Multilingüe**](multilingual.md): Cómo funciona la localización
- [**Convertidor MCP a ATDF**](../usage_examples.md#convertidor-mcp-a-atdf): Herramientas para convertir desde el formato MCP
- [**Contribuir**](contributing.md): Cómo contribuir al proyecto
- [**Registro de Cambios**](changelog.md): Historial de cambios

---

[Repositorio GitHub](https://github.com/MauricioPerera/agent-tool-description-format) | [Historial de Cambios](changelog.md) 
