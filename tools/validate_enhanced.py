#!/usr/bin/env python3
"""
ATDF Enhanced Validator - Valida descripciones de herramientas contra el esquema ATDF mejorado.

Este script verifica que una descripción de herramienta cumpla con el esquema
ATDF 0.2.0 (formato extendido).
"""

import sys
import os
import json
import argparse
import jsonschema
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atdf_validator")


def load_json(file_path):
    """Cargar un archivo JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: Archivo '{file_path}' no encontrado.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: JSON inválido en '{file_path}': {e}")
        return None


def validate_tool(tool_file, schema_file):
    """Validar una descripción de herramienta contra el esquema ATDF mejorado."""
    # Cargar esquema y herramienta
    schema = load_json(schema_file)
    if not schema:
        logger.error(f"No se pudo cargar el esquema desde '{schema_file}'.")
        return False

    tool = load_json(tool_file)
    if not tool:
        logger.error(f"No se pudo cargar la herramienta desde '{tool_file}'.")
        return False

    # Validar
    try:
        jsonschema.validate(instance=tool, schema=schema)
        logger.info(f"✅ '{tool_file}' es válido según el esquema ATDF mejorado.")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"❌ Error de validación en '{tool_file}':")
        logger.error(f"  - {e.message}")
        logger.error(f"  - Ruta: {e.json_path}")
        return False


def main():
    """Función principal para la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Validador de formato ATDF mejorado (v0.2.0)"
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Archivo JSON con la descripción ATDF a validar",
        required=True,
    )
    parser.add_argument(
        "--schema", "-s", help="Archivo JSON con el esquema ATDF mejorado"
    )

    args = parser.parse_args()

    # Si no se proporciona un esquema, usar el predeterminado
    if not args.schema:
        args.schema = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "schema/enhanced_atdf_schema.json",
        )

    # Validar la herramienta
    if validate_tool(args.input, args.schema):
        print(
            f"✅ Validación exitosa: '{args.input}' cumple con el esquema ATDF mejorado."
        )
        sys.exit(0)
    else:
        print(f"❌ Error: '{args.input}' no cumple con el esquema ATDF mejorado.")
        sys.exit(1)


if __name__ == "__main__":
    main()
