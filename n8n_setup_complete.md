# ✅ Guía Completa: ATDF + MCP + n8n (FUNCIONANDO)

## 🗂️ Tabla de contenido
- [🎉 Estado Actual](#-estado-actual-todo-funcionando)
- [🚀 Configuración Paso a Paso](#-configuración-paso-a-paso)
- [🔧 Configuraciones Avanzadas](#-configuraciones-avanzadas)
- [📊 Monitoreo y Debugging](#-monitoreo-y-debugging)
- [🎯 Resumen de la Solución](#-resumen-de-la-solución)
- [🎉 ¡Listo para Usar!](#--listo-para-usar)
- [🔐 Importación por API (REST) y Autenticación](#-importación-por-api-rest-y-autenticación)
- [🧩 Workflow Code v3](#-workflow-complete-travel-booking-via-atdf-mcp-code-v3)
- [🧪 Troubleshooting API](#-troubleshooting-api)

> Referencias rápidas: ver `GUIA_INTEGRACION_N8N.md` y `n8n-workflows/README.md` para detalles de importación y ejecución del workflow Code v3.

## 🎉 Estado Actual: ¡TODO FUNCIONANDO!

- ✅ Bridge ATDF-MCP ejecutándose en `http://localhost:8001`
- ✅ 2 herramientas ATDF detectadas (hotel reservation, flight booking)
- ✅ Endpoints de salud y herramientas respondiendo correctamente
- ✅ Listo para usar con nodos MCP nativos de n8n

## 🚀 Configuración Paso a Paso

### Paso 1: Verificar que todo esté corriendo

```bash
# Verificar el bridge
curl http://localhost:8001/health

# Debería responder:
# {"status": "healthy", "server": "ATDF-MCP Bridge", "version": "1.0.0", ...}

# Verificar herramientas disponibles
curl http://localhost:8001/tools

# Debería mostrar las herramientas ATDF convertidas a formato MCP
```

### Paso 2: Configurar n8n

1. **Abrir n8n** (si no está abierto):
   ```bash
   n8n
   ```

2. **Crear nuevo workflow**

3. **Añadir nodo "MCP Client"**:
   - Buscar "MCP Client" en la lista de nodos
   - Configurar:
     - **Server URL**: `http://localhost:8001/sse`
     - **Operation**: `listTools` (para empezar)

### Paso 3: Importar Workflow de Ejemplo

Usa el archivo: `examples/n8n_working_example.json`

### Paso 4: Probar la Integración

1. **Ejecutar el nodo "List ATDF Tools"**
   - Debería mostrar las 2 herramientas disponibles
   - Verificar que los metadatos ATDF se preserven

2. **Ejecutar el nodo "Call ATDF Tool"**
   - Usar los nombres de herramientas del paso anterior
   - Probar con diferentes parámetros

## 🔧 Configuraciones Avanzadas

### Usar Diferentes Operaciones MCP

```javascript
// En nodo MCP Client, puedes usar:

// 1. Listar herramientas
{
  "operation": "listTools"
}

// 2. Ejecutar herramienta específica
{
  "operation": "callTool",
  "toolName": "nombre_de_la_herramienta",
  "arguments": {
    "parametro1": "valor1",
    "parametro2": "valor2"
  }
}
```

## 📊 Monitoreo y Debugging

### Logs del Bridge

El bridge muestra logs en tiempo real en la terminal.

### Endpoints de Debugging

```bash
# Estado del bridge
curl http://localhost:8001/health

# Lista de herramientas
curl http://localhost:8001/tools
```

## 🎯 Resumen de la Solución

**El problema original**: `npm install n8n-nodes-atdf-mcp` falló porque el paquete no está publicado.

**La solución implementada**: Usar el **Bridge ATDF-MCP** que convierte herramientas ATDF al protocolo MCP, permitiendo usar los **nodos MCP nativos** de n8n.

**Resultado**: Integración completa y funcional entre ATDF, MCP y n8n sin necesidad de instalar paquetes personalizados.

---

## 🎉 ¡Listo para Usar!

Ahora puedes crear workflows en n8n que usen herramientas ATDF a través del protocolo MCP. ¡La integración está completa y funcionando!

---

## 🔐 Importación por API (REST) y Autenticación

Para gestionar workflows vía API necesitas que n8n esté corriendo y una API key.

### Requisitos
- n8n corriendo en `http://localhost:5678`
- API habilitada y cabecera `X-N8N-API-KEY`

### Comandos de verificación
```bash
# Verificar editor (UI)
curl -s http://localhost:5678 | head -c 200

# Listar workflows (API)
curl -s -H "X-N8N-API-KEY: <API_KEY>" \
  http://localhost:5678/api/v1/workflows | head -c 300
```

### Importar workflow Code v3 por API
```bash
# Importar únicamente el workflow Code v3
WORKFLOW_FILE="n8n-workflows/complete-travel-workflow-code-v3.json" \
N8N_API_KEY="<API_KEY>" \
python import_workflows_to_n8n.py

# Confirmar por ID (ejemplo del ID creado)
curl -s -H "X-N8N-API-KEY: <API_KEY>" \
  http://localhost:5678/api/v1/workflows/98PshpVrKFAma04t | head -c 400
```

### Notas importantes
- La API de n8n espera un objeto de workflow con claves permitidas: `name`, `nodes`, `connections`, `settings`.
- No enviar propiedades de solo lectura (`active`, `staticData`, etc.).
- El script `import_workflows_to_n8n.py` ha sido ajustado para:
  - Usar `X-N8N-API-KEY` si `N8N_API_KEY` está definido.
  - Filtrar el payload a las claves permitidas por la API de creación.
  - Permitir importar un archivo específico con `WORKFLOW_FILE`.
  - Considerar exitosas respuestas `200` y `201`.

---

## 🧩 Workflow “Complete Travel Booking via ATDF-MCP (Code v3)”

**Archivo**: `n8n-workflows/complete-travel-workflow-code-v3.json`

**Descripción**:
- Implementa reserva de hotel y vuelo usando nodos `Code` que llaman al MCP Bridge.
- Usa cadenas de fecha naïve para evitar errores de offset.
- Los nodos `Code` leen datos desde `$json` y usan `this.helpers.httpRequest`.

**Nodos**:
- `Set Travel Data`: provee parámetros de entrada (ej. `check_in`, `check_out`, `travel_date`).
- `Book Hotel` (Code): `POST http://localhost:8001/mcp` con `name: 'hotel_reservation'` y argumentos desde `$json`.
- `Book Flight` (Code): `POST http://localhost:8001/mcp` con `name: 'flight_booking'` y argumentos desde `$json`.

**Conexiones**:
- `Set Travel Data` → `Book Hotel` → `Book Flight`

**Ejecución (UI)**:
1. Abrir `http://localhost:5678/`.
2. Buscar el workflow por nombre.
3. Pulsar `Execute Workflow`.
4. Ver confirmaciones con IDs en la salida de cada nodo `Code`.

---

## 🧪 Troubleshooting API

- `"'X-N8N-API-KEY' header required"`: añade la cabecera con tu API key.
- `request/body must have required property 'name'`: envía el objeto de workflow directamente (sin envolver en `workflow`).
- `request/body/active is read-only` / `must NOT have additional properties`: filtra propiedades a las permitidas.