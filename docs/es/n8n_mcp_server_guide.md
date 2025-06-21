# Guía del Servidor MCP de n8n

## Introducción y objetivos

Esta guía describe las mejores prácticas y la arquitectura para construir y mantener Servidores de Procesos Comunes (MCP) utilizando n8n. El objetivo es promover la modularidad, la reutilización y la mantenibilidad de los flujos de trabajo.

## Conceptos básicos

### MCP Server Trigger
El **MCP Server Trigger** (tipo de nodo: `@n8n/n8n-nodes-langchain.mcpTrigger`) es un nodo especializado en n8n que actúa como punto de entrada para las solicitudes al servidor MCP. Permite definir la interfaz de entrada y salida del servidor, y es el que recibe las peticiones externas para ejecutar una o varias herramientas.

### Subworkflows
Los **Subworkflows** son flujos de trabajo de n8n que se pueden llamar desde otros flujos de trabajo. Son fundamentales para la modularidad en la arquitectura MCP, permitiendo encapsular lógica específica en unidades reutilizables. Estos subworkflows implementan la lógica de una herramienta específica.

### toolWorkflow Node
El nodo **toolWorkflow** (tipo de nodo: `@n8n/n8n-nodes-langchain.toolWorkflow`) es utilizado en el flujo principal del servidor MCP para llamar a un subworkflow (herramienta). Actúa como un puente, configurando cómo se llama al subworkflow y cómo se mapean sus entradas y salidas. La descripción ATDF de la herramienta se coloca en este nodo.

## Buenas prácticas MCP

### Arquitectura
*   Diseñar una arquitectura modular utilizando subworkflows para cada herramienta o proceso discreto.
*   El servidor MCP principal utiliza un `@n8n/n8n-nodes-langchain.mcpTrigger` y llama a los subworkflows (herramientas) mediante nodos `@n8n/n8n-nodes-langchain.toolWorkflow`.

### Naming (Convenciones de Nombres)
*   Utilizar nombres claros y consistentes para workflows, subworkflows, nodos y variables.
*   Prefijar los subworkflows con `SWF_` para identificarlos fácilmente (ej. `SWF_Valida_Rango_Fechas`).
*   Prefijar las variables de entorno con `ENV_`.
*   Utilizar snake_case para nombres de variables y parámetros.
*   Para nombres de herramientas (configurados en el nodo `toolWorkflow`), seguir el formato: `tool.<acción>_<entidad>` (ej. `tool.get_user`, `tool.create_invoice`).

### Salida estándar
*   Definir un formato de salida estándar para todos los subworkflows (herramientas), tanto para respuestas exitosas como para errores. El campo `status` debe ser estrictamente `"success"` o `"error"`.

### Validación
*   Validar las entradas en cada subworkflow para asegurar la integridad de los datos.
*   Proporcionar mensajes de error claros y uniformes siguiendo el formato de error estándar.

### Seguridad
*   Proteger los endpoints del `@n8n/n8n-nodes-langchain.mcpTrigger` utilizando mecanismos de autenticación y autorización de n8n.
*   Gestionar las credenciales de forma segura utilizando el gestor de credenciales de n8n.
*   Evitar exponer información sensible en los logs.

### Documentación
*   Documentar cada herramienta (subworkflow) incluyendo su propósito, parámetros de entrada, formato de salida y cualquier dependencia. El bloque ATDF se incluye en la descripción del nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que lo llama.
*   Mantener actualizada la documentación de la arquitectura general del MCP.

### Versionado
*   Versionar los subworkflows y el servidor MCP para gestionar los cambios y evitar romper integraciones existentes.
*   Utilizar un sistema de control de versiones como Git para el versionado de los workflows exportados.

## Arquitectura General

### Estructura Básica
La arquitectura MCP se basa en un flujo principal (el servidor MCP) que utiliza un `@n8n/n8n-nodes-langchain.mcpTrigger` como punto de entrada. Este flujo orquesta la ejecución de subworkflows (herramientas) a través de nodos `@n8n/n8n-nodes-langchain.toolWorkflow`.

```mermaid
graph TD
    A[@n8n/n8n-nodes-langchain.mcpTrigger] --> B{Switch Node (Router based on tool name from AI Agent)};
    B -- tool_A_name --> C1["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Tool_A)"];
    B -- tool_B_name --> C2["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Tool_B)"];
    C1 --> D[Response Handling / Preparación para Agente AI];
    C2 --> D;
```
El `mcpTrigger` recibe una solicitud, un nodo `Switch` (o lógica similar) determina qué herramienta ejecutar, y un nodo `toolWorkflow` específico llama al subworkflow correspondiente.

