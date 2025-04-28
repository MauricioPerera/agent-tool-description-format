# Changelog

All notable changes to the **Agent Tool Description Format (ATDF)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-28

### Added
- Initial draft of the ATDF protocol specification (`docs/specification.md`).
- JSON Schema for tool descriptions (`schema/atdf_schema.json`).
- Example tool descriptions in `schema/examples/`:
  - `hole_maker.json`: Tool for creating holes in solid surfaces.
  - `paint_brush.json`: Tool for applying paint.
  - `text_translator.json`: Tool for translating text.
- Python tools for validation and demonstration:
  - `tools/validator.py`: Validates tool descriptions against the schema.
  - `tools/demo/loader.py` and `tools/demo/agent_example.py`: Demo for loading and selecting tools.
- Initial test suite in `tests/` for validator and example validation.
- Documentation files:
  - `README.md`: Project overview and quick start guide.
  - `docs/contributing.md`: Guidelines for contributors.
  - `docs/license.md`: License details.
- MIT License (`LICENSE`).

### Notes
- This is a draft release, open for feedback and contributions.
- Contact Mauricio Perera at [mauricio.perera@gmail.com](mailto:mauricio.perera@gmail.com) for questions or suggestions.
