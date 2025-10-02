# ATDF CLI Reference

## Installation
```
pip install -e .
```

## Commands

### `atdf validate`
Validate un descriptor ATDF.
```
atdf validate path/to/tool.json --smart
```

### `atdf convert`
Convertir catálogos MCP o ATDF a formato enhanced.
```
atdf convert schema/examples/hole_maker.json out/enhanced.json --enhanced --author "Docs Team"
```

### `atdf enrich`
Enriquece in-place un descriptor básico añadiendo metadata/localización heurística.
```
atdf enrich schema/examples/basic_tool.json
```

Para más opciones ejecute `atdf --help`.
