# Agent Tool Description Format (ATDF)

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/MauricioPerera/agent-tool-description-format)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/MauricioPerera/agent-tool-description-format/actions)

ATDF is an open protocol for describing tools functionally, enabling AI agents to select and use them based on purpose, context, and operation, without relying on technical details.

## Why ATDF?
ATDF simplifies tool integration for AI agents by providing a standardized, functional description format. It eliminates the need for hard-coded tool names or complex technical specs, making agents more adaptable and future-proof.

## Features
- Simple, human-readable JSON/YAML format.
- Model, tool, and prompt agnostic.
- Supports physical and digital tools.
- Validation via JSON Schema.
- Multilingual support (descriptions in English, Spanish, Portuguese, and more).
- Metadata for better organization.
- Usage examples for easier understanding.
- Prerequisites and feedback mechanisms.

## Versions
ATDF is available in two compatible versions:

### Version 0.1.0 (Basic)
- Core functionality with essential fields.
- Simple structure for basic tool descriptions.
- Perfect for getting started or simpler use cases.

### Version 0.2.0 (Enhanced)
- All basic functionality plus optional advanced features:
  - Metadata fields for better organization.
  - Built-in multilingual support.
  - Prerequisites and dependencies.
  - Usage examples with expected outputs.
  - Progress and completion indicators.
- Fully backwards compatible with v0.1.0.

## Installation
```
git clone https://github.com/MauricioPerera/agent-tool-description-format.git
cd agent-tool-description-format
pip install -r tools/requirements.txt
```

## Quick Start
Validate a tool description:
```
python tools/validator.py schema/examples/hole_maker.json
```

Run the demo:
```
python tools/demo/agent_example.py
```

Run the multilingual demo:
```
python tools/demo/trilingual_agent.py
```

Run the showcase demo (with enhanced features):
```
python tools/demo/atdf_showcase.py
```

## Example Tool Description

### Basic (v0.1.0)
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  "when_to_use": "Usar cuando necesites generar un agujero en una pared",
  "how_to_use": {
    "inputs": [
      { "name": "location", "type": "string", "description": "Ubicación del agujero" },
      { "name": "bit_id", "type": "string", "description": "ID de la broca" }
    ],
    "outputs": {
      "success": "Agujero creado con éxito",
      "failure": [
        { "code": "invalid_bit", "description": "Broca no compatible" }
      ]
    }
  }
}
```

### Enhanced (v0.2.0)
For an example of a tool with enhanced features, see [schema/examples/enhanced_hole_maker.json](schema/examples/enhanced_hole_maker.json).

## Multilingual Support
ATDF supports tool descriptions in any language. The protocol itself is language-agnostic, allowing AI agents to work with tool descriptions in the user's preferred language. Examples are provided in English, Spanish and Portuguese.

See the [multilingual documentation](docs/multilingual.md) for details on how to implement multilingual tool support.

## Documentation
- [Specification](docs/specification.md): Technical details of the protocol.
- [Contributing](docs/contributing.md): How to contribute.
- [Examples](schema/examples): Sample tool descriptions.
- [Multilingual Support](docs/multilingual.md): Information about multilingual features.
- [Changelog](docs/changelog.md): Version history and changes.

## Get Involved
Have ideas or feedback? Open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues)!

## License
MIT License. See [LICENSE](LICENSE).

## Status
Current version: 0.2.0. Contributions welcome!
