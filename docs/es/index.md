[Inicio](index.md) | [Especificación](specification.md) | [Ejemplos](examples.md) | [Contribuir](contributing.md) | [Multilingüe](multilingual.md) | [Historial de Cambios](changelog.md) | [Licencia](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](index.md) | [Português (pt)](../pt/index.md)

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
- [Ejemplos](examples.md): Descripciones de herramientas de muestra y cómo crear las tuyas.
- [Soporte Multilingüe](multilingual.md): Información sobre el uso de múltiples idiomas.
- [Contribuir](contributing.md): Directrices para contribuir a ATDF.
- [Historial de Cambios](changelog.md): Historial de versiones y cambios de ATDF.

## Primeros Pasos

Para comenzar a usar ATDF, puedes:

1.  **Explorar Ejemplos**: Revisa las [descripciones de herramientas de ejemplo](examples.md) para entender el formato.
2.  **Crear las Tuyas**: Sigue la [especificación](specification.md) para crear descripciones de herramientas.
3.  **Validar Herramientas**: Usa el validador para asegurar que tus descripciones de herramientas sean válidas:
    ```bash
    python tools/validator.py ruta/a/tu/herramienta.json
    ```
4.  **Probar la Demo**: Ejecuta los agentes de demostración para ver ATDF en acción:
    ```bash
    python tools/demo/atdf_showcase.py
    ```
    (Nota: estos scripts podrían necesitar existir o ser adaptados)

## Casos de Uso

ATDF está diseñado para una amplia gama de aplicaciones, incluyendo:

- **Agentes de IA**: Ayudar a los sistemas de IA a seleccionar y usar herramientas apropiadamente.
- **Robótica**: Describir herramientas físicas para sistemas robóticos.
- **Integración de API**: Estandarizar descripciones de APIs y servicios web.
- **Aplicaciones Multimodales**: Unificar diferentes tipos de herramientas en un formato común.
- **Sistemas Multilingües**: Soportar descripciones de herramientas en diferentes idiomas.

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