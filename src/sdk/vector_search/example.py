#!/usr/bin/env python3
"""
Ejemplo de uso de la búsqueda vectorial de ATDF en Python.

Este script demuestra:
1. Cómo configurar un almacén vectorial
2. Cómo indexar herramientas ATDF
3. Cómo realizar búsquedas semánticas
4. Comparación entre búsqueda normal y vectorial

Para ejecutar este ejemplo:
    python -m sdk.vector_search.example
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atdf-vector-example")

# Importaciones de ATDF
from sdk.atdf_sdk import ATDFTool, ATDFToolbox

# Verificar si las dependencias están instaladas
try:
    from sdk.vector_search import ATDFVectorStore

    HAS_VECTOR_DEPENDENCIES = True
except ImportError:
    logger.warning(
        "Dependencias de búsqueda vectorial no instaladas. "
        "Ejecuta: pip install lancedb sentence-transformers"
    )
    HAS_VECTOR_DEPENDENCIES = False

# Ejemplo de herramientas para demostración
EXAMPLE_TOOLS = [
    {
        "tool_id": "send_email",
        "description": "Send an email to a recipient",
        "when_to_use": "When you need to send an email message to someone",
        "localization": {
            "es": {
                "description": "Enviar un correo electrónico a un destinatario",
                "when_to_use": "Cuando necesites enviar un mensaje por correo electrónico a alguien",
            }
        },
        "how_to_use": {
            "inputs": [
                {
                    "name": "to",
                    "type": "string",
                    "description": "Email address of the recipient",
                },
                {
                    "name": "subject",
                    "type": "string",
                    "description": "Subject of the email",
                },
                {
                    "name": "body",
                    "type": "string",
                    "description": "Content of the email message",
                },
            ],
            "outputs": {
                "success": "Email sent successfully",
                "failure": [
                    {
                        "error": "invalid_email",
                        "message": "The recipient email is invalid",
                    }
                ],
            },
        },
        "metadata": {
            "tags": ["communication", "email", "message"],
            "category": "communication",
        },
        "examples": [
            {
                "title": "Send a simple email",
                "description": "Send an email with a simple message",
                "params": {
                    "to": "recipient@example.com",
                    "subject": "Hello",
                    "body": "This is a test email.",
                },
            }
        ],
    },
    {
        "tool_id": "search_web",
        "description": "Search the web for information",
        "when_to_use": "When you need to find information on the internet",
        "localization": {
            "es": {
                "description": "Buscar información en la web",
                "when_to_use": "Cuando necesites encontrar información en internet",
            }
        },
        "how_to_use": {
            "inputs": [
                {"name": "query", "type": "string", "description": "Search query"}
            ],
            "outputs": {
                "success": "Search results",
                "failure": [{"error": "no_results", "message": "No results found"}],
            },
        },
        "metadata": {"tags": ["search", "web", "internet"], "category": "information"},
    },
    {
        "tool_id": "translate_text",
        "description": "Translate text between languages",
        "when_to_use": "When you need to translate text from one language to another",
        "localization": {
            "es": {
                "description": "Traducir texto entre idiomas",
                "when_to_use": "Cuando necesites traducir un texto de un idioma a otro",
            }
        },
        "how_to_use": {
            "inputs": [
                {"name": "text", "type": "string", "description": "Text to translate"},
                {
                    "name": "source_lang",
                    "type": "string",
                    "description": "Source language code",
                },
                {
                    "name": "target_lang",
                    "type": "string",
                    "description": "Target language code",
                },
            ],
            "outputs": {
                "success": "Translated text",
                "failure": [
                    {
                        "error": "unsupported_language",
                        "message": "Language not supported",
                    }
                ],
            },
        },
        "metadata": {
            "tags": ["language", "translation", "text"],
            "category": "language",
        },
    },
    {
        "tool_id": "get_weather",
        "description": "Get current weather information for a location",
        "when_to_use": "When you need to know the current weather in a specific location",
        "localization": {
            "es": {
                "description": "Obtener información meteorológica actual para una ubicación",
                "when_to_use": "Cuando necesites conocer el clima actual en una ubicación específica",
            }
        },
        "how_to_use": {
            "inputs": [
                {
                    "name": "location",
                    "type": "string",
                    "description": "City or location name",
                }
            ],
            "outputs": {
                "success": "Weather information",
                "failure": [
                    {"error": "location_not_found", "message": "Location not found"}
                ],
            },
        },
        "metadata": {
            "tags": ["weather", "location", "forecast"],
            "category": "information",
        },
    },
    {
        "tool_id": "set_reminder",
        "description": "Set a reminder for a specific time",
        "when_to_use": "When you need to be reminded about something at a specific time",
        "localization": {
            "es": {
                "description": "Establecer un recordatorio para una hora específica",
                "when_to_use": "Cuando necesites que te recuerden algo a una hora específica",
            }
        },
        "how_to_use": {
            "inputs": [
                {
                    "name": "time",
                    "type": "string",
                    "description": "Time for the reminder",
                },
                {
                    "name": "message",
                    "type": "string",
                    "description": "Reminder message",
                },
            ],
            "outputs": {
                "success": "Reminder set",
                "failure": [
                    {"error": "invalid_time", "message": "Invalid time format"}
                ],
            },
        },
        "metadata": {
            "tags": ["reminder", "time", "notification"],
            "category": "productivity",
        },
    },
]


def print_header(title: str) -> None:
    """Imprimir un encabezado con formato"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)


