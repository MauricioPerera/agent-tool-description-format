# Lista de verificación de cierre — Versión 2.1.0

Esta checklist resume las tareas finales para preparar y publicar la versión 2.1.0 del SDK de ATDF. Úsala como guía antes de generar la etiqueta y anunciar la versión.

## 1. Limpieza de código y dependencias
- [ ] Revisar `sdk/vector_search/vector_store.py` y eliminar métodos síncronos duplicados, manteniendo solo las corrutinas y sus _wrappers_ `*_sync`.
- [ ] Confirmar que cualquier cambio de limpieza está cubierto por pruebas existentes o nuevas (por ejemplo, uso mixto de `return_scores`).
- [ ] Ejecutar `pip list --outdated` (o equivalente) para detectar dependencias críticas que convenga actualizar antes del release.

## 2. Cobertura de pruebas
- [ ] Añadir/ejecutar pruebas para:
  - [ ] Búsquedas consecutivas con y sin `return_scores` sobre la misma consulta.
  - [ ] Comportamiento del parámetro `limit` en modos con puntuación y legado.
  - [ ] Casos límite (consultas vacías, sin resultados y coincidencias exactas con `score == threshold`).
- [ ] Ejecutar `python -m unittest tests.test_vector_search` y cualquier suite adicional afectada.
- [ ] Registrar resultados de las pruebas en `DELIVERY_SUMMARY.md` o herramienta equivalente.

## 3. Documentación
- [ ] Actualizar la guía del SDK con una tabla rápida que compare los modos con puntuación vs. legado, aclarando que `score = 0.0` proviene del _fallback_ por palabras clave.
- [ ] Añadir ejemplos mínimos para `find_tools_by_text(return_scores=False)` en los fragmentos de código principales (README, ejemplos y demos).
- [x] Revisar `CHANGELOG.md` para asegurar que el bloque _Unreleased_ se convierta en `v2.1.0 - 2025-02-14` con fecha final y enlaces a PR/commits relevantes.

## 4. Comunicación del release
- [ ] Preparar la nota de lanzamiento (ES/EN/PT si aplica) utilizando `RELEASE_NOTES_v2.1.0_ES.md` como base y crear las traducciones pendientes.
- [ ] Publicar la nota en el canal oficial (GitHub Releases, blog interno, etc.) incluyendo pasos de migración y resumen ejecutivo.
- [ ] Informar a los equipos consumidores (n8n, integraciones MCP, automatizaciones internas) sobre el cambio por defecto a `(herramienta, puntuación)`.

## 5. Post-lanzamiento
- [ ] Monitorizar métricas y feedback de usuarios durante la primera semana para detectar problemas con el flag `return_scores`.
- [ ] Crear issues de seguimiento para mejoras futuras (p. ej., helper `find_tools_plain`, documentación ampliada de puntuaciones).
- [ ] Agendar una revisión retrospectiva para capturar aprendizajes de la migración y priorizar las próximas tareas del backlog.

> ✅ Marca cada elemento a medida que lo completes para garantizar un cierre ordenado del release.
