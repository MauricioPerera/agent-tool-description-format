# Mejores Prácticas ATDF

## 🎯 Visión General

Este documento proporciona las mejores prácticas para implementar y usar el **Agent Tool Description Format (ATDF)** de manera efectiva, asegurando consistencia, mantenibilidad y una excelente experiencia de usuario.

## 📋 Índice

1. [Diseño de Herramientas](#diseño-de-herramientas)
2. [Manejo de Errores](#manejo-de-errores)
3. [Validación de Entrada](#validación-de-entrada)
4. [Documentación](#documentación)
5. [Seguridad](#seguridad)
6. [Performance](#performance)
7. [Testing](#testing)
8. [Mantenimiento](#mantenimiento)

---

## 🔧 Diseño de Herramientas

### ✅ **Hacer**

#### 1. **Nombres Descriptivos y Únicos**
```json
{
  "name": "hotel_reservation_v2",
  "description": "Make a hotel reservation with advanced validation and ATDF error handling"
}
```

**Razón**: Los nombres deben ser únicos y descriptivos para evitar conflictos y facilitar la identificación.

#### 2. **Descripciones Claras y Específicas**
```json
{
  "description": "Reserve a hotel room with automatic validation of dates, room availability, and guest information. Supports multiple room types and provides detailed error feedback for invalid inputs."
}
```

**Razón**: Las descripciones claras ayudan a los agentes de IA a entender cuándo y cómo usar la herramienta.

#### 3. **Esquemas de Entrada Bien Definidos**
```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "guest_name": {
        "type": "string",
        "description": "Full legal name of the primary guest",
        "minLength": 1,
        "maxLength": 100,
        "pattern": "^[a-zA-Z\\s]+$"
      },
      "email": {
        "type": "string",
        "format": "email",
        "description": "Valid email address for booking confirmation"
      },
      "check_in": {
        "type": "string",
        "format": "date-time",
        "description": "Check-in date and time (ISO 8601 format)"
      },
      "check_out": {
        "type": "string",
        "format": "date-time",
        "description": "Check-out date and time (ISO 8601 format)"
      },
      "room_type": {
        "type": "string",
        "enum": ["single", "double", "suite", "family"],
        "description": "Type of room to reserve"
      },
      "guests": {
        "type": "integer",
        "minimum": 1,
        "maximum": 6,
        "description": "Number of guests (varies by room type)"
      },
      "special_requests": {
        "type": "string",
        "description": "Optional special requests or notes",
        "maxLength": 500
      }
    },
    "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
  }
}
```

**Razón**: Los esquemas bien definidos proporcionan validación automática y documentación clara.

#### 4. **Ejemplos Incluidos**
```json
{
  "examples": [
    {
      "name": "Basic reservation",
      "description": "Simple hotel reservation for 2 guests",
      "input": {
        "guest_name": "John Doe",
        "email": "john.doe@example.com",
        "check_in": "2025-02-15T14:00:00Z",
        "check_out": "2025-02-17T12:00:00Z",
        "room_type": "double",
        "guests": 2
      }
    },
    {
      "name": "Family reservation",
      "description": "Family suite reservation with special requests",
      "input": {
        "guest_name": "Maria Garcia",
        "email": "maria.garcia@example.com",
        "check_in": "2025-03-01T15:00:00Z",
        "check_out": "2025-03-05T11:00:00Z",
        "room_type": "family",
        "guests": 4,
        "special_requests": "Non-smoking room, high floor preferred"
      }
    }
  ]
}
```

**Razón**: Los ejemplos ayudan a los agentes a entender el uso correcto de la herramienta.

### ❌ **No Hacer**

#### 1. **Nombres Genéricos o Confusos**
```json
// ❌ Malo
{
  "name": "tool1",
  "description": "Does something"
}

// ✅ Bueno
{
  "name": "flight_booking",
  "description": "Book airline tickets with seat selection and meal preferences"
}
```

#### 2. **Esquemas Sin Validación**
```json
// ❌ Malo
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "data": {
        "type": "string"
      }
    }
  }
}

// ✅ Bueno
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "flight_number": {
        "type": "string",
        "pattern": "^[A-Z]{2}\\d{3,4}$",
        "description": "Flight number (e.g., AA123, BA1234)"
      }
    }
  }
}
```

---

## 🚨 Manejo de Errores

### ✅ **Hacer**

#### 1. **Tipos de Error Específicos**
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/invalid-date-range",
      "title": "Invalid Date Range",
      "detail": "Check-out date must be at least 1 day after check-in date",
      "instance": "/api/errors/date-range-001",
      "tool_name": "hotel_reservation",
      "parameter_name": "check_out",
      "suggested_value": "2025-02-16T12:00:00Z",
      "context": {
        "check_in": "2025-02-15T14:00:00Z",
        "check_out": "2025-02-15T16:00:00Z",
        "minimum_stay": "1 day"
      }
    }
  ]
}
```

#### 2. **Valores Sugeridos Útiles**
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Email Format",
      "detail": "The email address format is invalid",
      "tool_name": "user_registration",
      "parameter_name": "email",
      "suggested_value": "john.doe@example.com",
      "context": {
        "provided_value": "john.doe@",
        "expected_format": "user@domain.com"
      }
    }
  ]
}
```

#### 3. **Contexto Enriquecido**
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/business-rule",
      "title": "Room Not Available",
      "detail": "The requested room type is not available for the selected dates",
      "tool_name": "hotel_reservation",
      "parameter_name": "room_type",
      "suggested_value": "double",
      "context": {
        "requested_room": "suite",
        "available_rooms": ["single", "double"],
        "date_range": "2025-02-15 to 2025-02-17",
        "alternative_dates": ["2025-02-20 to 2025-02-22"]
      }
    }
  ]
}
```

### ❌ **No Hacer**

#### 1. **Mensajes de Error Genéricos**
```json
// ❌ Malo
{
  "errors": [
    {
      "type": "error",
      "title": "Error",
      "detail": "Something went wrong"
    }
  ]
}

// ✅ Bueno
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Check-in Date",
      "detail": "Check-in date cannot be in the past. Please select a future date."
    }
  ]
}
```

#### 2. **Falta de Contexto**
```json
// ❌ Malo
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Input",
      "detail": "Invalid input provided"
    }
  ]
}

