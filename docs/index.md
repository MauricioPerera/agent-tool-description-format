# Agent Tool Description Format (ATDF) - Documentación

## 🎯 ¿Qué es ATDF?

El **Agent Tool Description Format (ATDF)** es un estándar abierto para describir herramientas de agentes de IA y manejar respuestas de error de manera estandarizada. ATDF proporciona **plantillas y especificaciones agnósticas al código** que funcionan independientemente del lenguaje de programación o framework utilizado.

## 📚 Documentación Principal

- **[Especificación ATDF](./ATDF_SPECIFICATION.md)** - Especificación completa del formato
- **[Conceptos Fundamentales](./CONCEPTS.md)** - Explicación de conceptos clave
- **[Ejemplos de Implementación](./examples.md)** - Ejemplos en múltiples lenguajes y herramientas
- **[Guía de Implementación](./IMPLEMENTATION_GUIDE.md)** - Cómo implementar ATDF
- **[Mejores Prácticas](./BEST_PRACTICES.md)** - Recomendaciones para implementación

### 📊 **Recursos Visuales**
- **[Diagramas Mermaid](./MERMAID_DIAGRAMS.md)** - Diagramas de flujo y arquitectura ATDF

## 🎯 Plantillas ATDF

### 1. **Plantilla de Descripción de Herramienta**

#### Estructura Básica
```json
{
  "tools": [
    {
      "name": "string",
      "description": "string",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  ]
}
```

#### Plantilla Completa
```json
{
  "tools": [
    {
      "name": "nombre_herramienta",
      "description": "Descripción clara de lo que hace la herramienta",
      "version": "1.0.0",
      "tags": ["categoria1", "categoria2"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "parametro1": {
            "type": "string",
            "description": "Descripción del parámetro",
            "minLength": 1
          },
          "parametro2": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "description": "Descripción del parámetro"
          }
        },
        "required": ["parametro1", "parametro2"]
      },
      "examples": [
        {
          "name": "Ejemplo básico",
          "input": {
            "parametro1": "valor_ejemplo",
            "parametro2": 10
          }
        }
      ]
    }
  ]
}
```

### 2. **Plantilla de Respuesta de Error ATDF**

#### Estructura de Error
```json
{
  "errors": [
    {
      "type": "string",
      "title": "string",
      "detail": "string",
      "instance": "string",
      "tool_name": "string",
      "parameter_name": "string",
      "suggested_value": "string|null",
      "context": "object"
    }
  ]
}
```

#### Plantilla de Error con Contexto
```json
{
  "errors": [
    {
      "type": "https://api.example.com/errors/tipo-error",
      "title": "Título del Error",
      "detail": "Descripción detallada del problema",
      "instance": "/api/errors/uuid-unico",
      "tool_name": "nombre_herramienta",
      "parameter_name": "parametro_problematico",
      "suggested_value": "valor_sugerido",
      "context": {
        "informacion_adicional": "valor",
        "timestamp": "2025-01-15T12:00:00Z"
      }
    }
  ]
}
```

## 🔧 Tipos de Error Estándar

| Tipo | URI | Descripción | Uso |
|------|-----|-------------|-----|
| Validation Error | `https://api.example.com/errors/validation-error` | Errores de validación de entrada | Parámetros inválidos |
| Invalid Date | `https://api.example.com/errors/invalid-date` | Fechas inválidas | Fechas en el pasado |
| Invalid Route | `https://api.example.com/errors/invalid-route` | Rutas inválidas | Origen = destino |
| Business Rule | `https://api.example.com/errors/business-rule` | Reglas de negocio | Límites de capacidad |
| Authentication | `https://api.example.com/errors/authentication` | Errores de autenticación | Credenciales inválidas |
| Authorization | `https://api.example.com/errors/authorization` | Errores de autorización | Permisos insuficientes |

## 🚀 Implementación Rápida

### 1. **Definir Descripción de Herramienta**
Usa la plantilla ATDF para describir tu herramienta:

```json
{
  "tools": [
    {
      "name": "hotel_reservation",
      "description": "Make a hotel reservation with validation",
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
  ]
}
```

### 2. **Definir Respuesta de Error**
Usa la plantilla ATDF para errores:

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

### 🔧 **Implementaciones Disponibles**

- **[Python (FastAPI)](./examples.md#fastapi-python)**
- **[JavaScript (Express.js)](./examples.md#expressjs-nodejs)**
- **[Java (Spring Boot)](./examples.md#spring-boot-java)**
- **[C# (ASP.NET Core)](./examples.md#aspnet-core-c)**
- **[Go (Gin)](./examples.md#go-gin)**
- **[Rust (Actix-web)](./examples.md#rust-actix-web)**

## 🎯 Casos de Uso

### 🤖 **Agentes de IA**
- Descripción estandarizada de herramientas
- Manejo automático de errores
- Corrección automática con valores sugeridos
- Integración con cualquier agente compatible

### 🔌 **APIs y Microservicios**
- Formato de error consistente
- Documentación automática
- Validación de entrada estandarizada
- Interoperabilidad entre servicios

### 🛠️ **Herramientas de Desarrollo**
- Generación automática de documentación
- Testing estandarizado
- Monitoreo y logging consistente
- Debugging mejorado

## 📊 Beneficios

| Beneficio | Descripción |
|-----------|-------------|
| **Interoperabilidad** | Funciona con cualquier agente de IA o sistema |
| **Estandarización** | Formato consistente independiente de la implementación |
| **Contexto Enriquecido** | Errores con información detallada para corrección |
| **Extensibilidad** | Fácil de extender para casos de uso específicos |
| **Mantenibilidad** | Código más limpio y fácil de mantener |

## 🚀 **Próximos Pasos**

1. **[Leer la Especificación](./ATDF_SPECIFICATION.md)** para entender el formato completo
2. **[Revisar los Conceptos](./CONCEPTS.md)** para entender los fundamentos
3. **[Explorar Ejemplos](./examples.md)** para ver implementaciones reales
4. **[Seguir la Guía](./IMPLEMENTATION_GUIDE.md)** para crear tu primera herramienta

## 🔗 Enlaces Útiles

- **[Documentación Completa](https://mauricioperera.github.io/agent-tool-description-format/)**
- **[Repositorio GitHub](https://github.com/MauricioPerera/agent-tool-description-format)**
- **[Especificación ATDF](./ATDF_SPECIFICATION.md)**
- **[Ejemplos de Implementación](./examples.md)**
- **[Guía de Implementación](./IMPLEMENTATION_GUIDE.md)**

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](../LICENSE) para más detalles.

---

**ATDF** - Plantillas estandarizadas para herramientas de agentes de IA 🚀 