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

## Preguntas Frecuentes (FAQ)

**1. ¿Qué pasa si un subworkflow (herramienta) falla inesperadamente?**
   - El nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que llama al subworkflow debería, idealmente, capturar este fallo.
   - Si el subworkflow está bien diseñado (según esta guía), debería devolver un JSON con `status: "error"` y detalles del error. El `toolWorkflow` pasará esta respuesta al `@n8n/n8n-nodes-langchain.mcpTrigger`.
   - Si el subworkflow falla de forma catastrófica (ej. un nodo crashea sin manejo de errores configurado con `onError`), el `toolWorkflow` podría recibir un error más genérico o fallar él mismo. Es importante configurar la opción "Settings" > "Error Workflow" en n8n para manejar errores no capturados a nivel de instancia o workflow.
   - Dentro del subworkflow, nodos críticos (como llamadas a APIs externas, ej. `Google Calendar`) deberían tener su propia gestión de errores (ej. usando la pestaña "Settings" > "Continue On Fail" o configurando un "Error Workflow" específico para ese nodo) para asegurar que se devuelve un JSON de error estándar en lugar de un crash abrupto.

**2. ¿Se puede tener un subworkflow que invoque a otro subworkflow?**
   - Sí, absolutamente. Esta es una práctica recomendada para la composición de herramientas y la reutilización de lógica.
   - Un subworkflow (ej. "Herramienta Compleja A") puede usar un nodo `n8n-nodes-base.executeWorkflow` para llamar a otro subworkflow más simple (ej. "Sub-Herramienta B").
   - El subworkflow llamador ("Herramienta Compleja A") debería manejar la respuesta (éxito o error) del subworkflow llamado ("Sub-Herramienta B") y luego formatear su propia respuesta estándar para el `toolWorkflow` que lo llamó originalmente. El ejemplo "Valida disponibilidad" que llama a "Valida rango de fechas" ilustra este patrón.

**3. ¿Cómo versionar correctamente los subworkflows y mantener compatibilidad?**
   - **Nomenclatura:** Incluir un número de versión en el nombre del subworkflow (ej. `SWF_MiHerramienta_v1`, `SWF_MiHerramienta_v2`).
   - **ATDF:** La descripción ATDF en el nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que llama al subworkflow debe reflejar claramente la versión de la herramienta que está exponiendo y los parámetros/salidas esperados para esa versión.
   - **Cambios no Rompientes:** Si añades nueva funcionalidad opcional o campos no obligatorios a la salida, puedes mantener la misma versión mayor y actualizar una menor (ej. v1.1). Asegúrate que la ATDF se actualice.
   - **Cambios Rompientes:** Si cambias nombres de parámetros, tipos de datos, eliminas campos de la salida, o cambias la lógica fundamental de una manera que no es compatible con versiones anteriores, debes crear una nueva versión del subworkflow (ej. `SWF_MiHerramienta_v2`). El flujo principal del servidor MCP debería entonces usar un nuevo nodo `@n8n/n8n-nodes-langchain.toolWorkflow` para exponer esta nueva versión (ej. `tool.mi_herramienta_v2`).
   - **Git:** Utiliza un sistema de control de versiones como Git para guardar las exportaciones JSON de tus workflows. Las ramas o tags pueden ayudar a gestionar las versiones.
   - **Deprecación:** Considera mantener versiones antiguas por un tiempo y marcarlas como deprecadas en su ATDF, indicando cuál es la nueva versión a utilizar.

## Pruebas y Depuración (Tests and Debugging)

