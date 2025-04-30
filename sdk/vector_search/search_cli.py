#!/usr/bin/env python3
"""
CLI para búsqueda vectorial de herramientas ATDF.

Este módulo proporciona una interfaz de línea de comandos para indexar
y buscar herramientas ATDF utilizando búsqueda semántica.
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.utils import load_tools_from_directory
from .vector_store import ATDFVectorStore

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ATDFSearchCLI:
    """CLI para búsqueda vectorial de herramientas ATDF."""
    
    def __init__(self):
        """Inicializar CLI de búsqueda."""
        self.vector_store = None
        self.db_path = "./atdf_vector_db"
        self.model_name = "all-MiniLM-L6-v2"
        self.collection_name = "atdf_tools"
    
    async def initialize(self, db_path: Optional[str] = None) -> bool:
        """
        Inicializar el almacenamiento vectorial.
        
        Args:
            db_path: Ruta opcional para la base de datos
            
        Returns:
            True si la inicialización fue exitosa
        """
        if db_path:
            self.db_path = db_path
            
        self.vector_store = ATDFVectorStore(
            db_path=self.db_path,
            model_name=self.model_name,
            collection_name=self.collection_name
        )
        
        return await self.vector_store.initialize()
    
    async def index_directory(self, directory_path: str) -> bool:
        """
        Indexar herramientas ATDF desde un directorio.
        
        Args:
            directory_path: Ruta al directorio con archivos ATDF
            
        Returns:
            True si la indexación fue exitosa
        """
        if not self.vector_store:
            if not await self.initialize():
                return False
        
        logger.info(f"Cargando herramientas desde: {directory_path}")
        tools = load_tools_from_directory(directory_path)
        logger.info(f"Se encontraron {len(tools)} herramientas")
        
        if not tools:
            logger.error("No se encontraron herramientas para indexar")
            return False
        
        return await self.vector_store.create_from_tools(tools)
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar herramientas ATDF.
        
        Args:
            query: Consulta en lenguaje natural
            limit: Número máximo de resultados
            
        Returns:
            Lista de herramientas ATDF ordenadas por relevancia
        """
        if not self.vector_store:
            if not await self.initialize():
                return []
        
        options = {"limit": limit}
        results = await self.vector_store.search_tools(query, options)
        return results


def print_tool(tool: Dict[str, Any], verbose: bool = False) -> None:
    """
    Imprimir información de una herramienta.
    
    Args:
        tool: Herramienta ATDF
        verbose: Si es True, muestra información detallada
    """
    score = tool.get("score", None)
    score_str = f" (Puntuación: {score:.2f})" if score else ""
    
    print(f"\n{'-' * 50}")
    print(f"Nombre: {tool.get('name', 'Sin nombre')}{score_str}")
    print(f"Descripción: {tool.get('description', 'Sin descripción')}")
    
    if verbose:
        if "parameters" in tool and tool["parameters"]:
            print("\nParámetros:")
            for param in tool["parameters"]:
                param_name = param.get("name", "Sin nombre")
                param_desc = param.get("description", "Sin descripción")
                print(f"  - {param_name}: {param_desc}")
        
        if "returns" in tool:
            print(f"\nRetorno: {tool.get('returns', 'Sin información de retorno')}")
        
        if "examples" in tool and tool["examples"]:
            print("\nEjemplos:")
            for i, example in enumerate(tool["examples"]):
                print(f"  {i+1}. {example}")
    
    print(f"{'-' * 50}")


async def main(args) -> int:
    """
    Función principal del CLI.
    
    Args:
        args: Argumentos de línea de comandos
        
    Returns:
        Código de salida (0 en caso de éxito)
    """
    cli = ATDFSearchCLI()
    
    if args.db_path:
        cli.db_path = args.db_path
    
    if args.model:
        cli.model_name = args.model
    
    # Inicializar
    if not await cli.initialize():
        logger.error("Error al inicializar el almacenamiento vectorial")
        return 1
    
    # Indexar directorio
    if args.index:
        if not os.path.isdir(args.index):
            logger.error(f"El directorio {args.index} no existe")
            return 1
        
        logger.info(f"Indexando directorio: {args.index}")
        result = await cli.index_directory(args.index)
        
        if result:
            count = await cli.vector_store.count_tools()
            logger.info(f"Indexación completada. {count} herramientas indexadas")
        else:
            logger.error("Error al indexar herramientas")
            return 1
    
    # Buscar
    if args.query:
        logger.info(f"Buscando: {args.query}")
        results = await cli.search(args.query, limit=args.limit)
        
        if not results:
            logger.info("No se encontraron resultados")
            return 0
        
        logger.info(f"Se encontraron {len(results)} resultados")
        
        for tool in results:
            print_tool(tool, verbose=args.verbose)
        
        # Exportar resultados si se solicitó
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultados exportados a: {args.output}")
    
    return 0


def main_entry():
    """Punto de entrada para la CLI."""
    parser = argparse.ArgumentParser(description="Búsqueda vectorial de herramientas ATDF")
    
    parser.add_argument("--db-path", 
                        help="Ruta para la base de datos vectorial")
    
    parser.add_argument("--model", 
                        help="Modelo de embedding a utilizar")
    
    parser.add_argument("--index", 
                        help="Directorio con herramientas ATDF para indexar")
    
    parser.add_argument("--query", 
                        help="Consulta en lenguaje natural para buscar herramientas")
    
    parser.add_argument("--limit", type=int, default=5,
                        help="Número máximo de resultados (predeterminado: 5)")
    
    parser.add_argument("--verbose", action="store_true",
                        help="Mostrar información detallada de las herramientas")
    
    parser.add_argument("--output",
                        help="Archivo para exportar resultados en formato JSON")
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.index and not args.query:
        parser.print_help()
        print("\nError: Debe especificar al menos una acción: --index o --query")
        sys.exit(1)
    
    # Ejecutar función principal
    try:
        exit_code = asyncio.run(main(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_entry() 