// ✅ Bueno
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Invalid Guest Count",
      "detail": "The number of guests exceeds the maximum allowed for this room type",
      "context": {
        "provided_guests": 6,
        "room_type": "single",
        "max_guests": 2
      }
    }
  ]
}
```

---

## ✅ Validación de Entrada

### ✅ **Hacer**

#### 1. **Validación en Múltiples Niveles**
```python
# Nivel 1: Validación de esquema JSON
def validate_schema(data, schema):
    try:
        jsonschema.validate(data, schema)
        return None
    except jsonschema.ValidationError as e:
        return str(e)

# Nivel 2: Validación de reglas de negocio
def validate_business_rules(data):
    errors = []
    
    # Validar fechas
    check_in = datetime.fromisoformat(data["check_in"].replace("Z", "+00:00"))
    check_out = datetime.fromisoformat(data["check_out"].replace("Z", "+00:00"))
    
    if check_in < datetime.now():
        errors.append({
            "type": "https://api.example.com/errors/invalid-date",
            "title": "Invalid Check-in Date",
            "detail": "Check-in date cannot be in the past",
            "parameter_name": "check_in",
            "suggested_value": datetime.now().isoformat()
        })
    
    if check_out <= check_in:
        errors.append({
            "type": "https://api.example.com/errors/invalid-date-range",
            "title": "Invalid Date Range",
            "detail": "Check-out must be after check-in",
            "parameter_name": "check_out"
        })
    
    return errors

# Nivel 3: Validación de disponibilidad
def validate_availability(data):
    # Verificar disponibilidad en base de datos
    pass
```

#### 2. **Validación Progresiva**
```python
def validate_hotel_reservation(data):
    # Paso 1: Validar esquema básico
    schema_error = validate_schema(data, HOTEL_SCHEMA)
    if schema_error:
        return [create_atdf_error("validation", "Schema Validation Error", schema_error)]
    
    # Paso 2: Validar reglas de negocio
    business_errors = validate_business_rules(data)
    if business_errors:
        return business_errors
    
    # Paso 3: Validar disponibilidad
    availability_error = validate_availability(data)
    if availability_error:
        return [availability_error]
    
    return None  # Sin errores