**1. Pruebas de Subworkflows (Herramientas) de Forma Aislada**
   - **Entorno de Prueba:** Considera tener un workflow de n8n dedicado para probar tus subworkflows individualmente antes de integrarlos en el servidor MCP principal.
   - **Disparador Manual:** En este workflow de prueba, puedes usar un nodo `n8n-nodes-base.manualTrigger` (o simplemente el botón "Execute Workflow" con datos de entrada fijos si el subworkflow empieza con `n8n-nodes-base.executeWorkflowTrigger`) para iniciar la ejecución.
   - **Datos de Entrada:** Prepara un nodo `n8n-nodes-base.set` o `n8n-nodes-base.function` para simular los datos de entrada (parámetros) que el subworkflow esperaría recibir del nodo `@n8n/n8n-nodes-langchain.toolWorkflow`.
   - **Llamada al Subworkflow:** Utiliza un nodo `n8n-nodes-base.executeWorkflow` para llamar al subworkflow que quieres probar, pasando los datos de entrada simulados.
   - **Verificación de Salida:** Observa la salida del nodo `Execute Workflow`. Verifica que:
     - Para casos de éxito, el JSON de salida coincida con la estructura `{ "status": "success", "data": { ... }, "meta": { ... } }` definida.
     - Para casos de error conocidos (ej. parámetros inválidos), el JSON de salida sea `{ "status": "error", "data": { "code": "...", ... }, "meta": { ... } }`.
     - Los datos dentro de `data` y `meta` sean los correctos para cada caso de prueba.
   - **Casos de Prueba:** Diseña múltiples casos de prueba, incluyendo:
     - Entradas válidas (camino feliz).
     - Entradas inválidas (ej. campos faltantes, formatos incorrectos, valores fuera de rango).
     - Casos límite.
     - Errores esperados de servicios externos (si el subworkflow llama a otras APIs).

**2. Interpretación de Logs**
   - **Logs del `@n8n/n8n-nodes-langchain.mcpTrigger`:**
     - Mostrará la solicitud completa recibida del agente AI (Langchain), incluyendo el nombre de la herramienta y los parámetros.
     - Registrará la respuesta final enviada de vuelta al agente AI después de que el `toolWorkflow` y el subworkflow se hayan ejecutado.
     - Los errores que ocurran directamente en el `mcpTrigger` o si un `toolWorkflow` no devuelve una respuesta válida pueden aparecer aquí.
   - **Logs del `@n8n/n8n-nodes-langchain.toolWorkflow`:**
     - Mostrará los parámetros que recibió (potencialmente transformados desde la entrada del `mcpTrigger`, ej. por `$fromAI()`).
     - Indicará a qué subworkflow está llamando.
     - Registrará la respuesta JSON completa que recibió del subworkflow.
     - Si el `toolWorkflow` mismo falla (ej. no puede encontrar el subworkflow especificado, o hay un error en la configuración de mapeo de entradas), el error se verá en este nodo.
   - **Logs del Subworkflow (durante pruebas aisladas):**
     - Al probar con `Execute Workflow`, puedes ver los datos de entrada que recibió el subworkflow y la salida de cada nodo dentro de él. Esto es crucial para depurar la lógica interna.
     - Utiliza el panel de "Execution Log" en n8n para rastrear el flujo de datos y los errores en cada paso del subworkflow.

**3. Captura de Errores Silenciosos o Inesperados**
   - **Diseño Robusto de Subworkflows:** La causa más común de "errores silenciosos" (donde el agente AI no recibe una respuesta de error clara) es un subworkflow que no maneja todas sus rutas de error.
   - **Revisar Ramas de `IF`/`Switch`:** Asegúrate que todas las posibles ramas de tus nodos `IF` o `Switch` terminen en un nodo `Set` que produzca la estructura de salida estándar (éxito o error). Si una rama no produce una salida JSON válida, el `toolWorkflow` podría no saber qué responder.
   - **Manejo de Errores en Nodos Críticos:** Para nodos que pueden fallar (ej. `HTTP Request`, `Google Calendar`, o cualquier nodo que llame a un servicio externo):
     - Utiliza la pestaña "Settings" > "Continue On Fail" (si aplica y quieres manejar el error manualmente después) o configura un "Error Workflow" para ese nodo.
     - Si usas "Continue On Fail", el siguiente nodo debe ser un `IF` que verifique si el nodo anterior produjo un error (usualmente `$json.error` estará presente). Si hay error, redirige a un `Set` para formatear el error estándar.
   - **Error Workflow Global de n8n:** Configura un "Error Workflow" global en la configuración de tu instancia de n8n. Este workflow se ejecutará si cualquier ejecución de workflow falla de manera no controlada, permitiéndote loguear el error o notificar a los administradores. Esto es un último recurso pero útil para errores completamente inesperados.
   - **Validación de Salida del Subworkflow (Avanzado):** En el flujo principal, después del nodo `@n8n/n8n-nodes-langchain.toolWorkflow`, podrías añadir un nodo `IF` o `Function` para verificar si la respuesta recibida del subworkflow es estructuralmente válida (ej. tiene un campo `status` que es `success` o `error`). Si no, podrías forzar una respuesta de error genérica. (Ver sección "Manejo de Errores Globales en el Flujo Principal").

