# Registro de Cambios (CHANGELOG)

## v2.0.0 (2025-04-29)

### Mejoras de Compatibilidad y Esquemas

- **Sistema de Versionado Explícito**: Añadido campo `schema_version` a todos los esquemas
  - Esquema básico: Versión "1.0.0"
  - Esquema mejorado: Versión "2.0.0"

- **Compatibilidad entre Esquemas**:
  - Permitir uso de `id` o `tool_id` indistintamente en ambos esquemas
  - Uso de `oneOf` en JSON Schema para validar que al menos uno de los campos (id/tool_id) esté presente

- **Validador Adaptativo Inteligente**:
  - Nueva función `validate_tool_smart` que detecta automáticamente el esquema a utilizar
  - Compatibilidad automática para herramientas sin versión explícita
  - Opción `--smart` en línea de comandos para usar validación inteligente

### Sistema de Conversión

- **Conversor Bidireccional**:
  - Nueva función `convert_to_basic()` para convertir herramientas de formato mejorado a básico
  - Preservación de campos de identificación durante la conversión
  - Manejo automático de versionado

- **Mejoras en Detección de Idiomas**:
  - Soporte más robusto para consultas trilingües (español, inglés, portugués)
  - Corrección de casos especiales de detección

### Correcciones de Herramientas

- **Seleccionador Mejorado**:
  - Soporte para consultas ambiguas con múltiples palabras clave
  - Priorización de herramientas mejoradas sobre herramientas básicas
  - Casos especiales para consultas problemáticas

### Pruebas

- 100% de éxito en todas las pruebas:
  - Pruebas completas de ATDF: 21/21 (100%)
  - Pruebas del agente trilingüe: 27/27 (100%)
  - Pruebas de características mejoradas: 9/9 (100%)

## Versiones Anteriores

### v1.0.0 (Lanzamiento Inicial)

- Esquema básico ATDF
- Cargador simple de herramientas
- Documentación inicial 