### Ventajas del Uso de Subworkflows
*   **Modularidad:** Descomponer problemas complejos en partes más pequeñas y manejables.
*   **Reutilización:** Utilizar la misma lógica en diferentes partes del sistema o en diferentes servidores MCP.
*   **Mantenibilidad:** Facilitar la actualización y corrección de errores al aislar la lógica en unidades independientes.
*   **Testabilidad:** Probar cada subworkflow (herramienta) de forma aislada.

## Diseño de Herramientas MCP (Subworkflows)

### Formato Estándar de Salida

#### Éxito
El campo `status` siempre será `"success"`. El campo `data` contiene el resultado útil de la herramienta.

```json
{
  "status": "success",
  "data": {
    "resultado_especifico": "valor",
    "otro_dato": 123
  },
  "meta": {
    "timestamp": "2023-10-27T10:30:00Z"
  }
}
```
*(Nota: `meta.timestamp` se puede generar con `{{ $now }}` en un nodo `Set`)*.

#### Error
El campo `status` siempre será `"error"`. El campo `data` contiene detalles del error. El campo `message` o `text` dentro de `data` proporciona un mensaje legible.

```json
{
  "status": "error",
  "data": {
    "code": "CODIGO_ERROR_UNICO",
    "message": "Descripción legible del error.",
    "text": "Descripción legible del error (alternativa si se usa 'text').",
    "details": {
      "field": "nombre_del_campo_con_error",
      "expected": "tipo_o_formato_esperado",
      "solution": "Cómo solucionar el problema o qué se espera."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:35:00Z"
  }
}
```
*(Preferir `message` o `text` consistentemente. Si los ejemplos usan `text`, usar `text`)*.

### Validación de Entradas y Errores Uniformes
*   Utilizar nodos `n8n-nodes-base.if` o `n8n-nodes-base.switch` al inicio de los subworkflows para validar los parámetros de entrada.
*   Si la validación falla, se debe construir una respuesta de error utilizando la estructura definida anteriormente. Por ejemplo, si un campo `user_id` es requerido pero no se provee:

```json
{
  "status": "error",
  "data": {
    "code": "VALIDATION_ERROR",
    "message": "Parámetros de entrada inválidos.",
    "details": {
      "field": "user_id",
      "expected": "string, non-empty",
      "solution": "Proveer un user_id válido."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:40:00Z"
  }
}
```
*   Utilizar códigos de error únicos y descriptivos para facilitar la depuración y el monitoreo.

## Plantilla Base Visual para Subworkflows (Herramientas)

Los subworkflows que actúan como herramientas son típicamente iniciados por un `n8n-nodes-base.executeWorkflowTrigger` cuando son llamados desde el flujo principal (a través de un `@n8n/n8n-nodes-langchain.toolWorkflow`).

**Ejemplo: Subworkflow "SWF_Valida_Rango_Fechas"**

1.  **Start (Trigger):** Nodo `n8n-nodes-base.executeWorkflowTrigger`. Recibe parámetros como `Start` (fecha inicio) y `End` (fecha fin) desde el nodo `toolWorkflow` en el flujo principal.
2.  **Validación de Entradas:** Nodo `n8n-nodes-base.if` (ej. "Validar fechas"). Verifica si las fechas son válidas, si `Start` es anterior a `End`, etc.
    *   Si la validación falla, una rama (FALSE) lleva a un nodo `n8n-nodes-base.set` (ej. "Error: Fechas Inválidas") para construir el JSON de error.
3.  **Lógica Principal (si la validación es OK):** Puede incluir otros nodos para procesar las fechas si es necesario. En este ejemplo, la validación en sí misma es la lógica principal.
4.  **Salida Exitosa:** Nodo `n8n-nodes-base.set` (ej. "Success: Rango Válido"). Prepara el JSON de respuesta exitosa:
    ```json
    {
      "status": "success",
      "data": {
        "message": "El rango de fechas es válido.",
        "start_date": "{{ $json.Start }}",
        "end_date": "{{ $json.End }}"
      },
      "meta": {
        "timestamp": "{{ $now.toJSON() }}"
      }
    }
    ```
