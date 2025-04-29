import json
import jsonschema
import sys
import os
import argparse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('atdf_validator')

def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in '{file_path}': {e}")
        return None

def validate_tool(tool_file, schema_file=None):
    """Validate a tool description against the ATDF schema."""
    # Determinar la ruta del esquema si no se proporciona
    if schema_file is None:
        schema_file = os.path.join(os.path.dirname(__file__), "../schema/atdf_schema.json")
    
    # Cargar esquema y descripción de herramienta
    schema = load_json(schema_file)
    if not schema:
        logger.error(f"Could not load schema from '{schema_file}'.")
        return False
    
    tool = load_json(tool_file)
    if not tool:
        logger.error(f"Could not load tool from '{tool_file}'.")
        return False

    # Validar
    try:
        jsonschema.validate(instance=tool, schema=schema)
        logger.info(f"✅ '{tool_file}' is valid according to the ATDF schema.")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"❌ Validation error in '{tool_file}':")
        logger.error(f"  - {e.message}")
        logger.error(f"  - Path: {e.json_path}")
        return False

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Validate ATDF tool descriptions against a schema.")
    parser.add_argument("tool_file", help="Path to the ATDF tool description JSON file to validate")
    parser.add_argument("--schema", "-s", help="Path to the schema file to validate against (default: ../schema/atdf_schema.json)")
    
    args = parser.parse_args()
    
    # Validar
    success = validate_tool(args.tool_file, args.schema)
    
    # Establecer código de salida
    sys.exit(0 if success else 1)
