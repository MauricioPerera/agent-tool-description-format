[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Enriched Responses Guide](enriched_responses_guide.md) | [n8n MCP Guide](n8n_mcp_server_guide.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

**Languages:** [English (en)](index.md) | [Español (es)](../es/index.md) | [Português (pt)](../pt/index.md)

## 📚 ATDF Documentation

### 📖 **Main Documents**
- **[README](../../README.md)** - Introduction and quick start
- **[ATDF Specification](../docs/ATDF_SPECIFICATION.md)** - Complete format specification
- **[Core Concepts](../docs/CONCEPTS.md)** - Key concepts explained
- **[Implementation Examples](../docs/examples.md)** - Examples in multiple languages and tools
- **[Implementation Guide](./IMPLEMENTATION_GUIDE.md)** - How to implement ATDF
- **[Best Practices](./BEST_PRACTICES.md)** - Implementation recommendations

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
- **[Examples](examples.md)** - Sample tool descriptions and usage patterns
- **[Enriched Responses Guide](enriched_responses_guide.md)** - **NEW** - Complete guide to the enriched response standard
- **[n8n MCP Guide](n8n_mcp_server_guide.md)** - Integration guide for n8n workflows

### Development & Contribution

- **[Contributing](contributing.md)** - How to contribute to ATDF
- **[Multilingual](multilingual.md)** - Multilingual support and localization
- **[Changelog](changelog.md)** - Version history and changes

### Legal

- **[License](license.md)** - MIT License details

## 🎯 Quick Start

### 1. Understanding Enriched Responses

The core innovation of ATDF v2.0.0 is the **Enriched Response Standard**. Instead of simple error messages, tools now provide comprehensive context:

```json
{
  "status": "error",
  "data": {
    "code": "INVALID_DATE_RANGE",
    "message": "Date range validation failed",
    "details": {
      "field": "date_range",
      "received": { "start_date": "2023-12-01", "end_date": "2023-11-01" },
      "expected": {
        "conditions": [
          "start_date must be before end_date",
          "both dates must be after current date"
        ],
        "examples": { "valid_range": { "start_date": "2023-10-28", "end_date": "2023-11-15" } }
      },
      "solution": "Adjust dates so that start_date is before end_date and both are after current date"
    }
  },
  "meta": { "timestamp": "2023-10-27T10:35:00Z" }
}
```

### 2. Basic Tool Description

```json
{
  "schema_version": "2.0.0",
  "tool_id": "date_validator",
  "description": "Validates date ranges with enriched error responses",
  "when_to_use": "When you need to validate date ranges with detailed feedback",
  "how_to_use": {
    "inputs": [
      {
        "name": "start_date",
        "type": "string",
        "description": "Start date in ISO 8601 format",
        "required": true
      },
      {
        "name": "end_date", 
        "type": "string",
        "description": "End date in ISO 8601 format",
        "required": true
      }
    ],
    "outputs": {
      "success": "Date range is valid",
      "failure": [
        {
          "code": "INVALID_DATE_RANGE",
          "description": "Date range validation failed"
        }
      ]
    }
  }
}
```

### 3. Implementation Example

```python
from examples.enriched_responses_example import EnrichedResponseValidator

validator = EnrichedResponseValidator()
result = validator.validate_date_range("2023-12-01T10:00:00Z", "2023-11-01T15:30:00Z")
print(json.dumps(result, indent=2))
```

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