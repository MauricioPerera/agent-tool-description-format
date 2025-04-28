# Agent Tool Description Format (ATDF)

ATDF is an open protocol for describing tools functionally, enabling AI agents to select and use them based on purpose, context, and operation, without relying on technical details.

## Features
- Simple, human-readable JSON/YAML format.
- Model, tool, and prompt agnostic.
- Supports physical and digital tools.
- Validation via JSON Schema.

## Installation
```bash
git clone https://github.com/<your-username>/agent-tool-description-format.git
cd agent-tool-description-format
pip install -r tools/requirements.txt
```

## Quick Start
Validate a tool description:
```bash
python tools/validator.py schema/examples/hole_maker.json
```

Run the demo:
```bash
python tools/demo/agent_example.py
```

## Documentation
- [Specification](docs/specification.md): Technical details of the protocol.
- [Contributing](docs/contributing.md): How to contribute.
- [Examples](schema/examples): Sample tool descriptions.

## License
MIT License. See [LICENSE](LICENSE).

## Status
Current version: 0.1.0 (Draft). Contributions welcome!
# agent-tool-description-format
