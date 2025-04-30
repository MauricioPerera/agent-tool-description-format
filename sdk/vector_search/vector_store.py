"""
Implementación del almacenamiento vectorial para herramientas ATDF.

Este módulo contiene la clase principal para indexar y buscar
herramientas ATDF utilizando embeddings y búsqueda semántica.
"""

import os
import json
import tempfile
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

import numpy as np

# Importación opcional de dependencias
try:
    import lancedb
    from lancedb.table import Table
    from sentence_transformers import SentenceTransformer
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)


class ATDFVectorStore:
    """
    Almacenamiento vectorial para herramientas ATDF.
    
    Esta clase permite indexar y buscar herramientas ATDF utilizando
    búsqueda semántica basada en embeddings.
    """
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        db_path: Optional[str] = None,
        table_name: str = "atdf_tools"
    ):
        """
        Inicializar el almacenamiento vectorial.
        
        Args:
            model_name: Nombre del modelo de SentenceTransformer a utilizar
            db_path: Ruta a la base de datos LanceDB (None para usar una en memoria)
            table_name: Nombre de la tabla en LanceDB
            
        Raises:
            ImportError: Si las dependencias opcionales no están instaladas
        """
        if not VECTOR_SEARCH_AVAILABLE:
            raise ImportError(
                "Las dependencias para búsqueda vectorial no están instaladas. "
                "Instálalas con: pip install lancedb sentence-transformers"
            )
        
        self.model_name = model_name
        self.table_name = table_name
        
        # Usar un directorio temporal si no se proporciona ruta
        if db_path is None:
            self._temp_dir = tempfile.TemporaryDirectory()
            db_path = self._temp_dir.name
            self._is_temp = True
        else:
            self._is_temp = False
        
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Inicializar la base de datos
        self.db = lancedb.connect(db_path)
        self._initialize_table()
    
    def _initialize_table(self):
        """
        Inicializar o abrir la tabla en LanceDB.
        """
        # Comprobar si la tabla existe
        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
        else:
            # Datos de inicialización con la estructura deseada
            init_data = [{
                "id": "_init_",
                "name": "_init_",
                "description": "_init_",
                "parameters": [],
                "vector": np.zeros(self.embedding_dim, dtype=np.float32),
                "raw_data": "{}"
            }]
            
            # Crear tabla permitiendo que LanceDB infiera el esquema
            # Ya no pasamos explícitamente nuestro `schema` dict
            self.table = self.db.create_table(
                self.table_name,
                data=init_data
            )
            # Eliminar el registro de inicialización
            self.table.delete("id = '_init_'")
    
    def _create_text_representation(self, tool: Dict[str, Any]) -> str:
        """
        Crear una representación textual de una herramienta para generar embeddings.
        
        Args:
            tool: Diccionario con datos de la herramienta
            
        Returns:
            Representación textual de la herramienta
        """
        text = f"{tool['name']}: {tool['description']}"
        
        if 'parameters' in tool and tool['parameters']:
            for param in tool['parameters']:
                text += f" {param['name']}: {param['description']}"
        
        return text
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generar embedding para un texto.
        
        Args:
            text: Texto para generar embedding
            
        Returns:
            Vector de embedding
        """
        return self.model.encode(text, show_progress_bar=False)
    
    def add_tool(self, tool: Dict[str, Any]) -> bool:
        """
        Añadir una herramienta al almacenamiento vectorial.
        
        Args:
            tool: Diccionario con datos de la herramienta
            
        Returns:
            True si la herramienta se ha añadido correctamente
        """
        if 'name' not in tool or 'description' not in tool:
            logger.warning("La herramienta debe tener al menos un nombre y una descripción")
            return False
        
        # Crear ID para la herramienta
        tool_id = tool.get('id', tool['name'].lower().replace(' ', '_'))
        
        # Generar texto para embedding
        text_repr = self._create_text_representation(tool)
        
        # Generar embedding
        vector = self._generate_embedding(text_repr)
        
        # Preparar parámetros para almacenamiento
        parameters = tool.get('parameters', [])
        
        # Preparar datos para inserción
        data = {
            "id": tool_id,
            "name": tool['name'],
            "description": tool['description'],
            "parameters": parameters,
            "vector": vector,
            "raw_data": json.dumps(tool)
        }
        
        # Verificar si ya existe una herramienta con el mismo ID
        existing = self.table.search().where(f"id = '{tool_id}'").limit(1).to_pandas()
        
        if len(existing) > 0:
            # Actualizar herramienta existente
            self.table.delete(f"id = '{tool_id}'")
        
        # Insertar la herramienta
        self.table.add([data])
        return True
    
    def add_tools(self, tools: List[Dict[str, Any]]) -> int:
        """
        Añadir múltiples herramientas al almacenamiento vectorial.
        
        Args:
            tools: Lista de diccionarios con datos de herramientas
            
        Returns:
            Número de herramientas añadidas correctamente
        """
        successful = 0
        for tool in tools:
            if self.add_tool(tool):
                successful += 1
        
        return successful
    
    def search(
        self, 
        query: str, 
        limit: int = 5, 
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Buscar herramientas basadas en una consulta textual.
        
        Args:
            query: Consulta textual
            limit: Número máximo de resultados
            score_threshold: Umbral mínimo de puntuación (0-1)
            
        Returns:
            Lista de tuplas (herramienta, puntuación)
        """
        # Generar embedding para la consulta
        query_vector = self._generate_embedding(query)
        
        # Realizar búsqueda vectorial
        results = (
            self.table.search(query_vector)
            .limit(limit)
            .to_pandas()
        )
        
        # Preparar resultados
        tools_with_scores = []
        for _, row in results.iterrows():
            score = float(row['_distance'])
            
            # Normalizar distancia a puntuación (0-1)
            normalized_score = 1.0 - min(score, 2.0) / 2.0
            
            # Filtrar por umbral si se especifica
            if score_threshold is not None and normalized_score < score_threshold:
                continue
            
            # Recuperar datos originales
            tool_data = json.loads(row['raw_data'])
            
            tools_with_scores.append((tool_data, normalized_score))
        
        return tools_with_scores
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Obtener todas las herramientas almacenadas.
        
        Returns:
            Lista de herramientas
        """
        results = self.table.to_pandas()
        
        tools = []
        for _, row in results.iterrows():
            tool_data = json.loads(row['raw_data'])
            tools.append(tool_data)
        
        return tools
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener una herramienta por su ID.
        
        Args:
            tool_id: ID de la herramienta
            
        Returns:
            Datos de la herramienta o None si no se encuentra
        """
        results = self.table.search().where(f"id = '{tool_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return json.loads(results.iloc[0]['raw_data'])
    
    def delete_tool(self, tool_id: str) -> bool:
        """
        Eliminar una herramienta por su ID.
        
        Args:
            tool_id: ID de la herramienta
            
        Returns:
            True si la herramienta se ha eliminado correctamente
        """
        count = self.table.delete(f"id = '{tool_id}'")
        return count > 0
        
    def __del__(self):
        """
        Limpieza al destruir la instancia.
        """
        if hasattr(self, '_temp_dir') and self._is_temp:
            self._temp_dir.cleanup() 