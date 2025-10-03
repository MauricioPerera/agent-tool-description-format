#!/usr/bin/env python3
"""
Ejemplo de búsqueda vectorial con el SDK de ATDF.

Este script muestra cómo utilizar la funcionalidad de búsqueda
vectorial para encontrar herramientas similares semánticamente.

Requiere dependencias adicionales: pip install lancedb sentence-transformers
"""

import json
import os
from pathlib import Path

from sdk import ATDFSDK
from sdk.core.schema import ATDFTool, ATDFToolParameter


def create_sample_tools():
    """Crear herramientas de ejemplo para la demostración."""
    tools = []

    # Herramienta 1: Envío de correo electrónico
    email_params = [
        ATDFToolParameter(
            name="destinatario",
            description="Dirección de correo electrónico del destinatario",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="asunto",
            description="Asunto del correo electrónico",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="cuerpo",
            description="Contenido del correo electrónico",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="cc",
            description="Direcciones en copia, separadas por comas",
            type="string",
            required=False,
        ),
    ]

    email_tool = ATDFTool(
        name="Enviar Correo Electrónico",
        description="Envía un correo electrónico a un destinatario específico",
        parameters=email_params,
        category="comunicación",
        tags=["email", "correo", "mensaje"],
    )
    tools.append(email_tool)

    # Herramienta 2: Consulta de clima
    weather_params = [
        ATDFToolParameter(
            name="ciudad",
            description="Nombre de la ciudad para consultar el clima",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="dias",
            description="Número de días para el pronóstico",
            type="integer",
            required=False,
            default=1,
            min_value=1,
            max_value=7,
        ),
    ]

    weather_tool = ATDFTool(
        name="Consultar Clima",
        description="Obtiene el pronóstico del clima para una ciudad específica",
        parameters=weather_params,
        category="información",
        tags=["clima", "tiempo", "pronóstico"],
    )
    tools.append(weather_tool)

    # Herramienta 3: Búsqueda web
    search_params = [
        ATDFToolParameter(
            name="consulta",
            description="Términos de búsqueda",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="num_resultados",
            description="Número de resultados a devolver",
            type="integer",
            required=False,
            default=5,
            min_value=1,
            max_value=20,
        ),
    ]

    search_tool = ATDFTool(
        name="Búsqueda Web",
        description="Realiza una búsqueda en Internet y devuelve los resultados más relevantes",
        parameters=search_params,
        category="información",
        tags=["búsqueda", "web", "internet"],
    )
    tools.append(search_tool)

    # Herramienta 4: Traducción de texto
    translate_params = [
        ATDFToolParameter(
            name="texto", description="Texto a traducir", type="string", required=True
        ),
        ATDFToolParameter(
            name="idioma_destino",
            description="Idioma al que traducir el texto",
            type="string",
            required=True,
            enum=["español", "inglés", "francés", "alemán", "italiano", "portugués"],
        ),
        ATDFToolParameter(
            name="idioma_origen",
            description="Idioma del texto original (se detectará automáticamente si no se especifica)",
            type="string",
            required=False,
            enum=["español", "inglés", "francés", "alemán", "italiano", "portugués"],
        ),
    ]

    translate_tool = ATDFTool(
        name="Traducir Texto",
        description="Traduce un texto de un idioma a otro",
        parameters=translate_params,
        category="comunicación",
        tags=["traducción", "idioma", "lenguaje"],
    )
    tools.append(translate_tool)

    # Herramienta 5: Notificación por SMS
    sms_params = [
        ATDFToolParameter(
            name="telefono",
            description="Número de teléfono del destinatario",
            type="string",
            required=True,
        ),
        ATDFToolParameter(
            name="mensaje",
            description="Contenido del mensaje SMS",
            type="string",
            required=True,
        ),
    ]

    sms_tool = ATDFTool(
        name="Enviar SMS",
        description="Envía un mensaje SMS a un número de teléfono",
        parameters=sms_params,
        category="comunicación",
        tags=["sms", "mensaje", "texto"],
    )
    tools.append(sms_tool)

    return tools


def main():
    # Obtener ruta para almacenar la base vectorial
    db_path = Path(__file__).parent / "output" / "vector_db"
    db_path.mkdir(exist_ok=True, parents=True)

    print(f"Directorio para base vectorial: {db_path}")
    print("Iniciando SDK de ATDF con búsqueda vectorial...")

    try:
        # Inicializar el SDK con soporte de búsqueda vectorial
        sdk = ATDFSDK(vector_db_path=str(db_path), embedding_model="all-MiniLM-L6-v2")

        # Crear herramientas de ejemplo
        print("\nCreando herramientas de ejemplo...")
        tools = create_sample_tools()

        # Añadir herramientas al SDK
        for tool in tools:
            sdk.tools.append(tool)
            if sdk.vector_store:
                sdk.vector_store.add_tool(tool.to_dict())

        print(f"Se han creado {len(tools)} herramientas de ejemplo")

        # Realizar búsquedas
        if sdk.vector_store:
            print("\n=== Demostración de búsqueda vectorial ===")

            queries = [
                "Necesito enviar un mensaje a alguien",
                "Quiero saber cómo estará el tiempo mañana",
                "Tengo que encontrar información en internet",
                "Necesito convertir un texto a otro idioma",
                "Herramienta para enviar un mensaje de texto corto",
            ]

            for i, query in enumerate(queries, 1):
                print(f"\nBúsqueda {i}: '{query}'")
                try:
                    results = sdk.search_tools(
                        query=query, limit=2, score_threshold=0.5
                    )

                    print(f"Resultados encontrados: {len(results)}")

                    for j, (tool, score) in enumerate(results, 1):
                        print(f"  {j}. {tool.name} - Puntuación: {score:.2f}")
                        print(f"     Descripción: {tool.description}")
                        print(f"     Categoría: {tool.category}")
                        print(f"     Parámetros: {len(tool.parameters)}")
                except Exception as e:
                    print(f"Error al realizar la búsqueda: {str(e)}")
        else:
            print("\nLa búsqueda vectorial no está disponible.")
            print(
                "Instala las dependencias requeridas: pip install lancedb sentence-transformers"
            )

        print("\nEjemplo completado exitosamente.")

    except ImportError as e:
        print(f"\nError: {str(e)}")
        print(
            "\nPara ejecutar este ejemplo, instala las dependencias de búsqueda vectorial:"
        )
        print("pip install lancedb sentence-transformers numpy")


if __name__ == "__main__":
    main()
