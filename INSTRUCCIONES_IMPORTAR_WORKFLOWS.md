# 📋 Instrucciones para Importar Workflows en n8n

## 🎯 Workflows Creados

Se han creado 3 workflows listos para importar en n8n:

1. **Hotel Reservation Workflow** - `n8n-workflows/hotel-reservation-workflow.json`
2. **Flight Booking Workflow** - `n8n-workflows/flight-booking-workflow.json`  
3. **Complete Travel Workflow** - `n8n-workflows/complete-travel-workflow.json`

## 🚀 Pasos para Importar

### 1. Acceder a n8n
- Abre tu navegador y ve a: **http://localhost:5678**
- La interfaz de n8n debería estar disponible

### 2. Importar cada Workflow

Para cada archivo JSON en la carpeta `n8n-workflows/`:

#### Opción A: Importar desde la Interfaz Web
1. En n8n, haz clic en **"+ New Workflow"** o **"Import"**
2. Selecciona **"Import from File"** o **"Import from URL"**
3. Copia y pega el contenido completo del archivo JSON
4. Haz clic en **"Import"**

#### Opción B: Crear Workflow Nuevo y Pegar JSON
1. Crea un nuevo workflow en n8n
2. Ve a **Settings** → **Import/Export**
3. Pega el contenido del archivo JSON
4. Guarda el workflow

### 3. Configurar Credenciales (si es necesario)

Los workflows usan HTTP requests al MCP bridge. Si n8n requiere credenciales:
- Ve a **Credentials** en n8n
- Crea credenciales para HTTP requests si es necesario
- Configura la URL base: `http://localhost:8001`

## 📁 Archivos de Workflow

### 🏨 Hotel Reservation Workflow
**Archivo:** `hotel-reservation-workflow.json`
- **Función:** Reserva de hotel usando ATDF via MCP
- **Endpoint:** `http://localhost:8001/mcp`
- **Tool:** `hotel_reservation`

### ✈️ Flight Booking Workflow  
**Archivo:** `flight-booking-workflow.json`
- **Función:** Reserva de vuelo usando ATDF via MCP
- **Endpoint:** `http://localhost:8001/mcp`
- **Tool:** `flight_booking`

### 🌍 Complete Travel Workflow
**Archivo:** `complete-travel-workflow.json`
- **Función:** Reserva completa (hotel + vuelo) en secuencia
- **Endpoint:** `http://localhost:8001/mcp`
- **Tools:** `hotel_reservation` + `flight_booking`

## ⚙️ Configuración de los Workflows

### Datos de Entrada por Defecto:
- **Viajero:** Carlos Mendez
- **Email:** carlos.mendez@example.com
- **Ciudades:** Madrid → Barcelona
- **Fechas:** 28-30 Diciembre 2025
- **Habitación:** Suite para 2 huéspedes
- **Vuelo:** Clase business

### Modificar Datos:
1. En cada workflow, busca el nodo **"Set Travel Data"** o **"Set Data"**
2. Modifica los valores según tus necesidades
3. Guarda el workflow

## 🧪 Probar los Workflows

### Requisitos Previos:
1. **ATDF Server** corriendo en `http://localhost:8000`
2. **MCP Bridge** corriendo en `http://localhost:8001`

### Ejecutar Pruebas:
1. Abre el workflow en n8n
2. Haz clic en **"Test workflow"** o **"Execute Workflow"**
3. Verifica los resultados en cada nodo
4. Revisa las notificaciones de éxito/error

## 🔧 Solución de Problemas

### Error de Conexión:
- Verifica que el MCP Bridge esté corriendo: `http://localhost:8001/health`
- Verifica que el ATDF Server esté corriendo: `http://localhost:8000/tools`

### Error de Formato de Fecha:
- Las fechas deben estar en formato: `YYYY-MM-DDTHH:MM:SS`
- Ejemplo: `2025-12-28T15:00:00`

### Error de Tool Name:
- Verifica que los nombres de tools sean exactos: `hotel_reservation`, `flight_booking`

## 📊 Verificación de Éxito

Después de importar, deberías ver:
1. ✅ 3 workflows en tu lista de n8n
2. ✅ Cada workflow con sus nodos configurados
3. ✅ Conexiones entre nodos establecidas
4. ✅ Datos de prueba pre-configurados

## 🎉 ¡Listo!

Una vez importados, los workflows estarán listos para:
- Ejecutar reservas de hotel individuales
- Ejecutar reservas de vuelo individuales  
- Ejecutar el flujo completo de viaje (hotel + vuelo)
- Integrar con otros workflows de n8n
- Modificar según tus necesidades específicas

---

**💡 Tip:** Puedes duplicar estos workflows y modificarlos para diferentes casos de uso, ciudades, o integraciones adicionales.