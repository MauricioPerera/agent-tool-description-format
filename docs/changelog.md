[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

# Changelog

All notable changes to the **Agent Tool Description Format (ATDF)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-04-29

### Added
- Implementación de un SDK en Python (`sdk/`) para facilitar la interacción con herramientas ATDF.
- Módulo `core` en el SDK con clases de esquema (`ATDFTool`, `ATDFToolParameter`) y funciones de utilidad para carga y validación.
- Módulo `vector_search` en el SDK con `ATDFVectorStore` para búsqueda semántica de herramientas usando `lancedb` y `sentence-transformers`.
- Archivo `requirements.txt` definiendo dependencias básicas y opcionales (para búsqueda vectorial).
- Ejemplos de uso del SDK en `examples/`:
  - `basic_usage.py`: Demuestra carga, creación, y exportación.
  - `vector_search.py`: Demuestra la búsqueda vectorial.
- `README.md` actualizado con instrucciones de instalación y uso del SDK.

### Fixed
- Corregido error en `ATDFVectorStore` al crear tablas en `lancedb` pasando un diccionario como esquema.
- Eliminadas definiciones duplicadas de clases (`ATDFTool`, `ATDFToolbox`) en `sdk/atdf_sdk.py`.
- Añadida dependencia faltante `pandas` a `requirements.txt` (requerida por `lancedb`).

### Changed
- Refactorización del código relacionado con ATDF en un paquete SDK estructurado.

## [0.2.0] - 2025-05-15

### Added
- Enhanced schema with extended fields (`schema/enhanced_atdf_schema.json`).
- New optional fields in the ATDF format:
  - `metadata`: Information about the tool (version, author, tags, category, creation date).
  - `localization`: Support for multiple languages in a single file.
  - `prerequisites`: Prerequisites and dependencies for tool usage.
  - `feedback`: Progress indicators and completion signals.
  - `examples`: Examples of tool usage with inputs and expected outputs.
- Enhanced examples in `schema/examples/`:
  - `enhanced_hole_maker.json`: Full example with all extended features.
  - Multilingual examples for tools in English, Spanish, and Portuguese.
- New functionality in the SDK:
  - Support for tool conversion between basic and enhanced format.
  - Advanced search functionality with multilingual support.
  - Schema validation for both basic and enhanced formats.
- Improved test suite:
  - Tests for enhanced features (`tests/test_enhanced_features.py`).
  - Trilingual agent testing (`tests/test_trilingual_agent.py`).
  - Comprehensive tests for all functionality (`tests/test_atdf_complete.py`).
- New documentation:
  - Enhancement proposal for version 0.2.0.
  - Extended multilingual support documentation.

### Changed
- SDK now provides automatic language detection.
- Improved tool selection algorithm, now with context and language awareness.
- Better error handling and validation feedback.

### Notes
- Version 0.2.0 is fully backwards compatible with 0.1.0.
- Tools in basic format can be automatically converted to enhanced format.
- The enhanced format provides significant improvements for agent-tool interaction, especially for multilingual applications.

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