```

### ❌ **No Hacer**

#### 1. **Validación Inconsistente**
```python
# ❌ Malo - Validación inconsistente
def validate_email(email):
    if "@" in email:  # Validación muy básica
        return True
    return False

# ✅ Bueno - Validación robusta
import re
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

#### 2. **Validación Silenciosa**
```python
# ❌ Malo - No reporta errores específicos
def process_data(data):
    try:
        # Procesar datos
        return result
    except Exception:
        return None  # Error silencioso

# ✅ Bueno - Reporta errores específicos
def process_data(data):
    try:
        # Procesar datos
        return result
    except ValueError as e:
        return create_atdf_error("validation", "Invalid Data", str(e))
    except Exception as e:
        return create_atdf_error("internal", "Processing Error", str(e))
```

---

## 📚 Documentación

### ✅ **Hacer**

#### 1. **Documentación Completa de Herramientas**
```markdown
# Hotel Reservation Tool

## Descripción
Herramienta para realizar reservas de hotel con validación automática y manejo de errores ATDF.

## Parámetros de Entrada

### guest_name (string, requerido)
- **Descripción**: Nombre completo del huésped principal
- **Formato**: Solo letras y espacios
- **Longitud**: 1-100 caracteres
- **Ejemplo**: "John Doe"

### email (string, requerido)
- **Descripción**: Dirección de email válida
- **Formato**: RFC 5322
- **Ejemplo**: "john.doe@example.com"

### check_in (string, requerido)
- **Descripción**: Fecha y hora de llegada
- **Formato**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
- **Restricciones**: No puede ser en el pasado
- **Ejemplo**: "2025-02-15T14:00:00Z"

## Códigos de Error

| Código | Descripción | Solución |
|--------|-------------|----------|
| `invalid-date` | Fecha de llegada en el pasado | Usar fecha futura |
| `invalid-date-range` | Fecha de salida antes de llegada | Ajustar fechas |
| `room-unavailable` | Habitación no disponible | Cambiar tipo o fechas |

## Ejemplos de Uso

### Reserva Básica
```json
{
  "guest_name": "John Doe",
  "email": "john.doe@example.com",
  "check_in": "2025-02-15T14:00:00Z",
  "check_out": "2025-02-17T12:00:00Z",
  "room_type": "double",
  "guests": 2
}
```

### Respuesta Exitosa
```json
{
  "reservation_id": "RES-2025-001",
  "status": "confirmed",
  "message": "Hotel reservation created successfully"
}
```
```

#### 2. **Documentación de API**
```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: ATDF Hotel API
  version: 1.0.0
  description: API for hotel reservations with ATDF error handling

paths:
  /tools:
    get:
      summary: Get available tools
      responses:
        '200':
          description: List of available tools
          content:
            application/json:
              schema:
                type: object
                properties:
                  tools:
                    type: array
                    items:
                      $ref: '#/components/schemas/Tool'
  
  /api/hotel/reserve:
    post:
      summary: Make a hotel reservation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/HotelReservationRequest'
      responses:
        '200':
          description: Reservation created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HotelReservationResponse'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ATDFErrorResponse'

components:
  schemas:
    Tool:
      type: object
      properties:
        name:
          type: string
        description:
          type: string
        inputSchema:
          type: object
    
    ATDFErrorResponse:
      type: object
      properties:
        errors:
          type: array
          items:
            $ref: '#/components/schemas/ATDFError'
    
    ATDFError:
      type: object
      properties:
        type:
          type: string
        title:
          type: string
        detail:
          type: string
        instance:
          type: string
        tool_name:
          type: string
        parameter_name:
          type: string
        suggested_value:
          type: string
        context:
          type: object
```

### ❌ **No Hacer**

#### 1. **Documentación Incompleta**
```markdown
# ❌ Malo - Documentación incompleta
## Hotel Tool
Makes hotel reservations.

# ✅ Bueno - Documentación completa
## Hotel Reservation Tool
Comprehensive tool for making hotel reservations with automatic validation, availability checking, and detailed error feedback.
```

