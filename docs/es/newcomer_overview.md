# Guía para Nuevas Personas en el Proyecto

## Resumen rápido
Agent Tool Description Format (ATDF) es una especificación independiente de la implementación que estandariza cómo los agentes de IA descubren y operan herramientas externas. Define esquemas JSON para catálogos de herramientas y respuestas de error enriquecidas, permitiendo que los agentes razonen sobre cuándo y cómo invocar cada capacidad disponible.

## Estado actual
⚠️ Este plan de onboarding sigue pendiente de implementarse. Toma el esquema siguiente como una lista preliminar hasta que el equipo asigne responsables y se creen los materiales de apoyo.

## Estructura del repositorio
- **Esquemas (`schema/`)** – Documentos JSON Schema autorizados para los descriptores ATDF clásicos (1.x) y mejorados (2.x), junto con el sobre de errores enriquecidos.
- **Herramientas en Python (`tools/`, `sdk/`)** – Validadores de línea de comandos, utilidades de conversión y un SDK en Python (`ATDFTool`, cargadores de catálogos, búsqueda multilingüe, auto-selección) que interpretan descriptores y ejecutan consultas de catálogo de forma programática.
- **SDK de JavaScript (`js/`)** – Utilidades para Node.js/navegador que replican las funciones del SDK de Python, incluyendo búsqueda vectorial opcional, asistentes de localización y conversores MCP→ATDF.
- **Ejemplos (`examples/`)** – Aplicación de referencia en FastAPI, demostraciones de escenarios y pruebas de integración que muestran un manejo de errores ATDF de extremo a extremo, flujos de reservas y conexión con Model Context Protocol (MCP).
- **Documentación (`docs/`)** – Especificaciones, guías de implementación, recorridos de integración (FastAPI, n8n, monitoreo) y contenido multilingüe sincronizado entre inglés/español/portugués.
- **Automatización y flujos (`n8n-*`, `monitoring/`, `scripts/`)** – Flujos n8n listos para importar, tableros de monitoreo y scripts de apoyo para levantar entornos de demostración.

## Conceptos clave a dominar primero
1. **Descriptores de herramientas** – Comprende los campos obligatorios y opcionales en los esquemas ATDF clásico y mejorado, incluyendo metadatos de localización, prerrequisitos y ejemplos guiados.
2. **Respuestas de error enriquecidas** – Revisa el sobre de error compartido (`schema/enriched_response_schema.json`) para que tus servicios entreguen sugerencias de remediación accionables a los agentes.
3. **Patrones de uso de los SDK** – Estudia cómo los SDK de Python y JavaScript cargan catálogos, realizan búsqueda textual/vectorial y auto-seleccionan herramientas para evitar reimplementar lógica de parseo.
4. **Puente FastAPI MCP** – Usa la aplicación de ejemplo en `examples/` como implementación de referencia y banco de pruebas al integrar ATDF en nuevos entornos de ejecución.

## Buenas prácticas al trabajar en el repositorio
- Valida los descriptores desde temprano con `tools/validator.py` o `tools/validate_enhanced.py` antes de distribuirlos.
- Ejecuta las suites de pruebas en Python y JavaScript (`python tests/run_all_tests.py`, `npm test` dentro de `js/`) para detectar regresiones en los SDK.
- Utiliza los flujos FastAPI + n8n como pruebas de sistema al ajustar la lógica del servidor o las integraciones MCP.
- Mantén la documentación localizada: cualquier cambio en `docs/en` debe replicarse en `docs/es` y `docs/pt`.

## Pasos siguientes para tu onboarding
1. Lee la **Guía de Implementación** (`docs/IMPLEMENTATION_GUIDE.md`) para conocer los patrones arquitectónicos, la estrategia de validación y las consideraciones de despliegue.
2. Explora los **ejemplos de los SDK** en `sdk/` y `js/` para observar la carga de catálogos, el manejo de metadatos multilingües y la extracción de esquemas en acción.
3. Sigue los **recorridos n8n + MCP** (`docs/*n8n*`) para comprender la orquestación extremo a extremo y el manejo de errores en flujos de automatización.
4. Revisa los **manuales de monitoreo** (`monitoring/`) para aprender cómo los despliegues en producción rastrean métricas de errores ATDF y salud operativa.
