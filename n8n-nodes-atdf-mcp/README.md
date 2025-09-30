# n8n-nodes-atdf-mcp

Nodos personalizados de n8n para integración con ATDF (Agent Tool Description Format) y MCP (Model Context Protocol).

## 🚀 Características

- **ATDF MCP Client Node**: Conecta a servidores ATDF via protocolo MCP
- **ATDF MCP Server Node**: Expone workflows de n8n como herramientas ATDF
- **Soporte multiidioma**: Inglés, Español y Portugués
- **Validación de esquemas**: Validación automática de parámetros de entrada
- **Metadatos enriquecidos**: Soporte completo para metadatos ATDF
- **Configuración flexible**: Múltiples formatos de respuesta y opciones

## 📦 Instalación

### Instalación desde npm (Recomendado)

```bash
npm install n8n-nodes-atdf-mcp
```

### Instalación manual

1. Clona este repositorio:
```bash
git clone https://github.com/your-org/n8n-nodes-atdf-mcp.git
cd n8n-nodes-atdf-mcp
```

2. Instala las dependencias:
```bash
npm install
```

3. Construye el paquete:
```bash
npm run build
```

4. Enlaza el paquete localmente:
```bash
npm link
```

5. En tu instalación de n8n, enlaza el paquete:
```bash
npm link n8n-nodes-atdf-mcp
```

### Configuración en n8n

1. Reinicia tu instancia de n8n
2. Los nodos aparecerán en la categoría "ATDF MCP"
3. Configura las credenciales ATDF MCP API según sea necesario

## 🔧 Configuración

### Credenciales ATDF MCP API

Antes de usar los nodos, configura las credenciales:

1. Ve a **Configuración** > **Credenciales** en n8n
2. Crea nuevas credenciales "ATDF MCP API"
3. Configura:
   - **Server URL**: URL del servidor ATDF (ej: `http://localhost:8000`)
   - **API Key**: Clave API si es requerida
   - **Timeout**: Tiempo límite en milisegundos (por defecto: 30000)

## 📋 Uso

### ATDF MCP Client Node

El nodo cliente permite conectarse a servidores ATDF y ejecutar herramientas.

#### Operaciones disponibles:

1. **List Tools**: Obtiene la lista de herramientas disponibles
2. **Execute Tool**: Ejecuta una herramienta específica
3. **Get Tool Schema**: Obtiene el esquema de una herramienta

#### Ejemplo de uso:

```json
{
  "operation": "executeTool",
  "toolName": "file_operations",
  "toolParameters": {
    "action": "read",
    "path": "/path/to/file.txt"
  },
  "language": "es",
  "includeMetadata": true
}
```

### ATDF MCP Server Node

El nodo servidor expone workflows de n8n como herramientas ATDF.

#### Configuración de herramienta:

```json
{
  "name": "process_data",
  "description": "Procesa datos de entrada y genera un reporte",
  "when_to_use": "Usar cuando necesites procesar datos estructurados",
  "category": "data_processing",
  "input_schema": {
    "type": "object",
    "properties": {
      "data": {
        "type": "array",
        "description": "Datos a procesar"
      },
      "format": {
        "type": "string",
        "enum": ["json", "csv", "xml"],
        "description": "Formato de salida"
      }
    },
    "required": ["data"]
  },
  "tags": "processing, data, report"
}
```

#### Soporte multiidioma:

```json
{
  "es_description": "Procesa datos de entrada y genera un reporte detallado",
  "es_when_to_use": "Usar cuando necesites procesar datos estructurados y generar reportes",
  "pt_description": "Processa dados de entrada e gera um relatório detalhado",
  "pt_when_to_use": "Use quando precisar processar dados estruturados e gerar relatórios"
}
```

## 🔄 Flujos de trabajo de ejemplo

### Ejemplo 1: Cliente ATDF básico

