#!/usr/bin/env python3
"""
CLI para búsqueda vectorial de herramientas ATDF.

Este script proporciona una interfaz de línea de comandos para:
1. Indexar herramientas ATDF en una base de datos vectorial
2. Buscar herramientas utilizando consultas en lenguaje natural
3. Administrar la base de datos vectorial

Uso:
    python sdk/vector_search_cli.py index --tools-dir ./tools
    python sdk/vector_search_cli.py search "enviar un correo electrónico"
    python sdk/vector_search_cli.py search "find weather information" --limit 3 --lang en
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atdf-vector-cli")

# Verificar si las dependencias de búsqueda vectorial están instaladas
try:
    from sdk.atdf_sdk import ATDFTool, ATDFToolbox
    from sdk.vector_search import ATDFVectorStore

    HAS_VECTOR_DEPENDENCIES = True
except ImportError as e:
    logger.warning(
        f"Error al importar dependencias: {e}. "
        "Asegúrate de tener instaladas las dependencias necesarias: "
        "pip install lancedb sentence-transformers"
    )
    HAS_VECTOR_DEPENDENCIES = False


def load_tools_from_directory(tools_dir: str) -> List[Dict[str, Any]]:
    """
    Cargar herramientas ATDF desde un directorio.

    Args:
        tools_dir: Ruta al directorio con archivos JSON de herramientas

    Returns:
        Lista de diccionarios con datos de herramientas
    """
    tools = []
    tools_path = Path(tools_dir)

    if not tools_path.exists() or not tools_path.is_dir():
        logger.error(f"El directorio {tools_dir} no existe o no es un directorio")
        return []

    # Buscar archivos JSON en el directorio y subdirectorios
    json_files = list(tools_path.glob("**/*.json"))
    logger.info(f"Se encontraron {len(json_files)} archivos JSON en {tools_dir}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                tool_data = json.load(f)

                # Verificar que el archivo tiene la estructura mínima de una herramienta ATDF
                if all(key in tool_data for key in ["tool_id", "description"]):
                    tools.append(tool_data)
                    logger.debug(f"Cargada herramienta: {tool_data['tool_id']}")
                else:
                    logger.warning(
                        f"El archivo {json_file} no tiene la estructura "
                        "mínima de una herramienta ATDF"
                    )
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar el archivo JSON: {json_file}")
        except Exception as e:
            logger.error(f"Error al procesar el archivo {json_file}: {e}")

    return tools


async def index_tools(args) -> None:
    """
    Indexar herramientas en la base de datos vectorial.

    Args:
        args: Argumentos de línea de comandos
    """
    if not HAS_VECTOR_DEPENDENCIES:
        logger.error("Dependencias de búsqueda vectorial no instaladas")
        return

    # Cargar herramientas
    tools_data = []

    if args.tools_dir:
        tools_data = load_tools_from_directory(args.tools_dir)
        logger.info(
            f"Se cargaron {len(tools_data)} herramientas desde {args.tools_dir}"
        )

    if args.tools_file:
        try:
            with open(args.tools_file, "r", encoding="utf-8") as f:
                file_tools = json.load(f)
                if isinstance(file_tools, list):
                    tools_data.extend(file_tools)
                    logger.info(
                        f"Se cargaron {len(file_tools)} herramientas desde {args.tools_file}"
                    )
                else:
                    logger.error(
                        f"El archivo {args.tools_file} no contiene una lista de herramientas"
                    )
        except Exception as e:
            logger.error(f"Error al cargar herramientas desde {args.tools_file}: {e}")

    if not tools_data:
        logger.error("No se encontraron herramientas para indexar")
        return

    # Convertir a objetos ATDFTool
    atdf_tools = [ATDFTool(tool_data) for tool_data in tools_data]

    # Inicializar y crear vector store
    vector_store = ATDFVectorStore(db_path=args.db_path, model_name=args.model)

    logger.info(f"Inicializando almacén vectorial en {args.db_path}...")
    await vector_store.initialize()

    logger.info(f"Indexando {len(atdf_tools)} herramientas...")
    success = await vector_store.create_from_tools(atdf_tools)

    if success:
        logger.info("✅ Indexación completada con éxito")
    else:
        logger.error("❌ Error durante la indexación")


async def search_tools(args) -> None:
    """
    Buscar herramientas mediante consulta semántica.

    Args:
        args: Argumentos de línea de comandos
    """
    if not HAS_VECTOR_DEPENDENCIES:
        logger.error("Dependencias de búsqueda vectorial no instaladas")
        return

    # Verificar que existe la base de datos
    if not os.path.exists(args.db_path):
        logger.error(f"La base de datos {args.db_path} no existe")
        logger.info(
            "Primero debes indexar herramientas con: python sdk/vector_search_cli.py index"
        )
        return

    # Inicializar vector store
    vector_store = ATDFVectorStore(db_path=args.db_path, model_name=args.model)

    logger.info(f"Inicializando almacén vectorial en {args.db_path}...")
    await vector_store.initialize()

    # Configurar opciones de búsqueda
    options = {"limit": args.limit}

    if args.lang:
        options["language"] = args.lang

    if args.category:
        options["category"] = args.category

    if args.tags:
        options["tags"] = args.tags.split(",")

    # Realizar búsqueda
    logger.info(f"Buscando: '{args.query}'")
    results = await vector_store.search_tools(args.query, options)

    # Mostrar resultados
    if not results:
        print("\n❌ No se encontraron herramientas que coincidan con la consulta")
        return

    print(f"\n🔍 Resultados para: '{args.query}'")
    print("-" * 80)

    for i, tool_data in enumerate(results):
        tool = ATDFTool(tool_data)
        score = tool_data.get("score", None)

        print(f"\n{i+1}. {tool.tool_id}")
        print(f"   Descripción: {tool.description}")
        print(f"   Cuándo usar: {tool.when_to_use}")

        if score is not None:
            print(f"   Puntuación: {score:.4f}")

        if hasattr(tool, "metadata") and tool.metadata:
            if "tags" in tool.metadata:
                print(f"   Etiquetas: {', '.join(tool.metadata['tags'])}")
            if "category" in tool.metadata:
                print(f"   Categoría: {tool.metadata['category']}")

        # Mostrar inputs si se solicita detalle
        if args.detail:
            if hasattr(tool, "how_to_use") and "inputs" in tool.how_to_use:
                print("\n   Parámetros:")
                for param in tool.how_to_use["inputs"]:
                    print(f"     - {param.get('name')}: {param.get('description')}")

    print("\n" + "-" * 80)


async def manage_db(args) -> None:
    """
    Administrar la base de datos vectorial.

    Args:
        args: Argumentos de línea de comandos
    """
    if not HAS_VECTOR_DEPENDENCIES:
        logger.error("Dependencias de búsqueda vectorial no instaladas")
        return

    if args.info:
        if not os.path.exists(args.db_path):
            logger.error(f"La base de datos {args.db_path} no existe")
            return

        # Inicializar vector store
        vector_store = ATDFVectorStore(db_path=args.db_path, model_name=args.model)

        await vector_store.initialize()

        # Mostrar información
        db_size = sum(
            f.stat().st_size for f in Path(args.db_path).glob("**/*") if f.is_file()
        )

        print("\n📊 Información de la base de datos vectorial")
        print("-" * 80)
        print(f"Ubicación: {args.db_path}")
        print(f"Tamaño: {db_size / (1024*1024):.2f} MB")
        print(f"Modelo: {vector_store.model_name}")

        if vector_store.table:
            # Contar registros
            count = await vector_store.count_tools()
            print(f"Herramientas indexadas: {count}")

        print("-" * 80)

    elif args.reset:
        if os.path.exists(args.db_path):
            import shutil

            confirm = input(
                f"¿Estás seguro de que quieres eliminar la base de datos en {args.db_path}? (s/N): "
            )
            if confirm.lower() == "s":
                try:
                    shutil.rmtree(args.db_path)
                    print(f"✅ Base de datos en {args.db_path} eliminada correctamente")
                except Exception as e:
                    logger.error(f"Error al eliminar la base de datos: {e}")
            else:
                print("Operación cancelada")
        else:
            logger.error(f"La base de datos {args.db_path} no existe")


def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description="CLI para búsqueda vectorial de herramientas ATDF"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: index
    index_parser = subparsers.add_parser(
        "index", help="Indexar herramientas en la base de datos"
    )
    index_parser.add_argument(
        "--tools-dir", help="Directorio con herramientas ATDF (archivos JSON)"
    )
    index_parser.add_argument(
        "--tools-file", help="Archivo JSON con lista de herramientas ATDF"
    )
    index_parser.add_argument(
        "--db-path", default="./vector_db", help="Ruta para la base de datos vectorial"
    )
    index_parser.add_argument(
        "--model", default="all-MiniLM-L6-v2", help="Modelo de embeddings a utilizar"
    )

    # Comando: search
    search_parser = subparsers.add_parser(
        "search", help="Buscar herramientas mediante consulta semántica"
    )
    search_parser.add_argument("query", help="Consulta para buscar herramientas")
    search_parser.add_argument(
        "--limit", type=int, default=5, help="Número máximo de resultados"
    )
    search_parser.add_argument(
        "--lang", help="Código de idioma para la búsqueda (ej: es, en)"
    )
    search_parser.add_argument("--category", help="Filtrar por categoría")
    search_parser.add_argument(
        "--tags", help="Filtrar por etiquetas (separadas por comas)"
    )
    search_parser.add_argument(
        "--db-path", default="./vector_db", help="Ruta de la base de datos vectorial"
    )
    search_parser.add_argument(
        "--model", default="all-MiniLM-L6-v2", help="Modelo de embeddings a utilizar"
    )
    search_parser.add_argument(
        "--detail",
        action="store_true",
        help="Mostrar detalles completos de las herramientas",
    )

    # Comando: db
    db_parser = subparsers.add_parser(
        "db", help="Administrar la base de datos vectorial"
    )
    db_parser.add_argument(
        "--info", action="store_true", help="Mostrar información sobre la base de datos"
    )
    db_parser.add_argument(
        "--reset", action="store_true", help="Eliminar la base de datos existente"
    )
    db_parser.add_argument(
        "--db-path", default="./vector_db", help="Ruta de la base de datos vectorial"
    )
    db_parser.add_argument(
        "--model", default="all-MiniLM-L6-v2", help="Modelo de embeddings a utilizar"
    )

    args = parser.parse_args()

    # Verificar si hay comando
    if not args.command:
        parser.print_help()
        return

    # Ejecutar el comando correspondiente
    if not HAS_VECTOR_DEPENDENCIES:
        print("\n⚠️  Las dependencias de búsqueda vectorial no están instaladas.")
        print("   Ejecuta: pip install lancedb sentence-transformers")
        return

    try:
        if args.command == "index":
            asyncio.run(index_tools(args))
        elif args.command == "search":
            asyncio.run(search_tools(args))
        elif args.command == "db":
            asyncio.run(manage_db(args))
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)


if __name__ == "__main__":
    main()
