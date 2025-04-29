[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

# Agent Tool Description Format (ATDF) Specification (v0.1.0)

## Introduction

The **Agent Tool Description Format (ATDF)** is an open protocol designed to describe tools in a functional, implementation-agnostic manner. It enables AI agents to select and use tools based on their purpose, context, and operation, without relying on specific technical details or tool names. ATDF promotes flexibility, scalability, and interoperability across different agents and toolsets.

ATDF achieves this by standardizing tool descriptions around three core questions:
- **What** does the tool do?
- **When** should it be used?
- **How** is it used?

## Motivation

Current approaches to tool integration in AI agents often rely on hard-coded tool names, proprietary APIs, or detailed technical specifications. This creates dependencies that limit adaptability and complicate the adoption of new tools. ATDF addresses these challenges by providing a simple, functional description format that is:
- **Tool-agnostic**: Works with physical (e.g., drills) and digital (e.g., APIs) tools.
- **Model-agnostic**: Usable by any AI agent, regardless of its architecture.
- **Prompt-agnostic**: Allows prompts to reference tool functions (e.g., "make a hole") rather than specific tools.

## Specification

Each tool must be described in a structured format (JSON or YAML) with the following required fields:

### Structure
- **`tool_id`** (string): A unique identifier for the tool.
  - Example: `"hole_maker_v1"`
- **`description`** (string): A concise explanation of what the tool does, avoiding technical details.
  - Example: `"Permite crear agujeros en superficies sólidas"`
- **`when_to_use`** (string): The context or conditions under which the tool should be used.
  - Example: `"Usar cuando necesites generar un agujero en una pared u otra superficie perforable"`
- **`how_to_use`** (object): Details the operation of the tool, including inputs and outputs.
  - **`inputs`** (array): List of input parameters, each with:
    - `name` (string): Parameter name.
    - `type` (string): Data type (e.g., `"string"`, `"number"`).
    - `description` (string, optional): Parameter purpose.
  - **`outputs`** (object): Possible results of using the tool.
    - `success` (string): Message for successful operation.
    - `failure` (array): List of possible errors, each with:
      - `code` (string): Error identifier.
      - `description` (string): Error explanation.

### Example
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  "when_to_use": "Usar cuando necesites generar un agujero en una pared u otra superficie perforable",
  "how_to_use": {
    "inputs": [
      { "name": "location", "type": "string", "description": "Ubicación del agujero" },
      { "name": "bit_id", "type": "string", "description": "ID de la broca" }
    ],
    "outputs": {
      "success": "Agujero creado con éxito",
      "failure": [
        { "code": "invalid_bit", "description": "Broca no compatible" },
        { "code": "invalid_surface", "description": "Superficie no perforable" }
      ]
    }
  }
}
```

### JSON Schema
The structure of ATDF descriptions is formally defined in [schema/atdf_schema.json](../schema/atdf_schema.json). Tools must validate against this schema to ensure compliance.

## Rules and Considerations
- **Implementation Agnosticism**: Descriptions must focus on function, not implementation. For example, a tool described as "creates holes" could be a drill, laser, or other device.
- **Clarity**: Fields like `description` and `when_to_use` should be concise and understandable by both humans and AI agents.
- **Extensibility**: Future versions may add optional fields (e.g., `prerequisites`, `category`) while maintaining backward compatibility.
- **Validation**: Use the provided validator script (`tools/validator.py`) to check descriptions against the schema.

## Use Cases
- **Physical Tools**: Describing tools like drills, brushes, or hammers for robotic agents.
- **Digital Tools**: Defining APIs or software functions (e.g., text translation, image processing).
- **Hybrid Systems**: Enabling agents to switch between tools (e.g., from a drill to a laser) without changing prompts.

## Future Extensions
Planned enhancements for ATDF v0.2.0 and beyond include:
- Optional fields for prerequisites or tool categories.
- Support for complex input/output types (e.g., nested objects).
- Integration with tool discovery mechanisms.

## Contributions
ATDF is an open protocol, and contributions are welcome. Please see [Contributing](../docs/contributing.md) for guidelines on submitting issues, pull requests, or new tool descriptions.

## Contact
For questions or feedback, contact Mauricio Perera at [mauricio.perera@gmail.com](mailto:mauricio.perera@gmail.com) or open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues).

## License
ATDF is licensed under the MIT License. See [LICENSE](../LICENSE) for details.
