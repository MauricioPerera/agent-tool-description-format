# 🚀 Guía de Integración ATDF + MCP + n8n

## 📋 Estado Actual

✅ **Servidor ATDF**: Funcionando en puerto 8000  
✅ **Bridge MCP**: Funcionando en puerto 8001  
🔄 **n8n**: Descargando (terminal 15)

## 🎯 Cuando n8n esté listo

### 1. Verificar que n8n funciona
```bash
curl http://localhost:5678
```

### 2. Abrir n8n en el navegador
- URL: http://localhost:5678
- Crear cuenta o hacer login

### 3. Crear tu primer workflow ATDF

#### Paso 1: Nuevo Workflow
1. Click en "New workflow"
2. Nombra el workflow: "Test ATDF Integration"

#### Paso 2: Agregar nodo HTTP Request
1. Click en "+" para agregar nodo
2. Buscar "HTTP Request"
3. Configurar:
   - **Method**: GET
   - **URL**: `http://localhost:8001/tools`
   - **Headers**: `Content-Type: application/json`

#### Paso 3: Ejecutar y ver herramientas
1. Click en "Execute Node"
2. Deberías ver 2 herramientas ATDF:
   - Hotel Reservation Tool
   - Flight Booking Tool

#### Paso 4: Usar una herramienta ATDF
1. Agregar otro nodo HTTP Request
2. Configurar:
   - **Method**: POST
   - **URL**: `http://localhost:8001/call_tool`
   - **Body**: 
   ```json
   {
     "name": "hotel_reservation",
     "arguments": {
       "hotel_name": "Hotel Test",
       "check_in": "2025-10-01",
       "check_out": "2025-10-03",
       "guests": 2
     }
   }
   ```

### 4. Herramientas Disponibles

#### 🏨 Hotel Reservation
```json
{
  "name": "hotel_reservation",
  "arguments": {
    "hotel_name": "string",
    "check_in": "YYYY-MM-DD",
    "check_out": "YYYY-MM-DD", 
    "guests": "number"
  }
}
```

#### ✈️ Flight Booking
```json
{
  "name": "flight_booking",
  "arguments": {
    "origin": "string",
    "destination": "string",
    "departure_date": "YYYY-MM-DD",
    "passengers": "number"
  }
}
```

## 🔧 Comandos de Verificación

```bash
# Verificar todos los servicios
curl http://localhost:8000/health  # ATDF Server
curl http://localhost:8001/health  # MCP Bridge  
curl http://localhost:5678         # n8n

# Ver herramientas disponibles
curl http://localhost:8001/tools

# Probar herramienta directamente
curl -X POST http://localhost:8001/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "hotel_reservation",
    "arguments": {
      "hotel_name": "Test Hotel",
      "check_in": "2025-10-01", 
      "check_out": "2025-10-03",
      "guests": 2
    }
  }'
```

## 🎯 Workflows Avanzados

### Workflow de Viaje Completo
1. **Trigger**: Webhook o Schedule
2. **HTTP Request**: Buscar vuelos
3. **HTTP Request**: Reservar hotel
4. **Email**: Enviar confirmación

### Workflow con Validación
1. **HTTP Request**: Obtener herramientas disponibles
2. **Code Node**: Validar datos de entrada
3. **HTTP Request**: Llamar herramienta ATDF
4. **Switch Node**: Manejar respuestas/errores

## 🚨 Solución de Problemas

### Si n8n no responde:
```bash
# Verificar proceso
ps aux | grep n8n

# Reiniciar si es necesario
npx --yes n8n@latest start
```

### Si el bridge no tiene herramientas:
```bash
# Verificar servidor ATDF
curl http://localhost:8000/health

# Reiniciar bridge
python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
```

## 📚 Recursos

- **ATDF Docs**: `docs/ATDF_SPECIFICATION.md`
- **MCP Bridge**: `examples/mcp_atdf_bridge.py`
- **n8n Docs**: https://docs.n8n.io/

## 🔗 Referencias y siguientes pasos

- Autenticación y REST import: ver `n8n_setup_complete.md` → sección "Importación por API (REST) y Autenticación".
- Workflow Code v3: ver `n8n-workflows/README.md` → sección "Complete Travel Booking via ATDF-MCP (Code v3)".
- Endpoints MCP usados por Code v3: `POST http://localhost:8001/mcp` y `GET http://localhost:8001/tools`.

### Checklist rápido
- n8n corriendo en `http://localhost:5678`.
- API key funcional: `curl -s -H "X-N8N-API-KEY: <API_KEY>" http://localhost:5678/api/v1/workflows | head -c 300`.
- Importar Code v3 por REST:
```bash
WORKFLOW_FILE="n8n-workflows/complete-travel-workflow-code-v3.json" \
N8N_API_KEY="<API_KEY>" \
python import_workflows_to_n8n.py
```

Nota: el payload de creación debe incluir únicamente `name`, `nodes`, `connections`, `settings`.

---
*Guía creada: 2025-09-30 19:42*

## Relacionados
- API REST y Autenticación de n8n: `./n8n_setup_complete.md`
- Workflow Code v3 (n8n): `./n8n-workflows/README.md`
- Guía EN (n8n + MCP + ATDF): `./docs/en/n8n_mcp_server_guide.md`
- Guía ES (n8n + MCP + ATDF): `./docs/es/n8n_mcp_integracion_flujo.md`
- Índice temático n8n + MCP + ATDF: `./docs/n8n_mcp_atdf_index.md`