```json
{
  "nodes": [
    {
      "name": "ATDF MCP Client",
      "type": "n8n-nodes-atdf-mcp.atdfMcpClient",
      "parameters": {
        "operation": "listTools",
        "language": "es"
      },
      "credentials": {
        "atdfMcpApi": "atdf-server-credentials"
      }
    }
  ]
}
```

### Ejemplo 2: Servidor ATDF con webhook

```json
{
  "nodes": [
    {
      "name": "ATDF MCP Server",
      "type": "n8n-nodes-atdf-mcp.atdfMcpServer",
      "parameters": {
        "operation": "exposeTool",
        "toolConfig": {
          "name": "email_sender",
          "description": "Sends emails via SMTP",
          "category": "communication",
          "input_schema": "{\"type\":\"object\",\"properties\":{\"to\":{\"type\":\"string\"},\"subject\":{\"type\":\"string\"},\"body\":{\"type\":\"string\"}},\"required\":[\"to\",\"subject\",\"body\"]}"
        }
      }
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "toEmail": "={{$json.arguments.to}}",
        "subject": "={{$json.arguments.subject}}",
        "text": "={{$json.arguments.body}}"
      }
    }
  ]
}
```

## 🔗 Integración con MCP

Los nodos son totalmente compatibles con el protocolo MCP:

### Formato de solicitud MCP:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

### Formato de respuesta MCP:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool executed successfully"
      }
    ],
    "isError": false
  }
}
```

## 🌐 Soporte multiidioma

Los nodos soportan múltiples idiomas:

- **Inglés (en)**: Idioma por defecto
- **Español (es)**: Soporte completo
- **Portugués (pt)**: Soporte completo

### Configuración de idioma:

1. En el nodo cliente, selecciona el idioma en el parámetro "Language"
2. En el nodo servidor, configura descripciones en múltiples idiomas
3. El servidor responderá en el idioma solicitado por el cliente

## 🛠️ Desarrollo

### Estructura del proyecto:

```
n8n-nodes-atdf-mcp/
├── credentials/
│   └── AtdfMcpApi.credentials.ts
├── nodes/
│   ├── AtdfMcpClient/
│   │   ├── AtdfMcpClient.node.ts
│   │   └── atdf-mcp-client.svg
│   └── AtdfMcpServer/
│       ├── AtdfMcpServer.node.ts
│       └── atdf-mcp-server.svg
├── package.json
├── tsconfig.json
└── README.md
```

### Comandos de desarrollo:

```bash
# Desarrollo con watch mode
npm run dev

# Construcción
npm run build

# Linting
npm run lint

# Formateo de código
npm run format
```

## 🧪 Testing

### Pruebas del cliente:

```bash
# Probar conexión al servidor ATDF
curl -X GET http://localhost:8000/mcp/tools/list

# Ejecutar herramienta
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "tool_name",
      "arguments": {}
    }
  }'
```

### Pruebas del servidor:

```bash
# Probar webhook del servidor
curl -X POST http://localhost:5678/webhook/atdf-mcp-server \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
      "name": "your_tool_name",
      "arguments": {}
    }
  }'
```

## 📚 Recursos adicionales

- [Documentación ATDF](https://github.com/your-org/agent-tool-description-format)
- [Especificación MCP](https://modelcontextprotocol.io/)
- [Documentación n8n](https://docs.n8n.io/)
- [Guía de desarrollo de nodos n8n](https://docs.n8n.io/integrations/creating-nodes/)

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/your-org/n8n-nodes-atdf-mcp/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/your-org/n8n-nodes-atdf-mcp/discussions)
- **Email**: contact@atdf.dev

## 🔄 Changelog

### v1.0.0
- ✅ Nodo ATDF MCP Client
- ✅ Nodo ATDF MCP Server  
- ✅ Soporte multiidioma (en, es, pt)
- ✅ Validación de esquemas JSON
- ✅ Metadatos ATDF completos
- ✅ Compatibilidad MCP total