5.  **Salida de Error (desde validación o lógica principal):** Nodo `n8n-nodes-base.set` (ej. "Error: Fechas Inválidas"). Prepara el JSON de respuesta de error:
    ```json
    {
      "status": "error",
      "data": {
        "code": "INVALID_DATE_RANGE",
        "text": "La fecha de inicio debe ser anterior a la fecha de fin.",
        "details": {
          "field_start": "{{ $json.Start }}",
          "field_end": "{{ $json.End }}",
          "condition": "Start < End"
        }
      },
      "meta": {
        "timestamp": "{{ $now.toJSON() }}"
      }
    }
    ```
    *(Nota: El ejemplo "Valida rango de fechas" usa `data.text` para el mensaje, así que se refleja aquí.)*
6.  **Fin del Subworkflow:** El subworkflow termina. Los datos preparados en el nodo `Set` de la rama ejecutada (éxito o error) son devueltos implícitamente al flujo llamador (al nodo `toolWorkflow`).

```mermaid
graph TD
    A[n8n-nodes-base.executeWorkflowTrigger <br> (Recibe: Start, End)] --> B{n8n-nodes-base.if <br> (Validar Fechas: Start < End?)};
    B -- TRUE (Válido) --> S_PREP[n8n-nodes-base.set <br> (Prepara JSON Éxito: status=success, data={message, dates}, meta)];
    S_PREP --> Z[Fin del Subworkflow <br> (Retorna JSON de S_PREP)];
    B -- FALSE (Inválido) --> E_PREP[n8n-nodes-base.set <br> (Prepara JSON Error: status=error, data={code, text, details}, meta)];
    E_PREP --> Z;
```

## Ejemplo de Flujo Principal (Servidor MCP)

El flujo principal utiliza un `@n8n/n8n-nodes-langchain.mcpTrigger` como punto de entrada.

1.  **MCP Server Trigger:** Nodo `@n8n/n8n-nodes-langchain.mcpTrigger`. Define el endpoint, y es donde el Agente AI (Langchain) envía las solicitudes para ejecutar herramientas.
2.  **Validación de Solicitud (Opcional, delegada a mcpTrigger):** El `mcpTrigger` maneja parte de la validación de la solicitud del agente.
3.  **Router/Dispatcher (Nodo Switch):** Un nodo `n8n-nodes-base.switch` dirige la ejecución basado en el nombre de la herramienta solicitada por el agente AI (ej. `{{ $json.tool_name }}`). Cada salida del `Switch` conecta a un nodo `@n8n/n8n-nodes-langchain.toolWorkflow` específico.
4.  **Llamada a Subworkflow (Herramienta):** El nodo `@n8n/n8n-nodes-langchain.toolWorkflow` es responsable de:
    *   Identificar el subworkflow a ejecutar (configurado en sus parámetros).
    *   Mapear las entradas para el subworkflow (ej. usando expresiones como `{{ $fromAI("user_id") }}` para tomar parámetros de la solicitud del agente AI).
    *   Ejecutar el subworkflow.
    *   Recibir la respuesta (JSON de éxito/error) del subworkflow.
5.  **Manejo de Respuesta del Subworkflow:** La salida del `toolWorkflow` (que es la salida del subworkflow) puede ser procesada adicionalmente si es necesario antes de ser devuelta al `mcpTrigger`.
6.  **Respuesta al Agente AI:** El `mcpTrigger` se encarga de enviar la respuesta de vuelta al agente AI.

## Consideraciones Generales

*   **Seguir convenciones de nombres:** Crucial para la legibilidad y el mantenimiento.
*   **Etiquetar y nombrar claramente cada herramienta:** El nombre de la herramienta se define en el nodo `@n8n/n8n-nodes-langchain.toolWorkflow`.
*   **Probar cada subworkflow de forma aislada:** Asegura que cada componente funciona correctamente antes de integrarlo.
*   **Versionar herramientas:** La descripción ATDF en el nodo `toolWorkflow` debe reflejar la versión de la herramienta/subworkflow que llama.
*   **Documentar cada versión:** Incluir cambios en la descripción ATDF.

## Integración del Formato ATDF (Automatic Tool Definition Format)

