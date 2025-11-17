# 🧪 Prueba Completa ATDF + MCP + n8n

## ✅ Estado Actual Verificado

### Componentes Funcionando:
- ✅ **Servidor ATDF**: `localhost:8000` (2 herramientas disponibles)
- ✅ **n8n**: Versión 1.107.4 instalada
- ⚠️ **Bridge ATDF-MCP**: Necesita reinicio

## 🚀 Pasos para Prueba Completa

### 1. Reiniciar el Bridge ATDF-MCP

```bash
# En terminal Python
python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
```

### 2. Verificar Endpoints del Bridge

```bash
# Health check
curl http://localhost:8001/health

# Herramientas disponibles
curl http://localhost:8001/tools

# Endpoint SSE (para n8n)
curl http://localhost:8001/sse
```

### 3. Iniciar n8n

```bash
# En terminal separado
n8n start
```

### 4. Configurar n8n para MCP

1. **Abrir n8n**: `http://localhost:5678`
2. **Crear nuevo workflow**
3. **Agregar nodo "HTTP Request"** con:
   - **Method**: GET
   - **URL**: `http://localhost:8001/tools`
4. **Agregar nodo "MCP Client"** (si está disponible) con:
   - **Server URL**: `http://localhost:8001/sse`

### 5. Importar Workflow de Ejemplo

Usar el archivo: `examples/n8n_working_example.json`

```json
{
  "name": "ATDF-MCP Test Workflow",
  "nodes": [
    {
      "parameters": {
        "url": "http://localhost:8001/tools",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [240, 300],
      "id": "http-tools",
      "name": "Get ATDF Tools"
    },
    {
      "parameters": {
        "url": "http://localhost:8001/health",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300],
      "id": "http-health",
      "name": "Health Check"
    }
  ],
  "connections": {
    "Get ATDF Tools": {
      "main": [
        [
          {
            "node": "Health Check",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 🎯 Resultados Esperados

### Bridge Health Check:
```json
{
  "status": "healthy",
  "server": "ATDF-MCP Bridge",
  "version": "1.0.0",
  "atdf_server": "http://localhost:8000",
  "tools_count": 2,
  "timestamp": "2025-09-30T18:15:37.801832"
}
```

### Herramientas Disponibles:
```json
{
  "tools": [
    {
      "name": "hotel_reservation",
      "description": "Reservar un hotel con validación y manejo de errores ATDF"
    },
    {
      "name": "flight_booking", 
      "description": "Reservar un vuelo con validación y manejo de errores ATDF"
    }
  ]
}
```

## 🔧 Solución de Problemas

### Si el Bridge no responde:
1. Verificar que el servidor ATDF esté ejecutándose: `curl http://localhost:8000/health`
2. Reiniciar el bridge con logs: `python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000 --debug`

### Si n8n no encuentra las herramientas:
1. Verificar la URL del endpoint SSE: `http://localhost:8001/sse`
2. Usar nodos HTTP Request como alternativa
3. Verificar CORS si hay problemas de navegador

## 📊 Métricas de Éxito

- [ ] Bridge responde en `/health`
- [ ] Bridge lista 2 herramientas en `/tools`
- [ ] n8n se conecta al bridge
- [ ] Workflow ejecuta sin errores
- [ ] Se pueden invocar herramientas ATDF desde n8n

## 🎉 Próximos Pasos

Una vez verificado el funcionamiento:
1. Probar ejecución de herramientas específicas
2. Configurar workflows más complejos
3. Integrar con otros sistemas