def print_tool_result(
    index: int, tool: ATDFTool, score: Optional[float] = None
) -> None:
    """Imprimir información sobre una herramienta"""
    print(f"\n{index+1}. {tool.tool_id}")
    print(f"   Descripción: {tool.description}")
    print(f"   Cuándo usar: {tool.when_to_use}")
    if score is not None:
        print(f"   Puntuación: {score:.4f}")
    if hasattr(tool, "metadata") and tool.metadata:
        if "tags" in tool.metadata:
            print(f"   Etiquetas: {', '.join(tool.metadata['tags'])}")
        if "category" in tool.metadata:
            print(f"   Categoría: {tool.metadata['category']}")


async def compare_search_methods(
    toolbox: ATDFToolbox, query: str, language: str = None
) -> None:
    """Comparar búsqueda normal vs vectorial para una consulta"""
    print_header(f"Comparación de búsqueda para: '{query}'")

    # Búsqueda normal
    start_time = time.time()
    normal_kwargs = {"language": language} if language else {}
    normal_results = toolbox.find_tools_by_text(query, **normal_kwargs)
    normal_time = time.time() - start_time

    print(f"\n🔍 Búsqueda normal (tiempo: {normal_time:.4f}s)")
    if normal_results:
        for i, (tool, score) in enumerate(normal_results):
            print_tool_result(i, tool, score)
    else:
        print("   No se encontraron resultados")

    # Búsqueda vectorial (si está disponible)
    if toolbox.vector_store:
        start_time = time.time()
        vector_kwargs = {"language": language} if language else {}
        vector_results = toolbox.find_tools_by_text(
            query,
            use_vector_search=True,
            **vector_kwargs,
        )
        vector_time = time.time() - start_time

        print(f"\n🧠 Búsqueda vectorial (tiempo: {vector_time:.4f}s)")
        if vector_results:
            for i, (tool, score) in enumerate(vector_results):
                print_tool_result(i, tool, score)
        else:
            print("   No se encontraron resultados")
    else:
        print("\n❌ Búsqueda vectorial no disponible (dependencias no instaladas)")


async def demo_search_features(vector_store: "ATDFVectorStore") -> None:
    """Demostrar características avanzadas de búsqueda vectorial"""
    print_header("Demostración de búsqueda avanzada")

    # Búsqueda con opciones de filtrado
    print("\n🔍 Búsqueda filtrada por categoría 'communication'")
    results = await vector_store.search_tools(
        "send a message", options={"category": "communication", "limit": 3}
    )

    if results:
        for i, tool_data in enumerate(results):
            tool = ATDFTool(tool_data)
            score = tool_data.get("score", None)
            print_tool_result(i, tool, score)
    else:
        print("   No se encontraron resultados")

    # Búsqueda en español
    print("\n🔍 Búsqueda en español")
    results = await vector_store.search_tools(
        "recordar una tarea importante", options={"language": "es", "limit": 2}
    )

    if results:
        for i, tool_data in enumerate(results):
            tool = ATDFTool(tool_data)
            score = tool_data.get("score", None)
            print_tool_result(i, tool, score)
    else:
        print("   No se encontraron resultados")

    # Encontrar la mejor herramienta
    print("\n🎯 Encontrar la mejor herramienta para 'check current forecast'")
    best_tool = await vector_store.find_best_tool("check current forecast")

    if best_tool:
        tool = ATDFTool(best_tool)
        print(f"Mejor herramienta: {tool.tool_id}")
        print(f"Descripción: {tool.description}")
    else:
        print("   No se encontró ninguna herramienta adecuada")


async def main() -> None:
    """Función principal del ejemplo"""
    print_header("EJEMPLO DE BÚSQUEDA VECTORIAL ATDF")

    # Verificar dependencias
    if not HAS_VECTOR_DEPENDENCIES:
        print("\n⚠️  Este ejemplo requiere dependencias adicionales.")
        print("   Ejecuta: pip install lancedb sentence-transformers")
        return

    # Crear un directorio temporal para la base de datos
    db_path = "./example_vector_db"
    os.makedirs(db_path, exist_ok=True)

    try:
        # Paso 1: Crear e inicializar vector store
        print("\n1️⃣  Inicializando almacén vectorial...")
        vector_store = ATDFVectorStore(db_path=db_path)
        await vector_store.initialize()
        print("   ✅ Almacén vectorial inicializado correctamente")

        # Paso 2: Crear toolbox con vector store
        print("\n2️⃣  Creando toolbox...")
        toolbox = ATDFToolbox({"vector_store": vector_store})

        # Paso 3: Añadir herramientas de ejemplo
        print("\n3️⃣  Añadiendo herramientas de ejemplo...")
        for tool_data in EXAMPLE_TOOLS:
            toolbox.add_tool(tool_data)
        print(f"   ✅ Se añadieron {len(EXAMPLE_TOOLS)} herramientas")

        # Paso 4: Realizar comparaciones de búsqueda
        print("\n4️⃣  Ejecutando comparaciones de búsqueda...")

        # Comparación 1: Búsqueda simple
        await compare_search_methods(toolbox, "send a message")

        # Comparación 2: Búsqueda semántica más compleja
        await compare_search_methods(toolbox, "I need to communicate with someone")

        # Comparación 3: Búsqueda en español
        await compare_search_methods(toolbox, "obtener información del clima", "es")

        # Paso 5: Demostrar características avanzadas
        print("\n5️⃣  Demostrando características avanzadas...")
        await demo_search_features(vector_store)

        print("\n✅ Ejemplo completado con éxito!")

    except Exception as e:
        logger.error(f"Error en el ejemplo: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    finally:
        # No eliminamos la base de datos para que puedas examinarla
        print(f"\nLa base de datos vectorial se encuentra en: {db_path}")
        print("Para eliminarla, ejecuta: rm -rf example_vector_db")


if __name__ == "__main__":
    asyncio.run(main())
