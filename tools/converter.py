#!/usr/bin/env python3
"""
Conversor de formatos ATDF.

Este módulo proporciona funciones para convertir entre diferentes versiones
y formatos de ATDF, incluyendo la conversión del formato básico al mejorado.
"""

import os
import json
import yaml
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('converter')

def load_tool(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Cargar una herramienta desde un archivo JSON o YAML.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Diccionario con los datos de la herramienta o None si hay error
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"Archivo no encontrado: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.json']:
                data = json.load(f)
            elif file_extension in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                logger.error(f"Formato de archivo no soportado: {file_extension}")
                return None
        
        logger.info(f"Herramienta cargada desde {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error al cargar herramienta desde archivo {file_path}: {str(e)}")
        return None

def save_tool(tool: Dict[str, Any], file_path: Union[str, Path], format: str = "json") -> bool:
    """
    Guardar una herramienta en un archivo JSON o YAML.
    
    Args:
        tool: Diccionario con los datos de la herramienta
        file_path: Ruta al archivo de destino
        format: Formato de salida ("json" o "yaml")
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        file_path = Path(file_path)
        
        # Crear directorios si no existen
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == "json":
                json.dump(tool, f, indent=2, ensure_ascii=False)
            elif format.lower() in ["yaml", "yml"]:
                yaml.dump(tool, f, default_flow_style=False, allow_unicode=True)
            else:
                logger.error(f"Formato de salida no soportado: {format}")
                return False
        
        logger.info(f"Herramienta guardada en {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar herramienta en archivo {file_path}: {str(e)}")
        return False

def convert_to_enhanced(basic_tool: Dict[str, Any], author: str = "ATDF Converter", extract_language: bool = False) -> Dict[str, Any]:
    """
    Convertir una herramienta del formato básico al formato mejorado.
    
    Args:
        basic_tool: Herramienta en formato básico
        author: Autor para los metadatos
        extract_language: Si es True, intentará extraer información del idioma
        
    Returns:
        Herramienta en formato mejorado
    """
    if not basic_tool:
        return {}
    
    # Copiar la herramienta básica
    enhanced_tool = basic_tool.copy()
    
    # Añadir versión de esquema
    enhanced_tool["schema_version"] = "2.0.0"
    
    # Añadir sección de metadatos
    enhanced_tool["metadata"] = {
        "version": "1.0.0",
        "author": author,
        "tags": ["converted", "basic"],
        "category": "auto_converted",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    # Añadir sección de localización si se solicita
    if extract_language:
        # Detectar el idioma actual (simple)
        current_language = "en"  # Por defecto
        description = basic_tool.get("description", "")
        when_to_use = basic_tool.get("when_to_use", "")
        
        # Heurística simple basada en palabras comunes
        es_words = ["el", "la", "los", "las", "necesita", "para", "cuando", "hacer", "usar"]
        pt_words = ["o", "a", "os", "as", "precisa", "para", "quando", "fazer", "usar"]
        
        # Contar palabras en español y portugués
        es_count = sum(1 for word in es_words if word in description.lower() or word in when_to_use.lower())
        pt_count = sum(1 for word in pt_words if word in description.lower() or word in when_to_use.lower())
        
        if es_count > pt_count and es_count > 2:
            current_language = "es"
        elif pt_count > es_count and pt_count > 2:
            current_language = "pt"
        
        # Añadir localización
        enhanced_tool["localization"] = {
            current_language: {
                "description": description,
                "when_to_use": when_to_use
            }
        }
        
        # Actualizar en inglés si no lo está
        if current_language != "en":
            enhanced_tool["description"] = f"[Auto-translated from {current_language}] {description}"
            enhanced_tool["when_to_use"] = f"[Auto-translated from {current_language}] {when_to_use}"
    
    # Añadir sección de prerequisitos
    enhanced_tool["prerequisites"] = {
        "tools": [],
        "conditions": [],
        "permissions": []
    }
    
    # Añadir sección de feedback
    enhanced_tool["feedback"] = {
        "progress_indicators": ["Operation in progress"],
        "completion_signals": ["Operation completed"]
    }
    
    # Añadir sección de ejemplos
    enhanced_tool["examples"] = [
        {
            "goal": f"Example use of {basic_tool.get('tool_id', 'the tool')}",
            "input_values": {},
            "expected_result": basic_tool.get("how_to_use", {}).get("outputs", {}).get("success", "Success")
        }
    ]
    
    logger.info(f"Herramienta convertida a formato mejorado: {enhanced_tool.get('tool_id', 'unknown')}")
    return enhanced_tool

def convert_to_basic(enhanced_tool: Dict[str, Any], preserve_id_field: bool = True) -> Dict[str, Any]:
    """
    Convertir una herramienta del formato mejorado al formato básico.
    
    Args:
        enhanced_tool: Herramienta en formato mejorado
        preserve_id_field: Si es True, conserva el campo id si existe
        
    Returns:
        Herramienta en formato básico
    """
    if not enhanced_tool:
        return {}
    
    # Inicializar herramienta básica con los campos obligatorios
    basic_tool = {
        "schema_version": "1.0.0",
        "description": enhanced_tool.get("description", "No description provided"),
        "when_to_use": enhanced_tool.get("when_to_use", "No usage context provided"),
        "how_to_use": enhanced_tool.get("how_to_use", {"inputs": [], "outputs": {"success": "Success", "failure": []}})
    }
    
    # Añadir identificador, priorizando tool_id sobre id
    if "tool_id" in enhanced_tool:
        basic_tool["tool_id"] = enhanced_tool["tool_id"]
    elif "id" in enhanced_tool and preserve_id_field:
        basic_tool["id"] = enhanced_tool["id"]
    elif "id" in enhanced_tool:
        basic_tool["tool_id"] = enhanced_tool["id"]
    else:
        basic_tool["tool_id"] = "unknown_tool"
    
    # Verificar estructura de how_to_use
    if "how_to_use" not in enhanced_tool:
        basic_tool["how_to_use"] = {
            "inputs": [],
            "outputs": {
                "success": "Operation completed successfully",
                "failure": [
                    {
                        "code": "error_default",
                        "description": "An error occurred"
                    }
                ]
            }
        }
    
    logger.info(f"Herramienta convertida a formato básico: {basic_tool.get('tool_id', basic_tool.get('id', 'unknown'))}")
    return basic_tool 