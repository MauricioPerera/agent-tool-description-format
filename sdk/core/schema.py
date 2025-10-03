"""
Definiciones de esquema para herramientas ATDF.

Este módulo contiene las clases principales para definir y trabajar
con herramientas en formato ATDF (Agent Tool Description Format).
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field


class ATDFToolParameter(BaseModel):
    """
    Modelo para los parámetros de una herramienta ATDF.
    """
    name: str
    description: Optional[str] = None
    type: str
    required: bool = False
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class ATDFTool(BaseModel):
    """
    Modelo para una herramienta ATDF.
    """
    name: str
    description: str
    id: Optional[str] = None
    tool_id: Optional[str] = None
    version: Optional[str] = "1.0.0"
    parameters: List[ATDFToolParameter] = []
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Campos adicionales para compatibilidad con tests
    when_to_use: Optional[str] = None
    prerequisites: Optional[Dict[str, Any]] = {}
    feedback: Optional[Dict[str, Any]] = {}
    
    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Permitir inicialización con diccionarios o argumentos nombrados."""

        # Soportar el patrón legado ATDFTool(tool_dict)
        if data is not None:
            if not isinstance(data, dict):
                raise TypeError("ATDFTool espera un diccionario o argumentos nombrados")

            if kwargs:
                merged = {**data, **kwargs}
            else:
                merged = data
        else:
            merged = kwargs

        # Manejar el alias entre id y tool_id
        if 'tool_id' in merged and 'id' not in merged:
            merged['id'] = merged['tool_id']
        elif 'id' in merged and 'tool_id' not in merged:
            merged['tool_id'] = merged['id']

        if 'name' not in merged and 'tool_id' in merged:
            merged['name'] = merged['tool_id']

        super().__init__(**merged)
    
    @property
    def inputs(self):
        """Propiedad para mantener compatibilidad con tests antiguos."""
        return self.parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        result = self.model_dump(exclude_none=True)
        # Asegurar que tool_id siempre esté presente en la salida
        if 'id' in result and 'tool_id' not in result:
            result['tool_id'] = result['id']
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convertir la herramienta a formato JSON.
        
        Args:
            indent: Nivel de indentación para el JSON
            
        Returns:
            Representación JSON de la herramienta
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convertir a formato JSON Schema."""
        # Implementación básica como ejemplo
        schema = {
            "name": self.name,
            "description": self.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # Añadir parámetros
        for param in self.parameters:
            schema["parameters"]["properties"][param.name] = {
                "type": param.type,
                "description": param.description or ""
            }
            if param.required:
                schema["parameters"]["required"].append(param.name)
        
        return schema
    
    def copy(self) -> 'ATDFTool':
        """
        Crear una copia de la herramienta.
        
        Returns:
            Copia de la herramienta
        """
        return ATDFTool(
            name=self.name,
            description=self.description,
            id=self.id,
            version=self.version,
            parameters=self.parameters.copy() if self.parameters else None,
            category=self.category,
            tags=self.tags.copy() if self.tags else None,
            examples=self.examples.copy() if self.examples else None,
            metadata=self.metadata.copy() if self.metadata else None
        )

    def get_input_schema(self) -> Dict[str, Any]:
        """
        Genera un esquema de entrada para validación.
        Mantiene compatibilidad con versiones antiguas.
        
        Returns:
            Esquema de validación para los parámetros de entrada
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in self.parameters:
            schema["properties"][param.name] = {
                "type": param.type,
                "description": param.description or ""
            }
            if param.required:
                schema["required"].append(param.name)
                
        return schema 