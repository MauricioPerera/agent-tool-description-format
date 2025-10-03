# Lista de pendientes ATDF

## Épicas
- **E1. Documentación multilingüe consistente:** Garantizar que la documentación clave de ATDF esté alineada en inglés, español y portugués.
- **E2. Experiencia de desarrollador en SDKs:** Optimizar los SDK de Python y JavaScript para facilitar la adopción del formato ATDF.
- **E3. Automatización y validaciones:** Fortalecer las herramientas de validación y pipelines de control de calidad para descriptores ATDF.
- **E4. Integraciones operativas:** Expandir y mantener integraciones con n8n, MCP y sistemas de monitoreo asociados.

## Requerimientos
- **R1 (E1):** Elaborar una guía de contribución traducida y sincronizada en `docs/en`, `docs/es` y `docs/pt`.
- **R2 (E1):** Publicar plantillas de descriptores ATDF con ejemplos localizados.
- **R3 (E2):** Añadir ejemplos prácticos de uso de los SDK en escenarios reales.
- **R4 (E2):** Implementar pruebas automatizadas de regresión para las funciones críticas de los SDK.
- **R5 (E3):** Integrar el validador de esquemas en la pipeline CI/CD con reportes detallados.
- **R6 (E3):** Documentar respuestas de error enriquecidas y su manejo en agentes.
- **R7 (E4):** Actualizar los flujos de trabajo de n8n para reflejar las mejoras del protocolo ATDF.
- **R8 (E4):** Definir métricas clave y tableros de monitoreo estandarizados para despliegues ATDF.

## Historias de Usuario
- **HU1 (E1, R1):** Como contribuidor técnico, quiero una guía consolidada en los tres idiomas soportados para seguir el proceso correcto sin ambigüedades.
- **HU2 (E1, R2):** Como diseñador de herramientas, quiero plantillas localizadas de descriptores ATDF para acelerar la creación de nuevos recursos multilingües.
- **HU3 (E2, R3):** Como desarrollador backend, necesito ejemplos paso a paso de los SDK para integrar rápidamente ATDF en mi servicio.
- **HU4 (E2, R4):** Como responsable de calidad, deseo pruebas automatizadas que cubran los casos críticos para detectar regresiones antes del despliegue.
- **HU5 (E3, R5):** Como ingeniero de plataforma, quiero que la validación de esquemas se ejecute en CI/CD para prevenir la publicación de descriptores inválidos.
- **HU6 (E3, R6):** Como autor de herramientas, necesito lineamientos claros sobre cómo emitir respuestas de error enriquecidas para ayudar a los agentes a recuperarse.
- **HU7 (E4, R7):** Como integrador de n8n, deseo flujos actualizados que aprovechen las capacidades recientes del protocolo para automatizar tareas.
- **HU8 (E4, R8):** Como analista de operaciones, quiero tableros con métricas estandarizadas que me permitan monitorear el uso de ATDF en producción.

## Plan de Implementación, Validación, Corrección y Publicación

1. **Planificación y diseño (Implementación)**
   - Priorizar épicas y requerimientos según impacto y dependencias, definiendo responsables por iniciativa.
   - Crear hojas de ruta quincenales con entregables medibles para documentación, SDKs, automatización e integraciones.
   - Preparar entornos de desarrollo y tableros de seguimiento (por ejemplo, Kanban) para registrar avances y bloqueos.

2. **Desarrollo iterativo (Implementación)**
   - Redactar y actualizar la documentación multilingüe en ramas dedicadas, aplicando revisiones cruzadas entre equipos de idioma.
   - Implementar mejoras en SDKs y validadores con pruebas unitarias desde el inicio; documentar cambios en `CHANGELOG.md`.
   - Coordinar a los equipos de integraciones para ajustar flujos de n8n y tableros de monitoreo con pruebas sandbox previas.

3. **Validación integral (Validación)**
   - Ejecutar suites automatizadas (`python tests/run_all_tests.py`, `npm test` en `js/`) y validadores de esquemas para cada entrega.
   - Revisar manualmente la localización y coherencia de la documentación en los tres idiomas antes de fusionar cambios.
   - Validar flujos n8n/MCP en entornos de staging con datos de prueba representativos y reportar métricas clave.

4. **Gestión de hallazgos (Corrección)**
   - Registrar incidencias detectadas en QA o staging en un backlog de bugs priorizado por severidad y frecuencia.
   - Implementar correcciones rápidas mediante ramas de hotfix o iteraciones planificadas, incluyendo pruebas regresivas.
   - Actualizar las guías y notas de versión para reflejar las correcciones y lecciones aprendidas.

5. **Preparación y despliegue (Publicación)**
   - Completar checklist de publicación: validaciones exitosas, documentación sincronizada, métricas configuradas y aprobación de stakeholders.
   - Etiquetar versiones de SDKs y herramientas relacionadas siguiendo el esquema semántico y subir paquetes/bundles correspondientes.
   - Comunicar el despliegue a los equipos consumidores (documentación, changelog, canales internos) y monitorear en producción durante la ventana inicial.
