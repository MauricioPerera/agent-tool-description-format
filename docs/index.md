# Índice de Documentación ATDF

## 🎯 Bienvenido a ATDF

El **Agent Tool Description Format (ATDF)** es un estándar abierto para describir herramientas de agentes de IA y manejar respuestas de error de manera estandarizada. Esta documentación te guiará a través de todos los aspectos del formato ATDF.

## 📚 Documentación Principal

### 🔧 **Especificación y Conceptos**
- **[Especificación ATDF](./ATDF_SPECIFICATION.md)** - Especificación completa del formato ATDF
- **[Conceptos Fundamentales](./CONCEPTS.md)** - Explicación de los conceptos básicos de ATDF
- **[Arquitectura](./ARCHITECTURE.md)** - Diseño y arquitectura del sistema ATDF

### 🚀 **Implementación**
- **[Guía de Implementación](./IMPLEMENTATION_GUIDE.md)** - Cómo implementar ATDF en cualquier lenguaje
- **[Mejores Prácticas](./BEST_PRACTICES.md)** - Recomendaciones para implementaciones robustas
- **[Patrones de Diseño](./DESIGN_PATTERNS.md)** - Patrones comunes para implementaciones ATDF

### 📖 **Ejemplos y Tutoriales**
- **[Ejemplos por Lenguaje](./EXAMPLES.md)** - Ejemplos completos en múltiples lenguajes
- **[Tutoriales](./TUTORIALS.md)** - Tutoriales paso a paso para diferentes casos de uso
- **[Casos de Uso](./USE_CASES.md)** - Ejemplos de casos de uso reales

## 🎯 Guías por Lenguaje

### 🐍 **Python**
- [FastAPI](./examples/python/fastapi/)
- [Flask](./examples/python/flask/)
- [Django](./examples/python/django/)
- [SDK Python](./sdk/python/)

### 🟨 **JavaScript/Node.js**
- [Express.js](./examples/javascript/express/)
- [Koa](./examples/javascript/koa/)
- [SDK JavaScript](./sdk/javascript/)

### ☕ **Java**
- [Spring Boot](./examples/java/spring-boot/)
- [JAX-RS](./examples/java/jax-rs/)
- [SDK Java](./sdk/java/)

