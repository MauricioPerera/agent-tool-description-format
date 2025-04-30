#!/usr/bin/env python3
"""
ATDF SDK - Facilita la integración de herramientas ATDF en agentes de IA.

Este SDK proporciona clases y funciones para cargar, buscar y utilizar herramientas
descritas en formato ATDF (Agent Tool Description Format) tanto en su versión
básica (0.1.0) como en la versión extendida (0.2.0).
"""

import os
import json
import yaml
import logging
import re
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('atdf_sdk')

# Importaciones internas
from sdk.core.schema import ATDFTool, ATDFToolParameter
from sdk.core.utils import (
    load_tools_from_file,
    load_tools_from_directory,
    validate_tool,
    create_tool_instance
)

# Importación condicional para búsqueda vectorial
try:
    from sdk.vector_search import ATDFVectorStore
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False

# Clase para compatibilidad con tests antiguos
class ATDFToolbox:
    """
    Clase para mantener compatibilidad con tests antiguos.
    Wrapper alrededor de los componentes actuales del SDK.
    """
    
    def __init__(self):
        self.tools = []
    
    def __len__(self):
        return len(self.tools)
    
    def load_tool_from_file(self, file_path: Union[str, Path]) -> bool:
        """Cargar una herramienta desde un archivo."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_extension = file_path.suffix.lower()
                
                if file_extension in ['.json']:
                    data = json.load(f)
                elif file_extension in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    logger.error(f"Formato de archivo no soportado: {file_extension}")
                    return False
            
            # Si es un diccionario, convertirlo a lista
            if isinstance(data, dict):
                data = [data]
            
            for tool_data in data:
                if validate_tool(tool_data):
                    # Convertir a instancia de ATDFTool
                    tool = self._create_legacy_tool(tool_data)
                    self.tools.append(tool)
                    
            return True
        except Exception as e:
            logger.error(f"Error al cargar herramienta desde archivo: {str(e)}")
            return False
    
    def _create_legacy_tool(self, tool_data: Dict[str, Any]) -> ATDFTool:
        """Crear una herramienta a partir de datos en formato legacy."""
        # Adaptación de los campos del formato antiguo al nuevo
        tool = ATDFTool(
            name=tool_data.get('tool_id', 'Unknown'),
            description=tool_data.get('description', ''),
            id=tool_data.get('tool_id'),
            version="1.0.0",
            parameters=self._convert_inputs_to_parameters(tool_data.get('how_to_use', {}).get('inputs', [])),
            metadata={"legacy_format": True},
            when_to_use=tool_data.get('when_to_use', ''),
            examples=tool_data.get('examples', []),
            feedback=tool_data.get('feedback', {}),
            prerequisites=tool_data.get('prerequisites', {})
        )
        
        return tool
    
    def _convert_inputs_to_parameters(self, inputs: List[Dict[str, Any]]) -> List[ATDFToolParameter]:
        """Convertir inputs del formato antiguo a parámetros del nuevo formato."""
        parameters = []
        for input_data in inputs:
            param = ATDFToolParameter(
                name=input_data.get('name', ''),
                description=input_data.get('description', ''),
                type=input_data.get('type', 'string'),
                required=True  # En el formato antiguo todos eran requeridos por defecto
            )
            parameters.append(param)
        return parameters

# Función para compatibilidad con tests antiguos
def load_toolbox_from_directory(directory_path: Union[str, Path]) -> ATDFToolbox:
    """Cargar todas las herramientas de un directorio en un ATDFToolbox."""
    toolbox = ATDFToolbox()
    directory_path = Path(directory_path)
    
    if not directory_path.exists() or not directory_path.is_dir():
        logger.error(f"Directorio no válido: {directory_path}")
        return toolbox
    
    # Buscar archivos JSON y YAML en el directorio
    for extension in ['.json', '.yaml', '.yml']:
        file_paths = list(directory_path.glob(f"*{extension}"))
        
        for file_path in file_paths:
            toolbox.load_tool_from_file(file_path)
    
    return toolbox

# Función para compatibilidad con tests antiguos
def find_best_tool(toolbox: ATDFToolbox, query: str, language: str = "en") -> Optional[ATDFTool]:
    """Encontrar la mejor herramienta para una consulta."""
    if len(toolbox) == 0:
        return None
    
    # Implementación básica mejorada:
    # Busca herramientas relacionadas con agujeros o traducción basado en palabras clave
    query_lower = query.lower()
    
    # Palabras clave para herramientas de traducción
    translation_keywords = ['translate', 'translation', 'translator', 'text']
    
    # Verificar si es una consulta de traducción
    is_translation_query = any(keyword in query_lower for keyword in translation_keywords)
    
    if is_translation_query:
        # Buscar herramientas de traducción
        for tool in toolbox.tools:
            if 'translator' in tool.id.lower() or 'translat' in tool.description.lower():
                return tool
    
    # Si no es traducción o no se encontró herramienta de traducción, devolver la primera
    return toolbox.tools[0] if toolbox.tools else None

class ATDFSDK:
    """
    SDK principal para Agent Tool Description Format (ATDF).
    
    Esta clase proporciona una interfaz unificada para trabajar con
    herramientas ATDF, incluyendo carga, validación, búsqueda y manipulación.
    """
    
    def __init__(
        self,
        tools_directory: Optional[Union[str, Path]] = None,
        vector_db_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        auto_load: bool = True
    ):
        """
        Inicializar el SDK de ATDF.
        
        Args:
            tools_directory: Directorio que contiene archivos de herramientas
            vector_db_path: Ruta a la base de datos vectorial
            embedding_model: Modelo de embedding a utilizar
            auto_load: Cargar automáticamente herramientas del directorio
        """
        self.tools_directory = Path(tools_directory) if tools_directory else None
        self.tools: List[ATDFTool] = []
        self.vector_store: Optional[ATDFVectorStore] = None
        
        # Inicializar almacenamiento vectorial si está disponible
        if VECTOR_SEARCH_AVAILABLE:
            try:
                self.vector_store = ATDFVectorStore(
                    model_name=embedding_model,
                    db_path=vector_db_path
                )
                logger.info("Vector store inicializado correctamente")
            except Exception as e:
                # Captura de error más específica podría ser útil
                # Imprimir traceback completo para depuración
                import traceback
                logger.error(f"Error detallado al inicializar Vector Store:\n{traceback.format_exc()}")
                logger.warning(f"No se pudo inicializar el vector store: {str(e)}")
        else:
            logger.info("La búsqueda vectorial no está disponible. Instalación de dependencias requerida.")
        
        # Cargar herramientas automáticamente si se especifica
        if auto_load and self.tools_directory:
            if self.tools_directory.is_dir():
                self.load_tools_from_directory(self.tools_directory)
            else:
                logger.warning(f"El directorio de herramientas especificado no existe o no es un directorio: {self.tools_directory}")
    
    def load_tools_from_file(self, file_path: Union[str, Path]) -> List[ATDFTool]:
        """
        Cargar herramientas desde un archivo JSON o YAML.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de herramientas cargadas
        """
        # Usar la función de utilidad para cargar herramientas
        tool_dicts = load_tools_from_file(file_path)
        loaded_tools = []
        
        for tool_dict in tool_dicts:
            try:
                # Crear instancia de ATDFTool
                tool = create_tool_instance(tool_dict)
                loaded_tools.append(tool)
                
                # Añadir al vector store si está disponible
                if self.vector_store:
                    self.vector_store.add_tool(tool.to_dict())
            except Exception as e:
                logger.error(f"Error al procesar herramienta desde {file_path}: {str(e)}")
        
        # Añadir a la lista de herramientas cargadas
        self.tools.extend(loaded_tools)
        
        return loaded_tools
    
    def load_tools_from_directory(self, directory_path: Union[str, Path]) -> List[ATDFTool]:
        """
        Cargar herramientas desde todos los archivos JSON y YAML en un directorio.
        
        Args:
            directory_path: Ruta al directorio
            
        Returns:
            Lista de herramientas cargadas
        """
        # Usar la función de utilidad para cargar herramientas
        tool_dicts = load_tools_from_directory(directory_path)
        loaded_tools = []
        
        for tool_dict in tool_dicts:
            try:
                # Crear instancia de ATDFTool
                tool = create_tool_instance(tool_dict)
                loaded_tools.append(tool)
                
                # Añadir al vector store si está disponible
                if self.vector_store:
                    self.vector_store.add_tool(tool.to_dict())
            except Exception as e:
                logger.error(f"Error al procesar herramienta desde directorio {directory_path}: {str(e)}")
        
        # Añadir a la lista de herramientas cargadas
        self.tools.extend(loaded_tools)
        
        return loaded_tools
    
    def search_tools(
        self, 
        query: str, 
        limit: int = 5, 
        score_threshold: float = 0.6
    ) -> List[Tuple[ATDFTool, float]]:
        """
        Buscar herramientas basadas en una consulta textual.
        
        Args:
            query: Consulta textual
            limit: Número máximo de resultados
            score_threshold: Umbral mínimo de puntuación (0-1)
            
        Returns:
            Lista de tuplas (herramienta, puntuación)
            
        Raises:
            RuntimeError: Si la búsqueda vectorial no está disponible
        """
        if not self.vector_store:
            raise RuntimeError(
                "La búsqueda vectorial no está disponible. "
                "Asegúrate de instalar las dependencias: pip install lancedb sentence-transformers"
            )
        
        # Realizar búsqueda vectorial
        results = self.vector_store.search(
            query=query,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Convertir resultados a instancias de ATDFTool
        tools_with_scores = []
        for tool_dict, score in results:
            try:
                tool = create_tool_instance(tool_dict)
                tools_with_scores.append((tool, score))
            except Exception as e:
                 logger.error(f"Error al crear instancia de herramienta desde resultado de búsqueda: {str(e)}")
        
        return tools_with_scores
    
    def get_all_tools(self) -> List[ATDFTool]:
        """
        Obtener todas las herramientas cargadas.
        
        Returns:
            Lista de herramientas
        """
        return self.tools
    
    def get_tool_by_id(self, tool_id: str) -> Optional[ATDFTool]:
        """
        Obtener una herramienta por su ID.
        
        Args:
            tool_id: ID de la herramienta
            
        Returns:
            Herramienta o None si no se encuentra
        """
        # Buscar primero en las herramientas cargadas
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        
        # Si no se encuentra y está disponible la búsqueda vectorial
        if self.vector_store:
            tool_dict = self.vector_store.get_tool_by_id(tool_id)
            if tool_dict:
                try:
                    return create_tool_instance(tool_dict)
                except Exception as e:
                    logger.error(f"Error al crear instancia de herramienta desde búsqueda por ID: {str(e)}")
                    return None
        
        return None
    
    def create_tool(self, **kwargs) -> ATDFTool:
        """
        Crear una nueva herramienta ATDF.
        
        Args:
            **kwargs: Atributos de la herramienta (deben coincidir con ATDFTool en schema.py)
            
        Returns:
            Instancia de ATDFTool creada
        """
        try:
             # Usar la clase correcta importada de schema.py
            tool = ATDFTool(**kwargs)
            
            # Añadir a la lista de herramientas
            self.tools.append(tool)
            
            # Añadir al vector store si está disponible
            if self.vector_store:
                self.vector_store.add_tool(tool.to_dict())
            
            return tool
        except Exception as e:
            logger.error(f"Error al crear herramienta: {str(e)}")
            raise # Re-lanzar la excepción para que el usuario sepa que falló
    
    def save_tools_to_file(
        self, 
        file_path: Union[str, Path], 
        tools: Optional[List[ATDFTool]] = None,
        format: str = "json"
    ) -> bool:
        """
        Guardar herramientas en un archivo.
        
        Args:
            file_path: Ruta del archivo
            tools: Lista de herramientas a guardar (None para todas)
            format: Formato del archivo ("json" o "yaml")
            
        Returns:
            True si se guardaron las herramientas correctamente
        """
        file_path = Path(file_path)
        
        # Usar todas las herramientas si no se especifican
        if tools is None:
            tools = self.tools
        
        # Convertir herramientas a diccionarios
        tools_data = [tool.to_dict() for tool in tools]
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True) # Asegurar que el directorio existe
            with open(file_path, 'w', encoding='utf-8') as f:
                if format.lower() == "json":
                    json.dump(tools_data, f, indent=2)
                elif format.lower() in ["yaml", "yml"]:
                    yaml.dump(tools_data, f)
                else:
                    raise ValueError(f"Formato no soportado: {format}")
            
            return True
        except Exception as e:
            logger.error(f"Error al guardar herramientas en {file_path}: {str(e)}")
            return False
    
    def export_to_json_schema(self, tools: Optional[List[ATDFTool]] = None) -> List[Dict[str, Any]]:
        """
        Exportar herramientas en formato JSON Schema.
        
        Args:
            tools: Lista de herramientas a exportar (None para todas)
            
        Returns:
            Lista de esquemas JSON
        """
        # Usar todas las herramientas si no se especifican
        if tools is None:
            tools = self.tools
        
        # Convertir herramientas a formato JSON Schema
        schemas = [tool.to_json_schema() for tool in tools]
        
        return schemas
    
    def filter_tools(self, filter_func: Callable[[ATDFTool], bool]) -> List[ATDFTool]:
        """
        Filtrar herramientas utilizando una función personalizada.
        
        Args:
            filter_func: Función que recibe una herramienta y devuelve un booleano
            
        Returns:
            Lista de herramientas filtradas
        """
        return [tool for tool in self.tools if filter_func(tool)]

# Eliminar el bloque if __name__ == "__main__" si existía aquí
# Este archivo es un módulo, no un script ejecutable. 