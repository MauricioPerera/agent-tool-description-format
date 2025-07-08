# Changelog

All notable changes to the Agent Tool Description Format (ATDF) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-01-XX

### 🔄 Updated
- **Global Date Updates**: Updated all date references from 2024 to 2025 across the entire project
  - Updated example dates in all documentation files
  - Updated timestamps in JSON examples and error messages
  - Updated reservation IDs and booking references
  - Updated changelog version dates
  - Updated metadata timestamps in web documentation

### 📝 Documentation Updates
- **README.md**: Updated example timestamps and date references
- **ATDF_SPECIFICATION.md**: Updated check-in/check-out dates and example timestamps
- **CONCEPTS.md**: Updated example date references
- **IMPLEMENTATION_GUIDE.md**: Updated hotel reservation example dates
- **BEST_PRACTICES.md**: Updated all example dates and reservation IDs
- **EXAMPLES.md**: Updated all date examples and timestamps

### 🔧 Code Updates
- **examples/fastapi_mcp_integration.py**: Updated error message date examples
- **examples/mcp_client_example.py**: Updated reservation and booking dates
- **docs/en/fastapi_mcp_integration.md**: Updated all example dates
- **docs/en/fastapi_mcp_summary.md**: Updated validation date examples

### 🌐 Web Documentation
- **docs/web/versions.html**: Updated created_at and updated_at timestamps
- **docs/web/index.html**: Updated metadata timestamps
- **docs/version-comparison/README.md**: Updated example timestamps

### 📋 Enhancement Proposals
- **docs/enhancement_proposal.md**: Updated updated_at timestamps
- **docs/es/enhancement_proposal.md**: Updated updated_at timestamps  
- **docs/pt/enhancement_proposal.md**: Updated updated_at timestamps

### 🎯 Summary
This update ensures all project documentation and examples reflect the correct year (2025) when the project originated and was updated. All date references have been consistently updated across:
- 15+ documentation files
- 3 example code files
- 5 web documentation files
- 3 enhancement proposal files
- Multiple JSON examples and error messages

## [2.0.0] - 2025-01-XX

### 🚀 Added - Major New Features

#### **Enriched Response Standard** - Foundation of ATDF
- **NEW**: Comprehensive error responses with detailed `expected` field
- **NEW**: Self-documenting error messages with step-by-step solutions
- **NEW**: Validation results showing exactly which conditions failed
- **NEW**: Examples of valid and invalid inputs in error responses
- **NEW**: Solution field with actionable guidance for fixing issues
- **NEW**: Schema for validating enriched responses (`enriched_response_schema.json`)
- **NEW**: Complete implementation examples in Python
- **NEW**: Documentation guide for enriched responses (`enriched_responses_guide.md`)

#### Enhanced Schema Support
- **NEW**: Schema version compatibility field (`schema_version`) in both basic and enhanced schemas
- **NEW**: Smart validation function that auto-detects schema version
- **NEW**: Bidirectional conversion between basic and enhanced formats
- **NEW**: Alternative identifier support (`tool_id` and `id` fields)

#### Multilingual Improvements
- **ENHANCED**: Robust detection of Spanish, English, and Portuguese queries
- **ENHANCED**: Improved localization support in tool descriptions
- **ENHANCED**: Better error message localization

#### MCP Integration
- **NEW**: MCP (Model Context Protocol) to ATDF converters in Python
- **NEW**: MCP to ATDF converters in JavaScript
- **NEW**: Enhanced n8n integration with enriched response support

### 🔧 Changed

#### SDK Enhancements
- **ENHANCED**: Improved error handling with enriched response validation
- **ENHANCED**: Better tool loading and validation mechanisms
- **ENHANCED**: More robust parameter handling
- **ENHANCED**: Enhanced vector search capabilities

#### Documentation
- **UPDATED**: README with enriched response examples and benefits
- **UPDATED**: Complete documentation restructuring
- **NEW**: Practical implementation examples
- **NEW**: Best practices guide for enriched responses

### 🐛 Fixed

- **FIXED**: Schema validation issues with complex input types
- **FIXED**: Tool loading edge cases
- **FIXED**: Multilingual detection accuracy
- **FIXED**: Error message consistency

### 📚 Documentation

- **NEW**: `docs/en/enriched_responses_guide.md` - Complete guide to enriched responses
- **NEW**: `examples/enriched_responses_example.py` - Practical implementation examples
- **NEW**: `schema/enriched_response_schema.json` - Schema for validating enriched responses
- **UPDATED**: All existing documentation to reflect v2.0.0 changes

### 🔄 Migration Guide

#### From v1.x to v2.0.0

1. **Update Schema Version**: Add `"schema_version": "2.0.0"` to your tool descriptions
2. **Implement Enriched Responses**: Update your tools to use the new enriched response format
3. **Update Error Handling**: Replace simple error messages with detailed `expected` fields
4. **Validate Responses**: Use the new enriched response schema for validation

#### Example Migration

**Before (v1.x):**
```json
{
  "status": "error",
  "message": "Invalid date range"
}
```

**After (v2.0.0):**
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

## [1.2.0] - 2023-XX-XX

### Added
- Initial multilingual support
- Basic schema validation
- Python SDK foundation
- Vector search capabilities

### Changed
- Improved tool description format
- Enhanced documentation structure

### Fixed
- Various bug fixes and improvements

## [1.1.0] - 2023-XX-XX

### Added
- Basic ATDF specification
- JSON schema definitions
- Initial documentation

### Changed
- Core format improvements

## [1.0.0] - 2023-XX-XX

### Added
- Initial release of ATDF
- Basic tool description format
- Core documentation

---

## Contributing to Changelog

When adding new entries to this changelog, please follow these guidelines:

1. **Use the existing format** and structure
2. **Group changes** by type (Added, Changed, Fixed, etc.)
3. **Be descriptive** but concise
4. **Include migration notes** for breaking changes
5. **Add examples** when introducing new features
6. **Update version numbers** appropriately

## Version History

- **v2.0.1**: Global date updates from 2024 to 2025 across all documentation and examples
- **v2.0.0**: Enriched Response Standard, enhanced schemas, multilingual improvements
- **v1.2.0**: Multilingual support, basic validation, SDK foundation
- **v1.1.0**: Basic specification, JSON schemas, documentation
- **v1.0.0**: Initial release 