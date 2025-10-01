[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [n8n MCP Guide](n8n_mcp_server_guide.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

**Languages:** [English (en)](index.md) | [Español (es)](../es/index.md) | [Português (pt)](../pt/index.md)

## 🎯 Quick Start

1. **Pick the right schema**
   - 1.x basic (`schema/atdf_schema.json`): minimal descriptors with `tool_id`, `description`, `when_to_use`, and `how_to_use`.
   - 2.x enhanced (`schema/enhanced_atdf_schema.json`): adds `metadata`, `localization`, `prerequisites`, `examples`, and `feedback`.
   See [Version Compatibility](version_compatibility.md) if you are unsure.

2. **Draft the descriptor**

```json
{
  "schema_version": "2.0.0",
  "tool_id": "date_validator",
  "description": "Validates date ranges with enriched error responses",
  "when_to_use": "Use when you need a full explanation of invalid date ranges",
  "how_to_use": {
    "inputs": [
      {"name": "start_date", "type": "string", "description": "Start date in ISO 8601 format", "required": true},
      {"name": "end_date", "type": "string", "description": "End date in ISO 8601 format", "required": true}
    ],
    "outputs": {
      "success": "Date range is valid",
      "failure": [
        {"code": "INVALID_DATE_RANGE", "description": "Start date must be before end date"}
      ]
    }
  }
}
```

Set `schema_version` to `1.0.0` and omit optional sections like `metadata` and `examples` for a 1.x descriptor.

3. **Validate and test**

```bash
python tools/validator.py examples/date_validator.json --schema schema/atdf_schema.json
python tools/validate_enhanced.py examples/date_validator.json
python tests/run_all_tests.py
```

For enriched error payloads see the [Enriched Responses Guide](enriched_responses_guide.md).
## 📚 ATDF Documentation

### 📖 **Main Documents**
- **[README](../../README.md)** - Introduction and quick start
- **[ATDF Specification](../docs/ATDF_SPECIFICATION.md)** - Complete format specification
- **[Core Concepts](../docs/CONCEPTS.md)** - Key concepts explained
- **[Implementation Examples](../docs/examples.md)** - Examples in multiple languages and tools
- **[Implementation Guide](./IMPLEMENTATION_GUIDE.md)** - How to implement ATDF
- **[Best Practices](./BEST_PRACTICES.md)** - Implementation recommendations
- **[ATDF + MCP + n8n Flow](n8n_mcp_integration_flow.md)** - Architecture and usage options for MCP workflows

### 📊 **Visual Resources**
- **[Mermaid Diagrams](../MERMAID_DIAGRAMS.md)** - ATDF flow and architecture diagrams

## 🚀 What's New in v2.0.0

**Enriched Response Standard** - The foundation of ATDF with comprehensive error handling:

- **Detailed `expected` fields** that provide complete context about what was expected
- **Self-documenting error messages** with step-by-step solutions
- **Validation results** showing exactly which conditions failed
- **Examples of valid and invalid inputs** in error responses
- **Actionable solution guidance** for fixing issues

## 📚 Documentation Sections

### Core Documentation

- **[Specification](specification.md)** - The formal ATDF specification and technical details
- **[Version Compatibility](version_compatibility.md)** - Mapping between legacy labels and current schemas
- **[Examples](examples.md)** - Sample tool descriptions and usage patterns
- **[Enriched Responses Guide](enriched_responses_guide.md)** - **NEW** - Complete guide to the enriched response standard
- **[n8n MCP Guide](n8n_mcp_server_guide.md)** - Integration guide for n8n workflows

### Development & Contribution

- **[Contributing](contributing.md)** - How to contribute to ATDF
- **[Redesign Guidelines](redesign_guidelines.md)** - Planning considerations for future protocol versions
- **[Multilingual](multilingual.md)** - Multilingual support and localization
- **[Changelog](changelog.md)** - Version history and changes

### Legal

- **[License](license.md)** - MIT License details

## 🔧 Key Features

### Enriched Error Handling
- **Comprehensive Context**: Detailed information about what went wrong
- **Actionable Solutions**: Step-by-step guidance for fixing issues
- **Validation Results**: Specific feedback on which conditions failed
- **Examples**: Valid and invalid input examples

### Multilingual Support
- **Multiple Languages**: Support for Spanish, English, and Portuguese
- **Localized Messages**: Error messages in the user's preferred language
- **Consistent Format**: Same structure across all languages

### Schema Validation
- **Smart Detection**: Automatically detects schema version
- **Bidirectional Conversion**: Convert between basic and enhanced formats
- **Comprehensive Validation**: Validate both tool descriptions and responses

### Integration Ready
- **n8n Support**: Complete integration guide for n8n workflows
- **MCP Compatibility**: Convert from Model Context Protocol to ATDF
- **SDK Support**: Python SDK for easy implementation

## 📖 Getting Started

1. **Read the [Enriched Responses Guide](enriched_responses_guide.md)** to understand the core innovation
2. **Review [Examples](examples.md)** to see practical implementations
3. **Check the [Specification](specification.md)** for technical details
4. **Try the [n8n Integration](n8n_mcp_server_guide.md)** if you're using n8n

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details on:

- Code contributions
- Documentation improvements
- Bug reports
- Feature requests
- Translation contributions

## 📄 License

ATDF is licensed under the MIT License. See [License](license.md) for details.

---

**ATDF v2.0.0** - Standard format for describing tools functionally, enabling smarter, multilingual AI agents with enriched error handling. 
