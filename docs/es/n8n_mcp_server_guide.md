# Índice

- [Guía del Servidor MCP de n8n](#guía-del-servidor-mcp-de-n8n)
- [Introducción y objetivos](#introducción-y-objetivos)
- [Conceptos básicos](#conceptos-básicos)
  - [MCP Server Trigger](#mcp-server-trigger)
  - [Subworkflows](#subworkflows)
  - [toolWorkflow Node](#toolworkflow-node)
- [Buenas prácticas MCP](#buenas-prácticas-mcp)
  - [Arquitectura](#arquitectura)
  - [Naming (Convenciones de Nombres)](#naming-convenciones-de-nombres)
  - [Salida estándar](#salida-estándar)
  - [Validación](#validación)
  - [Seguridad](#seguridad)
  - [Documentación](#documentación)
  - [Versionado](#versionado)
  - [Principios Clave para la Robustez de Flujos de Trabajo](#principios-clave-para-la-robustez-de-flujos-de-trabajo)
- [Arquitectura General](#arquitectura-general)
  - [Estructura Básica](#estructura-básica)
  - [Ventajas del Uso de Subworkflows](#ventajas-del-uso-de-subworkflows)
- [Diseño de Herramientas MCP (Subworkflows)](#diseño-de-herramientas-mcp-subworkflows)
  - [Formato Estándar de Salida](#formato-estándar-de-salida)
  - [Validación de Entradas y Errores Uniformes](#validación-de-entradas-y-errores-uniformes)
- [Plantilla Base Visual para Subworkflows (Herramientas)](#plantilla-base-visual-para-subworkflows-herramientas)
- [Ejemplo de Flujo Principal (Servidor MCP)](#ejemplo-de-flujo-principal-servidor-mcp)
- [Consideraciones Generales](#consideraciones-generales)
- [Integración del Formato ATDF (Automatic Tool Definition Format)](#integración-del-formato-atdf-automatic-tool-definition-format)
  - [Cómo Integrarlo](#cómo-integrarlo)
  - [Campos Recomendados para ATDF](#campos-recomendados-para-atdf)
  - [Ejemplo de Bloque ATDF (YAML)](#ejemplo-de-bloque-atdf-yaml)
- [Uso de Subservidores MCP como Herramientas](#uso-de-subservidores-mcp-como-herramientas)
  - [Configuración](#configuración)
  - [Ventajas](#ventajas)
  - [Ejemplo Visual (Diagrama de Flujo)](#ejemplo-visual-diagrama-de-flujo)
- [Consideraciones sobre la Descripción de Herramientas Externas (vía MCP Client)](#consideraciones-sobre-la-descripción-de-herramientas-externas-vía-mcp-client)
- [Preguntas Frecuentes (FAQ)](#preguntas-frecuentes-faq)
- [Pruebas y Depuración](#pruebas-y-depuración)
- [Guía de Exportación/Importación y Versionado con Git](#guía-de-exportaciónimportación-y-versionado-con-git)
- [Uso de Etiquetas (Tags) en los Workflows de n8n](#uso-de-etiquetas-tags-en-los-workflows-de-n8n)
- [Manejo de Errores Globales en el Flujo Principal del Servidor MCP](#manejo-de-errores-globales-en-el-flujo-principal-del-servidor-mcp)

# Guía del Servidor MCP de n8n

## Introducción y objetivos

Esta guía describe las mejores prácticas y la arquitectura para construir y mantener Servidores de Procesos Comunes (MCP) utilizando n8n. El objetivo es promover la modularidad, la reutilización y la mantenibilidad de los flujos de trabajo.

## Conceptos básicos

### MCP Server Trigger
El **MCP Server Trigger** (tipo de nodo: `@n8n/n8n-nodes-langchain.mcpTrigger`) es un nodo especializado en n8n que actúa como punto de entrada para las solicitudes al servidor MCP. Permite definir la interfaz de entrada y salida del servidor, y es el que recibe las peticiones externas para ejecutar una o varias herramientas.

### Subworkflows
Los **Subworkflows** (flujos de trabajo secundarios) son flujos de trabajo de n8n que se pueden llamar desde otros flujos de trabajo. Son fundamentales para la modularidad en la arquitectura MCP, permitiendo encapsular lógica específica en unidades reutilizables. Estos subworkflows implementan la lógica de una herramienta específica.

### toolWorkflow Node
El nodo **toolWorkflow** (tipo de nodo: `@n8n/n8n-nodes-langchain.toolWorkflow`) es utilizado en el flujo principal del servidor MCP para llamar a un subworkflow (herramienta). Actúa como un puente, configurando cómo se llama al subworkflow y cómo se mapean sus entradas y salidas. La descripción ATDF de la herramienta se coloca en este nodo.

## Buenas prácticas MCP

### Arquitectura
*   Diseñar una arquitectura modular utilizando subworkflows para cada herramienta o proceso discreto.
*   El servidor MCP principal utiliza un `@n8n/n8n-nodes-langchain.mcpTrigger` y llama a los subworkflows (herramientas) mediante nodos `@n8n/n8n-nodes-langchain.toolWorkflow`.

### Naming (Convenciones de Nombres)
*   Utilizar nombres claros y consistentes para flujos de trabajo, subworkflows, nodos y variables.
*   Prefijar los subworkflows con `SWF_` para identificarlos fácilmente (ej. `SWF_Valida_Rango_Fechas`).
*   Prefijar las variables de entorno con `ENV_`.
*   Utilizar snake_case para nombres de variables y parámetros.
*   Para nombres de herramientas (configurados en el nodo `toolWorkflow`), seguir el formato: `tool.<acción>_<entidad>` (ej. `tool.get_user`, `tool.create_invoice`).

### Salida estándar
*   Definir un formato de salida estándar para todos los subworkflows (herramientas), tanto para respuestas exitosas como para errores. El campo `status` debe ser estrictamente `"success"` o `"error"`. (Ver "Diseño de Herramientas MCP > Formato Estándar de Salida").

### Validación
*   Validar las entradas en cada subworkflow para asegurar la integridad de los datos.
*   Proporcionar mensajes de error claros y uniformes siguiendo el formato de error estándar. (Ver "Diseño de Herramientas MCP > Validación de Entradas y Errores Uniformes").

### Seguridad
*   Proteger los endpoints del `@n8n/n8n-nodes-langchain.mcpTrigger` utilizando mecanismos de autenticación y autorización de n8n.
*   Gestionar las credenciales de forma segura utilizando el gestor de credenciales de n8n.
*   Evitar exponer información sensible en los logs.

### Documentación
*   Documentar cada herramienta (subworkflow) incluyendo su propósito, parámetros de entrada, formato de salida y cualquier dependencia. El bloque ATDF se incluye en la descripción del nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que lo llama.
*   Mantener actualizada la documentación de la arquitectura general del MCP.

### Versionado
*   Versionar los subworkflows y el servidor MCP para gestionar los cambios y evitar romper integraciones existentes.
*   Utilizar un sistema de control de versiones como Git para el versionado de los flujos de trabajo exportados. (Ver "Guía de Exportación/Importación y Versionado con Git").

### Principios Clave para la Robustez de Flujos de Trabajo
Para asegurar que los servidores MCP y sus herramientas (subworkflows) sean confiables y fáciles de depurar, se deben seguir estos principios fundamentales:
1.  **Adherencia al Formato de Salida Estándar:** Todo subworkflow (herramienta) debe devolver consistentemente el [Formato Estándar de Salida](#formato-estándar-de-salida) JSON, ya sea para éxito (`status: "success"`) o error (`status: "error"`), incluyendo los campos `data` y `meta` apropiados.
2.  **Validación Exhaustiva de Entradas:** Cada subworkflow debe validar rigurosamente sus parámetros de entrada al inicio. Ver la sección [Validación de Entradas y Errores Uniformes](#validación-de-entradas-y-errores-uniformes).
3.  **Manejo Explícito de Errores en Nodos Críticos:** Para nodos que realizan operaciones susceptibles a fallos (ej., llamadas a API externas con `HTTP Request`, interacciones con servicios como `Google Calendar`), configurar explícitamente el manejo de errores. Esto se puede hacer usando la opción "Configuración" > "Continue On Fail" en el nodo, seguido de un nodo `IF` para verificar si `$json.error` existe y así dirigir el flujo a la preparación de una respuesta de error estándar. Alternativamente, se puede usar la opción "Error Workflow" del nodo para dirigir el fallo a un flujo de trabajo de manejo de errores dedicado.
4.  **Cobertura de Todas las Rutas Lógicas:** Asegurar que todas las ramas posibles dentro de un flujo de trabajo (ej., en nodos `IF` o `Switch`) terminen explícitamente en un nodo que genere una salida estándar (éxito o error). Evitar "caminos muertos" donde una rama no produce una respuesta formateada, lo que podría llevar a errores silenciosos o respuestas inesperadas.
5.  **Uso Estratégico de "Error Workflows" de n8n:**
    *   **Nivel de Nodo:** Para nodos críticos o complejos como `@n8n/n8n-nodes-langchain.toolWorkflow`, configurar un "Error Workflow" específico en la pestaña "Configuración" del nodo puede proporcionar un manejo de fallos granular.
    *   **Nivel de Instancia (Global):** Configurar un "Error Workflow" global para la instancia de n8n (desde "Settings" / "Configuración" de n8n) sirve como una red de seguridad final para capturar y manejar cualquier error no controlado que pueda ocurrir en cualquier flujo de trabajo.
6.  **Registro (Logging) Significativo:** Implementar el registro de eventos importantes, parámetros de entrada clave y errores en puntos críticos de los flujos de trabajo. Utilizar el nodo `n8n-nodes-base.logMessage` o herramientas de observabilidad externas. Esto es crucial para la depuración y el monitoreo. (Ver "Pruebas y Depuración > Interpretación de Logs").

El cumplimiento de estos principios es fundamental y se detalla o ejemplifica en secciones posteriores como [Pruebas y Depuración](#pruebas-y-depuración) y [Manejo de Errores Globales en el Flujo Principal del Servidor MCP](#manejo-de-errores-globales-en-el-flujo-principal-del-servidor-mcp).

## Arquitectura General

### Estructura Básica
La arquitectura MCP se basa en un flujo principal (el servidor MCP) que utiliza un `@n8n/n8n-nodes-langchain.mcpTrigger` como punto de entrada. Este flujo orquesta la ejecución de subworkflows (herramientas) a través de nodos `@n8n/n8n-nodes-langchain.toolWorkflow`.

```mermaid
graph TD
    A[@n8n/n8n-nodes-langchain.mcpTrigger] --> B{Nodo Switch (Enrutador basado en nombre de herramienta del Agente AI)};
    B -- tool_A_name --> C1["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Tool_A)"];
    B -- tool_B_name --> C2["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Tool_B)"];
    C1 --> D[Manejo de Respuesta / Preparación para Agente AI];
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
*(Preferir `message` o `text` consistentemente. Si los ejemplos usan `text`, usar `text`. Asegurar que los códigos de error como `CODIGO_ERROR_UNICO` estén en mayúsculas y entre acentos graves si se referencian en texto.)*.

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
*   Utilizar códigos de error únicos y descriptivos (ej. `VALIDATION_ERROR`) para facilitar la depuración y el monitoreo.

## Plantilla Base Visual para Subworkflows (Herramientas)

Los subworkflows que actúan como herramientas son típicamente iniciados por un `n8n-nodes-base.executeWorkflowTrigger` (activador de ejecución de flujo de trabajo) cuando son llamados desde el flujo principal (a través de un `@n8n/n8n-nodes-langchain.toolWorkflow`). Es crucial seguir los [Principios Clave para la Robustez de Flujos de Trabajo](#principios-clave-para-la-robustez-de-flujos-de-trabajo) al diseñar estas plantillas.

**Ejemplo: Subworkflow "SWF_Valida_Rango_Fechas"**

1.  **Inicio (Activador):** Nodo `n8n-nodes-base.executeWorkflowTrigger`. Recibe parámetros como `Start` (fecha inicio) y `End` (fecha fin) desde el nodo `toolWorkflow` en el flujo principal.
2.  **Validación de Entradas:** Nodo `n8n-nodes-base.if` (ej. "Validar fechas"). Verifica si las fechas son válidas, si `Start` es anterior a `End`, etc. (Principio de Robustez #2).
    *   Si la validación falla, una rama (FALSE) lleva a un nodo `n8n-nodes-base.set` (ej. "Error: Fechas Inválidas") para construir el JSON de error estándar (Principio de Robustez #1).
3.  **Lógica Principal (si la validación es correcta):** Puede incluir otros nodos para procesar las fechas si es necesario. En este ejemplo, la validación en sí misma es la lógica principal.
4.  **Salida Exitosa:** Nodo `n8n-nodes-base.set` (ej. "Success: Rango Válido"). Prepara el JSON de respuesta exitosa estándar (Principio de Robustez #1).
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
5.  **Salida de Error (desde validación o lógica principal):** Nodo `n8n-nodes-base.set` (ej. "Error: Fechas Inválidas"). Prepara el JSON de respuesta de error estándar (Principio de Robustez #1).
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
    *(Nota: El ejemplo "Valida rango de fechas" usa `data.text` para el mensaje, así que se refleja aquí. El código de error `INVALID_DATE_RANGE` está en mayúsculas.)*
6.  **Fin del Subworkflow:** El subworkflow termina. Los datos preparados en el nodo `Set` de la rama ejecutada (éxito o error) son devueltos implícitamente al flujo llamador (al nodo `toolWorkflow`). Asegurar cobertura de todas las rutas lógicas (Principio de Robustez #4).

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
3.  **Router/Dispatcher (Nodo Switch):** Un nodo `n8n-nodes-base.switch` dirige la ejecución basado en el nombre de la herramienta solicitada por el agente AI (ej. `{{ $json.tool_name }}`). Cada salida del `Switch` conecta a un nodo `@n8n/n8n-nodes-langchain.toolWorkflow` específico. (Ver "Manejo de Errores Globales" para errores de enrutamiento).
4.  **Llamada a Subworkflow (Herramienta):** El nodo `@n8n/n8n-nodes-langchain.toolWorkflow` es responsable de:
    *   Identificar el subworkflow a ejecutar (configurado en sus parámetros).
    *   Mapear las entradas para el subworkflow (ej. usando expresiones como `{{ $fromAI("user_id") }}` para tomar parámetros de la solicitud del agente AI).
    *   Ejecutar el subworkflow.
    *   Recibir la respuesta (JSON de éxito/error) del subworkflow. (Ver "Manejo de Errores Globales" para fallos del `toolWorkflow` o respuestas inválidas).
5.  **Manejo de Respuesta del Subworkflow:** La salida del `toolWorkflow` (que es la salida del subworkflow) puede ser procesada adicionalmente si es necesario antes de ser devuelta al `mcpTrigger`.
6.  **Respuesta al Agente AI:** El `mcpTrigger` se encarga de enviar la respuesta de vuelta al agente AI.

## Consideraciones Generales

*   **Seguir convenciones de nombres:** Crucial para la legibilidad y el mantenimiento.
*   **Etiquetar y nombrar claramente cada herramienta:** El nombre de la herramienta se define en el nodo `@n8n/n8n-nodes-langchain.toolWorkflow`.
*   **Probar cada subworkflow de forma aislada:** Asegura que cada componente funciona correctamente antes de integrarlo. (Ver "Pruebas y Depuración").
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

### Mini-Plantilla ATDF Comentada (YAML)

```yaml
---
# Nombre descriptivo de la herramienta, visible para el agente AI.
# name: tool.mi_accion.mi_entidad
# (El 'name' suele ser manejado por el MCP Trigger o ToolWorkflow,
#  esta sección ATDF va en el campo 'description' de ese nodo)

# Descripción concisa de lo que hace la herramienta.
description: Realiza una acción específica sobre una entidad.

# Instrucciones sobre cómo usar la herramienta, incluyendo entradas y salidas.
how_to_use:
  inputs:
    # Lista de parámetros de entrada que la herramienta espera.
    - name: parametro_requerido
      type: string # Tipos comunes: string, number, boolean, object, array
      required: true # true si el parámetro es obligatorio, false si es opcional.
      description: Descripción detallada de este parámetro y su propósito.
                  # Incluir ejemplos de valores si es útil.
    - name: parametro_opcional
      type: number
      required: false
      description: Parámetro que no es estrictamente necesario.
      default: 10 # Valor por defecto si no se provee (informativo para el ATDF).

  outputs:
    # Descripción de la estructura de salida que la herramienta devuelve.
    # Esto debe alinearse con el Formato Estándar de Salida de la guía.
    status: string # Siempre "success" o "error".
    data: object # Contenedor para los datos de la respuesta.
      # Sub-campos de 'data' si status es "success":
      # resultado_exito: string
      # otro_dato: number
      # Sub-campos de 'data' si status es "error":
      # code: string
      # message: string (o text)
      # details: object (con campos field, expected, solution)
    meta: object # Metadatos de la respuesta.
      # timestamp: string # Fecha y hora en formato ISO 8601.

# Cuándo se debe usar esta herramienta. Describe los casos de uso apropiados.
when_to_use: Ideal para cuando se necesita [describir el escenario de uso].
             No usar si [describir contraindicaciones o alternativas].
---
```

### Validación de la Sintaxis ATDF (YAML)
El ATDF se escribe en YAML. Para asegurar que la sintaxis de tu descripción ATDF es correcta antes de pegarla en el campo de descripción de un nodo n8n, es muy recomendable validarla. Puedes usar:
- **Editores de Código Modernos:** Muchos editores como VS Code (con extensiones para YAML) resaltan errores de sintaxis YAML en tiempo real.
- **Linters de YAML en Línea:** Existen numerosas herramientas web donde puedes pegar tu YAML para verificar su validez (busca "yaml linter online").
- **Integración Continua (CI):** En un entorno de desarrollo más avanzado con Git, puedes integrar un linter de YAML en tu proceso de CI/CD para automáticamente verificar los archivos ATDF si los gestionas como archivos separados antes de copiarlos a n8n.

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
   - Un subworkflow bien diseñado, siguiendo los [Principios Clave para la Robustez](#principios-clave-para-la-robustez-de-flujos-de-trabajo), devolverá un JSON de error estándar.
   - Si el subworkflow falla catastróficamente (un nodo crashea sin aplicar el Principio de Robustez #3 o #4), el `toolWorkflow` podría recibir un error genérico. En este caso, es crucial el Principio de Robustez #5 (uso de "Error Workflows" de nodo o globales).
   - Para nodos críticos dentro del subworkflow (ej. llamadas a APIs externas), se debe aplicar el Principio de Robustez #3.

**2. ¿Se puede tener un subworkflow que invoque a otro subworkflow?**
   - Sí, absolutamente. Esta es una práctica recomendada para la composición de herramientas y la reutilización de lógica.
   - Un subworkflow (ej. "Herramienta Compleja A") puede usar un nodo `n8n-nodes-base.executeWorkflow` para llamar a otro subworkflow más simple (ej. "Sub-Herramienta B").
   - El subworkflow llamador ("Herramienta Compleja A") debería manejar la respuesta (éxito o error) del subworkflow llamado ("Sub-Herramienta B") y luego formatear su propia respuesta estándar (Principio de Robustez #1) para el `toolWorkflow` que lo llamó originalmente. El ejemplo "Valida disponibilidad" que llama a "Valida rango de fechas" ilustra este patrón.

**3. ¿Cómo versionar correctamente los subworkflows y mantener compatibilidad?**
   - **Nomenclatura:** Incluir un número de versión en el nombre del subworkflow (ej. `SWF_MiHerramienta_v1`, `SWF_MiHerramienta_v2`).
   - **ATDF:** La descripción ATDF en el nodo `@n8n/n8n-nodes-langchain.toolWorkflow` que llama al subworkflow debe reflejar claramente la versión de la herramienta que está exponiendo y los parámetros/salidas esperados para esa versión. Cualquier desviación debe ser considerada un error por el subworkflow (Principio de Robustez #2).
   - **Cambios no Rompientes:** Si añades nueva funcionalidad opcional o campos no obligatorios a la salida, puedes mantener la misma versión mayor y actualizar una menor (ej. v1.1). Asegúrate que la ATDF se actualice.
   - **Cambios Rompientes:** Si cambias nombres de parámetros, tipos de datos, eliminas campos de la salida, o cambias la lógica fundamental de una manera que no es compatible con versiones anteriores, debes crear una nueva versión del subworkflow (ej. `SWF_MiHerramienta_v2`). El flujo principal del servidor MCP debería entonces usar un nuevo nodo `@n8n/n8n-nodes-langchain.toolWorkflow` para exponer esta nueva versión (ej. `tool.mi_herramienta_v2`).
   - **Git:** Utiliza un sistema de control de versiones como Git para guardar las exportaciones JSON de tus flujos de trabajo. Las ramas o `tags` pueden ayudar a gestionar las versiones.
   - **Deprecación:** Considera mantener versiones antiguas por un tiempo y marcarlas como deprecadas en su ATDF, indicando cuál es la nueva versión a utilizar.

## Pruebas y Depuración

Esta sección se enfoca en cómo verificar la implementación de los [Principios Clave para la Robustez de Flujos de Trabajo](#principios-clave-para-la-robustez-de-flujos-de-trabajo) y depurar problemas.

**1. Pruebas de Subworkflows (Herramientas) de Forma Aislada**
   - **Entorno de Prueba:** Considera tener un flujo de trabajo de n8n dedicado para probar tus subworkflows individualmente antes de integrarlos en el servidor MCP principal.
   - **Activador Manual:** En este flujo de trabajo de prueba, puedes usar un nodo `n8n-nodes-base.manualTrigger` (o simplemente el botón "Execute Workflow" con datos de entrada fijos si el subworkflow empieza con `n8n-nodes-base.executeWorkflowTrigger`) para iniciar la ejecución.
   - **Datos de Entrada:** Prepara un nodo `n8n-nodes-base.set` o `n8n-nodes-base.function` para simular los datos de entrada (parámetros) que el subworkflow esperaría recibir del nodo `@n8n/n8n-nodes-langchain.toolWorkflow`.
   - **Llamada al Subworkflow:** Utiliza un nodo `n8n-nodes-base.executeWorkflow` para llamar al subworkflow que quieres probar, pasando los datos de entrada simulados.
   - **Verificación de Salida:** Observa la salida del nodo `Execute Workflow`. Verifica que:
     - Para casos de éxito, el JSON de salida coincida con el [Formato Estándar de Salida](#formato-estándar-de-salida) con `status: "success"`.
     - Para casos de error conocidos (ej. parámetros inválidos), el JSON de salida coincida con el [Formato Estándar de Salida](#formato-estándar-de-salida) con `status: "error"` y un `data.code` apropiado.
     - Los datos dentro de `data` y `meta` sean los correctos para cada caso de prueba.
   - **Casos de Prueba:** Diseña múltiples casos de prueba, incluyendo:
     - Entradas válidas (camino feliz) (Verifica Principio de Robustez #1 y #2).
     - Entradas inválidas (ej. campos faltantes, formatos incorrectos, valores fuera de rango) (Verifica Principio de Robustez #2).
     - Casos límite.
     - Errores esperados de servicios externos (si el subworkflow llama a otras APIs, verifica Principio de Robustez #3).

**2. Interpretación de Logs**
   (Ver Principio de Robustez #6 sobre la importancia del logging)
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
   - **Diseño Robusto de Subworkflows (Principio de Robustez #4):** La causa más común de "errores silenciosos" es un subworkflow que no maneja todas sus rutas de error.
   - **Revisar Ramas de `IF`/`Switch` (Principio de Robustez #4):** Asegúrate que todas las posibles ramas de tus nodos `IF` o `Switch` terminen en un nodo `Set` que produzca la estructura de salida estándar (éxito o error).
   - **Manejo de Errores en Nodos Críticos (Principio de Robustez #3):** Para nodos que pueden fallar (ej. `HTTP Request`, `Google Calendar`):
     - Utiliza la pestaña "Configuración" > "Continue On Fail" o configura un "Error Workflow" para ese nodo.
     - Si usas "Continue On Fail", el siguiente nodo debe ser un `IF` que verifique si el nodo anterior produjo un error (usualmente `$json.error` estará presente) y redirija adecuadamente.
   - **Error Workflow Global de n8n (Principio de Robustez #5):** Configura un "Error Workflow" global en tu instancia de n8n como último recurso.
   - **Validación de Salida del Subworkflow (Avanzado):** En el flujo principal, después del nodo `@n8n/n8n-nodes-langchain.toolWorkflow`, podrías añadir un nodo `IF` o `Function` para verificar la estructura de la respuesta. Esto se describe en [Manejo de Errores Globales en el Flujo Principal del Servidor MCP](#manejo-de-errores-globales-en-el-flujo-principal-del-servidor-mcp).

## Guía de Exportación/Importación y Versionado con Git

**1. Exportación e Importación de Workflows en n8n**
   - **Formato de Exportación:** n8n permite exportar flujos de trabajo en formato JSON.
     - Para exportar un flujo de trabajo, ábrelo, haz clic en el menú de tres puntos (⋮) en la esquina superior derecha y selecciona "Descargar".
     - Se recomienda guardar el JSON **no compactado (formateado para legibilidad)**. Aunque el archivo es más grande, es mucho más fácil de leer y revisar diferencias (`diffs`) en Git. Si n8n exporta por defecto en formato compacto, puedes usar herramientas externas (como `jq` en la línea de comandos o un editor de código) para formatear el JSON antes de confirmarlo en Git: `jq . workflow_compacto.json > workflow_legible.json`.
   - **Importación:** Para importar un flujo de trabajo, desde la pantalla principal de "Workflows" en n8n, haz clic en "Nuevo" y luego selecciona "Importar desde archivo" (o "Importar desde URL" si el JSON está alojado en una URL).

**2. Estrategia de Versionado con Git**
   - **Beneficios de Git:**
     - **Historial de Cambios:** Rastrea cada cambio realizado a tus flujos de trabajo.
     - **Colaboración:** Permite a múltiples desarrolladores trabajar en los mismos flujos de trabajo.
     - **Ramificación (`Branching`):** Desarrolla nuevas funcionalidades o corrige errores en ramas separadas sin afectar la versión principal.
     - **Reversión:** Facilita volver a versiones anteriores si algo sale mal.
     - **Revisión de Código:** Permite revisar los cambios (`diffs` en el JSON) antes de fusionarlos.
   - **¿Qué incluir en el Repositorio?**
     - Los archivos JSON exportados de tus flujos de trabajo de n8n.
     - Potencialmente, scripts de utilidad (ej. para formatear JSON, para despliegues).
     - Documentación adicional si no está toda dentro de los ATDF de los nodos.

**3. Organización del Repositorio (Sugerencias)**
   - No hay una única forma correcta, pero aquí algunas estructuras comunes:
     - **Por Tipo de Flujo de Trabajo:**
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
   - **Nombres de Archivos:** Usa nombres de archivo descriptivos, idealmente incluyendo el nombre del flujo de trabajo y su versión (ej. `SWF_GetUserProfile_v2.json`). Esto ayuda incluso antes de abrir el archivo.
   - **Archivos `.gitattributes` (Avanzado):** Para mejorar los `diffs` de JSON en Git, puedes añadir un archivo `.gitattributes` en la raíz de tu repositorio con el siguiente contenido para que Git trate los JSON de manera más inteligente para los `diffs` (puede requerir configuración adicional o no ser soportado por todas las interfaces de Git):
     ```
     *.json diff=json
     ```

**4. Flujo de Trabajo Básico con Git**
   - **Clonar:** `git clone <url_repositorio>`
   - **Crear Rama:** `git checkout -b mi_nueva_funcionalidad`
   - **Modificar Flujos de Trabajo:** Haz cambios en n8n, exporta el JSON, reemplaza el archivo antiguo en tu copia local del repositorio.
   - **Revisar Cambios:** `git diff nombre_workflow.json` (para ver qué cambió en el JSON).
   - **Añadir y Confirmar:**
     ```bash
     git add nombre_workflow.json
     git commit -m "feat: Añadida validación de entrada a SWF_GetUserProfile_v1"
     ```
     (Sigue una convención para los mensajes de `commit`, ej. Conventional Commits).
   - **Empujar Cambios:** `git push origin mi_nueva_funcionalidad`
   - **Pull Request / Merge Request:** Crea un Pull Request (o Merge Request) en tu plataforma Git (GitHub, GitLab, etc.) para fusionar los cambios a la rama principal (ej. `main` o `develop`).

## Uso de Etiquetas (Tags) en los Workflows de n8n

**1. Beneficios del Uso de Etiquetas**
   - En entornos de n8n con una gran cantidad de flujos de trabajo, las etiquetas (`tags`) son una herramienta poderosa para organizar, filtrar y encontrar flujos de trabajo rápidamente.
   - Permiten categorizar los flujos de trabajo por diversos criterios, como su función, estado, versión, o el proyecto al que pertenecen.
   - Facilitan la gestión y el mantenimiento, especialmente en equipos grandes o con múltiples proyectos.

**2. Cómo Usar Etiquetas en n8n**
   - Para añadir o editar etiquetas de un flujo de trabajo, puedes hacerlo desde la vista de lista de "Workflows":
     - Pasa el cursor sobre el flujo de trabajo.
     - Haz clic en el icono de etiqueta (`tag`) que aparece.
     - Escribe el nombre de la etiqueta y presiona Enter. Puedes añadir múltiples etiquetas.
   - También puedes gestionar etiquetas al editar un flujo de trabajo, usualmente en un panel de configuración del flujo de trabajo mismo (la ubicación exacta puede variar ligeramente con versiones de n8n).

**3. Estrategias de Etiquetado Sugeridas para Servidores MCP y Herramientas**
   - **Tipo de Flujo de Trabajo:**
     - `mcp-server`: Para el flujo de trabajo principal que actúa como servidor MCP (el que contiene el `@n8n/n8n-nodes-langchain.mcpTrigger`).
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
   - Un flujo de trabajo servidor MCP para usuarios podría tener las etiquetas: `mcp-server`, `module:user-management`, `v1.0`, `status:active`.
   - Un subworkflow que es una herramienta para obtener perfiles de usuario: `mcp-tool`, `tool:user-management`, `tool-version:1.0`, `status:active`.
   - Un subworkflow de utilidad para validar fechas usado por varias herramientas: `subworkflow-helper`, `module:utils`, `v1.0`, `status:active`.

**5. Filtrado por Etiquetas**
   - En la vista de lista de "Workflows" de n8n, usualmente hay una barra de búsqueda o un control de filtro que permite escribir nombres de etiquetas para mostrar solo los flujos de trabajo que las contengan. Esto agiliza enormemente la localización de flujos de trabajo específicos.

**Recomendación:** Define una convención de etiquetado para tu equipo u organización y sé consistente en su aplicación. Un buen sistema de etiquetado es invaluable a medida que tu instancia de n8n crece.

## Manejo de Errores Globales en el Flujo Principal del Servidor MCP

Esta sección aborda cómo el flujo principal del servidor MCP debe manejar fallos relacionados con la orquestación de herramientas, complementando los [Principios Clave para la Robustez de Flujos de Trabajo](#principios-clave-para-la-robustez-de-flujos-de-trabajo) que se aplican a cada subworkflow.

**1. Importancia del Manejo de Errores a Nivel del Servidor Principal**
   - Asegura que el agente AI que consume el servidor MCP reciba una respuesta coherente (Principio de Robustez #1) incluso si ocurren problemas inesperados en la orquestación de las herramientas antes de que un subworkflow específico sea invocado o después de que este (supuestamente) haya completado su ejecución.

**2. Escenarios de Error en el Flujo Principal y Cómo Manejarlos**

   **a. Fallo del Nodo `@n8n/n8n-nodes-langchain.toolWorkflow`**
      - **Causa Posible:** El subworkflow especificado en el nodo `toolWorkflow` no existe (ej. ID incorrecto, no importado), o hay un problema crítico con la configuración del propio nodo `toolWorkflow`.
      - **Manejo:**
        - Aplicar el Principio de Robustez #5: Configurar la pestaña "Configuración" > "Error Workflow" para el nodo `@n8n/n8n-nodes-langchain.toolWorkflow`. Este Error Workflow dedicado debe generar una respuesta JSON estándar (ej. con `status: "error"`, `data.code: "TOOL_EXECUTION_FAILED"`, y un mensaje apropiado).
        - Un "Error Workflow" global para la instancia de n8n (Principio de Robustez #5) también actuaría como un seguro.

   **b. Subworkflow Devuelve una Respuesta Estructuralmente Inválida**
      - **Causa Posible:** Un subworkflow (herramienta) termina y devuelve datos, pero estos no se ajustan al formato esperado (ej. falta el campo `status`, o `status` no es ni `"success"` ni `"error"`). Esto indica un incumplimiento del Principio de Robustez #1 por parte del subworkflow.
      - **Manejo:**
        - Después de cada nodo `@n8n/n8n-nodes-langchain.toolWorkflow` (o después de un nodo `Switch` que enruta a varios `toolWorkflows`), añadir un nodo `n8n-nodes-base.if` para validar la estructura de la respuesta.
        - **Condiciones del `IF`:** Verificar si el campo `status` existe y si es `"success"` o `"error"`.
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
                  "tool_name": "{{ $json.tool_name_if_available }}",
                  "received_response_preview": "{{ JSON.stringify($json).slice(0, 200) }}"
                }
              },
              "meta": {
                "timestamp": "{{ $now.toJSON() }}"
              }
            }
            ```
        - **Rama TRUE del `IF` (Respuesta Válida):** Continuar el flujo normalmente.

   **c. Error en el Router (ej. Nodo `Switch`)**
      - **Causa Posible:** El nombre de la herramienta proporcionado por el agente AI no coincide con ninguna de las rutas definidas en el nodo `Switch`.
      - **Manejo:**
        - El nodo `Switch` en n8n tiene una salida "Default" o "Fallback". Conectar esta salida a un nodo `n8n-nodes-base.set`.
        - Este nodo `Set` debe generar una respuesta de error estándar (Principio de Robustez #1) indicando que la herramienta no fue encontrada.
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
   - **Consistencia:** Todos los errores generados por el flujo principal deben seguir el formato JSON estándar (Principio de Robustez #1).
   - **Logging (Registro) (Principio de Robustez #6):** Considera añadir nodos de log (ej. `n8n-nodes-base.logMessage`) en estas rutas de error globales para facilitar la depuración.
   - **Error Workflow Global de n8n (Principio de Robustez #5):** Un Error Workflow global es una red de seguridad crucial.

Un manejo de errores robusto a nivel del flujo principal del servidor MCP complementa el manejo de errores dentro de cada subworkflow, creando un sistema más resiliente y predecible.
