# Ejemplos de ATDF - Múltiples Lenguajes y Herramientas

## 🎯 Visión General

Esta sección proporciona ejemplos prácticos del **Agent Tool Description Format (ATDF)** implementado en diferentes lenguajes de programación, frameworks y herramientas no-code, mostrando la versatilidad y universalidad del formato.

## 📋 Índice de Ejemplos

### 🔧 **Implementaciones Completas**
- [FastAPI (Python)](#fastapi-python)
- [Express.js (Node.js)](#expressjs-nodejs)
- [Spring Boot (Java)](#spring-boot-java)
- [ASP.NET Core (C#)](#aspnet-core-c)
- [Flask (Python)](#flask-python)

### 🔄 **Herramientas No-Code**
- [N8N Workflow](#n8n-workflow)
- [Zapier Automation](#zapier-automation)
- [Make (Integromat)](#make-integromat)

### 🎯 **Ejemplos Específicos**
- [Descripción de Herramientas](#descripción-de-herramientas)
- [Manejo de Errores](#manejo-de-errores)
- [Validación de Entrada](#validación-de-entrada)
- [Integración con Agentes](#integración-con-agentes)

---

## 🔧 Implementaciones Completas

### FastAPI (Python) {#fastapi-python}

#### Estructura del Proyecto
```
fastapi-atdf-example/
├── main.py
├── models.py
├── tools/
│   ├── __init__.py
│   ├── hotel_tool.py
│   └── flight_tool.py
├── errors/
│   ├── __init__.py
│   └── atdf_errors.py
└── requirements.txt
```

#### Implementación Principal
```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any
import uuid
from datetime import datetime

app = FastAPI(title="ATDF Example", version="1.0.0")

# Modelos ATDF
class ATDFErrorDetail(BaseModel):
    type: str
    title: str
    detail: str
    instance: str
    tool_name: str
    parameter_name: str
    suggested_value: str | None = None
    context: Dict[str, Any] = {}

class ATDFErrorResponse(BaseModel):
    errors: List[ATDFErrorDetail]

# Herramientas disponibles
TOOLS = {
    "hotel_reservation": {
        "name": "hotel_reservation",
        "description": "Make a hotel reservation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "guest_name": {"type": "string", "description": "Guest name"},
                "email": {"type": "string", "format": "email"},
                "check_in": {"type": "string", "format": "date-time"},
                "check_out": {"type": "string", "format": "date-time"},
                "room_type": {"type": "string", "enum": ["single", "double", "suite"]},
                "guests": {"type": "integer", "minimum": 1, "maximum": 4}
            },
            "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
        }
    }
}

@app.get("/tools")
async def get_tools():
    """Endpoint para obtener descripción de herramientas ATDF"""
    return {"tools": list(TOOLS.values())}

@app.post("/api/hotel/reserve")
async def reserve_hotel(request: Dict[str, Any]):
    """Ejemplo de reserva de hotel con manejo de errores ATDF"""
    try:
        # Validación de negocio
        check_in = datetime.fromisoformat(request["check_in"].replace("Z", "+00:00"))
        if check_in < datetime.now():
            return create_atdf_error(
                "https://api.example.com/errors/invalid-date",
                "Invalid Check-in Date",
                "Check-in date cannot be in the past",
                "hotel_reservation",
                "check_in",
                datetime.now().isoformat(),
                {"current_time": datetime.now().isoformat()}
            )
        
        # Lógica de negocio exitosa
        return {
            "reservation_id": str(uuid.uuid4()),
            "status": "confirmed",
            "message": "Hotel reservation created successfully"
        }
        
    except Exception as e:
        return create_atdf_error(
            "https://api.example.com/errors/validation-error",
            "Validation Error",
            str(e),
            "hotel_reservation",
            "unknown",
            None,
            {"error_type": type(e).__name__}
        )

def create_atdf_error(type_uri: str, title: str, detail: str, tool_name: str, 
                     parameter_name: str, suggested_value: str | None, context: Dict[str, Any]):
    """Función auxiliar para crear errores ATDF"""
    return ATDFErrorResponse(
        errors=[
            ATDFErrorDetail(
                type=type_uri,
                title=title,
                detail=detail,
                instance=f"/api/errors/{uuid.uuid4()}",
                tool_name=tool_name,
                parameter_name=parameter_name,
                suggested_value=suggested_value,
                context=context
            )
        ]
    )
```

### Express.js (Node.js) {#expressjs-nodejs}

#### Estructura del Proyecto
```
express-atdf-example/
├── package.json
├── server.js
├── tools/
│   ├── hotelTool.js
│   └── flightTool.js
├── errors/
│   └── atdfErrors.js
└── middleware/
    └── validation.js
```

#### Implementación Principal
```javascript
// server.js
const express = require('express');
const { body, validationResult } = require('express-validator');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

// Definición de herramientas ATDF
const tools = {
  hotel_reservation: {
    name: "hotel_reservation",
    description: "Make a hotel reservation",
    inputSchema: {
      type: "object",
      properties: {
        guest_name: {
          type: "string",
          description: "Guest name"
        },
        email: {
          type: "string",
          format: "email"
        },
        check_in: {
          type: "string",
          format: "date-time"
        },
        check_out: {
          type: "string",
          format: "date-time"
        },
        room_type: {
          type: "string",
          enum: ["single", "double", "suite"]
        },
        guests: {
          type: "integer",
          minimum: 1,
          maximum: 4
        }
      },
      required: ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
    }
  }
};

// Endpoint para obtener herramientas
app.get('/tools', (req, res) => {
  res.json({ tools: Object.values(tools) });
});

// Endpoint para reserva de hotel
app.post('/api/hotel/reserve', [
  body('guest_name').notEmpty().withMessage('Guest name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('check_in').isISO8601().withMessage('Valid check-in date is required'),
  body('check_out').isISO8601().withMessage('Valid check-out date is required'),
  body('room_type').isIn(['single', 'double', 'suite']).withMessage('Invalid room type'),
  body('guests').isInt({ min: 1, max: 4 }).withMessage('Guests must be between 1 and 4')
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json(createATDFError(
      'https://api.example.com/errors/validation-error',
      'Validation Error',
      'Input validation failed',
      'hotel_reservation',
      'input',
      null,
      { validation_errors: errors.array() }
    ));
  }

  // Validación de negocio
  const checkIn = new Date(req.body.check_in);
  if (checkIn < new Date()) {
    return res.status(400).json(createATDFError(
      'https://api.example.com/errors/invalid-date',
      'Invalid Check-in Date',
      'Check-in date cannot be in the past',
      'hotel_reservation',
      'check_in',
      new Date().toISOString(),
      { current_time: new Date().toISOString() }
    ));
  }

  // Lógica de negocio exitosa
  res.json({
    reservation_id: uuidv4(),
    status: 'confirmed',
    message: 'Hotel reservation created successfully'
  });
});

function createATDFError(type, title, detail, toolName, parameterName, suggestedValue, context) {
  return {
    errors: [{
      type,
      title,
      detail,
      instance: `/api/errors/${uuidv4()}`,
      tool_name: toolName,
      parameter_name: parameterName,
      suggested_value: suggestedValue,
      context
    }]
  };
}

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Spring Boot (Java) {#spring-boot-java}

#### Estructura del Proyecto
```
spring-boot-atdf-example/
├── src/main/java/com/example/atdf/
│   ├── AtdfApplication.java
│   ├── controller/
│   │   ├── ToolController.java
│   │   └── HotelController.java
│   ├── model/
│   │   ├── ATDFError.java
│   │   └── ATDFTool.java
│   └── service/
│       └── HotelService.java
├── pom.xml
└── application.properties
```

#### Implementación Principal
```java
// ToolController.java
@RestController
@RequestMapping("/api")
public class ToolController {
    
    @GetMapping("/tools")
    public Map<String, List<ATDFTool>> getTools() {
        ATDFTool hotelTool = new ATDFTool();
        hotelTool.setName("hotel_reservation");
        hotelTool.setDescription("Make a hotel reservation");
        
        Map<String, Object> inputSchema = new HashMap<>();
        inputSchema.put("type", "object");
        
        Map<String, Object> properties = new HashMap<>();
        properties.put("guest_name", Map.of("type", "string", "description", "Guest name"));
        properties.put("email", Map.of("type", "string", "format", "email"));
        properties.put("check_in", Map.of("type", "string", "format", "date-time"));
        properties.put("check_out", Map.of("type", "string", "format", "date-time"));
        properties.put("room_type", Map.of("type", "string", "enum", Arrays.asList("single", "double", "suite")));
        properties.put("guests", Map.of("type", "integer", "minimum", 1, "maximum", 4));
        
        inputSchema.put("properties", properties);
        inputSchema.put("required", Arrays.asList("guest_name", "email", "check_in", "check_out", "room_type", "guests"));
        
        hotelTool.setInputSchema(inputSchema);
        
        return Map.of("tools", Arrays.asList(hotelTool));
    }
}

// HotelController.java
@RestController
@RequestMapping("/api/hotel")
public class HotelController {
    
    @Autowired
    private HotelService hotelService;
    
    @PostMapping("/reserve")
    public ResponseEntity<?> reserveHotel(@RequestBody Map<String, Object> request) {
        try {
            // Validación de negocio
            String checkInStr = (String) request.get("check_in");
            LocalDateTime checkIn = LocalDateTime.parse(checkInStr.replace("Z", ""));
            
            if (checkIn.isBefore(LocalDateTime.now())) {
                ATDFError error = createATDFError(
                    "https://api.example.com/errors/invalid-date",
                    "Invalid Check-in Date",
                    "Check-in date cannot be in the past",
                    "hotel_reservation",
                    "check_in",
                    LocalDateTime.now().toString(),
                    Map.of("current_time", LocalDateTime.now().toString())
                );
                return ResponseEntity.badRequest().body(Map.of("errors", Arrays.asList(error)));
            }
            
            // Lógica de negocio exitosa
            String reservationId = UUID.randomUUID().toString();
            return ResponseEntity.ok(Map.of(
                "reservation_id", reservationId,
                "status", "confirmed",
                "message", "Hotel reservation created successfully"
            ));
            
        } catch (Exception e) {
            ATDFError error = createATDFError(
                "https://api.example.com/errors/validation-error",
                "Validation Error",
                e.getMessage(),
                "hotel_reservation",
                "unknown",
                null,
                Map.of("error_type", e.getClass().getSimpleName())
            );
            return ResponseEntity.badRequest().body(Map.of("errors", Arrays.asList(error)));
        }
    }
    
    private ATDFError createATDFError(String type, String title, String detail, 
                                     String toolName, String parameterName, 
                                     String suggestedValue, Map<String, Object> context) {
        ATDFError error = new ATDFError();
        error.setType(type);
        error.setTitle(title);
        error.setDetail(detail);
        error.setInstance("/api/errors/" + UUID.randomUUID());
        error.setToolName(toolName);
        error.setParameterName(parameterName);
        error.setSuggestedValue(suggestedValue);
        error.setContext(context);
        return error;
    }
}
```

## 🔄 Herramientas No-Code

### N8N Workflow {#n8n-workflow}

#### Descripción de Herramienta ATDF
```json
{
  "tools": [
    {
      "name": "n8n_hotel_reservation",
      "description": "N8N workflow for hotel reservation with ATDF error handling",
      "version": "1.0.0",
      "tags": ["n8n", "workflow", "hotel", "booking"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "guest_name": {
            "type": "string",
            "description": "Full name of the guest",
            "minLength": 1
          },
          "email": {
            "type": "string",
            "format": "email",
            "description": "Guest email address"
          },
          "check_in": {
            "type": "string",
            "format": "date-time",
            "description": "Check-in date and time"
          },
          "check_out": {
            "type": "string",
            "format": "date-time",
            "description": "Check-out date and time"
          },
          "room_type": {
            "type": "string",
            "enum": ["single", "double", "suite"],
            "description": "Type of room"
          },
          "guests": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Number of guests"
          }
        },
        "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
      }
    }
  ]
}
```

#### Configuración del Nodo HTTP Request
```json
{
  "method": "POST",
  "url": "https://your-n8n-instance.com/webhook/hotel-reservation",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "guest_name": "{{ $json.guest_name }}",
    "email": "{{ $json.email }}",
    "check_in": "{{ $json.check_in }}",
    "check_out": "{{ $json.check_out }}",
    "room_type": "{{ $json.room_type }}",
    "guests": "{{ $json.guests }}"
  }
}
```

#### Configuración del Nodo Set (Validación)
```javascript
// Validar fecha de llegada
const checkIn = new Date($input.first().json.check_in);
const now = new Date();

if (checkIn < now) {
  return {
    errors: [{
      type: "https://api.example.com/errors/invalid-date",
      title: "Invalid Check-in Date",
      detail: "Check-in date cannot be in the past",
      instance: "/api/errors/" + Date.now(),
      tool_name: "n8n_hotel_reservation",
      parameter_name: "check_in",
      suggested_value: now.toISOString(),
      context: {
        current_time: now.toISOString(),
        provided_date: $input.first().json.check_in
      }
    }]
  };
}

// Continuar con el flujo normal
return $input.first().json;
```

#### Configuración del Nodo Webhook (Respuesta)
```json
{
  "reservation_id": "{{ $json.reservation_id }}",
  "status": "{{ $json.status }}",
  "message": "{{ $json.message }}"
}
```

### Zapier Automation {#zapier-automation}

#### Descripción de Herramienta ATDF
```json
{
  "tools": [
    {
      "name": "zapier_hotel_reservation",
      "description": "Zapier automation for hotel reservation with ATDF error handling",
      "version": "1.0.0",
      "tags": ["zapier", "automation", "hotel", "booking"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "guest_name": {
            "type": "string",
            "description": "Full name of the guest"
          },
          "email": {
            "type": "string",
            "format": "email",
            "description": "Guest email address"
          },
          "check_in": {
            "type": "string",
            "format": "date-time",
            "description": "Check-in date and time"
          },
          "check_out": {
            "type": "string",
            "format": "date-time",
            "description": "Check-out date and time"
          },
          "room_type": {
            "type": "string",
            "enum": ["single", "double", "suite"],
            "description": "Type of room"
          },
          "guests": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Number of guests"
          }
        },
        "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
      }
    }
  ]
}
```

#### Configuración del Trigger (Webhook)
```json
{
  "url": "https://hooks.zapier.com/hooks/catch/123456/abc123/",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### Configuración del Action (Code)
```javascript
// Validar fecha de llegada
const checkIn = new Date(inputData.check_in);
const now = new Date();

if (checkIn < now) {
  return {
    errors: [{
      type: "https://api.example.com/errors/invalid-date",
      title: "Invalid Check-in Date",
      detail: "Check-in date cannot be in the past",
      instance: "/api/errors/" + Date.now(),
      tool_name: "zapier_hotel_reservation",
      parameter_name: "check_in",
      suggested_value: now.toISOString(),
      context: {
        current_time: now.toISOString(),
        provided_date: inputData.check_in
      }
    }]
  };
}

// Crear reserva
const reservationId = Date.now().toString();
return {
  reservation_id: reservationId,
  status: "confirmed",
  message: "Hotel reservation created successfully"
};
```

### Make (Integromat) {#make-integromat}

#### Descripción de Herramienta ATDF
```json
{
  "tools": [
    {
      "name": "make_hotel_reservation",
      "description": "Make (Integromat) scenario for hotel reservation with ATDF error handling",
      "version": "1.0.0",
      "tags": ["make", "integromat", "scenario", "hotel", "booking"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "guest_name": {
            "type": "string",
            "description": "Full name of the guest"
          },
          "email": {
            "type": "string",
            "format": "email",
            "description": "Guest email address"
          },
          "check_in": {
            "type": "string",
            "format": "date-time",
            "description": "Check-in date and time"
          },
          "check_out": {
            "type": "string",
            "format": "date-time",
            "description": "Check-out date and time"
          },
          "room_type": {
            "type": "string",
            "enum": ["single", "double", "suite"],
            "description": "Type of room"
          },
          "guests": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Number of guests"
          }
        },
        "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
      }
    }
  ]
}
```

#### Configuración del Módulo Webhook
```json
{
  "url": "https://hook.eu1.make.com/abc123def456",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### Configuración del Módulo Router (Validación)
```javascript
// Condición: Validar fecha de llegada
const checkIn = new Date(1.check_in);
const now = new Date();

if (checkIn < now) {
  // Ruta de error
  return {
    errors: [{
      type: "https://api.example.com/errors/invalid-date",
      title: "Invalid Check-in Date",
      detail: "Check-in date cannot be in the past",
      instance: "/api/errors/" + Date.now(),
      tool_name: "make_hotel_reservation",
      parameter_name: "check_in",
      suggested_value: now.toISOString(),
      context: {
        current_time: now.toISOString(),
        provided_date: 1.check_in
      }
    }]
  };
} else {
  // Ruta de éxito
  return 1;
}
```

#### Configuración del Módulo HTTP (Respuesta)
```json
{
  "reservation_id": "{{1.reservation_id}}",
  "status": "{{1.status}}",
  "message": "{{1.message}}"
}
```

### N8N - Configuración de Respuestas

#### Respuesta de Éxito (JSON Output)
```json
{
  "booking_id": "N8N-2025-001",
  "status": "confirmed",
  "message": "Flight booking created successfully",
  "details": {
    "passenger_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "flight_number": "AA123",
    "departure": "2025-01-20T10:00:00Z",
    "arrival": "2025-01-20T12:30:00Z",
    "origin": "JFK",
    "destination": "LAX",
    "seat_class": "economy",
    "total_price": 299.99,
    "confirmation_code": "N8N-FLT-001234"
  }
}
```

#### Respuesta de Error (Error Trigger)
```json
{
  "errors": [
    {
      "type": "https://n8n.example.com/errors/invalid-route",
      "title": "Invalid Flight Route",
      "detail": "Origin and destination airports cannot be the same",
      "instance": "/api/errors/n8n-e62aa61e-d844-4761-82c3-531a070fb139",
      "tool_name": "flight_booking",
      "parameter_name": "route",
      "suggested_value": "LAX",
      "context": {
        "origin": "JFK",
        "destination": "JFK",
        "available_destinations": ["LAX", "ORD", "DFW", "ATL"]
      }
    }
  ]
}
```

### Zapier - Configuración de Respuestas

#### Respuesta de Éxito (Webhook Response)
```json
{
  "order_id": "ZAP-2025-001",
  "status": "processed",
  "message": "E-commerce order created successfully",
  "details": {
    "customer_name": "John Doe",
    "email": "john.doe@example.com",
    "order_items": [
      {
        "product_id": "PROD-001",
        "name": "Wireless Headphones",
        "quantity": 2,
        "price": 99.99
      }
    ],
    "total_amount": 199.98,
    "shipping_address": "123 Main St, City, State 12345",
    "tracking_number": "ZAP-TRK-001234"
  }
}
```

#### Respuesta de Error (Error Path)
```json
{
  "errors": [
    {
      "type": "https://zapier.example.com/errors/insufficient-stock",
      "title": "Insufficient Stock",
      "detail": "Requested quantity exceeds available stock",
      "instance": "/api/errors/zap-f73bb62f-e955-4872-93d4-642181082240",
      "tool_name": "ecommerce_order",
      "parameter_name": "quantity",
      "suggested_value": 1,
      "context": {
        "product_id": "PROD-001",
        "requested_quantity": 5,
        "available_stock": 2,
        "product_name": "Wireless Headphones"
      }
    }
  ]
}
```

### Make - Configuración de Respuestas

#### Respuesta de Éxito (HTTP Response)
```json
{
  "appointment_id": "MAKE-2025-001",
  "status": "scheduled",
  "message": "Medical appointment scheduled successfully",
  "details": {
    "patient_name": "Maria Garcia",
    "email": "maria.garcia@example.com",
    "doctor_name": "Dr. Smith",
    "specialty": "Cardiology",
    "appointment_date": "2025-01-25T14:00:00Z",
    "duration": "30 minutes",
    "location": "Medical Center - Floor 3",
    "confirmation_code": "MAKE-APT-001234",
    "reminder_sent": true
  }
}
```

#### Respuesta de Error (Error Handler)
```json
{
  "errors": [
    {
      "type": "https://make.example.com/errors/schedule-conflict",
      "title": "Schedule Conflict",
      "detail": "Doctor is not available at the requested time",
      "instance": "/api/errors/make-g84cc73g-f066-5983-04e5-753292193351",
      "tool_name": "medical_appointment",
      "parameter_name": "appointment_time",
      "suggested_value": "2025-01-25T15:00:00Z",
      "context": {
        "requested_time": "2025-01-25T14:00:00Z",
        "doctor_id": "DOC-001",
        "available_slots": [
          "2025-01-25T15:00:00Z",
          "2025-01-25T16:00:00Z",
          "2025-01-26T09:00:00Z"
        ],
        "conflict_reason": "Existing appointment"
      }
    }
  ]
}
```

## 🎯 Ejemplos Específicos

### Descripción de Herramientas

#### Plantilla Básica
```json
{
  "tools": [
    {
      "name": "mi_herramienta",
      "description": "Descripción de lo que hace la herramienta",
      "inputSchema": {
        "type": "object",
        "properties": {
          "parametro1": {
            "type": "string",
            "description": "Descripción del parámetro"
          }
        },
        "required": ["parametro1"]
      }
    }
  ]
}
```

#### Plantilla con Validaciones
```json
{
  "tools": [
    {
      "name": "validacion_avanzada",
      "description": "Herramienta con validaciones complejas",
      "inputSchema": {
        "type": "object",
        "properties": {
          "email": {
            "type": "string",
            "format": "email",
            "description": "Email válido"
          },
          "edad": {
            "type": "integer",
            "minimum": 18,
            "maximum": 100,
            "description": "Edad entre 18 y 100"
          },
          "categorias": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["tecnologia", "deportes", "cultura"]
            },
            "description": "Categorías permitidas"
          }
        },
        "required": ["email", "edad"]
      }
    }
  ]
}
```

### Manejo de Errores

#### Error de Validación
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Validation Error",
      "detail": "Email format is invalid",
      "instance": "/api/errors/123e4567-e89b-12d3-a456-426614174000",
      "tool_name": "mi_herramienta",
      "parameter_name": "email",
      "suggested_value": "usuario@ejemplo.com",
      "context": {
        "provided_value": "email_invalido",
        "validation_rule": "email_format"
      }
    }
  ]
}
```

#### Error de Regla de Negocio
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/business-rule",
      "title": "Capacity Exceeded",
      "detail": "Maximum capacity of 100 users reached",
      "instance": "/api/errors/123e4567-e89b-12d3-a456-426614174001",
      "tool_name": "registro_usuario",
      "parameter_name": "capacity",
      "suggested_value": null,
      "context": {
        "current_capacity": 100,
        "requested_capacity": 101,
        "max_capacity": 100
      }
    }
  ]
}
```

### Validación de Entrada

#### Validación de Fechas
```javascript
// En cualquier lenguaje o herramienta
function validateDate(checkIn, checkOut) {
  const now = new Date();
  const checkInDate = new Date(checkIn);
  const checkOutDate = new Date(checkOut);
  
  if (checkInDate < now) {
    return {
      errors: [{
        type: "https://api.example.com/errors/invalid-date",
        title: "Invalid Check-in Date",
        detail: "Check-in date cannot be in the past",
        instance: "/api/errors/" + Date.now(),
        tool_name: "hotel_reservation",
        parameter_name: "check_in",
        suggested_value: now.toISOString(),
        context: {
          current_time: now.toISOString(),
          provided_date: checkIn
        }
      }]
    };
  }
  
  if (checkOutDate <= checkInDate) {
    return {
      errors: [{
        type: "https://api.example.com/errors/invalid-date",
        title: "Invalid Check-out Date",
        detail: "Check-out date must be after check-in date",
        instance: "/api/errors/" + Date.now(),
        tool_name: "hotel_reservation",
        parameter_name: "check_out",
        suggested_value: new Date(checkInDate.getTime() + 24*60*60*1000).toISOString(),
        context: {
          check_in_date: checkIn,
          check_out_date: checkOut
        }
      }]
    };
  }
  
  return null; // No hay errores
}
```

#### Validación de Rango de Fechas

```javascript
// Validar que las fechas estén dentro del rango permitido
function validateDateRange(checkIn, checkOut, minDays = 1, maxDays = 30) {
  const checkInDate = new Date(checkIn);
  const checkOutDate = new Date(checkOut);
  const daysDiff = (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24);
  
  if (daysDiff < minDays) {
    return {
      errors: [{
        type: "https://api.example.com/errors/business-rule",
        title: "Minimum Stay Required",
        detail: `Minimum stay is ${minDays} day(s)`,
        instance: "/api/errors/" + Date.now(),
        tool_name: "hotel_reservation",
        parameter_name: "check_out",
        suggested_value: new Date(checkInDate.getTime() + minDays*24*60*60*1000).toISOString(),
        context: {
          min_days: minDays,
          requested_days: daysDiff
        }
      }]
    };
  }
  
  if (daysDiff > maxDays) {
    return {
      errors: [{
        type: "https://api.example.com/errors/business-rule",
        title: "Maximum Stay Exceeded",
        detail: `Maximum stay is ${maxDays} days`,
        instance: "/api/errors/" + Date.now(),
        tool_name: "hotel_reservation",
        parameter_name: "check_out",
        suggested_value: new Date(checkInDate.getTime() + maxDays*24*60*60*1000).toISOString(),
        context: {
          max_days: maxDays,
          requested_days: daysDiff
        }
      }]
    };
  }
  
  return null; // No hay errores
}
```

### Ejemplo de Consumo por Agente de IA

#### Solicitud del Agente
```json
{
  "tool_name": "hotel_reservation",
  "parameters": {
    "guest_name": "John Doe",
    "email": "john.doe@example.com",
    "check_in": "2025-01-14T10:00:00Z",
    "check_out": "2025-01-16T12:00:00Z",
    "room_type": "double",
    "guests": 2
  }
}
```

#### Respuesta de Éxito
```json
{
  "reservation_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "confirmed",
  "message": "Hotel reservation created successfully",
  "details": {
    "guest_name": "John Doe",
    "email": "john.doe@example.com",
    "check_in": "2025-01-15T14:00:00Z",
    "check_out": "2025-01-17T12:00:00Z",
    "room_type": "double",
    "guests": 2,
    "total_price": 299.99,
    "confirmation_number": "HTL-2025-001234",
    "cancellation_policy": "Free cancellation until 24 hours before check-in",
    "hotel_info": {
      "name": "Grand Hotel",
      "address": "123 Main Street, City",
      "phone": "+1-555-0123"
    }
  }
}
```

#### Respuesta de Error (para corrección automática)
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/invalid-date",
      "title": "Invalid Check-in Date",
      "detail": "Check-in date cannot be in the past",
      "instance": "/api/errors/e62aa61e-d844-4761-82c3-531a070fb139",
      "tool_name": "hotel_reservation",
      "parameter_name": "check_in",
      "suggested_value": "2025-01-15T12:00:17.148869",
      "context": {
        "current_time": "2025-01-15T12:00:17.148869",
        "provided_date": "2025-01-14T10:00:00Z"
      }
    }
  ]
}
```

#### Respuesta de Error (Múltiples Errores)
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/invalid-date",
      "title": "Invalid Check-in Date",
      "detail": "Check-in date cannot be in the past",
      "instance": "/api/errors/e62aa61e-d844-4761-82c3-531a070fb139",
      "tool_name": "hotel_reservation",
      "parameter_name": "check_in",
      "suggested_value": "2025-01-15T12:00:17.148869",
      "context": {
        "current_time": "2025-01-15T12:00:17.148869",
        "provided_date": "2025-01-14T10:00:00Z"
      }
    },
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Email Format",
      "detail": "Email address format is invalid",
      "instance": "/api/errors/f73bb62f-e955-4872-93d4-642181082240",
      "tool_name": "hotel_reservation",
      "parameter_name": "email",
      "suggested_value": "john.doe@example.com",
      "context": {
        "provided_value": "invalid-email",
        "validation_rule": "email_format"
      }
    }
  ]
}
```

#### Respuesta de Error (Regla de Negocio)
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/business-rule",
      "title": "Room Not Available",
      "detail": "Selected room type is not available for the requested dates",
      "instance": "/api/errors/g84cc73g-f066-5983-04e5-753292193351",
      "tool_name": "hotel_reservation",
      "parameter_name": "room_type",
      "suggested_value": "single",
      "context": {
        "requested_room_type": "suite",
        "available_room_types": ["single", "double"],
        "check_in": "2025-01-15T14:00:00Z",
        "check_out": "2025-01-17T12:00:00Z",
        "alternative_suggestions": [
          {
            "room_type": "single",
            "price": 199.99,
            "availability": "confirmed"
          },
          {
            "room_type": "double",
            "price": 249.99,
            "availability": "confirmed"
          }
        ]
      }
    }
  ]
}
```

