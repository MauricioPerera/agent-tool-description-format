[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

# Agent Tool Description Format (ATDF)

Welcome to the documentation for the **Agent Tool Description Format (ATDF)**, an open protocol for describing tools functionally to enable AI agents to select and use them based on purpose, context, and operation, without relying on specific implementation details.

## Current Version

**Current version: 0.2.0** - See the [changelog](changelog.md) for details on the latest updates.

## Introduction

ATDF is designed to solve the problem of tool integration for AI agents. Instead of requiring hard-coded tool names or complex technical APIs, ATDF provides a standardized way to describe tools based on:

1. **What** the tool does
2. **When** it should be used
3. **How** it is used

This functional approach allows AI agents to select tools based on the task at hand, rather than requiring specific knowledge about tool names or APIs.

## Key Features

### Core Features (v0.1.0)
- **Simple, Human-Readable Format**: JSON/YAML structure that's easy to understand.
- **Model Agnostic**: Works with any AI agent model.
- **Tool Agnostic**: Describes both physical tools (e.g., drills) and digital tools (e.g., APIs).
- **Prompt Agnostic**: Tool selection based on function, not specific names.
- **Schema Validation**: JSON Schema for validating tool descriptions.

### Enhanced Features (v0.2.0)
- **Metadata Support**: Organize tools with version, author, tags, and category information.
- **Rich Multilingual Support**: Built-in localization for multiple languages.
- **Prerequisites and Dependencies**: Specify required tools, conditions, and permissions.
- **Feedback Mechanisms**: Progress indicators and completion signals.
- **Usage Examples**: Real-world examples with inputs and expected outputs.
- **Complex Input Types**: Support for nested objects and advanced schemas.

## Quick Links

- [Specification](specification.md): Detailed technical specification of the ATDF protocol.
- [Examples](examples.md): Sample tool descriptions and how to create your own.
- [Multilingual Support](multilingual.md): Information about using multiple languages.
- [Version Comparison](version-comparison/README.md): Detailed comparison between ATDF versions.
- [SDK Documentation](sdk.md): How to use the ATDF SDK in your applications.
- [Contributing](contributing.md): Guidelines for contributing to ATDF.
- [Changelog](changelog.md): History of ATDF versions and changes.

## Getting Started

To start using ATDF, you can:

1. **Explore Examples**: Check out the [example tool descriptions](examples.md) to understand the format.
2. **Create Your Own**: Follow the [specification](specification.md) to create tool descriptions.
3. **Validate Tools**: Use the validator to ensure your tool descriptions are valid:
   ```bash
   python tools/validator.py path/to/your/tool.json
   ```
4. **Try the Demo**: Run the demonstration agents to see ATDF in action:
   ```bash
   python tools/demo/atdf_showcase.py
   ```

## Use Cases

ATDF is designed for a wide range of applications, including:

- **AI Agents**: Helping AI systems select and use tools appropriately.
- **Robotics**: Describing physical tools for robotic systems.
- **API Integration**: Standardizing descriptions of APIs and web services.
- **Multimodal Applications**: Bridging different types of tools in a unified format.
- **Multilingual Systems**: Supporting tool descriptions across different languages.

## License

ATDF is licensed under the MIT License. See the [LICENSE](license.md) file for details.

---

[GitHub Repository](https://github.com/MauricioPerera/agent-tool-description-format) | [Changelog](changelog.md) 