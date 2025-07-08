# Ejemplos de ATDF - Múltiples Lenguajes y Frameworks

## 🎯 Visión General

Esta sección proporciona ejemplos prácticos del **Agent Tool Description Format (ATDF)** implementado en diferentes lenguajes de programación y frameworks, mostrando la versatilidad y universalidad del formato.

## 📋 Índice de Ejemplos

### 🔧 **Implementaciones Completas**
- [FastAPI (Python)](#fastapi-python)
- [Express.js (Node.js)](#expressjs-nodejs)
- [Spring Boot (Java)](#spring-boot-java)
- [ASP.NET Core (C#)](#aspnet-core-c)
- [Flask (Python)](#flask-python)

### 🎯 **Ejemplos Específicos**
- [Descripción de Herramientas](#descripción-de-herramientas)
- [Manejo de Errores](#manejo-de-errores)
- [Validación de Entrada](#validación-de-entrada)
- [Integración con Agentes](#integración-con-agentes)

---

## 🔧 Implementaciones Completas

### FastAPI (Python)

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

### Express.js (Node.js)

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

  const { check_in } = req.body;
  const checkInDate = new Date(check_in);
  
  if (checkInDate < new Date()) {
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
  console.log('ATDF Example server running on port 3000');
});
```

### Spring Boot (Java)

#### Estructura del Proyecto
```
spring-atdf-example/
├── src/main/java/com/example/atdf/
│   ├── AtdfApplication.java
│   ├── controller/
│   │   └── ToolController.java
│   ├── model/
│   │   ├── ATDFError.java
│   │   ├── ATDFErrorResponse.java
│   │   └── Tool.java
│   └── service/
│       └── HotelService.java
└── pom.xml
```

#### Implementación Principal
```java
// ToolController.java
@RestController
@RequestMapping("/api")
public class ToolController {
    
    @GetMapping("/tools")
    public Map<String, List<Tool>> getTools() {
        List<Tool> tools = Arrays.asList(
            new Tool(
                "hotel_reservation",
                "Make a hotel reservation",
                createHotelSchema()
            )
        );
        return Map.of("tools", tools);
    }
    
    @PostMapping("/hotel/reserve")
    public ResponseEntity<?> reserveHotel(@RequestBody @Valid HotelReservationRequest request) {
        try {
            // Validación de negocio
            if (request.getCheckIn().isBefore(LocalDateTime.now())) {
                ATDFErrorResponse error = createATDFError(
                    "https://api.example.com/errors/invalid-date",
                    "Invalid Check-in Date",
                    "Check-in date cannot be in the past",
                    "hotel_reservation",
                    "check_in",
                    LocalDateTime.now().toString(),
                    Map.of("current_time", LocalDateTime.now().toString())
                );
                return ResponseEntity.badRequest().body(error);
            }
            
            // Lógica de negocio exitosa
            HotelReservationResponse response = new HotelReservationResponse(
                UUID.randomUUID().toString(),
                "confirmed",
                "Hotel reservation created successfully"
            );
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            ATDFErrorResponse error = createATDFError(
                "https://api.example.com/errors/validation-error",
                "Validation Error",
                e.getMessage(),
                "hotel_reservation",
                "unknown",
                null,
                Map.of("error_type", e.getClass().getSimpleName())
            );
            return ResponseEntity.badRequest().body(error);
        }
    }
    
    private ATDFErrorResponse createATDFError(String type, String title, String detail,
                                            String toolName, String parameterName,
                                            String suggestedValue, Map<String, Object> context) {
        ATDFError error = new ATDFError(
            type, title, detail, "/api/errors/" + UUID.randomUUID(),
            toolName, parameterName, suggestedValue, context
        );
        return new ATDFErrorResponse(Arrays.asList(error));
    }
}

// ATDFError.java
@Data
@AllArgsConstructor
public class ATDFError {
    private String type;
    private String title;
    private String detail;
    private String instance;
    private String toolName;
    private String parameterName;
    private String suggestedValue;
    private Map<String, Object> context;
}

// ATDFErrorResponse.java
@Data
@AllArgsConstructor
public class ATDFErrorResponse {
    private List<ATDFError> errors;
}
```

---

## 🎯 Ejemplos Específicos

### Descripción de Herramientas

#### Herramienta de Búsqueda Web
```json
{
  "name": "web_search",
  "description": "Search the web for current information",
  "version": "1.0.0",
  "tags": ["search", "web", "information"],
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query",
        "minLength": 1,
        "maxLength": 500
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results",
        "minimum": 1,
        "maximum": 20,
        "default": 10
      },
      "language": {
        "type": "string",
        "description": "Search language",
        "enum": ["en", "es", "fr", "de"],
        "default": "en"
      }
    },
    "required": ["query"]
  },
  "examples": [
    {
      "name": "Basic search",
      "input": {
        "query": "latest AI developments",
        "max_results": 5
      }
    }
  ]
}
```

#### Herramienta de Análisis de Sentimientos
```json
{
  "name": "sentiment_analysis",
  "description": "Analyze the sentiment of text content",
  "version": "1.0.0",
  "tags": ["nlp", "analysis", "sentiment"],
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Text to analyze",
        "minLength": 1,
        "maxLength": 10000
      },
      "language": {
        "type": "string",
        "description": "Text language for better accuracy",
        "enum": ["auto", "en", "es", "fr", "de"],
        "default": "auto"
      },
      "detailed": {
        "type": "boolean",
        "description": "Return detailed analysis",
        "default": false
      }
    },
    "required": ["text"]
  }
}
```

### Manejo de Errores

#### Error de Autenticación
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/authentication",
      "title": "Authentication Required",
      "detail": "Valid API key is required to access this tool",
      "instance": "/api/errors/auth-required-001",
      "tool_name": "web_search",
      "parameter_name": "api_key",
      "suggested_value": null,
      "context": {
        "missing_header": "X-API-Key",
        "documentation_url": "https://api.example.com/docs/authentication"
      }
    }
  ]
}
```

#### Error de Límite de Uso
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/rate-limit",
      "title": "Rate Limit Exceeded",
      "detail": "You have exceeded the rate limit of 100 requests per hour",
      "instance": "/api/errors/rate-limit-001",
      "tool_name": "web_search",
      "parameter_name": "rate_limit",
      "suggested_value": null,
      "context": {
        "current_usage": 100,
        "limit": 100,
        "reset_time": "2024-01-15T13:00:00Z",
        "upgrade_url": "https://api.example.com/pricing"
      }
    }
  ]
}
```

### Validación de Entrada

#### Validación de Email
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Email Format",
      "detail": "The provided email address is not in a valid format",
      "instance": "/api/errors/email-validation-001",
      "tool_name": "user_registration",
      "parameter_name": "email",
      "suggested_value": null,
      "context": {
        "field_path": ["body", "email"],
        "input_value": "invalid-email",
        "expected_format": "user@domain.com"
      }
    }
  ]
}
```