## Guía de Exportación/Importación y Versionado con Git

**1. Exportación e Importación de Workflows en n8n**
   - **Formato de Exportación:** n8n permite exportar workflows en formato JSON.
     - Para exportar un workflow, abre el workflow, haz clic en el menú de tres puntos (⋮) en la esquina superior derecha y selecciona "Download".
     - Se recomienda guardar el JSON **no compactado (unminified/pretty-printed)**. Aunque el archivo es más grande, es mucho más fácil de leer y revisar diferencias (diffs) en Git. Si n8n exporta por defecto en formato compacto, puedes usar herramientas externas (como `jq` en la línea de comandos o un editor de código) para "prettify" el JSON antes de confirmarlo en Git: `jq . workflow_compacto.json > workflow_legible.json`.
   - **Importación:** Para importar un workflow, desde la pantalla principal de Workflows en n8n, haz clic en "New" y luego selecciona "Import from file" (o "Import from URL" si el JSON está hosteado).

**2. Estrategia de Versionado con Git**
   - **Beneficios de Git:**
     - **Historial de Cambios:** Rastrea cada cambio realizado a tus workflows.
     - **Colaboración:** Permite a múltiples desarrolladores trabajar en los mismos workflows.
     - **Ramificación (Branching):** Desarrolla nuevas funcionalidades o corrige errores en ramas separadas sin afectar la versión principal.
     - **Reversión:** Facilita volver a versiones anteriores si algo sale mal.
     - **Revisión de Código:** Permite revisar los cambios (diffs en el JSON) antes de fusionarlos.
   - **¿Qué incluir en el Repositorio?**
     - Los archivos JSON exportados de tus workflows de n8n.
     - Potencialmente, scripts de utilidad (ej. para formatear JSON, para despliegues).
     - Documentación adicional si no está toda dentro de los ATDF de los nodos.

**3. Organización del Repositorio (Sugerencias)**
   - No hay una única forma correcta, pero aquí algunas estructuras comunes:
     - **Por Tipo de Workflow:**
       ```
       /repository-root
       ├── mcp_servers/
       │   ├── auth_server_main.json
       │   └── user_management_server_main.json
       ├── tools/  (o subworkflows/)
       │   ├── SWF_GetUserProfile_v1.json
       │   ├── SWF_UpdateUserProfile_v1.json
       │   ├── SWF_ValidateDateRange_v1.json
       ├── utilities/ (subworkflows no expuestos como herramientas directas)
       │   └── SWF_FormatAddress_v1.json
       └── README.md
       ```
     - **Por Dominio o Proyecto:**
       ```
       /repository-root
       ├── project_alpha/
       │   ├── mcp_server_alpha.json
       │   ├── tools/
       │   │   └── SWF_AlphaTool1_v1.json
       │   └── subworkflows_internal/
       │       └── SWF_AlphaHelper_v1.json
       ├── project_beta/
       │   ├── mcp_server_beta.json
       │   └── tools/
       │       └── SWF_BetaTool1_v1.json
       └── shared_tools/
           └── SWF_CommonUtil_v1.json
       ```
   - **Consistencia:** Elige una estructura y sé consistente.
   - **Nombres de Archivos:** Usa nombres de archivo descriptivos, idealmente incluyendo el nombre del workflow y su versión (ej. `SWF_GetUserProfile_v2.json`). Esto ayuda incluso antes de abrir el archivo.
   - **Archivos `.gitattributes` (Avanzado):** Para mejorar los diffs de JSON en Git, puedes añadir un archivo `.gitattributes` en la raíz de tu repositorio con el siguiente contenido para que Git trate los JSON de manera más inteligente para los diffs (puede requerir configuración adicional o no ser soportado por todas las interfaces de Git):
     ```
     *.json diff=json
     ```

**4. Flujo de Trabajo Básico con Git**
   - **Clonar:** `git clone <url_repositorio>`
   - **Crear Rama:** `git checkout -b mi_nueva_funcionalidad`
   - **Modificar Workflows:** Haz cambios en n8n, exporta el JSON, reemplaza el archivo antiguo en tu copia local del repositorio.
   - **Revisar Cambios:** `git diff nombre_workflow.json` (para ver qué cambió en el JSON).
   - **Añadir y Confirmar:**
     ```bash
     git add nombre_workflow.json
     git commit -m "feat: Añadida validación de entrada a SWF_GetUserProfile_v1"
     ```
     (Sigue una convención para los mensajes de commit, ej. Conventional Commits).
   - **Empujar Cambios:** `git push origin mi_nueva_funcionalidad`
   - **Pull Request / Merge:** Crea un Pull Request (o Merge Request) en tu plataforma Git (GitHub, GitLab, etc.) para fusionar los cambios a la rama principal (ej. `main` o `develop`).

