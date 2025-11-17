# Notas de lanzamiento v2.1.0

_Fecha de publicación: 2025-02-14_

## Resumen ejecutivo
La versión **2.1.0** del SDK de ATDF consolida la transición hacia una búsqueda con puntuaciones explícitas, manteniendo la compatibilidad con integraciones existentes. Se refuerzan la documentación y los ejemplos para guiar a los equipos durante la migración y se valida el comportamiento con nueva cobertura de pruebas.

## Novedades destacadas
- **Búsqueda con puntuación unificada**: `ATDFToolbox.find_tools_by_text` devuelve ahora tuplas `(herramienta, score)` por defecto, exponiendo la similitud calculada en los flujos modernos.
- **Compatibilidad inmediata**: Se incorpora el flag `return_scores=False` para que los consumidores heredados sigan recibiendo únicamente instancias de `ATDFTool` sin modificar su código.
- **Documentación mejorada**: El README del SDK, las guías de búsqueda vectorial y los ejemplos muestran patrones lado a lado para iterar con y sin puntuaciones.
- **Regresión cubierta**: Nuevas pruebas garantizan que el modo legado conserve el tipo de retorno esperado y que las puntuaciones sean siempre `float`, incluso en el _fallback_ por palabras clave.

## Compatibilidad y migración
- El cambio de comportamiento por defecto se documenta como _breaking change_ en `CHANGELOG.md`, con pasos claros para actualizar bucles `for` existentes.
- Las integraciones que prefieran no tocar su código pueden activar `return_scores=False` de manera transitoria.
- Se recomienda actualizar los consumidores para aprovechar la puntuación (permite ordenar, filtrar y auditar búsquedas).

## Documentación actualizada
- `CHANGELOG.md` describe el cambio y las opciones de migración.
- `sdk/README.md`, `sdk/examples.py` y `sdk/vector_search/README.md` incluyen fragmentos de código con ambas modalidades.
- Los ejemplos ahora destacan el uso del score `0.0` cuando se recurre al buscador por palabras clave como _fallback_.

## Calidad y pruebas
- Suite unitaria: `python -m unittest tests.test_vector_search`.
- Se añaden escenarios que cubren las búsquedas vectoriales y el flujo heredado sin puntuaciones.

## Recomendaciones posteriores al lanzamiento
1. Comunicar a los integradores que el modo con puntuación será el estándar recomendado a partir de ahora.
2. Monitorizar logs en ambientes productivos para confirmar que el _fallback_ por palabras clave mantiene una tasa de aciertos adecuada.
3. Planificar la deprecación del modo sin puntuaciones en una versión mayor (p. ej. v3.0.0) una vez completada la adopción.

---
¿Listo para publicar? Actualiza la fecha, comparte el enlace al changelog completo y anuncia la disponibilidad de **ATDF SDK v2.1.0** en los canales internos y externos.
