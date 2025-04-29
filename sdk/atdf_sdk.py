#!/usr/bin/env python3
"""
ATDF SDK - Facilita la integración de herramientas ATDF en agentes de IA.

Este SDK proporciona clases y funciones para cargar, buscar y utilizar herramientas
descritas en formato ATDF (Agent Tool Description Format) tanto en su versión
básica (0.1.0) como en la versión extendida (0.2.0).
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional, Union, Callable

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('atdf_sdk')

class ATDFTool:
    """Clase que representa una herramienta ATDF con métodos para acceder a sus propiedades."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Inicializar una herramienta ATDF desde un diccionario de datos.
        
        Args:
            data: Diccionario con los datos de la herramienta en formato ATDF.
        """
        self._data = data
        
        # Validación básica
        required_fields = ['tool_id', 'description', 'when_to_use', 'how_to_use']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido '{field}' no encontrado en la descripción de la herramienta.")
    
    @property
    def tool_id(self) -> str:
        """Obtener el ID de la herramienta."""
        return self._data['tool_id']
    
    @property
    def description(self, language: Optional[str] = None) -> str:
        """
        Obtener la descripción de la herramienta, posiblemente en un idioma específico.
        
        Args:
            language: Código de idioma (e.g., 'es', 'en'). Si no se especifica, se usa el idioma
                     predeterminado de la herramienta.
        
        Returns:
            Descripción de la herramienta en el idioma especificado, o en el idioma predeterminado
            si no se especifica o no está disponible en el idioma solicitado.
        """
        if language and 'localization' in self._data and language in self._data['localization']:
            return self._data['localization'][language]['description']
        return self._data['description']
    
    @property
    def when_to_use(self, language: Optional[str] = None) -> str:
        """
        Obtener el contexto de uso de la herramienta, posiblemente en un idioma específico.
        
        Args:
            language: Código de idioma (e.g., 'es', 'en'). Si no se especifica, se usa el idioma
                     predeterminado de la herramienta.
        
        Returns:
            Contexto de uso de la herramienta en el idioma especificado, o en el idioma predeterminado
            si no se especifica o no está disponible en el idioma solicitado.
        """
        if language and 'localization' in self._data and language in self._data['localization']:
            return self._data['localization'][language]['when_to_use']
        return self._data['when_to_use']
    
    @property
    def inputs(self) -> List[Dict[str, Any]]:
        """Obtener la lista de parámetros de entrada de la herramienta."""
        return self._data['how_to_use']['inputs']
    
    @property
    def success_message(self) -> str:
        """Obtener el mensaje de éxito de la herramienta."""
        return self._data['how_to_use']['outputs']['success']
    
    @property
    def failure_messages(self) -> List[Dict[str, str]]:
        """Obtener la lista de posibles errores de la herramienta."""
        return self._data['how_to_use']['outputs']['failure']
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Obtener los metadatos de la herramienta si están disponibles."""
        return self._data.get('metadata', {})
    
    @property
    def examples(self) -> List[Dict[str, Any]]:
        """Obtener los ejemplos de uso de la herramienta si están disponibles."""
        return self._data.get('examples', [])
    
    @property
    def prerequisites(self) -> Dict[str, List[str]]:
        """Obtener los prerrequisitos de la herramienta si están disponibles."""
        return self._data.get('prerequisites', {})
    
    @property
    def feedback(self) -> Dict[str, List[str]]:
        """Obtener la información de feedback de la herramienta si está disponible."""
        return self._data.get('feedback', {})
    
    @property
    def supported_languages(self) -> List[str]:
        """Obtener la lista de idiomas soportados por la herramienta."""
        if 'localization' in self._data:
            return list(self._data['localization'].keys())
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir la herramienta a un diccionario."""
        return self._data
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Generar un esquema JSON para validar las entradas de la herramienta.
        
        Returns:
            Esquema JSON para validar entradas.
        """
        properties = {}
        required = []
        
        for input_param in self.inputs:
            name = input_param['name']
            param_type = input_param['type']
            description = input_param.get('description', '')
            
            if param_type == 'string':
                properties[name] = {"type": "string", "description": description}
            elif param_type == 'number':
                properties[name] = {"type": "number", "description": description}
            elif param_type == 'boolean':
                properties[name] = {"type": "boolean", "description": description}
            elif param_type == 'object' and 'schema' in input_param:
                properties[name] = input_param['schema']
                properties[name]['description'] = description
            
            # Asumir que todos los parámetros son requeridos por ahora
            required.append(name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def __str__(self) -> str:
        """Representación de cadena de la herramienta."""
        return f"ATDFTool(id={self.tool_id})"
    
    def __repr__(self) -> str:
        """Representación de cadena detallada de la herramienta."""
        return f"ATDFTool(id={self.tool_id}, desc={self.description[:30]}...)"


class ATDFToolbox:
    """Clase que representa una colección de herramientas ATDF con métodos para buscarlas y seleccionarlas."""
    
    def __init__(self):
        """Inicializar un conjunto vacío de herramientas."""
        self.tools: List[ATDFTool] = []
        self._tool_ids: Dict[str, int] = {}  # Mapeo de IDs de herramientas a índices
    
    def add_tool(self, tool: Union[ATDFTool, Dict[str, Any]]) -> None:
        """
        Añadir una herramienta al conjunto.
        
        Args:
            tool: Herramienta ATDF o diccionario con datos de herramienta.
        """
        if isinstance(tool, dict):
            tool = ATDFTool(tool)
        
        tool_id = tool.tool_id
        if tool_id in self._tool_ids:
            # Reemplazar herramienta existente
            idx = self._tool_ids[tool_id]
            self.tools[idx] = tool
            logger.info(f"Herramienta '{tool_id}' reemplazada.")
        else:
            # Añadir nueva herramienta
            self.tools.append(tool)
            self._tool_ids[tool_id] = len(self.tools) - 1
            logger.info(f"Herramienta '{tool_id}' añadida.")
    
    def remove_tool(self, tool_id: str) -> bool:
        """
        Eliminar una herramienta del conjunto.
        
        Args:
            tool_id: ID de la herramienta a eliminar.
            
        Returns:
            True si la herramienta fue eliminada, False si no se encontró.
        """
        if tool_id in self._tool_ids:
            idx = self._tool_ids[tool_id]
            del self.tools[idx]
            del self._tool_ids[tool_id]
            
            # Reconstruir el mapeo de IDs
            self._tool_ids = {t.tool_id: i for i, t in enumerate(self.tools)}
            
            logger.info(f"Herramienta '{tool_id}' eliminada.")
            return True
        
        logger.warning(f"Herramienta '{tool_id}' no encontrada.")
        return False
    
    def get_tool(self, tool_id: str) -> Optional[ATDFTool]:
        """
        Obtener una herramienta por su ID.
        
        Args:
            tool_id: ID de la herramienta a obtener.
            
        Returns:
            Herramienta ATDF si se encuentra, None en caso contrario.
        """
        if tool_id in self._tool_ids:
            return self.tools[self._tool_ids[tool_id]]
        return None
    
    def load_tool_from_file(self, filepath: str) -> bool:
        """
        Cargar una herramienta desde un archivo JSON.
        
        Args:
            filepath: Ruta al archivo JSON con la descripción de la herramienta.
            
        Returns:
            True si la herramienta se cargó correctamente, False en caso contrario.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.add_tool(data)
                return True
        except Exception as e:
            logger.error(f"Error al cargar la herramienta desde '{filepath}': {e}")
            return False
    
    def load_tools_from_directory(self, directory: str, recursive: bool = False) -> int:
        """
        Cargar todas las herramientas ATDF desde un directorio.
        
        Args:
            directory: Ruta al directorio que contiene los archivos JSON con descripciones ATDF.
            recursive: Si es True, busca también en subdirectorios.
            
        Returns:
            Número de herramientas cargadas correctamente.
        """
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"Error: Directorio '{directory}' no existe o no es un directorio.")
            return 0
        
        count = 0
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(root, filename)
                    if self.load_tool_from_file(filepath):
                        count += 1
            
            if not recursive:
                break
        
        logger.info(f"Se cargaron {count} herramientas desde '{directory}'.")
        return count
    
    def find_tools_by_text(self, text: str, language: Optional[str] = None) -> List[ATDFTool]:
        """
        Encontrar herramientas que coincidan con un texto de búsqueda.
        
        Args:
            text: Texto a buscar en descripciones y contextos de uso.
            language: Idioma preferido para la búsqueda (opcional).
            
        Returns:
            Lista de herramientas que coinciden con la búsqueda, ordenadas por relevancia.
        """
        matches = []
        for tool in self.tools:
            score = 0
            
            # Buscar en los campos principales
            if language and 'localization' in tool.to_dict() and language in tool.to_dict()['localization']:
                desc = tool.to_dict()['localization'][language]['description'].lower()
                when = tool.to_dict()['localization'][language]['when_to_use'].lower()
            else:
                desc = tool.description.lower()
                when = tool.when_to_use.lower()
            
            # Coincidencia exacta (mayor puntuación)
            if text.lower() in desc or text.lower() in when:
                score += 10
            
            # Coincidencia por palabras clave
            keywords = self._extract_keywords(text)
            for keyword in keywords:
                if keyword in desc:
                    score += 3
                if keyword in when:
                    score += 2
            
            # Revisar etiquetas si están disponibles
            if 'metadata' in tool.to_dict() and 'tags' in tool.to_dict()['metadata']:
                tags = [tag.lower() for tag in tool.to_dict()['metadata']['tags']]
                for keyword in keywords:
                    if any(keyword in tag for tag in tags):
                        score += 1
            
            # Revisar ejemplos si están disponibles
            for example in tool.examples:
                example_title = example.get('title', '').lower()
                example_desc = example.get('description', '').lower()
                if text.lower() in example_title or text.lower() in example_desc:
                    score += 1
            
            if score > 0:
                matches.append((tool, score))
        
        # Ordenar por puntuación (mayor a menor)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [tool for tool, _ in matches]
    
    def select_tool_for_task(self, task_description: str, language: Optional[str] = None) -> Optional[ATDFTool]:
        """
        Seleccionar la herramienta más adecuada para una tarea específica.
        
        Args:
            task_description: Descripción de la tarea a realizar.
            language: Idioma preferido para la búsqueda (opcional).
            
        Returns:
            La herramienta más adecuada si se encuentra, None en caso contrario.
        """
        matches = self.find_tools_by_text(task_description, language)
        return matches[0] if matches else None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extraer palabras clave de un texto.
        
        Args:
            text: Texto del que extraer palabras clave.
            
        Returns:
            Lista de palabras clave.
        """
        # Eliminar signos de puntuación y convertir a minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Dividir en palabras y filtrar palabras vacías
        words = [word.strip() for word in text.split() if len(word.strip()) > 2]
        
        # Eliminar palabras comunes (stopwords)
        stopwords = {
            'the', 'and', 'for', 'with', 'that', 'this', 'you', 'not', 'but',
            'are', 'from', 'have', 'has', 'had', 'was', 'were', 'will',
            'can', 'could', 'should', 'would', 'may', 'might', 'must',
            'then', 'than', 'when', 'where', 'what', 'which', 'who', 'whom', 'whose',
            'how', 'why', 'there', 'here', 'now', 'then', 'some', 'any', 'all',
            'many', 'much', 'more', 'most', 'other', 'another', 'such',
            
            # Español
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'lo', 'al', 'del',
            'que', 'esto', 'eso', 'aquello', 'como', 'cómo', 'cuando', 'cuándo',
            'donde', 'dónde', 'quien', 'quién', 'quienes', 'qué', 'porque', 'por',
            'para', 'sin', 'sobre', 'bajo', 'desde', 'hasta', 'entre', 'hacia',
            'ser', 'estar', 'haber', 'tener', 'hacer', 'poder', 'deber', 'querer'
        }
        
        keywords = [word for word in words if word not in stopwords]
        
        return keywords
    
    def __len__(self) -> int:
        """Obtener el número de herramientas en el conjunto."""
        return len(self.tools)
    
    def __iter__(self):
        """Iterar sobre las herramientas del conjunto."""
        return iter(self.tools)
    
    def __getitem__(self, index: int) -> ATDFTool:
        """Obtener una herramienta por su índice."""
        return self.tools[index]


# Funciones de utilidad

def load_toolbox_from_directory(directory: str, recursive: bool = False) -> ATDFToolbox:
    """
    Cargar todas las herramientas ATDF desde un directorio en un nuevo conjunto de herramientas.
    
    Args:
        directory: Ruta al directorio que contiene los archivos JSON con descripciones ATDF.
        recursive: Si es True, busca también en subdirectorios.
        
    Returns:
        Conjunto de herramientas ATDF cargadas desde el directorio.
    """
    toolbox = ATDFToolbox()
    toolbox.load_tools_from_directory(directory, recursive)
    return toolbox

def find_best_tool(toolbox: ATDFToolbox, goal: str, language: Optional[str] = None) -> Optional[ATDFTool]:
    """
    Encontrar la mejor herramienta para un objetivo específico.
    
    Args:
        toolbox: Conjunto de herramientas ATDF.
        goal: Objetivo o descripción de la tarea.
        language: Idioma preferido para la búsqueda (opcional).
        
    Returns:
        La mejor herramienta si se encuentra, None en caso contrario.
    """
    return toolbox.select_tool_for_task(goal, language)

if __name__ == "__main__":
    # Ejemplo de uso
    print("ATDF SDK - Agent Tool Description Format")
    print("Este módulo no está diseñado para ejecutarse directamente.")
    print("Importe las clases y funciones en su código:")
    print("  from atdf_sdk import ATDFTool, ATDFToolbox, load_toolbox_from_directory") 