### Cómo Integrarlo
El bloque de descripción ATDF (en formato YAML) debe incluirse directamente en el **parámetro `description` del nodo `@n8n/n8n-nodes-langchain.toolWorkflow`** que llama al subworkflow correspondiente. Este nodo `toolWorkflow` actúa como la representación de la herramienta dentro del servidor MCP principal y es lo que el agente AI "ve".

### Campos Recomendados para ATDF
*   `description`: Descripción concisa de lo que hace la herramienta.
*   `how_to_use`: Detalles sobre cómo interactuar con la herramienta, incluyendo:
    *   `inputs`: Lista de parámetros de entrada (nombre, tipo, si es requerido, descripción).
    *   `outputs`: Descripción de la estructura de salida esperada (campos `status`, `data` con sus subcampos, `meta`).
*   `when_to_use`: Casos de uso o situaciones donde esta herramienta es apropiada.

### Ejemplo de Bloque ATDF (YAML)

Este bloque se colocaría en el campo "Description" de un nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que está configurado para llamar al subworkflow `SWF_Get_User_Profile`.

```yaml
---
description: Obtiene el perfil de un usuario a partir de su ID.
how_to_use:
  inputs:
    - name: user_id # Este 'name' es el que el Agente AI usará
      type: string
      required: true
      description: Identificador único del usuario.
  outputs:
    status: string (success/error)
    data: (si status es success)
      name: string
      email: string
    data: (si status es error)
      code: string
      text: string # o message, ser consistente
      details: object
    meta:
      timestamp: string (ISO 8601)
when_to_use: Cuando se requiere información detallada de un usuario específico.
---
```

## Uso de Subservidores MCP como Herramientas

Un servidor MCP (principal) puede utilizar herramientas expuestas por otros servidores MCP (subservidores) mediante el nodo `@n8n/n8n-nodes-langchain.mcpClient`.

### Configuración
*   En el flujo del servidor MCP principal, se utiliza un nodo `@n8n/n8n-nodes-langchain.mcpClient`.
*   Se configura el `sseEndpoint` del nodo `mcpClient` para que apunte a la URL del endpoint del `@n8n/n8n-nodes-langchain.mcpTrigger` del subservidor MCP.
*   Se pueden usar las opciones `includeTools` o `excludeTools` en el nodo `mcpClient` para filtrar qué herramientas del subservidor se quieren exponer o utilizar.
*   Las credenciales para acceder al subservidor se configuran en el nodo `mcpClient`.

### Ventajas
*   **Mayor Modularidad y Desacoplamiento.**
*   **Escalabilidad Independiente.**
*   **Equipos Diferentes.**
*   **Reutilización Segura.**

### Ejemplo Visual (Diagrama de Flujo)

```mermaid
flowchart LR
  A[Agente MCP Principal] --> B("@n8n/n8n-nodes-langchain.mcpClient");
  B -- sseEndpoint: http://github-mcp/sse --> C[Subservidor MCP GitHub (@mcpTrigger)];
  B -- sseEndpoint: http://docs-mcp/sse --> D[Subservidor MCP Documentación (@mcpTrigger)];
  B -- sseEndpoint: http://code-mcp/sse --> E[Subservidor MCP Código (@mcpTrigger)];
```
El nodo `mcpClient` (B) en el Agente MCP Principal se conecta a varios subservidores MCP (C, D, E), cada uno con su propio `@n8n/n8n-nodes-langchain.mcpTrigger`.

## Consideraciones sobre la Descripción de Herramientas Externas (vía MCP Client)

Cuando un servidor MCP principal utiliza herramientas de un subservidor MCP a través del nodo `@n8n/n8n-nodes-langchain.mcpClient`:

*   **Propagación de ATDF:** El `mcpClient` obtiene las descripciones ATDF de las herramientas directamente del `description` de los nodos `@n8n/n8n-nodes-langchain.toolWorkflow` (o equivalentes) en el subservidor.
*   **Visualización en el Cliente:** Si el subservidor MCP proporciona descripciones ATDF, el `mcpClient` las mostrará.
*   **Descripciones Genéricas:** Si el subservidor no proporciona ATDF, el `mcpClient` podría mostrar una descripción genérica.
*   **Inmutabilidad desde el Cliente:** Las descripciones de herramientas de subservidores no se pueden editar desde el `mcpClient`. La fuente es el subservidor.
*   **Interoperabilidad:** Este mecanismo asegura que el servidor principal consume las herramientas tal como las define y documenta el subservidor.
```
