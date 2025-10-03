#!/usr/bin/env python3
"""
Convertidor de MCP (Model Context Protocol) a ATDF (Agent Tool Description Format).

Este módulo proporciona funciones para convertir herramientas desde el formato MCP
utilizado por algunos modelos de lenguaje, al formato ATDF estándar.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .converter import convert_to_enhanced, save_tool

# Referencia a funciones existentes del proyecto
from .validator import validate_tool_smart

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_converter")


def mcp_to_atdf(
    mcp_tool: Dict[str, Any], enhanced: bool = False, author: str = "MCP Converter"
) -> Dict[str, Any]:
    """
    Convierte una herramienta MCP a formato ATDF.

    Args:
        mcp_tool (Dict): Objeto JSON de una herramienta MCP.
        enhanced (bool): Si es True, convierte al formato mejorado de ATDF.
        author (str): Autor para los metadatos en formato mejorado.

    Returns:
        Dict: Objeto ATDF válido.

    Raises:
        ValueError: Si faltan campos obligatorios o la validación falla.
    """
    # Validar campos obligatorios en MCP
    required_mcp_fields = ["name", "inputSchema"]
    for field in required_mcp_fields:
        if field not in mcp_tool:
            raise ValueError(f"Campo obligatorio '{field}' no encontrado en MCP")

    # Mapear campos MCP → ATDF
    atdf_tool = {
        "schema_version": "1.0.0",
        "tool_id": mcp_tool["name"],
        "description": mcp_tool.get("description", "Sin descripción proporcionada"),
        "when_to_use": _extract_when_to_use(mcp_tool),
        "how_to_use": {
            "inputs": _parse_inputs(mcp_tool["inputSchema"]),
            "outputs": _default_outputs(),
        },
    }

    # Validar con el esquema ATDF
    if not validate_tool_smart(atdf_tool):
        raise ValueError("[✗] Validación ATDF fallida")

    logger.info(f"[✓] {atdf_tool['tool_id']} validado exitosamente como ATDF")

    # Convertir a formato mejorado si se solicita
    if enhanced:
        atdf_tool = convert_to_enhanced(atdf_tool, author=author, extract_language=True)
        logger.info(f"Herramienta convertida a formato ATDF mejorado")

    return atdf_tool


def _extract_when_to_use(mcp_tool: Dict[str, Any]) -> str:
    """
    Extrae o genera contexto de uso desde MCP.

    Args:
        mcp_tool: Objeto JSON de la herramienta MCP.

    Returns:
        String con el contexto de uso para ATDF.
    """
    # Priorizar anotaciones MCP si existen
    if "annotations" in mcp_tool:
        context_hints = [
            f"Uso: {hint}"
            for key, hint in mcp_tool["annotations"].items()
            if key in ["context", "usage", "purpose"]
        ]
        if context_hints:
            return " ".join(context_hints)

    # Generar mensaje por defecto
    return (
        f"Usar cuando se requiera {mcp_tool.get('description', '').lower().strip('.')}"[
            :200
        ]
    )


def _parse_inputs(input_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convierte JSON Schema de MCP a formato inputs de ATDF.

    Args:
        input_schema: Esquema de entrada MCP.

    Returns:
        Lista de parámetros en formato ATDF.
    """
    inputs = []

    # Procesar las propiedades del esquema
    for param_name, param_def in input_schema.get("properties", {}).items():
        input_param = {
            "name": param_name,
            "type": param_def.get("type", "unknown"),
            "description": param_def.get("description", f"Parámetro {param_name}"),
        }

        # Marcar como requerido si está en la lista required
        if "required" in input_schema and param_name in input_schema["required"]:
            input_param["required"] = True

        inputs.append(input_param)

    return inputs


def _default_outputs(
    success_msg: str = None, failure_codes: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Genera estructura de salidas para ATDF.

    Args:
        success_msg: Mensaje personalizado de éxito.
        failure_codes: Lista de códigos y descripciones de error.

    Returns:
        Estructura de outputs válida para ATDF.
    """
    # Mensaje de éxito por defecto o personalizado
    if not success_msg:
        success_msg = "Operación completada exitosamente"

    # Códigos de error por defecto o personalizados
    if not failure_codes:
        failure_codes = [
            {"code": "invalid_input", "description": "Entrada inválida o incompleta"},
            {"code": "tool_error", "description": "Error interno de la herramienta"},
        ]

    return {"success": success_msg, "failure": failure_codes}


def convert_mcp_file(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    format: str = "json",
    enhanced: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Convierte un archivo de herramienta MCP a formato ATDF.

    Args:
        input_file: Ruta al archivo MCP a convertir.
        output_file: Ruta donde guardar el resultado. Si es None, solo retorna el resultado.
        format: Formato de salida ("json" o "yaml").
        enhanced: Si es True, convierte al formato mejorado.

    Returns:
        Dict con la herramienta convertida o None si hay errores.
    """
    try:
        input_path = Path(input_file)

        # Verificar existencia del archivo
        if not input_path.exists():
            logger.error(f"Archivo no encontrado: {input_path}")
            return None

        # Cargar archivo MCP
        with open(input_path, "r", encoding="utf-8") as f:
            if input_path.suffix.lower() == ".json":
                mcp_data = json.load(f)
            else:
                logger.error(f"Formato no soportado: {input_path.suffix}")
                return None

        # Convertir a ATDF
        atdf_result = mcp_to_atdf(mcp_data, enhanced=enhanced)

        # Guardar si se especificó archivo de salida
        if output_file:
            save_tool(atdf_result, output_file, format=format)
            logger.info(f"Herramienta guardada en {output_file}")

        return atdf_result

    except Exception as e:
        logger.error(f"Error en la conversión: {str(e)}")
        return None


# Ejemplo de uso independiente
if __name__ == "__main__":
    # Ejemplo MCP: Herramienta 'fetch'
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

    try:
        # Convertir a ATDF
        atdf_result = mcp_to_atdf(mcp_tool_example)

        # Imprimir resultado
        print("\n✅ ATDF generado:")
        print(json.dumps(atdf_result, indent=2))

        # Opcionalmente convertir y guardar en formato mejorado
        enhanced_result = mcp_to_atdf(mcp_tool_example, enhanced=True)
        save_tool(enhanced_result, "./examples/fetch_enhanced.json")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