## Uso de Etiquetas (Tags) en los Workflows de n8n

**1. Beneficios del Uso de Etiquetas**
   - En entornos de n8n con una gran cantidad de workflows, las etiquetas (tags) son una herramienta poderosa para organizar, filtrar y encontrar workflows rápidamente.
   - Permiten categorizar los workflows por diversos criterios, como su función, estado, versión, o el proyecto al que pertenecen.
   - Facilitan la gestión y el mantenimiento, especialmente en equipos grandes o con múltiples proyectos.

**2. Cómo Usar Etiquetas en n8n**
   - Para añadir o editar etiquetas de un workflow, puedes hacerlo desde la vista de lista de workflows:
     - Pasa el cursor sobre el workflow.
     - Haz clic en el icono de etiqueta (tag) que aparece.
     - Escribe el nombre de la etiqueta y presiona Enter. Puedes añadir múltiples etiquetas.
   - También puedes gestionar etiquetas al editar un workflow, usualmente en un panel de configuración del workflow mismo (la ubicación exacta puede variar ligeramente con versiones de n8n).

**3. Estrategias de Etiquetado Sugeridas para Servidores MCP y Herramientas**
   - **Tipo de Workflow:**
     - `mcp-server`: Para el workflow principal que actúa como servidor MCP (el que contiene el `@n8n/n8n-nodes-langchain.mcpTrigger`).
     - `mcp-tool`: Para subworkflows que representan una herramienta específica y son llamados por un `@n8n/n8n-nodes-langchain.toolWorkflow`.
     - `subworkflow-helper`: Para subworkflows internos que no son herramientas directas pero son reutilizados por otros (ej. una utilidad de formato).
   - **Dominio/Funcionalidad de la Herramienta:**
     - `tool:user-management`
     - `tool:document-processing`
     - `tool:calendar-operations`
     - `module:authentication`
   - **Versión:**
     - `v1.0`
     - `v1.1`
     - `v2.0-beta`
     - `tool-version:1.2` (si quieres ser más específico para diferenciar de la versión del servidor MCP)
   - **Estado:**
     - `status:active`
     - `status:development`
     - `status:deprecated` (para herramientas o servidores que serán reemplazados)
     - `status:experimental`
   - **Proyecto o Cliente (si aplica):**
     - `project:alpha`
     - `client:acme-corp`
   - **Prioridad o Criticidad (opcional):**
     - `priority:high`
     - `critical`

**4. Ejemplos Combinados**
   - Un workflow servidor MCP para usuarios podría tener las etiquetas: `mcp-server`, `module:user-management`, `v1.0`, `status:active`.
   - Un subworkflow que es una herramienta para obtener perfiles de usuario: `mcp-tool`, `tool:user-management`, `tool-version:1.0`, `status:active`.
   - Un subworkflow de utilidad para validar fechas usado por varias herramientas: `subworkflow-helper`, `module:utils`, `v1.0`, `status:active`.

**5. Filtrado por Etiquetas**
   - En la vista de lista de workflows de n8n, usualmente hay una barra de búsqueda o un control de filtro que permite escribir nombres de etiquetas para mostrar solo los workflows que las contengan. Esto agiliza enormemente la localización de workflows específicos.

**Recomendación:** Define una convención de etiquetado para tu equipo u organización y sé consistente en su aplicación. Un buen sistema de etiquetado es invaluable a medida que tu instancia de n8n crece.

## Manejo de Errores Globales en el Flujo Principal del Servidor MCP

**1. Importancia del Manejo de Errores a Nivel del Servidor Principal**
   - Aunque cada subworkflow (herramienta) debe ser responsable de manejar sus propios errores y devolver una respuesta estándar, el flujo principal del servidor MCP también debe estar preparado para ciertos tipos de fallos.
   - Esto asegura que el agente AI que consume el servidor MCP reciba una respuesta coherente incluso si ocurren problemas inesperados en la orquestación de las herramientas.

