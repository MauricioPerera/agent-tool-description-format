[Inicio](index.md) | [Especificación](specification.md) | [Ejemplos](examples.md) | [Guía MCP de n8n](n8n_mcp_server_guide.md) | [Contribuir](contributing.md) | [Multilingüe](multilingual.md) | [Historial de Cambios](changelog.md) | [Licencia](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](index.md) | [Português (pt)](../pt/index.md)

## 🚀 Inicio Rápido

1. **Elige el esquema adecuado**
   - 1.x básico (`schema/atdf_schema.json`): descripciones esenciales con `tool_id`, `description`, `when_to_use` y `how_to_use`.
   - 2.x mejorado (`schema/enhanced_atdf_schema.json`): añade `metadata`, `localization`, `prerequisites`, `examples` y `feedback`.
   Consulta la [Compatibilidad de Versiones](version_compatibility.md) si tienes dudas.

2. **Redacta el descriptor**

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

Consulta la [Guía de Respuestas Enriquecidas](enriched_responses_guide.md) para diseñar errores detallados.

## 📚 Documentación principal
- **[Especificación ATDF](../docs/ATDF_SPECIFICATION.md)** – Referencia completa del formato
- **[Conceptos Fundamentales](../docs/CONCEPTS.md)** – Explicación de los conceptos clave
- **[Ejemplos de Implementación](../docs/examples.md)** – Casos en múltiples lenguajes y frameworks
- **[Guía de Implementación](IMPLEMENTATION_GUIDE.md)** – Cómo agregar ATDF a tus herramientas
- **[Mejores Prácticas](BEST_PRACTICES.md)** – Recomendaciones y patrones comprobados
- **[Flujo ATDF + MCP + n8n](n8n_mcp_integracion_flujo.md)** – Arquitectura y escenarios de integración

### Recursos visuales
- **[Diagramas Mermaid](../MERMAID_DIAGRAMS.md)** – Diagramas de flujo y arquitectura ATDF

## 🔌 Integraciones destacadas
- **n8n + MCP + ATDF**: sigue la [guía de integración](n8n_mcp_integracion_flujo.md) para conectar el bridge ATDF-MCP y ejecutar herramientas desde n8n (nodos nativos o personalizados).
- **API REST y Autenticación de n8n**: `../../n8n_setup_complete.md` — cómo autenticar y importar workflows por REST.
- **Workflow Code v3 (n8n)**: `../../n8n-workflows/README.md` — flujo de viaje completo usando MCP Bridge.
- **Guía rápida (ES)**: `../../GUIA_INTEGRACION_N8N.md` — configuración ATDF + MCP + n8n.
- **Índice central n8n + MCP + ATDF**: `../n8n_mcp_atdf_index.md` — mapa unificado de documentación.
- **Bridge ATDF-MCP local**:
  ```bash
  python examples/fastapi_mcp_integration.py
  python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
  ```

## ⭐ Características clave
- **Errores enriquecidos**: contexto completo (`expected`, soluciones, valores sugeridos).
- **Soporte multilingüe**: localización integrada para descripciones y errores.
- **Validación automática**: detecta la versión del esquema y valida entradas/salidas.
- **Interoperabilidad**: SDKs en Python y JavaScript, conversores MCP y nodos para n8n.

## 📦 Casos de uso
- **Agentes de IA** que necesitan descubrir herramientas por función y contexto.
- **APIs y microservicios** que requieren respuestas de error consistentes.
- **Workflows no-code** (n8n, Zapier) que consumen metadatos declarativos.
- **Mercados de herramientas** con catálogos multilingües y permisos granulares.

## 🤝 Cómo contribuir
- Revisa la [guía de contribución](contributing.md) para flujos de trabajo, checklist de PR y estilo.
- Ejecuta `python tests/run_all_tests.py` y `npm test` (en `js/`) antes de enviar cambios.
- Mantén sincronizadas las traducciones en `docs/en`, `docs/es` y `docs/pt`.

## 📄 Licencia
ATDF se distribuye bajo la licencia MIT. Consulta [License](license.md) para más detalles.

---

**ATDF v2.0.0** – Formato estándar para describir herramientas funcionalmente, habilitando agentes más inteligentes y flujos multilingües con manejo de errores enriquecido.
