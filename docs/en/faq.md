# Frequently Asked Questions (FAQ) - ATDF v2.0.0

## General Questions

### Q: What is ATDF v2.0.0?
**A:** ATDF v2.0.0 introduces the **Enriched Response Standard** as the foundation of the Agent Tool Description Format. This version focuses on comprehensive error handling with detailed context, actionable solutions, and self-documenting responses.

### Q: What's the main difference between v1.x and v2.0.0?
**A:** The main difference is the introduction of enriched responses. Instead of simple error messages like `"Invalid input"`, v2.0.0 provides detailed context about what was expected, what was received, and how to fix the issue.

### Q: Is v2.0.0 backward compatible?
**A:** Partially. While the basic tool description format remains compatible, the error response format has changed significantly. Tools using the old error format will need to be updated to use enriched responses.

## Enriched Responses

### Q: What is an enriched response?
**A:** An enriched response is a comprehensive error message that includes:
- **Detailed context** about what went wrong
- **Specific expectations** with conditions and constraints
- **Examples** of valid and invalid inputs
- **Actionable solutions** with step-by-step guidance
- **Validation results** showing which conditions failed

### Q: Why are enriched responses important?
**A:** Enriched responses provide several benefits:
- **Better user experience** with clear guidance
- **Reduced support tickets** as users can self-solve issues
- **Improved debugging** with detailed error context
- **AI-ready** for intelligent error handling by AI agents
- **Self-documenting** responses serve as documentation

### Q: How do I implement enriched responses?
**A:** You can implement enriched responses in several ways:
1. **Follow the structure** defined in the enriched response schema
2. **Extend the base validator** class for custom validations
3. **Use the provided examples** as templates

### Q: What's the structure of an enriched error response?
**A:** An enriched error response follows this structure:
```json
{
  "status": "error",
  "data": {
    "code": "UNIQUE_ERROR_CODE",
    "message": "Human-readable description",
    "details": {
      "field": "field_name",
      "received": { /* what was received */ },
      "expected": { /* what was expected */ },
      "validation_results": { /* specific failures */ },
      "solution": "Step-by-step solution"
    }
  },
  "meta": {
    "timestamp": "ISO 8601 timestamp"
  }
}
```

## Implementation Questions

### Q: How do I migrate from v1.x to v2.0.0?
**A:** Follow these steps:
1. **Add schema_version**: Add `"schema_version": "2.0.0"` to tool descriptions
2. **Update error handling**: Replace simple error messages with enriched responses
3. **Use validation patterns**: Leverage the provided validation patterns
4. **Test thoroughly**: Validate all error scenarios

### Q: Can I use the old error format in v2.0.0?
**A:** While technically possible, it's not recommended. The enriched response format is the foundation of v2.0.0 and provides significant benefits. Tools using the old format won't benefit from the improved error handling.

### Q: How do I validate enriched responses?
**A:** You can validate enriched responses using:
1. **JSON Schema**: Use `schema/enriched_response_schema.json`
2. **SDK validation**: Use the provided validation functions
3. **Manual testing**: Check that all required fields are present

### Q: What validation patterns are available?
**A:** The following validation patterns are provided:
- **Email validation** (RFC 5322 compliant)
- **Password strength** (configurable requirements)
- **Date range validation** (ISO 8601 with business logic)
- **URL validation** (HTTP/HTTPS format)
- **JSON validation** (syntax and format)
- **String length validation** (min/max constraints)
- **Required field validation** (null/empty checking)

## Error Codes and Naming

### Q: How should I name error codes?
**A:** Error codes should follow these conventions:
- **UPPERCASE** with underscores
- **Descriptive** and specific to the error
- **Consistent** across your entire system
- **Examples**: `INVALID_DATE_RANGE`, `WEAK_PASSWORD`, `EMPTY_EMAIL`

### Q: Can I create custom error codes?
**A:** Yes, you can create custom error codes. Just follow the naming conventions and ensure they're unique within your system. Consider using a prefix for your domain (e.g., `MYAPP_INVALID_INPUT`).

### Q: How many error codes should I have?
**A:** Aim for a balance between specificity and maintainability:
- **Too few**: Generic codes like `ERROR` or `INVALID` aren't helpful
- **Too many**: Having hundreds of codes becomes hard to maintain
- **Sweet spot**: 10-50 codes covering your main error scenarios

## Expected Field Details

