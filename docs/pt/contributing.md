[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/contributing.md) | [Español (es)](../es/contributing.md) | [Português (pt)](contributing.md)

# Contributing to Agent Tool Description Format (ATDF)

Thank you for your interest in contributing to the **Agent Tool Description Format (ATDF)**! We welcome contributions from the community to improve the protocol, add examples, enhance tools, or refine documentation. This guide outlines how you can get involved.

## How to Contribute

### 1. Reporting Issues
If you find a bug, have a feature request, or want to suggest an improvement:
- Check the [GitHub Issues](https://github.com/MauricioPerera/agent-tool-description-format/issues) to avoid duplicates.
- Open a new issue with a clear title and description, including:
  - A brief summary of the problem or suggestion.
  - Steps to reproduce (if applicable).
  - Any relevant logs or screenshots.
- Use the appropriate issue template (if available).

### 2. Submitting Pull Requests
To propose changes (e.g., new tool descriptions, code improvements, or documentation updates):
1. Fork the repository and create a new branch:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Make your changes, ensuring they follow the guidelines below.
3. Commit your changes with a clear message:
   ```
   git commit -m "Add feature: description of your change"
   ```
4. Push to your fork and submit a pull request (PR) to the `main` branch:
   ```
   git push origin feature/your-feature-name
   ```
5. In the PR description, explain:
   - What the change does.
   - Why it's needed.
   - Any related issues (e.g., "Fixes #123").

### 3. Adding Tool Descriptions
To contribute new tool descriptions:
- Place the JSON file in `schema/examples/` (e.g., `new_tool.json`).
- Ensure it validates against the schema (`schema/atdf_schema.json`) using:
  ```
  python tools/validator.py schema/examples/new_tool.json
  ```
- Include a brief description in the PR, explaining the tool's purpose and use case.

## Contribution Guidelines
- **Code Style**:
  - For Python, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.
  - For JSON, use 2-space indentation and ensure schema compliance.
- **Documentation**:
  - Update relevant documentation (e.g., `docs/specification.md`) for major changes.
  - Keep Markdown files clear and concise.
- **Testing**:
  - Add tests for new features or scripts in `tests/`.
  - Ensure all tests pass:
    ```
    python -m unittest discover tests
    ```
- **Commit Messages**:
  - Use clear, descriptive messages (e.g., "Add text_translator.json example").
  - Reference related issues (e.g., "Fixes #123").

## Checklist para Pull Requests
- [ ] Referencie a versão de esquema alvo (veja [Compatibilidade de Versões](version_compatibility.md)) e defina `schema_version` explicitamente.
- [ ] Valide todos os descritores modificados com `tools/validator.py` (1.x) e `tools/validate_enhanced.py` (2.x).
- [ ] Execute `python tests/run_all_tests.py` e, se alterar o SDK JS, `npm test` dentro de `js/`.
- [ ] Atualize a documentação localizada em `docs/en`, `docs/es` e `docs/pt` quando a mudança impactar usuários.
- [ ] (Uso interno) Anexe ou referencie atualizações de workflow BMAD caso modifique `bmad.config.yml` ou scripts de integração.
- [ ] Inclua um breve resumo dos testes na descrição do PR.
- **Code Style**:
  - For Python, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.
  - For JSON, use 2-space indentation and ensure schema compliance.
- **Documentation**:
  - Update relevant documentation (e.g., `docs/specification.md`) for major changes.
  - Keep Markdown files clear and concise.
- **Testing**:
  - Add tests for new features or scripts in `tests/`.
  - Ensure all tests pass:
    ```
    python -m unittest discover tests
    ```
- **Commit Messages**:
  - Use clear, descriptive messages (e.g., "Add text_translator.json example").
  - Reference related issues (e.g., "Fixes #123").

## Code of Conduct
We aim to maintain a respectful and inclusive community. Please adhere to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## Getting Help
If you have questions or need assistance:
- Open an [issue](https://github.com/MauricioPerera/agent-tool-description-format/issues) with the 'question' label.
- Contact Mauricio Perera at [mauricio.perera@gmail.com](mailto:mauricio.perera@gmail.com).
- Join the conversation in [GitHub Issues](https://github.com/MauricioPerera/agent-tool-description-format/issues).

## License
By contributing, you agree that your contributions will be licensed under the [MIT License](../../LICENSE).

Thank you for helping make ATDF better!
