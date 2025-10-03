"""
Funciones de utilidad para el SDK de ATDF.

Este módulo proporciona funciones auxiliares para cargar, validar
y trabajar con herramientas ATDF.
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from sdk.core.schema import ATDFTool, ATDFToolParameter


logger = logging.getLogger(__name__)


def load_tools_from_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Cargar herramientas desde un archivo JSON o YAML.

    Args:
        file_path: Ruta al archivo

    Returns:
        Lista de herramientas en formato diccionario

    Raises:
        ValueError: Si el formato del archivo no es compatible
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        file_extension = file_path.suffix.lower()

        if file_extension in [".json"]:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error al decodificar JSON: {str(e)}")

        elif file_extension in [".yaml", ".yml"]:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Error al decodificar YAML: {str(e)}")
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_extension}")

    # Si es un objeto, convertirlo a lista
    if isinstance(data, dict):
        data = [data]

    # Validar cada herramienta
    valid_tools = []
    for tool in data:
        try:
            if validate_tool(tool):
                valid_tools.append(tool)
        except Exception as e:
            logger.warning(f"Herramienta no válida: {str(e)}")

    return valid_tools


def load_tools_from_directory(directory_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Cargar herramientas desde todos los archivos JSON y YAML en un directorio.

    Args:
        directory_path: Ruta al directorio

    Returns:
        Lista de herramientas en formato diccionario
    """
    directory_path = Path(directory_path)

    if not directory_path.exists() or not directory_path.is_dir():
        raise NotADirectoryError(f"Directorio no válido: {directory_path}")

    tools = []

    # Buscar archivos JSON y YAML en el directorio
    for extension in [".json", ".yaml", ".yml"]:
        file_paths = list(directory_path.glob(f"*{extension}"))

        for file_path in file_paths:
            try:
                file_tools = load_tools_from_file(file_path)
                tools.extend(file_tools)
            except Exception as e:
                logger.warning(f"Error al cargar archivo {file_path}: {str(e)}")

    return tools


def validate_tool(tool_data: Dict[str, Any]) -> bool:
    """
    Validar que un diccionario tiene la estructura correcta de una herramienta ATDF.

    Args:
        tool_data: Diccionario con datos de la herramienta

    Returns:
        True si la herramienta es válida

    Raises:
        ValueError: Si la herramienta no es válida
    """
    # Verificar campos obligatorios
    # Comprobar 'name' o 'tool_id' como campos alternativos
    if "name" not in tool_data and "tool_id" not in tool_data:
        raise ValueError(f"Campo obligatorio 'name' o 'tool_id' no encontrado")

    if "description" not in tool_data:
        raise ValueError(f"Campo obligatorio 'description' no encontrado")

    # Validar parámetros si existen
    if "parameters" in tool_data and tool_data["parameters"]:
        # Verificar que sea una lista
        if not isinstance(tool_data["parameters"], list):
            raise ValueError("El campo 'parameters' debe ser una lista")

        # Validar cada parámetro
        for param in tool_data["parameters"]:
            if not isinstance(param, dict):
                raise ValueError("Cada parámetro debe ser un objeto")

            # Verificar campos obligatorios del parámetro
            param_required_fields = ["name", "description"]
            for field in param_required_fields:
                if field not in param:
                    raise ValueError(
                        f"Campo obligatorio '{field}' no encontrado en parámetro"
                    )

    return True


def create_tool_instance(tool_data: Dict[str, Any]) -> ATDFTool:
    """
    Crear una instancia de ATDFTool a partir de datos en formato diccionario.

    Args:
        tool_data: Diccionario con datos de la herramienta

    Returns:
        Instancia de ATDFTool

    Raises:
        ValueError: Si la herramienta no es válida
    """
    # Validar la herramienta
    if not validate_tool(tool_data):
        raise ValueError("Datos de herramienta no válidos")

    # Extraer parámetros si existen
    parameters = []
    if "parameters" in tool_data and tool_data["parameters"]:
        for param_data in tool_data["parameters"]:
            # Convertir tipo si existe
            param_type = param_data.get("type", "string")

            # Crear instancia de parámetro
            parameter = ATDFToolParameter(
                name=param_data["name"],
                description=param_data["description"],
                type=param_type,
                required=param_data.get("required", False),
                enum=param_data.get("enum"),
                default=param_data.get("default"),
                min_value=param_data.get("min_value"),
                max_value=param_data.get("max_value"),
                pattern=param_data.get("pattern"),
            )
            parameters.append(parameter)

    # Obtener el nombre de la herramienta ('name' o 'tool_id')
    tool_name = tool_data.get("name")
    if tool_name is None:
        tool_name = tool_data.get("tool_id")

    # Crear instancia de herramienta
    tool = ATDFTool(
        name=tool_name,
        description=tool_data["description"],
        id=tool_data.get("id") or tool_data.get("tool_id"),
        version=tool_data.get("version"),
        parameters=parameters,
        category=tool_data.get("category"),
        tags=tool_data.get("tags", []),
        examples=tool_data.get("examples", []),
        metadata=tool_data.get("metadata", {}),
    )

    return tool