### Q: What should I include in the expected field?
**A:** The expected field should include:
- **Conditions**: List of validation rules that must be met
- **Format**: Expected format specification
- **Constraints**: Min/max values, patterns, etc.
- **Examples**: Valid and invalid input examples
- **Context**: Additional information that helps understand requirements

### Q: How detailed should the expected field be?
**A:** Be as detailed as necessary for users to understand and fix the issue:
- **Too vague**: "Must be valid" doesn't help
- **Too verbose**: Don't include irrelevant information
- **Just right**: Include specific conditions, examples, and constraints

### Q: Should I include examples in the expected field?
**A:** Yes, examples are very helpful. Include:
- **Valid examples**: Show what works
- **Invalid examples**: Show what doesn't work and why
- **Edge cases**: Include boundary conditions when relevant

## Performance and Best Practices

### Q: Do enriched responses impact performance?
**A:** The performance impact is minimal:
- **Small overhead**: Additional JSON fields are lightweight
- **Lazy evaluation**: Only generate detailed info when needed
- **Caching**: Cache common error responses if needed
- **Benefits outweigh costs**: Better user experience is worth the small overhead

### Q: How do I handle sensitive information in error responses?
**A:** Be careful with sensitive data:
- **Don't expose passwords** or tokens in error messages
- **Mask sensitive fields** (e.g., show only first/last characters)
- **Log sensitive data** separately for debugging
- **Use generic messages** for security-related errors

### Q: Should I translate error messages?
**A:** Yes, consider localization:
- **User-facing messages** should be in the user's language
- **Error codes** should remain in English for consistency
- **Examples** can be localized when relevant
- **Use the localization features** provided by ATDF

## Integration Questions

### Q: How do enriched responses work with n8n?
**A:** Enriched responses work seamlessly with n8n:
- **ATDF blocks** in toolWorkflow nodes can include error examples
- **Error handling** in subworkflows should use enriched responses
- **User interface** will display the detailed error information
- **AI agents** can better understand and handle errors

### Q: Can I use enriched responses with MCP?
**A:** Yes, enriched responses are compatible with MCP:
- **MCP to ATDF converters** handle enriched responses
- **Error propagation** works through MCP clients
- **Consistent format** across different protocols
- **Better tool descriptions** for MCP tools

### Q: How do enriched responses work with AI agents?
**A:** Enriched responses are designed for AI agents:
- **Structured information** that AI can parse and understand
- **Clear error codes** for decision making
- **Actionable solutions** that AI can suggest
- **Context awareness** for better tool selection

## Troubleshooting

### Q: My enriched response doesn't validate against the schema
**A:** Common issues:
- **Missing required fields**: Ensure all required fields are present
- **Wrong data types**: Check that fields have correct types
- **Invalid error codes**: Use UPPERCASE with underscores
- **Missing timestamp**: Include ISO 8601 timestamp in meta

### Q: Users say error messages are too verbose
**A:** Balance detail with usability:
- **Progressive disclosure**: Show basic message first, details on demand
- **Configurable verbosity**: Allow users to choose detail level
- **Focus on solutions**: Emphasize how to fix the problem
- **Test with real users**: Get feedback on message clarity

### Q: How do I test enriched responses?
**A:** Test thoroughly:
- **Unit tests**: Test each validation scenario
- **Integration tests**: Test with real tools and workflows
- **User testing**: Get feedback from actual users
- **Schema validation**: Ensure responses match the schema

## Future Questions

### Q: Will there be more validation patterns in future versions?
**A:** Yes, we plan to add more patterns:
- **Domain-specific patterns** (e.g., credit card validation)
- **Industry patterns** (e.g., healthcare, finance)
- **Custom pattern builder** for creating new patterns
- **Pattern marketplace** for sharing community patterns

### Q: Will enriched responses support more languages?
**A:** Yes, we're working on:
- **More language support** beyond English, Spanish, Portuguese
- **Automatic translation** of error messages
- **Cultural adaptation** of examples and solutions
- **RTL language support** for Arabic, Hebrew, etc.

### Q: How can I contribute to ATDF?
**A:** We welcome contributions:
- **Submit issues** for bugs or feature requests
- **Create pull requests** for improvements
- **Add validation patterns** for new use cases
- **Improve documentation** or translations
- **Share examples** of how you're using ATDF

---

**Need more help?** Check the [documentation](index.md), [examples](../examples/), or [GitHub issues](https://github.com/MauricioPerera/agent-tool-description-format/issues). 