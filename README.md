# Agent Tool Description Format (ATDF)

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/MauricioPerera/agent-tool-description-format)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/MauricioPerera/agent-tool-description-format/actions/workflows/ci.yml/badge.svg)](https://github.com/MauricioPerera/agent-tool-description-format/actions)

ATDF is an open protocol for describing tools functionally, enabling AI agents to select and use them based on purpose, context, and operation, without relying on technical details.

## Why ATDF?
ATDF simplifies tool integration for AI agents by providing a standardized, functional description format. It eliminates the need for hard-coded tool names or complex technical specs, making agents more adaptable and future-proof.

## Features
- Simple, human-readable JSON/YAML format.
- Model, tool, and prompt agnostic.
- Supports physical and digital tools.
- Validation via JSON Schema.

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

## Example Tool Description
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

## Documentation
- [Specification](docs/specification.md): Technical details of the protocol.
- [Contributing](docs/contributing.md): How to contribute.
- [Examples](schema/examples): Sample tool descriptions.

## Get Involved
Have ideas or feedback? Open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues) or join the [discussion](https://github.com/MauricioPerera/agent-tool-description-format/discussions)!

## License
MIT License. See [LICENSE](LICENSE).

## Status
Current version: 0.1.0 (Draft). Contributions welcome!
