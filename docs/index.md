[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Workflow](workflow.md) | [FAQ](faq.md) | [Changelog](changelog.md) | [License](license.md)

# Agent Tool Description Format (ATDF)

Welcome to the **Agent Tool Description Format (ATDF)**, an open protocol for describing tools functionally, enabling AI agents to select and use them based on purpose, context, and operation, without relying on technical details.

## What is ATDF?
ATDF provides a standardized JSON/YAML format to describe tools, answering three key questions:
- **What** does the tool do?
- **When** should it be used?
- **How** is it used?

This makes it:
- **Tool-agnostic**: Works with physical (e.g., drills) and digital (e.g., APIs) tools.
- **Model-agnostic**: Usable by any AI agent.
- **Prompt-agnostic**: Allows prompts to focus on functions (e.g., "make a hole").

## Multilingual Support
ATDF supports tool descriptions in multiple languages. The protocol is language-neutral, making it ideal for creating AI agents that can interact with users in their native language.

Currently supported languages:
- English
- Spanish
- Portuguese

## Get Started
- **Read the Specification**: Learn the technical details in [Specification](specification.md).
- **Explore Examples**: Check out sample tool descriptions in [Examples](examples.md) or the [GitHub repository](https://github.com/MauricioPerera/agent-tool-description-format/tree/main/schema/examples).
- **Contribute**: See how to get involved in [Contributing](contributing.md).
- **Validate Tools**: Use the [validator script](https://github.com/MauricioPerera/agent-tool-description-format/blob/main/tools/validator.py) to ensure compliance.
- **Multilingual Support**: Learn about multilingual features in [Multilingual](multilingual.md).
- **Understand the Workflow**: See visual diagrams of how ATDF works in [Workflow](workflow.md).
- **Common Questions**: Find answers to common questions in [FAQ](faq.md).

## Quick Example
```json
{
  "tool_id": "hole_maker_v1",
  "description": "Creates holes in solid surfaces",
  "when_to_use": "Use when you need to make a hole in a wall or other drillable surface",
  "how_to_use": {
    "inputs": [
      { "name": "location", "type": "string", "description": "Location of the hole" },
      { "name": "bit_id", "type": "string", "description": "Identifier of the drill bit to use" }
    ],
    "outputs": {
      "success": "Hole created successfully",
      "failure": [
        { "code": "invalid_bit", "description": "The selected drill bit is not compatible with the surface" }
      ]
    }
  }
}
```

## Contact
Have questions or feedback? Reach out to Mauricio Perera at [mauricio.perera@gmail.com](mailto:mauricio.perera@gmail.com) or open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues).

## License
ATDF is licensed under the MIT License. See [License](license.md) for details.

---

[GitHub Repository](https://github.com/MauricioPerera/agent-tool-description-format) | [Changelog](changelog.md) 