#### Validación de Rango de Fechas
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/invalid-date-range",
      "title": "Invalid Date Range",
      "detail": "End date must be after start date",
      "instance": "/api/errors/date-range-001",
      "tool_name": "event_scheduling",
      "parameter_name": "end_date",
      "suggested_value": "2024-02-15T18:00:00Z",
      "context": {
        "start_date": "2024-02-15T18:00:00Z",
        "end_date": "2024-02-15T17:00:00Z",
        "minimum_duration": "1 hour"
      }
    }
  ]
}
```

---

## 🔄 Integración con Agentes

### Ejemplo de Consumo por Agente de IA

```python
import requests
import json

class ATDFAgent:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_tools(self):
        """Obtiene la lista de herramientas disponibles"""
        response = requests.get(f"{self.base_url}/tools")
        return response.json()["tools"]
    
    def execute_tool(self, tool_name, parameters):
        """Ejecuta una herramienta específica"""
        response = requests.post(
            f"{self.base_url}/api/{tool_name}/execute",
            json=parameters
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return self.handle_atdf_error(error_data)
    
    def handle_atdf_error(self, error_data):
        """Maneja errores ATDF y sugiere correcciones"""
        for error in error_data["errors"]:
            print(f"Error: {error['title']}")
            print(f"Detail: {error['detail']}")
            print(f"Tool: {error['tool_name']}")
            print(f"Parameter: {error['parameter_name']}")
            
            if error['suggested_value']:
                print(f"Suggested value: {error['suggested_value']}")
                # El agente puede usar el valor sugerido para reintentar
                return self.retry_with_suggestion(error, error['suggested_value'])
        
        return error_data
    
    def retry_with_suggestion(self, error, suggested_value):
        """Reintenta la operación con el valor sugerido"""
        # Implementación de reintento automático
        pass

# Uso del agente
agent = ATDFAgent("http://localhost:8000")
tools = agent.get_tools()
print("Available tools:", [tool["name"] for tool in tools])

# Ejecutar herramienta
result = agent.execute_tool("hotel_reservation", {
    "guest_name": "John Doe",
    "email": "john@example.com",
    "check_in": "2024-01-15T14:00:00Z",
    "check_out": "2024-01-17T12:00:00Z",
    "room_type": "double",
    "guests": 2
})
```

---

## 📚 Recursos Adicionales

### Enlaces Útiles
- [Especificación ATDF Completa](./ATDF_SPECIFICATION.md)
- [Mejores Prácticas](./BEST_PRACTICES.md)
- [Guía de Implementación](./IMPLEMENTATION_GUIDE.md)

### Ejemplos por Lenguaje
- [Python Examples](./examples/python/)
- [JavaScript Examples](./examples/javascript/)
- [Java Examples](./examples/java/)
- [C# Examples](./examples/csharp/)

---

**Nota**: Todos los ejemplos están diseñados para ser compatibles con la especificación ATDF 1.0.0 y pueden ser utilizados como base para implementaciones en producción.

**Documentación**: [https://mauricioperera.github.io/agent-tool-description-format/](https://mauricioperera.github.io/agent-tool-description-format/) 