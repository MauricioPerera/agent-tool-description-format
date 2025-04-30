# Frequently Asked Questions

[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Workflow](workflow.md) | [FAQ](faq.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/faq.md) | [Español (es)](../es/faq.md) | [Português (pt)](faq.md)

## General Questions

### What is ATDF?
ATDF (Agent Tool Description Format) is an open protocol for describing tools functionally, enabling AI agents to select and use them based on purpose, context, and operation, without relying on technical details.

### Why was ATDF created?
ATDF was created to address the limitations of current approaches to tool integration in AI agents, which often rely on hard-coded tool names, proprietary APIs, or detailed technical specifications. This creates dependencies that limit adaptability and complicate the adoption of new tools.

### Who can use ATDF?
ATDF is open for anyone to use, including developers building AI agents, robotics systems, or any application that needs to select tools based on functionality rather than specific implementations.

### Is ATDF open source?
Yes, ATDF is released under the MIT License, making it freely available for use, modification, and distribution.

## Technical Questions

### How does ATDF differ from other tool description formats?
ATDF focuses on functional descriptions rather than technical specifications. It answers "what", "when", and "how" questions about a tool, rather than detailing implementation specifics. This makes it more adaptable and future-proof.

### Can ATDF be used with physical tools (e.g., robots)?
Yes! ATDF was designed to be applicable to both digital tools (like APIs) and physical tools (like drills or brushes). The protocol is implementation-agnostic.

### How does ATDF handle different languages?
ATDF supports tool descriptions in any language. The protocol itself is language-neutral, and the implementation includes language detection to match user queries with tools described in the appropriate language.

### What format does ATDF use?
ATDF uses JSON or YAML for tool descriptions. The schema defines required fields like `tool_id`, `description`, `when_to_use`, and `how_to_use` (with inputs and outputs).

## Implementation Questions

### How do I validate my ATDF tool descriptions?
You can use the provided validator script:
```bash
python tools/validator.py schema/examples/my_tool.json
```

### Can I extend ATDF for my specific needs?
Yes, ATDF is designed to be extensible. While maintaining the core required fields, you can add additional fields or metadata for specific applications.

### How does an agent select the right tool using ATDF?
Agents typically match the user's goal or request against the `description` and `when_to_use` fields of available tools. The `how_to_use` field then provides the information needed to execute the selected tool.

### How can I contribute to ATDF?
You can contribute by:
- Submitting new tool descriptions
- Improving the documentation
- Enhancing the validator
- Adding support for new languages
- Creating implementations in different programming languages

See the [Contributing](contributing.md) page for more details.

## Multilingual Support Questions

### Which languages are currently supported?
ATDF currently has example tool descriptions in English, Spanish, and Portuguese, with a language detection mechanism that can identify queries in these languages.

### How does language detection work?
The implementation uses a simple keyword-based approach to detect the language of user queries. Advanced implementations could use more sophisticated language models.

### Can I add support for more languages?
Absolutely! You can create tool descriptions in any language and extend the language detection mechanism to recognize additional languages.

### Does ATDF require translation between languages?
No, ATDF doesn't require translation. Instead, it allows for equivalent tool descriptions in different languages, each describing the same functional tool but in a language that the user is comfortable with. 