# Table of Contents

- [n8n MCP Server Guide](#n8n-mcp-server-guide)
- [Introduction and Objectives](#introduction-and-objectives)
- [Basic Concepts](#basic-concepts)
  - [MCP Server Trigger](#mcp-server-trigger)
  - [Subworkflows](#subworkflows)
  - [toolWorkflow Node](#toolworkflow-node)
- [MCP Best Practices](#mcp-best-practices)
  - [Architecture](#architecture)
  - [Naming Conventions](#naming-conventions)
  - [Standard Output](#standard-output)
  - [Validation](#validation)
  - [Security](#security)
  - [Documentation](#documentation)
  - [Versioning](#versioning)
  - [Key Principles for Workflow Robustness](#key-principles-for-workflow-robustness)
- [General Architecture](#general-architecture)
  - [Basic Structure](#basic-structure)
  - [Advantages of Using Subworkflows](#advantages-of-using-subworkflows)
- [Designing MCP Tools (Subworkflows)](#designing-mcp-tools-subworkflows)
  - [Standard Output Format](#standard-output-format)
  - [Input Validation and Uniform Errors](#input-validation-and-uniform-errors)
- [Visual Base Template for Subworkflows (Tools)](#visual-base-template-for-subworkflows-tools)
- [Main Flow Example (MCP Server)](#main-flow-example-mcp-server)
- [General Considerations](#general-considerations)
- [Integrating the ATDF Format (Automatic Tool Definition Format)](#integrating-the-atdf-format-automatic-tool-definition-format)
  - [How to Integrate It](#how-to-integrate-it)
  - [Recommended Fields for ATDF](#recommended-fields-for-atdf)
  - [ATDF Block Example (YAML)](#atdf-block-example-yaml)
  - [Annotated ATDF Mini-Template (YAML)](#annotated-atdf-mini-template-yaml)
  - [Validating ATDF Syntax (YAML)](#validating-atdf-syntax-yaml)
- [Using MCP Sub-servers as Tools](#using-mcp-sub-servers-as-tools)
  - [Configuration](#configuration)
  - [Advantages](#advantages)
  - [Visual Example (Flowchart)](#visual-example-flowchart)
- [Considerations for Describing External Tools (via MCP Client)](#considerations-for-describing-external-tools-via-mcp-client)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
- [Testing and Debugging](#testing-and-debugging)
- [Export/Import and Git Versioning Guide](#exportimport-and-git-versioning-guide)
- [Using Tags in n8n Workflows](#using-tags-in-n8n-workflows)
- [Global Error Handling in the Main MCP Server Flow](#global-error-handling-in-the-main-mcp-server-flow)

# n8n MCP Server Guide

## Introduction and Objectives

This guide describes the best practices and architecture for building and maintaining Common Process Servers (MCP) using n8n. The goal is to promote modularity, reusability, and maintainability of workflows.

## Basic Concepts

### MCP Server Trigger
The **MCP Server Trigger** (node type: `@n8n/n8n-nodes-langchain.mcpTrigger`) is a specialized node in n8n that acts as an entry point for requests to the MCP server. It allows defining the server's input and output interface and receives external requests to execute one or more tools.

### Subworkflows
**Subworkflows** (secondary workflows) are n8n workflows that can be called from other workflows. They are fundamental for modularity in the MCP architecture, allowing specific logic to be encapsulated in reusable units. These subworkflows implement the logic of a specific tool.

### toolWorkflow Node
The **toolWorkflow** node (node type: `@n8n/n8n-nodes-langchain.toolWorkflow`) is used in the main MCP server flow to call a subworkflow (tool). It acts as a bridge, configuring how the subworkflow is called and how its inputs and outputs are mapped. The tool's ATDF description is placed in this node.

## MCP Best Practices

### Architecture
*   Design a modular architecture using subworkflows for each discrete tool or process.
*   The main MCP server uses an `@n8n/n8n-nodes-langchain.mcpTrigger` and calls subworkflows (tools) using `@n8n/n8n-nodes-langchain.toolWorkflow` nodes.

### Naming Conventions
*   Use clear and consistent names for workflows, subworkflows, nodes, and variables.
*   Prefix subworkflows with `SWF_` for easy identification (e.g., `SWF_ValidateDateRange`).
*   Prefix environment variables with `ENV_`.
*   Use snake_case for variable and parameter names.
*   For tool names (configured in the `toolWorkflow` node), follow the format: `tool.<action>_<entity>` (e.g., `tool.get_user`, `tool.create_invoice`).

### Standard Output
*   Define a standard output format for all subworkflows (tools), for both successful responses and errors. The `status` field must strictly be `"success"` or `"error"`. (See "Designing MCP Tools (Subworkflows) > Standard Output Format").

### Validation
*   Validate inputs in each subworkflow to ensure data integrity.
*   Provide clear and uniform error messages following the standard error format. (See "Designing MCP Tools (Subworkflows) > Input Validation and Uniform Errors").

### Security
*   Protect the `@n8n/n8n-nodes-langchain.mcpTrigger` endpoints using n8n authentication and authorization mechanisms.
*   Manage credentials securely using n8n's credential manager.
*   Avoid exposing sensitive information in logs.

### Documentation
*   Document each tool (subworkflow), including its purpose, input parameters, output format, and any dependencies. The ATDF block is included in the description of the `@n8n/n8n-nodes-langchain.toolWorkflow` node that calls it.
*   Keep the general MCP architecture documentation up to date.

### Versioning
*   Version subworkflows and the MCP server to manage changes and avoid breaking existing integrations.
*   Use a version control system like Git for versioning exported workflows. (See "Export/Import and Git Versioning Guide").

### Key Principles for Workflow Robustness
To ensure that MCP servers and their tools (subworkflows) are reliable and easy to debug, these fundamental principles should be followed:
1.  **Adherence to Standard Output Format:** Every subworkflow (tool) must consistently return the [Standard Output Format](#standard-output-format) JSON, whether for success (`status: "success"`) or error (`status: "error"`), including the appropriate `data` and `meta` fields.
2.  **Exhaustive Input Validation:** Each subworkflow must rigorously validate its input parameters at the beginning. See the [Input Validation and Uniform Errors](#input-validation-and-uniform-errors) section.
3.  **Explicit Error Handling in Critical Nodes:** For nodes that perform operations prone to failure (e.g., external API calls with `HTTP Request`, interactions with services like `Google Calendar`), explicitly configure error handling. This can be done using the "Settings" > "Continue On Fail" option in the node, followed by an `IF` node to check if `$json.error` exists and thus direct the flow to prepare a standard error response. Alternatively, the node's "Error Workflow" option can be used to direct the failure to a dedicated error handling workflow.
4.  **Coverage of All Logical Paths:** Ensure that all possible branches within a workflow (e.g., in `IF` or `Switch` nodes) explicitly end in a node that generates a standard output (success or error). Avoid "dead ends" where a branch does not produce a formatted response, which could lead to silent errors or unexpected responses.
5.  **Strategic Use of n8n "Error Workflows":**
    *   **Node Level:** For critical or complex nodes like `@n8n/n8n-nodes-langchain.toolWorkflow`, configuring a specific "Error Workflow" in the node's "Settings" tab can provide granular fault handling.
    *   **Instance Level (Global):** Configuring a global "Error Workflow" for the n8n instance (from n8n "Settings") serves as a final safety net to capture and handle any uncontrolled errors that may occur in any workflow.
6.  **Meaningful Logging:** Implement logging of important events, key input parameters, and errors at critical points in the workflows. Use the `n8n-nodes-base.logMessage` node or external observability tools. This is crucial for debugging and monitoring. (See "Testing and Debugging > Log Interpretation").

Compliance with these principles is fundamental and is detailed or exemplified in later sections such as [Testing and Debugging](#testing-and-debugging) and [Global Error Handling in the Main MCP Server Flow](#global-error-handling-in-the-main-mcp-server-flow).

## General Architecture

### Basic Structure
The MCP architecture is based on a main flow (the MCP server) that uses an `@n8n/n8n-nodes-langchain.mcpTrigger` as an entry point. This flow orchestrates the execution of subworkflows (tools) through `@n8n/n8n-nodes-langchain.toolWorkflow` nodes.

```mermaid
graph TD
    A[@n8n/n8n-nodes-langchain.mcpTrigger] --> B{Switch Node (Router based on AI Agent's tool name)};
    B -- tool_A_name --> C1["@n8n/n8n-nodes-langchain.toolWorkflow (configured for SWF_Tool_A)"];
    B -- tool_B_name --> C2["@n8n/n8n-nodes-langchain.toolWorkflow (configured for SWF_Tool_B)"];
    C1 --> D[Response Handling / Preparation for AI Agent];
    C2 --> D;
```
The `mcpTrigger` receives a request, a `Switch` node (or similar logic) determines which tool to execute, and a specific `toolWorkflow` node calls the corresponding subworkflow.

### Advantages of Using Subworkflows
*   **Modularity:** Decompose complex problems into smaller, manageable parts.
*   **Reusability:** Use the same logic in different parts of the system or in different MCP servers.
*   **Maintainability:** Facilitate updates and bug fixes by isolating logic into independent units.
*   **Testability:** Test each subworkflow (tool) in isolation.

## Designing MCP Tools (Subworkflows)

### Standard Output Format

#### Success
The `status` field will always be `"success"`. The `data` field contains the useful result of the tool.

```json
{
  "status": "success",
  "data": {
    "specific_result": "value",
    "other_data": 123
  },
  "meta": {
    "timestamp": "2023-10-27T10:30:00Z"
  }
}
```
*(Note: `meta.timestamp` can be generated with `{{ $now }}` in a `Set` node)*.

#### Error
The `status` field will always be `"error"`. The `data` field contains error details. The `message` or `text` field within `data` provides a human-readable message.

```json
{
  "status": "error",
  "data": {
    "code": "UNIQUE_ERROR_CODE",
    "message": "Readable error description.",
    "text": "Readable error description (alternative if 'text' is used).",
    "details": {
      "field": "name_of_field_with_error",
      "expected": "expected_type_or_format",
      "solution": "How to fix the problem or what is expected."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:35:00Z"
  }
}
```
*(Prefer `message` or `text` consistently. If examples use `text`, use `text`. Ensure error codes like `UNIQUE_ERROR_CODE` are uppercase and backticked if referenced in text.)*.

### Input Validation and Uniform Errors
*   Use `n8n-nodes-base.if` or `n8n-nodes-base.switch` nodes at the beginning of subworkflows to validate input parameters.
*   If validation fails, an error response using the structure defined above must be constructed. For example, if a `user_id` field is required but not provided:

```json
{
  "status": "error",
  "data": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters.",
    "details": {
      "field": "user_id",
      "expected": "string, non-empty",
      "solution": "Provide a valid user_id."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:40:00Z"
  }
}
```
*   Use unique and descriptive error codes (e.g., `VALIDATION_ERROR`) to facilitate debugging and monitoring.

## Visual Base Template for Subworkflows (Tools)

Subworkflows acting as tools are typically initiated by an `n8n-nodes-base.executeWorkflowTrigger` (execute workflow trigger) when called from the main flow (via an `@n8n/n8n-nodes-langchain.toolWorkflow`). It is crucial to follow the [Key Principles for Workflow Robustness](#key-principles-for-workflow-robustness) when designing these templates.

**Example: Subworkflow "SWF_ValidateDateRange"**

1.  **Start (Trigger):** `n8n-nodes-base.executeWorkflowTrigger` node. Receives parameters like `Start` (start date) and `End` (end date) from the `toolWorkflow` node in the main flow.
2.  **Input Validation:** `n8n-nodes-base.if` node (e.g., "Validate dates"). Checks if dates are valid, if `Start` is before `End`, etc. (Robustness Principle #2).
    *   If validation fails, a (FALSE) branch leads to an `n8n-nodes-base.set` node (e.g., "Error: Invalid Dates") to construct the standard error JSON (Robustness Principle #1).
3.  **Main Logic (if validation is correct):** May include other nodes to process dates if necessary. In this example, the validation itself is the main logic.
4.  **Successful Output:** `n8n-nodes-base.set` node (e.g., "Success: Valid Range"). Prepares the standard successful JSON response (Robustness Principle #1).
    ```json
    {
      "status": "success",
      "data": {
        "message": "The date range is valid.",
        "start_date": "{{ $json.Start }}",
        "end_date": "{{ $json.End }}"
      },
      "meta": {
        "timestamp": "{{ $now.toJSON() }}"
      }
    }
    ```
5.  **Error Output (from validation or main logic):** `n8n-nodes-base.set` node (e.g., "Error: Invalid Dates"). Prepares the standard error JSON response (Robustness Principle #1).
    ```json
    {
      "status": "error",
      "data": {
        "code": "INVALID_DATE_RANGE",
        "text": "The start date must be before the end date.",
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
    *(Note: The "ValidateDateRange" example uses `data.text` for the message, so it's reflected here. The error code `INVALID_DATE_RANGE` is uppercase.)*
6.  **End of Subworkflow:** The subworkflow ends. Data prepared in the `Set` node of the executed branch (success or error) is implicitly returned to the calling flow (to the `toolWorkflow` node). Ensure coverage of all logical paths (Robustness Principle #4).

```mermaid
graph TD
    A[n8n-nodes-base.executeWorkflowTrigger <br> (Receives: Start, End)] --> B{n8n-nodes-base.if <br> (Validate Dates: Start < End?)};
    B -- TRUE (Valid) --> S_PREP[n8n-nodes-base.set <br> (Prepare Success JSON: status=success, data={message, dates}, meta)];
    S_PREP --> Z[End of Subworkflow <br> (Returns JSON from S_PREP)];
    B -- FALSE (Invalid) --> E_PREP[n8n-nodes-base.set <br> (Prepare Error JSON: status=error, data={code, text, details}, meta)];
    E_PREP --> Z;
```

## Main Flow Example (MCP Server)

The main flow uses an `@n8n/n8n-nodes-langchain.mcpTrigger` as an entry point.

1.  **MCP Server Trigger:** `@n8n/n8n-nodes-langchain.mcpTrigger` node. Defines the endpoint, and is where the AI Agent (Langchain) sends requests to execute tools.
2.  **Request Validation (Optional, delegated to mcpTrigger):** The `mcpTrigger` handles part of the agent's request validation.
3.  **Router/Dispatcher (Switch Node):** An `n8n-nodes-base.switch` node directs execution based on the tool name requested by the AI agent (e.g., `{{ $json.tool_name }}`). Each `Switch` output connects to a specific `@n8n/n8n-nodes-langchain.toolWorkflow` node. (See "Global Error Handling in the Main MCP Server Flow" for routing errors).
4.  **Subworkflow Call (Tool):** The `@n8n/n8n-nodes-langchain.toolWorkflow` node is responsible for:
    *   Identifying the subworkflow to execute (configured in its parameters).
    *   Mapping inputs for the subworkflow (e.g., using expressions like `{{ $fromAI("user_id") }}` to take parameters from the AI agent's request).
    *   Executing the subworkflow.
    *   Receiving the response (success/error JSON) from the subworkflow. (See "Global Error Handling in the Main MCP Server Flow" for `toolWorkflow` failures or invalid responses).
5.  **Subworkflow Response Handling:** The output of the `toolWorkflow` (which is the subworkflow's output) can be further processed if necessary before being returned to the `mcpTrigger`.
6.  **Response to AI Agent:** The `mcpTrigger` is responsible for sending the response back to the AI agent.

## General Considerations

*   **Follow naming conventions:** Crucial for readability and maintenance.
*   **Clearly label and name each tool:** The tool name is defined in the `@n8n/n8n-nodes-langchain.toolWorkflow` node.
*   **Test each subworkflow in isolation:** Ensures each component works correctly before integration. (See "Testing and Debugging").
*   **Version tools:** The ATDF description in the `toolWorkflow` node should reflect the version of the tool/subworkflow it calls.
*   **Document each version:** Include changes in the ATDF description.

## Integrating the ATDF Format (Automatic Tool Definition Format)

### How to Integrate It
The ATDF description block (in YAML format) should be included directly in the **`description` parameter of the `@n8n/n8n-nodes-langchain.toolWorkflow` node** that calls the corresponding subworkflow. This `toolWorkflow` node acts as the representation of the tool within the main MCP server and is what the AI agent "sees".

### Recommended Fields for ATDF
*   `description`: Concise description of what the tool does.
*   `how_to_use`: Details on how to interact with the tool, including:
    *   `inputs`: List of input parameters (name, type, if required, description).
    *   `outputs`: Description of the expected output structure (`status`, `data` with its subfields, `meta`).
*   `when_to_use`: Use cases or situations where this tool is appropriate.

### ATDF Block Example (YAML)

This block would be placed in the "Description" field of an `@n8n/n8n-nodes-langchain.toolWorkflow` node that is configured to call the `SWF_Get_User_Profile` subworkflow.

```yaml
---
description: Gets a user's profile from their ID.
how_to_use:
  inputs:
    - name: user_id # This 'name' is what the AI Agent will use
      type: string
      required: true
      description: Unique identifier of the user.
  outputs:
    status: string (success/error)
    data: (if status is success)
      name: string
      email: string
    data: (if status is error)
      code: string
      text: string # or message, be consistent
      details: object
    meta:
      timestamp: string (ISO 8601)
when_to_use: When detailed information for a specific user is required.
---
```

### Annotated ATDF Mini-Template (YAML)

```yaml
---
# Descriptive name of the tool, visible to the AI agent.
# name: tool.my_action.my_entity
# (The 'name' is usually handled by the MCP Trigger or ToolWorkflow,
#  this ATDF section goes into the 'description' field of that node)

# Concise description of what the tool does.
description: Performs a specific action on an entity.

# Instructions on how to use the tool, including inputs and outputs.
how_to_use:
  inputs:
    # List of input parameters the tool expects.
    - name: required_parameter
      type: string # Common types: string, number, boolean, object, array
      required: true # true if the parameter is mandatory, false if optional.
      description: Detailed description of this parameter and its purpose.
                  # Include value examples if helpful.
    - name: optional_parameter
      type: number
      required: false
      description: Parameter that is not strictly necessary.
      default: 10 # Default value if not provided (informative for ATDF).

  outputs:
    # Description of the output structure the tool returns.
    # This must align with the Standard Output Format of the guide.
    status: string # Always "success" or "error".
    data: object # Container for the response data.
      # Sub-fields of 'data' if status is "success":
      # success_result: string
      # other_data: number
      # Sub-fields of 'data' if status is "error":
      # code: string
      # message: string (or text)
      # details: object (with fields field, expected, solution)
    meta: object # Response metadata.
      # timestamp: string # Date and time in ISO 8601 format.

# When this tool should be used. Describe appropriate use cases.
when_to_use: Ideal for when [describe use scenario] is needed.
             Do not use if [describe contraindications or alternatives].
---
```

### Validating ATDF Syntax (YAML)
ATDF is written in YAML. To ensure your ATDF description syntax is correct before pasting it into an n8n node's description field, it is highly recommended to validate it. You can use:
- **Modern Code Editors:** Many editors like VS Code (with YAML extensions) highlight YAML syntax errors in real-time.
- **Online YAML Linters:** Numerous web tools exist where you can paste your YAML to check its validity (search "yaml linter online").
- **Continuous Integration (CI):** In a more advanced development environment with Git, you can integrate a YAML linter into your CI/CD process to automatically check ATDF files if you manage them as separate files before copying them to n8n.

## Using MCP Sub-servers as Tools

A main MCP server can use tools exposed by other MCP servers (sub-servers) using the `@n8n/n8n-nodes-langchain.mcpClient` node.

### Configuration
*   In the main MCP server flow, an `@n8n/n8n-nodes-langchain.mcpClient` node is used.
*   The `sseEndpoint` of the `mcpClient` node is configured to point to the URL of the `@n8n/n8n-nodes-langchain.mcpTrigger` endpoint of the MCP sub-server.
*   The `includeTools` or `excludeTools` options in the `mcpClient` node can be used to filter which tools from the sub-server are exposed or used.
*   Credentials to access the sub-server are configured in the `mcpClient` node.

### Advantages
*   **Greater Modularity and Decoupling.**
*   **Independent Scalability.**
*   **Different Teams.**
*   **Secure Reusability.**

### Visual Example (Flowchart)

```mermaid
flowchart LR
  A[Main MCP Agent] --> B("@n8n/n8n-nodes-langchain.mcpClient");
  B -- sseEndpoint: http://github-mcp/sse --> C[GitHub MCP Sub-server (@mcpTrigger)];
  B -- sseEndpoint: http://docs-mcp/sse --> D[Docs MCP Sub-server (@mcpTrigger)];
  B -- sseEndpoint: http://code-mcp/sse --> E[Code MCP Sub-server (@mcpTrigger)];
```
The `mcpClient` node (B) in the Main MCP Agent connects to various MCP sub-servers (C, D, E), each with its own `@n8n/n8n-nodes-langchain.mcpTrigger`.

## Considerations for Describing External Tools (via MCP Client)

When a main MCP server uses tools from an MCP sub-server via the `@n8n/n8n-nodes-langchain.mcpClient` node:

*   **ATDF Propagation:** The `mcpClient` obtains ATDF descriptions of tools directly from the `description` of the `@n8n/n8n-nodes-langchain.toolWorkflow` nodes (or equivalents) in the sub-server.
*   **Client-Side Display:** If the MCP sub-server provides ATDF descriptions, the `mcpClient` will display them.
*   **Generic Descriptions:** If the sub-server does not provide ATDF, the `mcpClient` might display a generic description.
*   **Client-Side Immutability:** Descriptions of tools from sub-servers cannot be edited from the `mcpClient`. The source of truth is the sub-server.
*   **Interoperability:** This mechanism ensures that the main server consumes tools as defined and documented by the sub-server.

## Frequently Asked Questions (FAQ)

**1. What happens if a subworkflow (tool) fails unexpectedly?**
   - The `@n8n/n8n-nodes-langchain.toolWorkflow` node calling the subworkflow should ideally capture this failure.
   - A well-designed subworkflow, following the [Key Principles for Workflow Robustness](#key-principles-for-workflow-robustness), will return a standard error JSON.
   - If the subworkflow fails catastrophically (a node crashes without applying Robustness Principle #3 or #4), the `toolWorkflow` might receive a generic error. In this case, Robustness Principle #5 (use of node-specific or global "Error Workflows") is crucial.
   - For critical nodes within the subworkflow (e.g., external API calls), Robustness Principle #3 must be applied.

**2. Can a subworkflow invoke another subworkflow?**
   - Yes, absolutely. This is a recommended practice for tool composition and logic reuse.
   - A subworkflow (e.g., "Complex Tool A") can use an `n8n-nodes-base.executeWorkflow` node to call another simpler subworkflow (e.g., "Sub-Tool B").
   - The calling subworkflow ("Complex Tool A") should handle the response (success or error) from the called subworkflow ("Sub-Tool B") and then format its own standard response (Robustness Principle #1) for the `toolWorkflow` that originally called it. The "Validate Availability" example calling "Validate Date Range" illustrates this pattern.

**3. How to correctly version subworkflows and maintain compatibility?**
   - **Nomenclature:** Include a version number in the subworkflow name (e.g., `SWF_MyTool_v1`, `SWF_MyTool_v2`).
   - **ATDF:** The ATDF description in the `@n8n/n8n-nodes-langchain.toolWorkflow` node calling the subworkflow must clearly reflect the version of the tool it is exposing and the expected parameters/outputs for that version. Any deviation should be considered an error by the subworkflow (Robustness Principle #2).
   - **Non-Breaking Changes:** If you add new optional functionality or non-mandatory fields to the output, you can keep the same major version and update a minor one (e.g., v1.1). Ensure the ATDF is updated.
   - **Breaking Changes:** If you change parameter names, data types, remove output fields, or change fundamental logic in a way that is not backward compatible, you must create a new version of the subworkflow (e.g., `SWF_MyTool_v2`). The main MCP server flow should then use a new `@n8n/n8n-nodes-langchain.toolWorkflow` node to expose this new version (e.g., `tool.my_tool_v2`).
   - **Git:** Use a version control system like Git to save JSON exports of your workflows. Branches or `tags` can help manage versions.
   - **Deprecation:** Consider keeping old versions for a while and marking them as deprecated in their ATDF, indicating the new version to use.

## Testing and Debugging

This section focuses on how to verify the implementation of the [Key Principles for Workflow Robustness](#key-principles-for-workflow-robustness) and debug issues.

**1. Testing Subworkflows (Tools) in Isolation**
   - **Test Environment:** Consider having a dedicated n8n workflow to test your subworkflows individually before integrating them into the main MCP server.
   - **Manual Trigger:** In this test workflow, you can use an `n8n-nodes-base.manualTrigger` node (or simply the "Execute Workflow" button with fixed input data if the subworkflow starts with `n8n-nodes-base.executeWorkflowTrigger`) to initiate execution.
   - **Input Data:** Prepare an `n8n-nodes-base.set` or `n8n-nodes-base.function` node to simulate the input data (parameters) that the subworkflow would expect to receive from the `@n8n/n8n-nodes-langchain.toolWorkflow` node.
   - **Calling the Subworkflow:** Use an `n8n-nodes-base.executeWorkflow` node to call the subworkflow you want to test, passing the simulated input data.
   - **Output Verification:** Observe the output of the `Execute Workflow` node. Verify that:
     - For success cases, the output JSON matches the [Standard Output Format](#standard-output-format) with `status: "success"`.
     - For known error cases (e.g., invalid parameters), the output JSON matches the [Standard Output Format](#standard-output-format) with `status: "error"` and an appropriate `data.code`.
     - The data within `data` and `meta` are correct for each test case.
   - **Test Cases:** Design multiple test cases, including:
     - Valid inputs (happy path) (Verifies Robustness Principle #1 and #2).
     - Invalid inputs (e.g., missing fields, incorrect formats, out-of-range values) (Verifies Robustness Principle #2).
     - Edge cases.
     - Expected errors from external services (if the subworkflow calls other APIs, verifies Robustness Principle #3).

**2. Log Interpretation**
   (See Robustness Principle #6 on the importance of logging)
   - **Logs from `@n8n/n8n-nodes-langchain.mcpTrigger`:**
     - Will show the complete request received from the AI agent (Langchain), including the tool name and parameters.
     - Will record the final response sent back to the AI agent after the `toolWorkflow` and subworkflow have executed.
     - Errors occurring directly in the `mcpTrigger` or if a `toolWorkflow` does not return a valid response may appear here.
   - **Logs from `@n8n/n8n-nodes-langchain.toolWorkflow`:**
     - Will show the parameters it received (potentially transformed from the `mcpTrigger` input, e.g., by `$fromAI()`).
     - Will indicate which subworkflow it is calling.
     - Will record the complete JSON response it received from the subworkflow.
     - If the `toolWorkflow` itself fails (e.g., cannot find the specified subworkflow, or there is an error in input mapping configuration), the error will be seen in this node.
   - **Subworkflow Logs (during isolated testing):**
     - When testing with `Execute Workflow`, you can see the input data the subworkflow received and the output of each node within it. This is crucial for debugging internal logic.
     - Use the "Execution Log" panel in n8n to trace data flow and errors at each step of the subworkflow.

**3. Capturing Silent or Unexpected Errors**
   - **Robust Subworkflow Design (Robustness Principle #4):** The most common cause of "silent errors" is a subworkflow that does not handle all its error paths.
   - **Review `IF`/`Switch` Branches (Robustness Principle #4):** Ensure all possible branches of your `IF` or `Switch` nodes end in a `Set` node that produces the standard output structure (success or error).
   - **Error Handling in Critical Nodes (Robustness Principle #3):** For nodes that can fail (e.g., `HTTP Request`, `Google Calendar`):
     - Use the "Settings" > "Continue On Fail" tab or configure an "Error Workflow" for that node.
     - If using "Continue On Fail", the next node should be an `IF` that checks if the previous node produced an error (usually `$json.error` will be present) and redirects accordingly.
   - **Global n8n Error Workflow (Robustness Principle #5):** Configure a global "Error Workflow" in your n8n instance settings as a last resort.
   - **Subworkflow Output Validation (Advanced):** In the main flow, after the `@n8n/n8n-nodes-langchain.toolWorkflow` node, you could add an `IF` or `Function` node to check the response structure. This is described in [Global Error Handling in the Main MCP Server Flow](#global-error-handling-in-the-main-mcp-server-flow).

## Export/Import and Git Versioning Guide

**1. Exporting and Importing Workflows in n8n**
   - **Export Format:** n8n allows exporting workflows in JSON format.
     - To export a workflow, open it, click the three-dot menu (⋮) in the upper right corner, and select "Download".
     - It is recommended to save the JSON **unminified (formatted for readability)**. Although the file is larger, it is much easier to read and review differences (`diffs`) in Git. If n8n defaults to compact format, you can use external tools (like `jq` on the command line or a code editor) to "prettify" the JSON before committing it to Git: `jq . compact_workflow.json > readable_workflow.json`.
   - **Importing:** To import a workflow, from the main "Workflows" screen in n8n, click "New" and then select "Import from file" (or "Import from URL" if the JSON is hosted at a URL).

**2. Git Versioning Strategy**
   - **Benefits of Git:**
     - **Change History:** Tracks every change made to your workflows.
     - **Collaboration:** Allows multiple developers to work on the same workflows.
     - **Branching:** Develop new features or fix bugs in separate branches without affecting the main version.
     - **Reversion:** Makes it easy to revert to previous versions if something goes wrong.
     - **Code Review:** Allows reviewing changes (`diffs` in the JSON) before merging.
   - **What to Include in the Repository?**
     - Exported JSON files of your n8n workflows.
     - Potentially, utility scripts (e.g., for formatting JSON, for deployments).
     - Additional documentation if not all is within the nodes' ATDF.

**3. Repository Organization (Suggestions)**
   - There is no single correct way, but here are some common structures:
     - **By Workflow Type:**
       ```
       /repository-root
       ├── mcp_servers/
       │   ├── auth_server_main.json
       │   └── user_management_server_main.json
       ├── tools/  (or subworkflows/)
       │   ├── SWF_GetUserProfile_v1.json
       │   ├── SWF_UpdateUserProfile_v1.json
       │   ├── SWF_ValidateDateRange_v1.json
       ├── utilities/ (subworkflows not directly exposed as tools)
       │   └── SWF_FormatAddress_v1.json
       └── README.md
       ```
     - **By Domain or Project:**
       ```
       /repository-root
       ├── project_alpha/
       │   ├── mcp_server_alpha.json
       │   ├── tools/
       │   │   └── SWF_AlphaTool1_v1.json
       │   └── internal_subworkflows/
       │       └── SWF_AlphaHelper_v1.json
       ├── project_beta/
       │   ├── mcp_server_beta.json
       │   └── tools/
       │       └── SWF_BetaTool1_v1.json
       └── shared_tools/
           └── SWF_CommonUtil_v1.json
       ```
   - **Consistency:** Choose a structure and be consistent.
   - **File Names:** Use descriptive file names, ideally including the workflow name and its version (e.g., `SWF_GetUserProfile_v2.json`). This helps even before opening the file.
   - **`.gitattributes` Files (Advanced):** To improve JSON `diffs` in Git, you can add a `.gitattributes` file at the root of your repository with the following content so Git treats JSON files more intelligently for `diffs` (may require additional configuration or not be supported by all Git interfaces):
     ```
     *.json diff=json
     ```

**4. Basic Git Workflow**
   - **Clone:** `git clone <repository_url>`
   - **Create Branch:** `git checkout -b my_new_feature`
   - **Modify Workflows:** Make changes in n8n, export the JSON, replace the old file in your local repository copy.
   - **Review Changes:** `git diff workflow_name.json` (to see what changed in the JSON).
   - **Add and Commit:**
     ```bash
     git add workflow_name.json
     git commit -m "feat: Added input validation to SWF_GetUserProfile_v1"
     ```
     (Follow a convention for `commit` messages, e.g., Conventional Commits).
   - **Push Changes:** `git push origin my_new_feature`
   - **Pull Request / Merge Request:** Create a Pull Request (or Merge Request) on your Git platform (GitHub, GitLab, etc.) to merge changes into the main branch (e.g., `main` or `develop`).

## Using Tags in n8n Workflows

**1. Benefits of Using Tags**
   - In n8n environments with a large number of workflows, tags are a powerful tool for organizing, filtering, and quickly finding workflows.
   - They allow categorizing workflows by various criteria, such as their function, status, version, or the project they belong to.
   - They facilitate management and maintenance, especially in large teams or with multiple projects.

**2. How to Use Tags in n8n**
   - To add or edit workflow tags, you can do so from the workflow list view:
     - Hover over the workflow.
     - Click the tag icon that appears.
     - Type the tag name and press Enter. You can add multiple tags.
   - You can also manage tags when editing a workflow, usually in a workflow configuration panel (the exact location may vary slightly with n8n versions).

**3. Suggested Tagging Strategies for MCP Servers and Tools**
   - **Workflow Type:**
     - `mcp-server`: For the main workflow acting as an MCP server (the one containing the `@n8n/n8n-nodes-langchain.mcpTrigger`).
     - `mcp-tool`: For subworkflows representing a specific tool and called by an `@n8n/n8n-nodes-langchain.toolWorkflow`.
     - `subworkflow-helper`: For internal subworkflows that are not direct tools but are reused by others (e.g., a formatting utility).
   - **Tool Domain/Functionality:**
     - `tool:user-management`
     - `tool:document-processing`
     - `tool:calendar-operations`
     - `module:authentication`
   - **Version:**
     - `v1.0`
     - `v1.1`
     - `v2.0-beta`
     - `tool-version:1.2` (if you want to be more specific to differentiate from the MCP server version)
   - **Status:**
     - `status:active`
     - `status:development`
     - `status:deprecated` (for tools or servers that will be replaced)
     - `status:experimental`
   - **Project or Client (if applicable):**
     - `project:alpha`
     - `client:acme-corp`
   - **Priority or Criticality (optional):**
     - `priority:high`
     - `critical`

**4. Combined Examples**
   - An MCP server workflow for users might have the tags: `mcp-server`, `module:user-management`, `v1.0`, `status:active`.
   - A subworkflow that is a tool for getting user profiles: `mcp-tool`, `tool:user-management`, `tool-version:1.0`, `status:active`.
   - A utility subworkflow for validating dates used by several tools: `subworkflow-helper`, `module:utils`, `v1.0`, `status:active`.

**5. Filtering by Tags**
   - In the n8n "Workflows" list view, there is usually a search bar or filter control that allows you to type tag names to display only workflows containing them. This greatly speeds up locating specific workflows.

**Recommendation:** Define a tagging convention for your team or organization and be consistent in its application. A good tagging system is invaluable as your n8n instance grows.

## Global Error Handling in the Main MCP Server Flow

This section addresses how the main MCP server flow should handle failures related to tool orchestration, complementing the [Key Principles for Workflow Robustness](#key-principles-for-workflow-robustness) that apply to each subworkflow.

**1. Importance of Error Handling at the Main Server Level**
   - Ensures that the AI agent consuming the MCP server receives a coherent response (Robustness Principle #1) even if unexpected problems occur in tool orchestration before a specific subworkflow is invoked or after it has (supposedly) completed its execution.

**2. Error Scenarios in the Main Flow and How to Handle Them**

   **a. `@n8n/n8n-nodes-langchain.toolWorkflow` Node Failure**
      - **Possible Cause:** The subworkflow specified in the `toolWorkflow` node does not exist (e.g., incorrect ID, not imported), or there is a critical issue with the `toolWorkflow` node's own configuration that prevents it from even attempting to execute the subworkflow.
      - **Handling:**
        - Apply Robustness Principle #5: Configure the "Settings" > "Error Workflow" tab for the `@n8n/n8n-nodes-langchain.toolWorkflow` node. This dedicated Error Workflow can then generate a standard JSON response (e.g., with `status: "error"`, `data.code: "TOOL_EXECUTION_FAILED"`, and an appropriate message).
        - A global n8n instance "Error Workflow" (Robustness Principle #5) would also act as a safeguard.

   **b. Subworkflow Returns a Structurally Invalid Response**
      - **Possible Cause:** A subworkflow (tool) finishes and returns data, but it does not conform to the expected format (e.g., missing `status` field, or `status` is neither `"success"` nor `"error"`). This indicates a breach of Robustness Principle #1 by the subworkflow.
      - **Handling:**
        - After each `@n8n/n8n-nodes-langchain.toolWorkflow` node in the main flow (or after a `Switch` node routing to several `toolWorkflows`), add an `n8n-nodes-base.if` node to validate the response structure.
        - **`IF` Conditions:** Check if the `status` field exists and if it is either `"success"` OR `"error"`.
        - **`IF` FALSE Branch (Invalid Response):**
          - Connect to an `n8n-nodes-base.set` node that constructs a standard error response.
          - Example error JSON:
            ```json
            {
              "status": "error",
              "data": {
                "code": "INVALID_TOOL_RESPONSE_STRUCTURE",
                "message": "The tool returned a response with an unexpected structure.",
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
        - **`IF` TRUE Branch (Valid Response):** Continue the flow normally.

   **c. Error in Router (e.g., `Switch` Node)**
      - **Possible Cause:** The tool name provided by the AI agent does not match any of the routes defined in the `Switch` node.
      - **Handling:**
        - The `Switch` node in n8n has a "Default" or "Fallback" output. Connect this output to an `n8n-nodes-base.set` node.
        - This `Set` node should generate a standard error response (Robustness Principle #1) indicating the tool was not found.
        - Example error JSON:
          ```json
          {
            "status": "error",
            "data": {
              "code": "TOOL_NOT_FOUND",
              "message": "The requested tool is not available or not recognized.",
              "details": {
                "requested_tool_name": "{{ $json.tool_name_from_ai_if_available }}"
              }
            },
            "meta": {
              "timestamp": "{{ $now.toJSON() }}"
            }
          }
          ```

**3. Additional Considerations**
   - **Consistency:** All errors generated by the main flow must also follow the standard JSON format (Robustness Principle #1).
   - **Logging (Robustness Principle #6):** Consider adding log nodes (e.g., `n8n-nodes-base.logMessage`) in these global error paths to facilitate debugging orchestration issues.
   - **Global n8n Error Workflow (Robustness Principle #5):** A global Error Workflow is a crucial safety net.

Robust error handling at the main MCP server flow level complements error handling within each subworkflow, creating a more resilient and predictable system.
