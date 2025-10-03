#!/usr/bin/env python3
"""
Ejemplo de uso del convertidor MCP a ATDF.

Este script demuestra cómo utilizar el convertidor para transformar
herramientas desde el formato MCP al formato ATDF, tanto básico como mejorado.
"""

import json
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.converter import save_tool

# Importar el convertidor
from tools.mcp_converter import convert_mcp_file, mcp_to_atdf

# Crear directorio para los resultados
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)


def main():
    """Ejemplo principal de conversión MCP a ATDF."""

    print("🔄 Iniciando ejemplo de conversión MCP a ATDF...")

    # Ejemplo 1: Herramienta simple convertida programáticamente
    print("\n==== Ejemplo 1: Conversión programática simple ====")

    mcp_tool_example = {
        "name": "fetch",
        "description": "Recupera contenido de una URL",
        "annotations": {"context": "Cuando necesites obtener datos de una página web"},
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL a recuperar"},
                "raw": {
                    "type": "boolean",
                    "description": "Devolver HTML crudo (opcional)",
                },
            },
            "required": ["url"],
        },
    }

    # Convertir a formato básico
    basic_result = mcp_to_atdf(mcp_tool_example)
    basic_output_path = output_dir / "fetch_basic.json"
    save_tool(basic_result, basic_output_path)
    print(f"✅ Herramienta básica guardada en: {basic_output_path}")

    # Convertir a formato mejorado
    enhanced_result = mcp_to_atdf(mcp_tool_example, enhanced=True, author="MCP Example")
    enhanced_output_path = output_dir / "fetch_enhanced.json"
    save_tool(enhanced_result, enhanced_output_path)
    print(f"✅ Herramienta mejorada guardada en: {enhanced_output_path}")

    # Ejemplo 2: Múltiples herramientas MCP en un solo archivo
    print("\n==== Ejemplo 2: Procesamiento por lotes ====")

    # Crear un archivo MCP temporal para el ejemplo
    mcp_tools = {
        "tools": [
            {
                "name": "search",
                "description": "Busca información en la web",
                "annotations": {
                    "purpose": "Obtener resultados de búsqueda de un término"
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Término de búsqueda",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Número máximo de resultados",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "weather",
                "description": "Obtiene información meteorológica",
                "annotations": {
                    "context": "Para conocer las condiciones climáticas de una ubicación"
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Ciudad o coordenadas",
                        },
                        "units": {
                            "type": "string",
                            "description": "Unidades (metric/imperial)",
                        },
                    },
                    "required": ["location"],
                },
            },
        ]
    }

    # Guardar herramientas MCP en un archivo temporal
    mcp_file_path = output_dir / "mcp_tools.json"
    with open(mcp_file_path, "w", encoding="utf-8") as f:
        json.dump(mcp_tools, f, indent=2)

    # Procesar cada herramienta en el archivo
    batch_output_dir = output_dir / "batch"
    batch_output_dir.mkdir(exist_ok=True)

    for i, tool in enumerate(mcp_tools["tools"]):
        # Convertir y guardar cada herramienta
        atdf_tool = mcp_to_atdf(tool, enhanced=True)
        tool_path = batch_output_dir / f"{tool['name']}.json"
        save_tool(atdf_tool, tool_path)
        print(f"✅ Herramienta {i+1}/{len(mcp_tools['tools'])} convertida: {tool_path}")

    print("\n🎉 Conversión completada exitosamente!")
    print(f"📁 Resultados guardados en: {output_dir}")


if __name__ == "__main__":
    main()