## 🔗 Enlaces Útiles

- **[Especificación ATDF](./ATDF_SPECIFICATION.md)** - Especificación completa del formato
- **[Guía de Implementación](./IMPLEMENTATION_GUIDE.md)** - Cómo implementar ATDF
- **[Mejores Prácticas](./BEST_PRACTICES.md)** - Recomendaciones para implementaciones robustas

### Ejemplos por Lenguaje

- **[Python](./ATDF_SPECIFICATION.md#python)** - FastAPI, Flask, Django
- **[JavaScript](./ATDF_SPECIFICATION.md#javascript)** - Express.js, Node.js, React
- **[Java](./ATDF_SPECIFICATION.md#java)** - Spring Boot, Jakarta EE
- **[C#](./ATDF_SPECIFICATION.md#csharp)** - ASP.NET Core, .NET
- **[Go](./ATDF_SPECIFICATION.md#go)** - Gin, Echo, Fiber
- **[Rust](./ATDF_SPECIFICATION.md#rust)** - Actix-web, Rocket, Axum

### Ejemplos por Herramienta No-Code

- **[N8N](./ATDF_SPECIFICATION.md#n8n)** - Workflows y automatizaciones
- **[Zapier](./ATDF_SPECIFICATION.md#zapier)** - Integraciones y automatizaciones
- **[Make](./ATDF_SPECIFICATION.md#make)** - Scenarios y workflows
- **[IFTTT](./ATDF_SPECIFICATION.md#ifttt)** - Applets y automatizaciones
- **[Microsoft Power Automate](./ATDF_SPECIFICATION.md#power-automate)** - Flows y automatizaciones

---

**ATDF** - Ejemplos prácticos para cualquier lenguaje o herramienta 🚀 