# Guía de Rediseño de ATDF

## Propósito
Guía para definir una versión de próxima generación del Agent Tool Description Format (ATDF) sin romper la interoperabilidad con los ecosistemas de agentes existentes.

## Temas que cubrir
- **Alcance del protocolo**: Problema a resolver, escenarios soportados, relación con estándares existentes (JSON Schema, OpenAPI, MCP, etc.).
- **Modelo de datos**: Campos obligatorios, extensiones opcionales, alias, reglas de tipado, esquemas de parámetros, entradas condicionales.
- **Semántica de uso**: when_to_use, how_to_use, convenciones de entrada/salida, negociación de versiones, descubrimiento de capacidades.
- **Modelo de errores**: Estructura estándar de payloads, contexto diagnóstico, pistas de remediación, mapeo a errores de transporte o ejecución.
- **Ciclo de vida y versionado**: Flujo de publicación, política de versionado semántico, cronogramas de deprecación, expectativas de compatibilidad.
- **Seguridad y permisos**: Indicadores de alcances requeridos, límites de uso, nivel de riesgo, solicitudes de consentimiento.
- **Extensibilidad**: Mecanismos para metadatos específicos de proveedores, reglas de namespacing, proceso de registro para extensiones comunitarias.
- **Herramientas y soporte**: Validadores, SDKs, ejemplos, servidores de referencia, suites de conformidad.
- **Gobernanza**: Proceso de decisión, control de cambios, obligaciones de documentación, requisitos multilingües.

## Riesgos a evitar
- **Sobre-especificación**: Incluir supuestos sobre runtimes o capas de transporte que limiten la adopción.
- **Sub-especificación**: Dejar comportamientos clave ambiguos, especialmente en campos opcionales o valores por defecto.
- **Cambios disruptivos sin migración**: Eliminar o renombrar campos sin alias o ignorar el versionado semántico.
- **Lógica de negocio incrustada**: Permitir lógica ejecutable o estado dinámico dentro de las descripciones en lugar de metadatos declarativos.
- **Campos redundantes o en conflicto**: Introducir conceptos superpuestos que confundan a las implementaciones de agentes.
- **Descuidar la validación**: Publicar sin herramientas de linting, validación de esquemas o suites de conformidad.
- **Ignorar la localización**: No definir cómo deben entregarse las traducciones de descripciones y guías.
- **Puntos ciegos de seguridad**: Omitir formas de expresar permisos, necesidades de auditoría o consideraciones de privacidad.

## Proceso recomendado
1. Redacta un modelo de referencia que cubra los temas anteriores y recoge feedback de integradores.
2. Prototipa las actualizaciones de esquema y actualiza validadores, SDKs y documentación en paralelo.
3. Ofrece guías de migración, ejemplos prácticos y pruebas automatizadas antes de declarar estable el rediseño.
4. Establece artefactos de gobernanza (hoja de ruta, proceso de RFC, changelog) para gestionar futuras revisiones.
