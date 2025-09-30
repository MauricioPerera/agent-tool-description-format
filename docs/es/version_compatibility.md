[Inicio](index.md) | [Especificación](specification.md) | [Ejemplos](examples.md) | [Contribuir](contributing.md) | [Multilingüe](multilingual.md) | [Historial de Cambios](changelog.md) | [Licencia](license.md)

**Idiomas:** [English (en)](../en/version_compatibility.md) | [Español (es)](version_compatibility.md) | [Português (pt)](../pt/version_compatibility.md)

# Compatibilidad de Versiones ATDF

Esta guía resume cómo las versiones históricas de ATDF se relacionan con los esquemas JSON actuales y sus características.

## Matriz de esquemas y funcionalidades

| Versión de esquema | Nombre legado | Funcionalidades clave | Uso recomendado |
| ------------------- | ------------- | --------------------- | --------------- |
| 1.x (`schema/atdf_schema.json`) | ATDF v0.1 Básico | Metadatos fundamentales (`tool_id/id`, `description`, `when_to_use`, `how_to_use.inputs/outputs`) y catálogo simple de errores | Agentes que sólo necesitan llamadas declarativas |
| 2.x (`schema/enhanced_atdf_schema.json`) | ATDF v0.2 Mejorado | Añade `metadata`, `localization`, `prerequisites`, `examples` y campos estructurados de `feedback` | Asistentes multilingües, marketplaces y despliegues avanzados |
| Esquema de respuestas enriquecidas (`schema/enriched_response_schema.json`) | ATDF v2.0 Error Envelope | Payload canónico con `expected`, `solution` y bloques de contexto | Cualquier herramienta que devuelva orientación accionable |

## Notas de compatibilidad

- El esquema 2.x es un superconjunto de 1.x; las descripciones básicas siguen siendo válidas.
- Las herramientas mejoradas deben declarar `schema_version` = `"2.0.0"` (o superior) para que los validadores seleccionen el esquema correcto.
- Las respuestas de error enriquecidas pueden adoptarse de forma independiente siempre que respeten `enriched_response_schema.json`.
- Los documentos legados escritos para ATDF v0.1/v0.2 equivalen directamente a los esquemas 1.x/2.x anteriores. Actualiza la documentación para referenciar rutas de esquema cuando sea posible.

## Lista de verificación de migración

1. Confirma qué esquema debe usar la descripción y declara explícitamente `schema_version`.
2. Valida con `python tools/validator.py ... --schema schema/atdf_schema.json` para 1.x o `python tools/validate_enhanced.py ...` para 2.x.
3. Al migrar a 2.x, añade las nuevas secciones de manera incremental: comienza con `metadata.version`, luego localización y prerequisitos.
4. Adopta el esquema de errores enriquecidos junto con la actualización de la herramienta para entregar diagnósticos consistentes.
