# Agent Tool Description Format (ATDF)

[![Version](https://img.shields.io/badge/ATDF_Spec-v0.2.0-blue)](docs/specification.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-multilingual-orange)](docs/index.md)

**ATDF (Agent Tool Description Format)** is an open, standardized format for describing tools (both digital APIs and physical implements) in a way that allows AI agents to understand their purpose, context, and operation, enabling them to select and utilize tools effectively without relying on hard-coded names or specific implementation details.

This repository contains:

*   The **ATDF Specification**: Formal definition of the format.
*   **JSON Schemas**: For validating ATDF descriptions.
*   **Examples**: Demonstrating various tool descriptions.
*   **Documentation**: Detailed guides, usage examples, and contribution guidelines (available in multiple languages).
*   **Python SDK**: A helper library for working with ATDF descriptions in Python applications.

## What's New in v2.0.0

- **Schema Version Compatibility**: Both basic and enhanced schemas now include a `schema_version` field
- **Smart Validation**: New `validate_tool_smart` function automatically detects schema version
- **Bidirectional Conversion**: Convert between basic and enhanced formats in both directions
- **Robust Multilingual Support**: Improved detection of Spanish, English, and Portuguese queries
- **Alternative Identifiers**: Support for both `tool_id` and `id` fields interchangeably
- **MCP Format Converters**: New tools to convert from MCP (Model Context Protocol) to ATDF in both Python and JavaScript

See the [CHANGELOG](CHANGELOG.md) for full details and [Usage Examples](docs/usage_examples.md) for practical demonstrations.

## Key Goals of ATDF

*   **Functional Description**: Focus on *what* a tool does, *when* to use it, and *how* to use it, rather than technical implementation.
*   **Model Agnosticism**: Designed to work with various AI agent architectures.
*   **Tool Agnosticism**: Capable of describing diverse tools (APIs, physical tools, software functions).
*   **Standardization**: Provides a common language for tool description, facilitating interoperability.
*   **Multilingual Support**: Allows tool descriptions to be understood and used across different human languages.

## Documentation (Multilingual)

Comprehensive documentation detailing the ATDF specification, examples, usage guides, and contribution process is available in multiple languages.

➡️ **[Access the Documentation (Select Language)](docs/index.md)**

Key documents include:

*   [Specification](docs/specification.md): The core technical details of the format.
*   [Examples](docs/examples.md): Sample tool descriptions.
*   [Multilingual Support](docs/multilingual.md): How localization works.
*   [Usage Examples](docs/usage_examples.md): Practical examples of using ATDF.
*   [Contributing](docs/contributing.md): How to contribute to the format or documentation.
*   [Changelog](CHANGELOG.md): Version history.

## Python SDK for ATDF (Optional Helper Library)

[![SDK Version](https://img.shields.io/badge/SDK_Version-0.3.0-blue)](sdk/)
[![PyPI Status](https://img.shields.io/pypi/v/atdf-sdk.svg)](https://pypi.org/project/atdf-sdk/) <!-- Placeholder -->
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/MauricioPerera/agent-tool-description-format/actions) <!-- Assumes CI setup -->

Included in this repository is a Python SDK to facilitate working with ATDF descriptions.

**SDK Features:**

*   Load and validate ATDF descriptions (JSON, YAML).
*   Semantic tool search using vector embeddings (optional).
*   Programmatic creation and manipulation of tool descriptions.
*   Export to different formats (e.g., JSON Schema).
*   Convert between basic and enhanced formats.
*   Intelligent, version-aware validation.

### SDK Installation

You can install the SDK dependencies using pip and the provided requirements files.

**1. Basic Installation (Core SDK):**

Installs only the essential libraries needed to load, validate, and work with ATDF descriptions (like PyYAML and jsonschema).

```bash
# Clone the repo if you haven't already
# git clone https://github.com/MauricioPerera/agent-tool-description-format.git
# cd agent-tool-description-format

# Install core dependencies
pip install -r requirements.txt

# Alternatively, if the package is published on PyPI:
# pip install atdf-sdk 
```

**2. Installation with Vector Search Support:**

If you need the semantic search capabilities, install the additional vector dependencies *after* the basic installation:

```bash
# First, ensure core dependencies are installed (see step 1)

# Install optional vector search dependencies
pip install -r requirements-vector.txt

# Alternatively, if published with extras on PyPI:
# pip install atdf-sdk[vector]
```

**3. Development Installation:**

To set up a development environment with all dependencies (core, vector, demo, testing, docs):

```bash
# Installs everything from requirements.txt, requirements-vector.txt, 
# plus development tools like thefuzz and markdown-link-check
pip install -r requirements-dev.txt
```

### SDK Basic Usage

```python
# (Keep the existing SDK usage example here)
from sdk import ATDFSDK
from sdk.core.schema import ATDFTool, ATDFToolParameter

# Inicializar el SDK (cargará herramientas desde ./tools si existe)
sdk = ATDFSDK(tools_directory="./tools", auto_load=True)

# Cargar herramientas adicionales desde un directorio
tools_extra = sdk.load_tools_from_directory("./more_tools")

# Obtener todas las herramientas cargadas
all_tools = sdk.get_all_tools()

# Crear parámetros para una nueva herramienta
param1 = ATDFToolParameter(
    name="param1",
    description="Un parámetro de ejemplo de tipo texto",
    type="string",
    required=True
)
param2 = ATDFToolParameter(
    name="param2",
    description="Un parámetro de ejemplo de tipo numérico",
    type="number",
    required=False,
    default=42
)

# Crear una nueva herramienta usando las clases del esquema
nueva_herramienta = ATDFTool(
    name="Herramienta Nueva",
    description="Una herramienta creada programáticamente con el SDK",
    parameters=[param1, param2],
    tags=["sdk", "ejemplo"],
    category="testing"
)

# Añadir la herramienta creada al SDK
sdk.tools.append(nueva_herramienta)
if sdk.vector_store:
    sdk.vector_store.add_tool(nueva_herramienta.to_dict())

# Guardar todas las herramientas (incluida la nueva) en un archivo
sdk.save_tools_to_file("output/todas_las_herramientas.json", format="json")
```

### Advanced SDK Features (New in v2.0.0)

```python
# Smart validation of tools (auto-detects schema version)
from tools.validator import validate_tool_smart

# Convert between formats
from tools.converter import convert_to_enhanced, convert_to_basic, load_tool, save_tool

# See docs/usage_examples.md for complete usage examples
```

*(For detailed SDK usage and advanced features like vector search, please refer to the SDK's own documentation or examples within the `sdk/` directory - Link to be added)*

## Contributing

Contributions to both the ATDF specification and the Python SDK are welcome! Please read our [Contributing Guidelines](docs/contributing.md) before submitting pull requests or issues.

## License

The ATDF specification and the accompanying SDK are licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
