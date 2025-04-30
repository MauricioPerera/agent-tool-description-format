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

def validate_tool(tool_file, schema_file=None, ignore_additional_properties=False):
    """
    Validate a tool description against the ATDF schema.
    
    Args:
        tool_file: Path to the tool JSON file
        schema_file: Optional path to the schema file
        ignore_additional_properties: If True, ignore additional properties in the tool
        
    Returns:
        bool: True if validation is successful
    """
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
        # Si se debe ignorar propiedades adicionales, usar un validador personalizado
        if ignore_additional_properties:
            validator_class = jsonschema.validators.extend(
                jsonschema.validators.validator_for(schema),
                {'additionalProperties': lambda validator, aP, instance, schema: None}
            )
            validator = validator_class(schema)
            error = next(validator.iter_errors(tool), None)
            if error:
                logger.error(f"❌ Validation error in '{tool_file}':")
                logger.error(f"  - {error.message}")
                logger.error(f"  - Path: {error.json_path}")
                return False
        else:
            # Validación estándar
            jsonschema.validate(instance=tool, schema=schema)
        
        logger.info(f"✅ '{tool_file}' is valid according to the ATDF schema.")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"❌ Validation error in '{tool_file}':")
        logger.error(f"  - {e.message}")
        logger.error(f"  - Path: {e.json_path}")
        return False

def validate_tool_smart(tool_file, schema_basic=None, schema_enhanced=None):
    """
    Validate a tool description automatically selecting the appropriate schema
    based on its structure or schema_version field.
    
    Args:
        tool_file: Path to the tool JSON file
        schema_basic: Optional path to the basic schema file
        schema_enhanced: Optional path to the enhanced schema file
        
    Returns:
        bool: True if validation is successful
    """
    # Determinar rutas de esquemas si no se proporcionan
    if schema_basic is None:
        schema_basic = os.path.join(os.path.dirname(__file__), "../schema/atdf_schema.json")
    
    if schema_enhanced is None:
        schema_enhanced = os.path.join(os.path.dirname(__file__), "../schema/enhanced_atdf_schema.json")
        
    # Cargar la herramienta
    tool = load_json(tool_file)
    if not tool:
        logger.error(f"Could not load tool from '{tool_file}'.")
        return False
    
    # Detectar versión del esquema
    schema_version = tool.get("schema_version", "1.0.0")
    
    # Si no tiene versión, detectar por la presencia de campos avanzados
    if schema_version == "1.0.0" and not "schema_version" in tool:
        is_enhanced = any(key in tool for key in ["metadata", "examples", "localization", "prerequisites", "feedback"])
        
        if is_enhanced:
            schema_version = "2.0.0"
    
    # Seleccionar esquema basado en la versión
    if schema_version.startswith("2."):
        logger.info(f"Detected enhanced schema version {schema_version}, using enhanced validation")
        return validate_tool(tool_file, schema_enhanced)
    else:
        logger.info(f"Detected basic schema version {schema_version}, using basic validation")
        # Para herramientas básicas, siempre ignorar propiedades adicionales para mayor compatibilidad
        return validate_tool(tool_file, schema_basic, ignore_additional_properties=True)

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Validate ATDF tool descriptions against a schema.")
    parser.add_argument("tool_file", help="Path to the ATDF tool description JSON file to validate")
    parser.add_argument("--schema", "-s", help="Path to the schema file to validate against (default: auto-detect)")
    parser.add_argument("--smart", "-m", action="store_true", help="Use smart validation to auto-detect schema version")
    parser.add_argument("--ignore-additional", "-i", action="store_true", help="Ignore additional properties")
    
    args = parser.parse_args()
    
    # Validar
    if args.smart:
        success = validate_tool_smart(args.tool_file)
    else:
        success = validate_tool(args.tool_file, args.schema, args.ignore_additional)
    
    # Establecer código de salida
    sys.exit(0 if success else 1)
