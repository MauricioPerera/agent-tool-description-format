#!/usr/bin/env python3
"""
Ejemplo de uso del módulo de búsqueda vectorial de herramientas ATDF.

Este script demuestra cómo utilizar el módulo ATDFVectorStore para
indexar y buscar herramientas ATDF utilizando vectores semánticos.
"""

import json
import os
import sys
from pathlib import Path

# Añadir directorio padre al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar desde el SDK
from sdk.atdf_sdk import load_tools_from_directory
from sdk.vector_search import ATDFVectorStore

# Ruta de ejemplo para herramientas y base de datos
TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "examples", "tools")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "examples", "vector_db")


def create_index() -> ATDFVectorStore:
    """
    Crear un índice vectorial a partir de herramientas de ejemplo.

    Returns:
        Instancia de ATDFVectorStore inicializada
    """
    print(f"Cargando herramientas desde {TOOLS_DIR}...")
    tools = load_tools_from_directory(Path(TOOLS_DIR))

    if not tools:
        print(f"No se encontraron herramientas en {TOOLS_DIR}")
        print("Asegúrate de tener archivos JSON de herramientas en el directorio")
        sys.exit(1)

    print(f"Se cargaron {len(tools)} herramientas")

    # Crear almacén vectorial
    vector_store = ATDFVectorStore(db_path=DB_PATH)

    # Inicializar y crear índice
    vector_store.initialize_sync()
    print("Creando índice vectorial...")

    success = vector_store.create_from_tools_sync(tools)
    if not success:
        print("Error al crear índice vectorial")
        sys.exit(1)

    tool_count = vector_store.count_tools_sync()
    print(f"Índice creado correctamente con {tool_count} herramientas")

    return vector_store


def search_examples(vector_store: ATDFVectorStore) -> None:
    """
    Realizar búsquedas de ejemplo.

    Args:
        vector_store: Instancia de ATDFVectorStore inicializada
    """
    # Ejemplos de consultas
    examples = [
        "herramienta para buscar en archivos",
        "como puedo ejecutar un comando en la terminal",
        "necesito editar un archivo",
        "cómo puedo obtener información de internet",
        "eliminar un archivo",
    ]

    print("\n" + "=" * 80)
    print("EJEMPLOS DE BÚSQUEDA")
    print("=" * 80)

    for query in examples:
        print(f"\nConsulta: '{query}'")
        print("-" * 40)

        # Realizar búsqueda
        results = vector_store.search_tools_sync(query=query, options={"limit": 3})

        if not results:
            print("No se encontraron resultados")
            continue

        # Mostrar resultados
        print(f"Se encontraron {len(results)} resultados:")

        for i, result in enumerate(results):
            score = result.get("score", 0)
            score_percent = int(score * 100)

            print(f"  [{i+1}] {result.get('name')} ({score_percent}% relevancia)")

    print("\n" + "=" * 80)
    print("EJEMPLO CON FILTROS")
    print("=" * 80)

    # Ejemplo con filtros
    query = "buscar información"
    print(f"\nConsulta: '{query}' (filtrado por categoría 'data')")
    print("-" * 40)

    results = vector_store.search_tools_sync(
        query=query, options={"limit": 5, "category": "data"}
    )

    if not results:
        print("No se encontraron resultados")
    else:
        print(f"Se encontraron {len(results)} resultados:")

        for i, result in enumerate(results):
            score = result.get("score", 0)
            score_percent = int(score * 100)

            print(f"  [{i+1}] {result.get('name')} ({score_percent}% relevancia)")

            # Mostrar metadatos si existen
            if "metadata" in result and result["metadata"]:
                try:
                    metadata = json.loads(result["metadata"])
                    if "category" in metadata:
                        print(f"      Categoría: {metadata['category']}")
                    if "tags" in metadata and metadata["tags"]:
                        print(f"      Etiquetas: {', '.join(metadata['tags'])}")
                except:
                    pass


def main():
    """Función principal del script de ejemplo."""
    # Crear directorio para la base de datos si no existe
    os.makedirs(DB_PATH, exist_ok=True)

    # Crear índice
    vector_store = create_index()

    # Realizar búsquedas de ejemplo
    search_examples(vector_store)


if __name__ == "__main__":
    main()
