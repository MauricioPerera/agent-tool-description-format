# Guía de Implementación ATDF

## 🎯 Visión General

Esta guía te ayudará a implementar el **Agent Tool Description Format (ATDF)** en cualquier lenguaje de programación o framework. El formato ATDF es independiente de la implementación, por lo que puedes adaptarlo a tu stack tecnológico preferido.

## 📋 Índice

1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Arquitectura de Implementación](#arquitectura-de-implementación)
3. [Pasos de Implementación](#pasos-de-implementación)
4. [Patrones de Diseño](#patrones-de-diseño)
5. [Validación y Testing](#validación-y-testing)
6. [Despliegue y Producción](#despliegue-y-producción)

---

## 🔧 Conceptos Fundamentales

### ¿Qué Necesitas Implementar?

1. **Endpoint de Herramientas** (`/tools`)
   - Devuelve descripción de herramientas en formato ATDF
   - Esquemas de entrada para cada herramienta
   - Metadatos y ejemplos

2. **Manejo de Errores ATDF**
   - Conversión de errores a formato ATDF
   - Contexto enriquecido
   - Valores sugeridos

3. **Validación de Entrada**
   - Validación de esquemas JSON
   - Reglas de negocio
   - Mensajes de error estandarizados

### Estructura de Respuesta ATDF

```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/validation-error",
      "title": "Validation Error",
      "detail": "Detailed error description",
      "instance": "/api/errors/unique-id",
      "tool_name": "tool_name",
      "parameter_name": "parameter_name",
      "suggested_value": "suggested_value",
      "context": {}
    }
  ]
}
```

---

## 🏗️ Arquitectura de Implementación

### Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent/Client  │    │   ATDF Server   │    │   Business      │
│                 │    │                 │    │   Logic         │
│ 1. Get Tools    │───▶│ 2. /tools       │    │                 │
│ 2. Execute Tool │───▶│ 3. /api/tool    │───▶│ 4. Process      │
│ 3. Handle Error │◀───│ 4. ATDF Error   │◀───│ 5. Return       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

#### 1. **Tool Registry**
```python
# Ejemplo en Python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, description: str, schema: dict):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": schema
        }
    
    def get_tools(self):
        return list(self.tools.values())
    
    def get_tool(self, name: str):
        return self.tools.get(name)
```

#### 2. **Error Handler**
```python
# Ejemplo en Python
class ATDFErrorHandler:
    def __init__(self):
        self.error_types = {
            "validation": "https://api.example.com/errors/validation-error",
            "invalid_date": "https://api.example.com/errors/invalid-date",
            "business_rule": "https://api.example.com/errors/business-rule"
        }
    
    def create_error(self, error_type: str, title: str, detail: str,
                    tool_name: str, parameter_name: str,
                    suggested_value: str = None, context: dict = None):
        return {
            "errors": [{
                "type": self.error_types.get(error_type, error_type),
                "title": title,
                "detail": detail,
                "instance": f"/api/errors/{uuid.uuid4()}",
                "tool_name": tool_name,
                "parameter_name": parameter_name,
                "suggested_value": suggested_value,
                "context": context or {}
            }]
        }
```

#### 3. **Validation Middleware**
```python
# Ejemplo en Python
class ATDFValidator:
    def __init__(self, tool_registry: ToolRegistry, error_handler: ATDFErrorHandler):
        self.tool_registry = tool_registry
        self.error_handler = error_handler
    
    def validate_request(self, tool_name: str, data: dict):
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return self.error_handler.create_error(
                "not_found", "Tool Not Found", f"Tool '{tool_name}' not found",
                tool_name, "tool_name"
            )
        
        # Validar esquema
        schema = tool["inputSchema"]
        validation_errors = self.validate_schema(data, schema)
        
        if validation_errors:
            return self.error_handler.create_error(
                "validation", "Validation Error", "Input validation failed",
                tool_name, "input", None, {"validation_errors": validation_errors}
            )
        
        return None  # Sin errores
```

---

## 📝 Pasos de Implementación

### Paso 1: Configurar la Estructura del Proyecto

```
your-atdf-project/
├── src/
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tool_registry.py
│   │   └── tool_definitions.py
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── atdf_errors.py
│   │   └── error_handler.py
│   ├── validation/
│   │   ├── __init__.py
│   │   └── validator.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── middleware.py
├── tests/
├── docs/
└── requirements.txt
```

### Paso 2: Definir Herramientas

```python
# tool_definitions.py
HOTEL_RESERVATION_TOOL = {
    "name": "hotel_reservation",
    "description": "Make a hotel reservation with validation",
    "version": "1.0.0",
    "tags": ["travel", "booking"],
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
    },
    "examples": [
        {
            "name": "Basic reservation",
            "input": {
                "guest_name": "John Doe",
                "email": "john@example.com",
                        "check_in": "2025-01-15T14:00:00Z",
        "check_out": "2025-01-17T12:00:00Z",
                "room_type": "double",
                "guests": 2
            }
        }
    ]
}
```

### Paso 3: Implementar Endpoints

```python
# routes.py
from flask import Flask, request, jsonify
from .tools.tool_registry import ToolRegistry
from .errors.error_handler import ATDFErrorHandler
from .validation.validator import ATDFValidator

app = Flask(__name__)

# Inicializar componentes
tool_registry = ToolRegistry()
error_handler = ATDFErrorHandler()
validator = ATDFValidator(tool_registry, error_handler)

# Registrar herramientas
tool_registry.register_tool(
    "hotel_reservation",
    HOTEL_RESERVATION_TOOL["description"],
    HOTEL_RESERVATION_TOOL["inputSchema"]
)

@app.route('/tools', methods=['GET'])
def get_tools():
    """Endpoint para obtener descripción de herramientas"""
    return jsonify({"tools": tool_registry.get_tools()})

@app.route('/api/<tool_name>/execute', methods=['POST'])
def execute_tool(tool_name):
    """Endpoint para ejecutar herramientas"""
    try:
        data = request.get_json()
        
        # Validar entrada
        validation_error = validator.validate_request(tool_name, data)
        if validation_error:
            return jsonify(validation_error), 400
        
        # Ejecutar lógica de negocio
        result = execute_business_logic(tool_name, data)
        return jsonify(result)
        
    except Exception as e:
        error = error_handler.create_error(
            "internal_error",
            "Internal Server Error",
            str(e),
            tool_name,
            "unknown"
        )
        return jsonify(error), 500

def execute_business_logic(tool_name: str, data: dict):
    """Ejecuta la lógica de negocio específica"""
    if tool_name == "hotel_reservation":
        return handle_hotel_reservation(data)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def handle_hotel_reservation(data: dict):
    """Maneja la reserva de hotel con validaciones de negocio"""
    from datetime import datetime
    
    # Validar fechas
    check_in = datetime.fromisoformat(data["check_in"].replace("Z", "+00:00"))
    check_out = datetime.fromisoformat(data["check_out"].replace("Z", "+00:00"))
    
    if check_in < datetime.now():
        raise ValueError("Check-in date cannot be in the past")
    
    if check_out <= check_in:
        raise ValueError("Check-out must be after check-in")
    
    # Lógica de negocio exitosa
    return {
        "reservation_id": str(uuid.uuid4()),
        "status": "confirmed",
        "message": "Hotel reservation created successfully"
    }
```

### Paso 4: Manejo de Errores

```python
# atdf_errors.py
import uuid
from typing import Dict, Any, Optional

class ATDFError:
    def __init__(self, type_uri: str, title: str, detail: str,
                 tool_name: str, parameter_name: str,
                 suggested_value: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        self.type = type_uri
        self.title = title
        self.detail = detail
        self.instance = f"/api/errors/{uuid.uuid4()}"
        self.tool_name = tool_name
        self.parameter_name = parameter_name
        self.suggested_value = suggested_value
        self.context = context or {}
    
    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "detail": self.detail,
            "instance": self.instance,
            "tool_name": self.tool_name,
            "parameter_name": self.parameter_name,
            "suggested_value": self.suggested_value,
            "context": self.context
        }

class ATDFErrorResponse:
    def __init__(self, errors: list[ATDFError]):
        self.errors = errors
    
    def to_dict(self):
        return {"errors": [error.to_dict() for error in self.errors]}
```

---

## 🎨 Patrones de Diseño

### 1. **Factory Pattern para Herramientas**

```python
# tool_factory.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class Tool(ABC):
    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        pass

class HotelReservationTool(Tool):
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementación específica
        return {"reservation_id": "123", "status": "confirmed"}
    
    def get_schema(self) -> Dict[str, Any]:
        return HOTEL_RESERVATION_TOOL["inputSchema"]

class ToolFactory:
    _tools = {
        "hotel_reservation": HotelReservationTool,
        # Agregar más herramientas aquí
    }
    
    @classmethod
    def create_tool(cls, tool_name: str) -> Tool:
        if tool_name not in cls._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return cls._tools[tool_name]()
```

### 2. **Strategy Pattern para Validación**

```python
# validation_strategies.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Optional[str]:
        pass

class DateValidationStrategy(ValidationStrategy):
    def validate(self, data: Dict[str, Any]) -> Optional[str]:
        from datetime import datetime
        
        check_in = datetime.fromisoformat(data["check_in"].replace("Z", "+00:00"))
        if check_in < datetime.now():
            return "Check-in date cannot be in the past"
        return None

class EmailValidationStrategy(ValidationStrategy):
    def validate(self, data: Dict[str, Any]) -> Optional[str]:
        import re
        email = data.get("email", "")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email format"
        return None

class ValidationContext:
    def __init__(self):
        self.strategies = []
    
    def add_strategy(self, strategy: ValidationStrategy):
        self.strategies.append(strategy)
    
    def validate(self, data: Dict[str, Any]) -> list[str]:
        errors = []
        for strategy in self.strategies:
            error = strategy.validate(data)
            if error:
                errors.append(error)
        return errors
```

### 3. **Observer Pattern para Logging**

```python
# logging_observers.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class LoggingObserver(ABC):
    @abstractmethod
    def log(self, event: str, data: Dict[str, Any]):
        pass

class ConsoleLogger(LoggingObserver):
    def log(self, event: str, data: Dict[str, Any]):
        print(f"[{event}] {data}")

class FileLogger(LoggingObserver):
    def __init__(self, filename: str):
        self.filename = filename
    
    def log(self, event: str, data: Dict[str, Any]):
        with open(self.filename, 'a') as f:
            f.write(f"[{event}] {data}\n")

class LoggingSubject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer: LoggingObserver):
        self.observers.append(observer)
    
    def notify(self, event: str, data: Dict[str, Any]):
        for observer in self.observers:
            observer.log(event, data)
```

---

## 🧪 Validación y Testing

### 1. **Tests Unitarios**

```python
# test_atdf_implementation.py
import unittest
from unittest.mock import Mock, patch
from .tools.tool_registry import ToolRegistry
from .errors.error_handler import ATDFErrorHandler

class TestATDFImplementation(unittest.TestCase):
    def setUp(self):
        self.tool_registry = ToolRegistry()
        self.error_handler = ATDFErrorHandler()
    
    def test_tool_registration(self):
        """Test que las herramientas se registran correctamente"""
        self.tool_registry.register_tool(
            "test_tool",
            "Test tool description",
            {"type": "object", "properties": {}}
        )
        
        tools = self.tool_registry.get_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "test_tool")
    
    def test_error_creation(self):
        """Test que los errores ATDF se crean correctamente"""
        error = self.error_handler.create_error(
            "validation",
            "Test Error",
            "Test error detail",
            "test_tool",
            "test_param"
        )
        
        self.assertIn("errors", error)
        self.assertEqual(len(error["errors"]), 1)
        self.assertEqual(error["errors"][0]["title"], "Test Error")
    
    def test_validation_error_format(self):
        """Test que los errores de validación tienen el formato correcto"""
        error = self.error_handler.create_error(
            "validation",
            "Validation Error",
            "Invalid input",
            "test_tool",
            "input"
        )
        
        error_detail = error["errors"][0]
        required_fields = ["type", "title", "detail", "instance", 
                          "tool_name", "parameter_name"]
        
        for field in required_fields:
            self.assertIn(field, error_detail)
```

### 2. **Tests de Integración**

```python
# test_integration.py
import requests
import json

class TestATDFIntegration:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def test_tools_endpoint(self):
        """Test del endpoint /tools"""
        response = requests.get(f"{self.base_url}/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        
        # Verificar estructura de herramientas
        for tool in data["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_error_handling(self):
        """Test del manejo de errores ATDF"""
        # Enviar datos inválidos
        invalid_data = {
            "guest_name": "",  # Nombre vacío
            "email": "invalid-email",  # Email inválido
            "check_in": "2020-01-01T00:00:00Z",  # Fecha en el pasado
            "check_out": "2020-01-01T00:00:00Z",
            "room_type": "invalid_type",
            "guests": 0
        }
        
        response = requests.post(
            f"{self.base_url}/api/hotel_reservation/execute",
            json=invalid_data
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "errors" in error_data
        assert len(error_data["errors"]) > 0
        
        # Verificar estructura de error ATDF
        error = error_data["errors"][0]
        required_fields = ["type", "title", "detail", "instance", 
                          "tool_name", "parameter_name"]
        
        for field in required_fields:
            assert field in error
    
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
        
        response = requests.post(
            f"{self.base_url}/api/hotel_reservation/execute",
            json=valid_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reservation_id" in data
        assert "status" in data
```

---

## 🚀 Despliegue y Producción

### 1. **Configuración de Producción**

```python
# config.py
import os
from typing import Dict, Any

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Configuración de base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///atdf.db")
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "atdf.log")
    
    # Configuración de seguridad
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))
    
    # Configuración de herramientas
    TOOLS_CONFIG = {
        "hotel_reservation": {
            "enabled": True,
            "rate_limit": 50,
            "requires_auth": True
        }
    }
```

### 2. **Docker Configuration**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  atdf-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/atdf
      - LOG_LEVEL=INFO
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=atdf
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. **Monitoreo y Logging**

```python
# monitoring.py
import logging
import time
from functools import wraps
from typing import Callable, Any

def setup_logging():
    """Configura logging estructurado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('atdf.log'),
            logging.StreamHandler()
        ]
    )

def monitor_execution(func: Callable) -> Callable:
    """Decorator para monitorear ejecución de herramientas"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__name__)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"Tool executed successfully", extra={
                "execution_time": execution_time,
                "status": "success"
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(f"Tool execution failed: {str(e)}", extra={
                "execution_time": execution_time,
                "status": "error",
                "error": str(e)
            })
            
            raise
    
    return wrapper
```

---

## 📚 Recursos Adicionales

### Enlaces Útiles
- [Especificación ATDF](../docs/ATDF_SPECIFICATION.md)
- [Ejemplos de Implementación](../docs/examples.md)
- [Mejores Prácticas](./BEST_PRACTICES.md)

### Herramientas Recomendadas
- **Validación**: JSON Schema validators
- **Testing**: pytest, unittest
- **Documentación**: OpenAPI/Swagger
- **Monitoreo**: Prometheus, Grafana
- **Logging**: Structured logging libraries

---

**Nota**: Esta guía proporciona una base sólida para implementar ATDF. Adapta los ejemplos a tu lenguaje y framework específico, manteniendo la compatibilidad con la especificación ATDF.

**Documentación**: [https://mauricioperera.github.io/agent-tool-description-format/](https://mauricioperera.github.io/agent-tool-description-format/) 