#### 2. **Ejemplos Desactualizados**
```json
// ❌ Malo - Ejemplo desactualizado
{
  "name": "old_tool_name",
  "parameters": ["param1", "param2"]  // Formato antiguo
}

// ✅ Bueno - Ejemplo actualizado
{
  "name": "hotel_reservation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "guest_name": {"type": "string"}
    }
  }
}
```

---

## 🔒 Seguridad

### ✅ **Hacer**

#### 1. **Validación de Entrada Estricta**
```python
def sanitize_input(data):
    """Sanitiza y valida la entrada del usuario"""
    sanitized = {}
    
    # Validar y sanitizar nombre
    if 'guest_name' in data:
        name = data['guest_name'].strip()
        if re.match(r'^[a-zA-Z\s]{1,100}$', name):
            sanitized['guest_name'] = name
        else:
            raise ValueError("Invalid guest name format")
    
    # Validar email
    if 'email' in data:
        email = data['email'].strip().lower()
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            sanitized['email'] = email
        else:
            raise ValueError("Invalid email format")
    
    return sanitized
```

#### 2. **Autenticación y Autorización**
```python
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify(create_atdf_error(
                "https://api.example.com/errors/authentication",
                "Authentication Required",
                "Valid API key is required",
                "unknown",
                "api_key"
            )), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/hotel/reserve', methods=['POST'])
@require_api_key
def reserve_hotel():
    # Implementación de la herramienta
    pass
```

#### 3. **Rate Limiting**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "1000 per day"]
)

