# Agent Tool Description Format (ATDF) - Contributor Guide for AI Agents

This guide provides essential information for AI agents contributing to the Agent Tool Description Format (ATDF) project.

## 1. Project Overview for AI Agents

The **Agent Tool Description Format (ATDF)** is an open protocol designed to standardize how tools are described for AI agents. Its primary purpose is to enable AI agents to dynamically select and utilize tools based on their functional descriptions—what they do, when they should be used, and how they are operated—without needing to be hard-coded for specific tool names or implementation details. This promotes flexibility and interoperability between agents and a diverse range of tools.

## 2. Repository Structure

The ATDF repository is organized as follows:

-   **`schema/`**: Contains the JSON schema files that define the ATDF specification.
    -   `atdf_schema.json`: The core schema for basic tool descriptions.
    -   `enhanced_atdf_schema.json`: The schema for tool descriptions utilizing enhanced features (metadata, multilingual support, dependencies, etc.).
-   **`examples/`**: Contains example ATDF files in JSON format, illustrating how to describe various tools. It also includes related Python and TypeScript code examples demonstrating the use or generation of ATDF.
    -   `examples/output/`: May contain generated files from example scripts.
-   **`docs/`**: Contains user and developer documentation in Markdown format.
    -   `docs/en/`: English documentation.
    -   `docs/es/`: Spanish documentation.
    -   `docs/pt/`: Portuguese documentation.
-   **`tools/`**: Contains utility scripts for working with ATDF.
    -   `validator.py`: Validates ATDF files against the schemas.
    -   `validate_enhanced.py`: A dedicated script to validate against the enhanced schema.
    -   `mcp_converter.py`: Converts from other formats (like MCP) to ATDF (if applicable).
    -   `demo/`: May contain demonstration scripts.
-   **`sdk/`**: Contains the Python SDK for programmatic interaction with ATDF (parsing, validating, generating).
-   **`js/`**: Contains the JavaScript/TypeScript SDK for working with ATDF.
-   **`tests/`**: Contains test files for the schemas, SDKs, and utility scripts.

## 3. Working with ATDF Files (`.json`)

ATDF files, which describe tools, are primarily located in the `examples/` directory and its subdirectories. When creating or modifying these:

-   **Validation is Crucial:**
    -   Standard ATDF files (using only core features) should be validated against `schema/atdf_schema.json`.
    -   Enhanced ATDF files (using features defined in `enhanced_atdf_schema.json`, such as metadata, prerequisites, or multilingual fields) must be validated against `schema/enhanced_atdf_schema.json`.
    -   **General Validation Script:**
        ```bash
        python tools/validator.py <path_to_atdf_file.json> --schema <path_to_schema.json>
        ```
        (e.g., `python tools/validator.py examples/simple_tool.json --schema schema/atdf_schema.json`)
    -   **Enhanced Validation Script (recommended for files with enhanced features):**
        ```bash
        python tools/validate_enhanced.py <path_to_atdf_file.json>
        ```
        This script implicitly uses `schema/enhanced_atdf_schema.json`.
-   **Clarity:** Ensure that all descriptions (`description`, `how_to_use`, `when_to_use`, parameter descriptions, etc.) are clear, concise, and accurately reflect the tool's functionality from an AI agent's perspective.

## 4. Working with Documentation (`.md` files in `docs/`)

User and developer documentation is maintained in Markdown format within the `docs/` directory, with language-specific subdirectories (`en/`, `es/`, `pt/`).

-   **Structure:** Each language directory (e.g., `docs/en/`) has an `index.md` file that serves as its main landing page and contains the primary navigation links for that language.
-   **Adding New Documentation:**
    1.  If adding a new guide or significant section, create the Markdown file (e.g., `new_guide.md`) within *each* relevant language subdirectory (`docs/en/new_guide.md`, `docs/es/new_guide.md`, etc.).
    2.  Update the corresponding `index.md` file in each language directory to include a navigation link to your new document.
    3.  If the new document has its own Table of Contents, ensure all internal links (slugs) are correctly generated based on the translated headings for that specific language.
-   **Style:** Follow the existing Markdown style, formatting, and heading structure found in other documents for consistency.

## 5. Running Tests

The repository includes tests to ensure the integrity of schemas, SDKs, and utilities.

-   **Python Tests:**
    -   The primary script to execute most Python-related tests is `tests/run_all_tests.py`.
    -   Run this script from the repository root:
        ```bash
        python tests/run_all_tests.py
        ```
    -   Python dependencies are listed in `requirements.txt` (for core SDK) and `requirements-dev.txt` (for testing and development). It is highly recommended to use a Python virtual environment to manage these dependencies.
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements-dev.txt -r requirements.txt
        ```
-   **JavaScript/TypeScript SDK Tests:**
    -   Navigate to the `js/` directory.
    -   Follow the instructions in `js/README.md`. Typically, this involves:
        ```bash
        cd js/
        npm install
        npm test
        ```
-   **Requirement:** Ensure all relevant tests pass before submitting your changes in a Pull Request.

## 6. Contribution Guidelines for Agents

Follow these guidelines when contributing to the project:

-   **Branching:**
    -   Create a new branch for your changes from an up-to-date version of the main development branch (e.g., `main` or `develop`).
    -   Use a descriptive branch name, such as `feat/new-tool-example`, `fix/validator-bug`, or `docs/update-atdf-spec`.
-   **Commits:**
    -   Follow the **Conventional Commits** style for your commit messages (e.g., `feat: Add coffee maker tool example`, `fix: Correct schema validation for optional fields`, `docs: Clarify ATDF output structure`). This helps in automating changelog generation and makes the commit history more readable.
    -   Commits should be atomic, representing a single logical change or a small, related set of changes.
-   **Pull Requests (PRs):**
    -   Submit all changes to the main development branch via Pull Requests.
    -   Ensure your PR description is clear, explains the "what" and "why" of your changes, and references any related issues.
    -   Verify that all automated checks and tests (Python, JS, schema validation, linters, if applicable) pass for your PR.
    -   If you added or modified ATDF example files (`.json`), confirm they validate against the appropriate schema.
-   **Code and File Style:**
    -   **Python:** Adhere to PEP 8 style guidelines.
    -   **JSON/YAML:** Ensure files are well-formatted (e.g., "pretty-printed" with consistent indentation). For JSON files committed to the repository, use 2-space indentation for readability.
    -   **Markdown:** Maintain consistent formatting as seen in existing documentation files. Use linters if available.

## 7. General Considerations for Agents

-   This `AGENTS.md` file provides primary guidance for AI agent contributors. If more specific instructions exist in subdirectory `README.md` files or other specialized `AGENTS.md` files (should they be introduced later for specific components like SDKs), those more specific guides take precedence for that context.
-   When modifying code, schemas, examples, or documentation, always aim to maintain or improve clarity, consistency, and accuracy.
-   If you are unsure about a change, the best approach is to ask for clarification in your Pull Request or in a relevant issue.

Thank you for contributing to ATDF!