### 🔷 **C#**
- [ASP.NET Core](./examples/csharp/aspnet-core/)
- [Web API](./examples/csharp/web-api/)
- [SDK C#](./sdk/csharp/)

### 🦀 **Rust**
- [Actix Web](./examples/rust/actix-web/)
- [Warp](./examples/rust/warp/)
- [SDK Rust](./sdk/rust/)

### 🐹 **Go**
- [Gin](./examples/go/gin/)
- [Echo](./examples/go/echo/)
- [SDK Go](./sdk/go/)

## 🛠️ Herramientas y SDKs

### 📦 **SDKs Oficiales**
- **[Python SDK](./sdk/python/)** - SDK completo para Python con FastAPI, Flask, Django
- **[JavaScript SDK](./sdk/javascript/)** - SDK para Node.js y navegador
- **[Java SDK](./sdk/java/)** - SDK para Java y Spring Boot
- **[C# SDK](./sdk/csharp/)** - SDK para .NET y ASP.NET Core
- **[Rust SDK](./sdk/rust/)** - SDK para Rust con Actix Web
- **[Go SDK](./sdk/go/)** - SDK para Go con Gin y Echo

### 🔧 **Herramientas de Desarrollo**
- **[ATDF Validator](./tools/validator/)** - Validador de esquemas ATDF
- **[ATDF Generator](./tools/generator/)** - Generador de código para múltiples lenguajes
- **[ATDF Playground](./tools/playground/)** - Entorno de pruebas interactivo
- **[ATDF CLI](./tools/cli/)** - Herramienta de línea de comandos

### 📊 **Monitoreo y Testing**
- **[ATDF Testing Framework](./tools/testing/)** - Framework de testing para ATDF
- **[ATDF Metrics](./tools/metrics/)** - Métricas y monitoreo
- **[ATDF Debugger](./tools/debugger/)** - Herramienta de debugging

## 📋 Guías por Caso de Uso

### 🤖 **Agentes de IA**
- [Integración con OpenAI](./use-cases/ai-agents/openai/)
- [Integración con Anthropic](./use-cases/ai-agents/anthropic/)
- [Integración con LangChain](./use-cases/ai-agents/langchain/)
- [Agentes Personalizados](./use-cases/ai-agents/custom/)

### 🔌 **APIs y Microservicios**
- [API REST](./use-cases/apis/rest/)
- [GraphQL](./use-cases/apis/graphql/)
- [gRPC](./use-cases/apis/grpc/)
- [Microservicios](./use-cases/apis/microservices/)

### 🛠️ **Herramientas de Desarrollo**
- [Generación de Documentación](./use-cases/dev-tools/documentation/)
- [Testing Automatizado](./use-cases/dev-tools/testing/)
- [CI/CD](./use-cases/dev-tools/cicd/)
- [Monitoreo](./use-cases/dev-tools/monitoring/)

## 📚 Referencias

### 📖 **Especificaciones**
- [JSON Schema](https://json-schema.org/) - Esquemas JSON
- [OpenAPI](https://swagger.io/specification/) - Especificación OpenAPI
- [RFC 7807](https://tools.ietf.org/html/rfc7807) - Problem Details

### 🔗 **Estándares Relacionados**
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - Protocolo de contexto de modelo
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) - Llamadas de función OpenAI
- [Anthropic Tools](https://docs.anthropic.com/claude/docs/tools-and-functions) - Herramientas de Anthropic

### 📚 **Recursos Adicionales**
- [FAQ](./faq.md) - Preguntas frecuentes
- [Changelog](./changelog.md) - Historial de cambios
- [Contributing](./contributing.md) - Guía de contribución
- [License](./license.md) - Información de licencia

## 🚀 Comenzar Rápidamente

### 1. **Elegir un Lenguaje**
```bash
# Python (Recomendado para principiantes)
pip install fastapi uvicorn pydantic

# JavaScript
npm install express fastify

# Java
# Agregar dependencias de Spring Boot

# C#
dotnet add package Microsoft.AspNetCore.App
```

### 2. **Crear Primera Herramienta**
```python
# Ejemplo en Python
from fastapi import FastAPI

app = FastAPI()

@app.get("/tools")
async def get_tools():
    return {
        "tools": [{
            "name": "hello_world",
            "description": "Simple hello world tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }]
    }
```

### 3. **Probar la Herramienta**
```bash
# Iniciar servidor
uvicorn main:app --reload

# Probar endpoint
curl http://localhost:8000/tools
```

## 📞 Soporte y Comunidad

### 💬 **Canales de Soporte**
- 🐛 **GitHub Issues**: [Reportar Bugs](https://github.com/MauricioPerera/agent-tool-description-format/issues)
- 💡 **GitHub Discussions**: [Discusiones](https://github.com/MauricioPerera/agent-tool-description-format/discussions)

### 📖 **Recursos de Aprendizaje**
- 📚 **Documentación**: [https://mauricioperera.github.io/agent-tool-description-format/](https://mauricioperera.github.io/agent-tool-description-format/)
- 📚 **Repositorio**: [https://github.com/MauricioPerera/agent-tool-description-format](https://github.com/MauricioPerera/agent-tool-description-format)

### 🤝 **Contribuir**
- [Guía de Contribución](./contributing.md)
- [Código de Conducta](./CODE_OF_CONDUCT.md)
- [Roadmap](./ROADMAP.md)

---

**¿Necesitas ayuda?** Comienza con la [Guía de Implementación](./IMPLEMENTATION_GUIDE.md) o consulta los [Ejemplos](./EXAMPLES.md) para tu lenguaje preferido. 