**2. Escenarios de Error en el Flujo Principal y Cómo Manejarlos**

   **a. Fallo del Nodo `@n8n/n8n-nodes-langchain.toolWorkflow`**
      - **Causa Posible:** El subworkflow especificado en el nodo `toolWorkflow` no existe (ej. ID incorrecto, no importado), o hay un problema crítico con la configuración del propio nodo `toolWorkflow` que impide que siquiera intente ejecutar el subworkflow.
      - **Manejo:**
        - Configurar la pestaña "Settings" > "Error Workflow" para el nodo `@n8n/n8n-nodes-langchain.toolWorkflow`. Este workflow de error dedicado puede entonces generar una respuesta JSON estándar (ej. con `status: "error"`, `data.code: "TOOL_EXECUTION_FAILED"`, y un mensaje apropiado) que se devuelve al flujo principal.
        - Alternativamente, si no se usa un "Error Workflow" para el nodo, el flujo principal podría detenerse. Por ello, tener un "Error Workflow" a nivel de la instancia de n8n (global) es un buen seguro.

   **b. Subworkflow Devuelve una Respuesta Estructuralmente Inválida**
      - **Causa Posible:** Un subworkflow (herramienta) termina y devuelve datos, pero estos no se ajustan al formato esperado (ej. falta el campo `status`, o `status` no es ni `"success"` ni `"error"`).
      - **Manejo:**
        - Después de cada nodo `@n8n/n8n-nodes-langchain.toolWorkflow` en el flujo principal (o después de un nodo `Switch` que enruta a varios `toolWorkflows`), añadir un nodo `n8n-nodes-base.if` para validar la estructura de la respuesta.
        - **Condiciones del `IF`:**
          - Verificar si el campo `status` existe.
          - Verificar si `status` es igual a `"success"` O `status` es igual a `"error"`.
        - **Rama FALSE del `IF` (Respuesta Inválida):**
          - Conectar a un nodo `n8n-nodes-base.set` que construya una respuesta de error estándar.
          - Ejemplo de JSON de error:
            ```json
            {
              "status": "error",
              "data": {
                "code": "INVALID_TOOL_RESPONSE_STRUCTURE",
                "message": "La herramienta devolvió una respuesta con una estructura inesperada.",
                "details": {
                  "tool_name": "{{ $json.tool_name_if_available }}", // Nombre de la herramienta que falló
                  "received_response_preview": "{{ JSON.stringify($json).slice(0, 200) }}" // Un preview de lo que se recibió
                }
              },
              "meta": {
                "timestamp": "{{ $now.toJSON() }}"
              }
            }
            ```
        - **Rama TRUE del `IF` (Respuesta Válida):**
          - Continuar el flujo normalmente (esta es la respuesta del subworkflow que se pasará al `mcpTrigger`).

   **c. Error en el Router (ej. Nodo `Switch`)**
      - **Causa Posible:** El nombre de la herramienta proporcionado por el agente AI no coincide con ninguna de las rutas definidas en el nodo `Switch`.
      - **Manejo:**
        - El nodo `Switch` en n8n tiene una salida "Default" o "Fallback". Conectar esta salida a un nodo `n8n-nodes-base.set`.
        - Este nodo `Set` debe generar una respuesta de error estándar indicando que la herramienta no fue encontrada.
        - Ejemplo de JSON de error:
          ```json
          {
            "status": "error",
            "data": {
              "code": "TOOL_NOT_FOUND",
              "message": "La herramienta solicitada no está disponible o no es reconocida.",
              "details": {
                "requested_tool_name": "{{ $json.tool_name_from_ai_if_available }}"
              }
            },
            "meta": {
              "timestamp": "{{ $now.toJSON() }}"
            }
          }
          ```

**3. Consideraciones Adicionales**
   - **Consistencia:** Asegúrate que todos los errores generados por el flujo principal también sigan el formato JSON estándar.
   - **Logging:** Considera añadir nodos de log (ej. `n8n-nodes-base.logMessage`) en estas rutas de error globales para facilitar la depuración de problemas a nivel de orquestación.
   - **Error Workflow Global de n8n:** Como se mencionó antes, tener un Error Workflow configurado a nivel de instancia en n8n (accesible desde "Settings") es una red de seguridad crucial para capturar cualquier error no manejado en ninguno de tus workflows.

Un manejo de errores robusto a nivel del flujo principal del servidor MCP complementa el manejo de errores dentro de cada subworkflow, creando un sistema más resiliente y predecible.
```
