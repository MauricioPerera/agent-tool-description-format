#!/usr/bin/env python3
"""
Ejemplo básico de uso del SDK de ATDF.

Este script muestra las funcionalidades básicas del SDK para
cargar, manipular y guardar herramientas ATDF.
"""

import os
import json
from pathlib import Path

from sdk import ATDFSDK
from sdk.core.schema import ATDFTool, ATDFToolParameter


def main():
    # Obtener ruta al directorio de herramientas
    tools_dir = Path(__file__).parent.parent / "tools"
    
    print(f"Directorio de herramientas: {tools_dir}")
    print("Iniciando SDK de ATDF...")
    
    # Inicializar el SDK
    sdk = ATDFSDK(tools_directory=tools_dir)
    
    # Mostrar herramientas cargadas
    tools = sdk.get_all_tools()
    print(f"Se cargaron {len(tools)} herramientas:")
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name} - {tool.description[:50]}...")
    
    print("\nCreando una nueva herramienta...")
    
    # Crear parámetros
    param1 = ATDFToolParameter(
        name="param1",
        description="Un parámetro de ejemplo de tipo texto",
        type="string",
        required=True
    )
    
    param2 = ATDFToolParameter(
        name="param2",
        description="Un parámetro de ejemplo de tipo numérico",
        type="number",
        required=False,
        default=42
    )
    
    # Crear una nueva herramienta
    nueva_herramienta = ATDFTool(
        name="Herramienta de Ejemplo",
        description="Una herramienta de ejemplo para mostrar la funcionalidad del SDK de ATDF",
        parameters=[param1, param2],
        tags=["ejemplo", "demo", "sdk"],
        category="utilidades"
    )
    
    # Añadir al SDK
    sdk.tools.append(nueva_herramienta)
    
    print(f"Herramienta creada: {nueva_herramienta.name}")
    print(f"ID: {nueva_herramienta.id}")
    print(f"Parámetros: {len(nueva_herramienta.parameters)}")
    
    # Exportar a JSON Schema
    print("\nExportando herramientas a JSON Schema...")
    schemas = sdk.export_to_json_schema()
    
    print(f"Se exportaron {len(schemas)} esquemas")
    
    # Guardar ejemplo de esquema
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    schema_file = output_dir / "schemas.json"
    with open(schema_file, "w") as f:
        json.dump(schemas, f, indent=2)
    
    print(f"Esquemas guardados en: {schema_file}")
    
    # Guardar herramientas en archivos
    print("\nGuardando herramientas en archivos...")
    
    # Formato JSON
    json_file = output_dir / "herramientas.json"
    sdk.save_tools_to_file(json_file, format="json")
    print(f"Herramientas guardadas en JSON: {json_file}")
    
    # Formato YAML
    yaml_file = output_dir / "herramientas.yaml"
    sdk.save_tools_to_file(yaml_file, format="yaml")
    print(f"Herramientas guardadas en YAML: {yaml_file}")
    
    print("\nEjemplo completado exitosamente.")


if __name__ == "__main__":
    main() 