@app.route('/api/hotel/reserve', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key
def reserve_hotel():
    # Implementación de la herramienta
    pass
```

### ❌ **No Hacer**

#### 1. **Confiar en la Entrada del Usuario**
```python
# ❌ Malo - Sin validación
def process_data(data):
    return f"SELECT * FROM users WHERE name = '{data['name']}'"  # SQL Injection

# ✅ Bueno - Con validación
def process_data(data):
    name = sanitize_string(data['name'])
    return f"SELECT * FROM users WHERE name = ?", (name,)
```

#### 2. **Exponer Información Sensible**
```json
// ❌ Malo - Información sensible expuesta
{
  "errors": [
    {
      "detail": "Database connection failed: user=admin, password=secret123"
    }
  ]
}

// ✅ Bueno - Información segura
{
  "errors": [
    {
      "detail": "Database connection failed. Please try again later."
    }
  ]
}
```

---

## ⚡ Performance

### ✅ **Hacer**

#### 1. **Caché de Herramientas**
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_tool_definition(tool_name):
    """Cache de definiciones de herramientas"""
    return TOOL_DEFINITIONS.get(tool_name)

def get_tools_cached():
    """Obtiene herramientas con caché Redis"""
    cache_key = "tools:definitions"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    tools = list(TOOL_DEFINITIONS.values())
    redis_client.setex(cache_key, 3600, json.dumps(tools))  # Cache por 1 hora
    return tools
```

#### 2. **Validación Eficiente**
```python
# Compilar regex una vez
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
NAME_PATTERN = re.compile(r'^[a-zA-Z\s]{1,100}$')

def validate_email(email):
    return EMAIL_PATTERN.match(email) is not None

def validate_name(name):
    return NAME_PATTERN.match(name) is not None
```

#### 3. **Respuestas Optimizadas**
```python
def create_minimal_error_response(error_type, title, detail, tool_name, parameter_name):
    """Crea respuesta de error mínima para mejor performance"""
    return {
        "errors": [{
            "type": error_type,
            "title": title,
            "detail": detail,
            "instance": f"/api/errors/{uuid.uuid4()}",
            "tool_name": tool_name,
            "parameter_name": parameter_name
        }]
    }
```

### ❌ **No Hacer**

#### 1. **Validación Redundante**
```python
# ❌ Malo - Validación redundante
def validate_data(data):
    # Validar email múltiples veces
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
        return False
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return False
    return True

# ✅ Bueno - Validación única
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_data(data):
    return EMAIL_PATTERN.match(data['email']) is not None
```

#### 2. **Respuestas Sobredimensionadas**
```json
// ❌ Malo - Respuesta innecesariamente grande
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Validation Error",
      "detail": "Invalid input",
      "instance": "/api/errors/123",
      "tool_name": "hotel_reservation",
      "parameter_name": "email",
      "context": {
        "full_request": {...},  // Datos innecesarios
        "stack_trace": "...",   // Información de debug
        "timestamp": "...",
        "server_info": "..."
      }
    }
  ]
}
```

---

## 🧪 Testing

### ✅ **Hacer**

#### 1. **Tests Unitarios Completos**
```python
import unittest
from unittest.mock import Mock, patch

class TestATDFImplementation(unittest.TestCase):
    def setUp(self):
        self.tool_registry = ToolRegistry()
        self.error_handler = ATDFErrorHandler()
    
    def test_tool_registration(self):
        """Test que las herramientas se registran correctamente"""
        self.tool_registry.register_tool("test_tool", "Test", {})
        tools = self.tool_registry.get_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "test_tool")
    
    def test_error_format(self):
        """Test que los errores tienen el formato ATDF correcto"""
        error = self.error_handler.create_error(
            "validation", "Test", "Test detail", "test_tool", "test_param"
        )
        
        self.assertIn("errors", error)
        error_detail = error["errors"][0]
        required_fields = ["type", "title", "detail", "instance", 
                          "tool_name", "parameter_name"]
        
        for field in required_fields:
            self.assertIn(field, error_detail)
    
    def test_validation_errors(self):
        """Test de errores de validación específicos"""
        invalid_data = {
            "guest_name": "",
            "email": "invalid-email",
            "check_in": "2020-01-01T00:00:00Z"
        }
        
        errors = validate_hotel_reservation(invalid_data)
        self.assertIsNotNone(errors)
        self.assertGreater(len(errors), 0)
        
        # Verificar que hay errores específicos
        error_types = [e["type"] for e in errors]
        self.assertIn("https://api.example.com/errors/validation-error", error_types)
```

#### 2. **Tests de Integración**
```python
class TestATDFIntegration(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()
    
    def test_tools_endpoint(self):
        """Test del endpoint /tools"""
        response = self.client.get('/tools')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('tools', data)
        self.assertIsInstance(data['tools'], list)
    
    def test_error_handling(self):
        """Test del manejo de errores ATDF"""
        invalid_data = {
            "guest_name": "",
            "email": "invalid-email"
        }
        
        response = self.client.post('/api/hotel/reserve', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        
        error_data = response.get_json()
        self.assertIn('errors', error_data)
        self.assertGreater(len(error_data['errors']), 0)
    
    def test_successful_execution(self):
        """Test de ejecución exitosa"""
        valid_data = {
            "guest_name": "John Doe",
            "email": "john@example.com",
            "check_in": "2025-02-15T14:00:00Z",
            "check_out": "2025-02-17T12:00:00Z",
            "room_type": "double",
            "guests": 2
        }
        
        response = self.client.post('/api/hotel/reserve', json=valid_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('reservation_id', data)
        self.assertEqual(data['status'], 'confirmed')
```

#### 3. **Tests de Performance**
```python
import time
import threading

class TestATDFPerformance(unittest.TestCase):
    def test_concurrent_requests(self):
        """Test de requests concurrentes"""
        def make_request():
            response = self.client.get('/tools')
            self.assertEqual(response.status_code, 200)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
    def test_response_time(self):
        """Test de tiempo de respuesta"""
        start_time = time.time()
        response = self.client.get('/tools')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.1)  # Menos de 100ms
```

### ❌ **No Hacer**

#### 1. **Tests Incompletos**
```python
# ❌ Malo - Test incompleto
def test_tool(self):
    result = tool.execute({})
    assert result is not None

# ✅ Bueno - Test completo
def test_tool_execution(self):
    # Test caso exitoso
    valid_data = {"param": "value"}
    result = tool.execute(valid_data)
    self.assertIsNotNone(result)
    self.assertIn("status", result)
    
    # Test caso de error
    invalid_data = {"param": ""}
    result = tool.execute(invalid_data)
    self.assertIn("errors", result)
    self.assertGreater(len(result["errors"]), 0)
```

#### 2. **Tests Sin Limpieza**
```python
# ❌ Malo - Sin limpieza
def test_database_operation(self):
    # Crear datos de prueba
    create_test_data()
    result = perform_operation()
    assert result is not None
    # No limpia los datos de prueba

# ✅ Bueno - Con limpieza
def test_database_operation(self):
    # Setup
    test_data = create_test_data()
    
    try:
        # Test
        result = perform_operation()
        self.assertIsNotNone(result)
    finally:
        # Cleanup
        cleanup_test_data(test_data)
```

---

## 🔧 Mantenimiento

### ✅ **Hacer**

#### 1. **Versionado de Herramientas**
```python
class ToolVersion:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible(self, other):
        return self.major == other.major

class Tool:
    def __init__(self, name: str, version: ToolVersion, schema: dict):
        self.name = name
        self.version = version
        self.schema = schema
    
    def get_atdf_definition(self):
        return {
            "name": self.name,
            "version": str(self.version),
            "inputSchema": self.schema
        }
```

#### 2. **Logging Estructurado**
```python
import logging
import json
from datetime import datetime

class ATDFLogger:
    def __init__(self):
        self.logger = logging.getLogger('atdf')
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler('atdf.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
    
    def log_tool_execution(self, tool_name: str, input_data: dict, result: dict, execution_time: float):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "tool_execution",
            "tool_name": tool_name,
            "input_data": input_data,
            "result": result,
            "execution_time": execution_time
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_error(self, tool_name: str, error: dict, context: dict = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "tool_error",
            "tool_name": tool_name,
            "error": error,
            "context": context or {}
        }
        self.logger.error(json.dumps(log_entry))
```

#### 3. **Monitoreo y Métricas**
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Métricas Prometheus
tool_executions = Counter('atdf_tool_executions_total', 'Total tool executions', ['tool_name', 'status'])
tool_execution_duration = Histogram('atdf_tool_execution_duration_seconds', 'Tool execution duration', ['tool_name'])
active_tools = Gauge('atdf_active_tools', 'Number of active tools')

def monitor_tool_execution(tool_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                tool_executions.labels(tool_name=tool_name, status='success').inc()
                return result
            except Exception as e:
                tool_executions.labels(tool_name=tool_name, status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                tool_execution_duration.labels(tool_name=tool_name).observe(duration)
        
        return wrapper
    return decorator

@monitor_tool_execution('hotel_reservation')
def reserve_hotel(data):
    # Implementación de la herramienta
    pass
```

### ❌ **No Hacer**

#### 1. **Sin Versionado**
```python
# ❌ Malo - Sin versionado
def get_tool_definition():
    return {
        "name": "hotel_reservation",
        "schema": {...}
    }

# ✅ Bueno - Con versionado
def get_tool_definition():
    return {
        "name": "hotel_reservation",
        "version": "1.2.0",
        "schema": {...}
    }
```

#### 2. **Logging Inadecuado**
```python
# ❌ Malo - Logging básico
def execute_tool(data):
    print("Executing tool")  # Logging básico
    result = process_data(data)
    print("Tool executed")   # Sin contexto
    return result

# ✅ Bueno - Logging estructurado
def execute_tool(data):
    logger.info("Tool execution started", extra={
        "tool_name": "hotel_reservation",
        "input_size": len(str(data))
    })
    
    try:
        result = process_data(data)
        logger.info("Tool execution completed", extra={
            "tool_name": "hotel_reservation",
            "status": "success"
        })
        return result
    except Exception as e:
        logger.error("Tool execution failed", extra={
            "tool_name": "hotel_reservation",
            "error": str(e)
        })
        raise
```

---

## 📚 Recursos Adicionales

- [Especificación ATDF](../docs/ATDF_SPECIFICATION.md)
- [Conceptos Fundamentales](../docs/CONCEPTS.md)
- [Guía de Implementación](../docs/IMPLEMENTATION_GUIDE.md)
- [Ejemplos de Código](../docs/examples.md)

### Herramientas Recomendadas
- **Testing**: pytest, unittest, coverage
- **Logging**: structlog, loguru
- **Monitoreo**: Prometheus, Grafana
- **Documentación**: Sphinx, MkDocs
- **Validación**: jsonschema, pydantic

---

**Nota**: Estas mejores prácticas aseguran que tu implementación ATDF sea robusta, mantenible y escalable. Adapta estas recomendaciones a tu contexto específico y necesidades del proyecto.

**Documentación**: [https://mauricioperera.github.io/agent-tool-description-format/](https://mauricioperera.github.io/agent-tool-description-format/) 