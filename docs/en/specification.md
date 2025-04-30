[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

**Languages:** [English (en)](specification.md) | [Español (es)](../es/specification.md) | [Português (pt)](../pt/specification.md)

# Agent Tool Description Format (ATDF) Specification (v0.1.0 & v0.2.0)

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
The structure of ATDF descriptions is formally defined in [schema/atdf_schema.json](../../schema/atdf_schema.json). Tools must validate against this schema to ensure compliance.

## Rules and Considerations
- **Implementation Agnosticism**: Descriptions must focus on function, not implementation. For example, a tool described as "creates holes" could be a drill, laser, or other device.
- **Clarity**: Fields like `description` and `when_to_use` should be concise and understandable by both humans and AI agents.
- **Extensibility**: Future versions may add optional fields (e.g., `prerequisites`, `category`) while maintaining backward compatibility.
- **Validation**: Use the provided validator script (`tools/validator.py`) to check descriptions against the schema.

## Use Cases
- **Physical Tools**: Describing tools like drills, brushes, or hammers for robotic agents.
- **Digital Tools**: Defining APIs or software functions (e.g., text translation, image processing).
- **Hybrid Systems**: Enabling agents to switch between tools (e.g., from a drill to a laser) without changing prompts.

## Version Differences

### Version 0.1.0 (Basic)
The initial version focuses on the core functionality with minimal required fields:
- `tool_id`: Tool identifier
- `description`: What the tool does
- `when_to_use`: When to use the tool
- `how_to_use`: Input parameters and output messages

### Version 0.2.0 (Enhanced)
The enhanced version adds several optional fields to improve tool descriptions:

#### New Optional Fields
- **`metadata`** (object): Additional information about the tool.
  - `version` (string): Tool version.
  - `author` (string): Tool author or organization.
  - `tags` (array): Keywords related to the tool.
  - `category` (string): Tool category.
  - `created_at` (string): Creation date.
  - `updated_at` (string): Last update date.

- **`localization`** (object): Multilingual support.
  - Multiple language codes (e.g., `en`, `es`, `pt`), each containing:
    - `description` (string): Localized description.
    - `when_to_use` (string): Localized usage context.

- **`prerequisites`** (object): Requirements for using the tool.
  - `tools` (array): Other tools needed before using this one.
  - `conditions` (array): Environmental conditions required.
  - `permissions` (array): Required permissions or authorizations.

- **`feedback`** (object): Signals for monitoring tool usage.
  - `progress_indicators` (array): Signs that indicate progress.
  - `completion_signals` (array): Signs that the operation is complete.

- **`examples`** (array): Usage examples with:
  - `title` (string): Example title.
  - `description` (string): Example description.
  - `inputs` (object): Sample input values.
  - `expected_output`: Expected result.

#### Enhancements to Existing Fields
- Input parameters can now include complex schemas with nested objects.
- Output messages can have more detailed error structures.

#### Compatibility
v0.2.0 maintains backward compatibility with v0.1.0. All v0.1.0 tools are valid in v0.2.0, but newer fields are ignored by systems that only support v0.1.0.

### Example (Enhanced v0.2.0)
For a complete example of an enhanced tool description, see [schema/examples/enhanced_hole_maker.json](../../schema/examples/enhanced_hole_maker.json).

## Future Extensions
Planned enhancements for ATDF v0.3.0 and beyond include:
- Integration with tool discovery mechanisms.
- Support for tool chaining and workflows.
- Enhanced security considerations and access control.

## Contributions
ATDF is an open protocol, and contributions are welcome. Please see [Contributing](contributing.md) for guidelines on submitting issues, pull requests, or new tool descriptions.

## Contact
For questions or feedback, contact Mauricio Perera at [mauricio.perera@gmail.com](mailto:mauricio.perera@gmail.com) or open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues).

## License
ATDF is licensed under the MIT License. See [LICENSE](../../LICENSE) for details.
