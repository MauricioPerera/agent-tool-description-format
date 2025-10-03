#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ejemplos de uso del SDK de ATDF (Agent Tool Description Format).

Este archivo contiene ejemplos prácticos para demostrar las funcionalidades
principales del SDK de ATDF, incluyendo la carga de herramientas, búsqueda,
y selección automática de herramientas para diferentes tareas.
"""

import json
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar el SDK
sys.path.append(str(Path(__file__).parent.parent))

# Importar el SDK
from sdk.atdf_sdk import (
    ATDFTool,
    ATDFToolbox,
    load_toolbox_from_directory,
    find_best_tool,
)


def print_separator(title=""):
    """Imprime un separador para mejorar la legibilidad de la salida."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("-" * 80)


def ejemplo_cargar_herramientas():
    """Ejemplo: Cargar herramientas desde archivos y directorios."""
    print_separator("EJEMPLO: CARGAR HERRAMIENTAS")

    # Método 1: Cargar herramientas desde un directorio
    print("1. Cargando herramientas desde el directorio de ejemplos...")
    toolbox1 = load_toolbox_from_directory("schema/examples")
    print(f"   Se cargaron {len(toolbox1)} herramientas")

    # Método 2: Cargar herramientas individualmente
    print("\n2. Cargando herramientas individualmente...")
    toolbox2 = ATDFToolbox()

    # Cargar una herramienta específica
    toolbox2.load_tool_from_file("schema/examples/hole_maker.json")
    print(f"   Se cargó 1 herramienta: {toolbox2.tools[0].tool_id}")

    # Cargar otra herramienta
    toolbox2.load_tool_from_file("schema/examples/text_translator.json")
    print(f"   Ahora el toolbox tiene {len(toolbox2)} herramientas")

    # Listar las herramientas cargadas
    print("\n3. Herramientas disponibles:")
    for tool in toolbox1.tools:
        print(f"   - {tool.tool_id}: {tool.description}")

    return toolbox1


def ejemplo_buscar_herramientas(toolbox):
    """Ejemplo: Buscar herramientas por texto."""
    print_separator("EJEMPLO: BUSCAR HERRAMIENTAS")

    # Buscar herramientas en español
    print("1. Buscando herramientas en español relacionadas con 'agujero':")
    resultados_es = toolbox.find_tools_by_text("hacer un agujero", language="es")
    for tool, score in resultados_es:
        print(f"   - {tool.tool_id} (score: {score:.2f}): {tool.description}")

    # Compatibilidad: obtener solo herramientas sin puntuaciones
    solo_es = toolbox.find_tools_by_text(
        "hacer un agujero",
        language="es",
        return_scores=False,
    )
    print("   → Solo herramientas (modo legado):")
    for tool in solo_es:
        print(f"     * {tool.tool_id}: {tool.description}")

    # Buscar herramientas en inglés
    print("\n2. Buscando herramientas en inglés relacionadas con 'translate':")
    resultados_en = toolbox.find_tools_by_text("translate text", language="en")
    for tool, score in resultados_en:
        print(f"   - {tool.tool_id} (score: {score:.2f}): {tool.description}")

    # Buscar herramientas con un idioma no especificado (usará el predeterminado)
    print("\n3. Buscando herramientas con texto genérico sin especificar idioma:")
    resultados = toolbox.find_tools_by_text("paint")
    for tool, score in resultados:
        print(f"   - {tool.tool_id} (score: {score:.2f}): {tool.description}")


def ejemplo_seleccion_automatica(toolbox):
    """Ejemplo: Seleccionar automáticamente la herramienta más adecuada para una tarea."""
    print_separator("EJEMPLO: SELECCIÓN AUTOMÁTICA DE HERRAMIENTAS")

    # Caso 1: Tarea en español
    tarea_es = "Necesito hacer un agujero en la pared para colgar un cuadro"
    print(f"1. Tarea (ES): '{tarea_es}'")
    herramienta_es = find_best_tool(toolbox, tarea_es, language="es")

    if herramienta_es:
        print(f"   Herramienta seleccionada: {herramienta_es.tool_id}")
        print(f"   Descripción: {herramienta_es.description}")
        print(f"   Cuándo usar: {herramienta_es.when_to_use}")
    else:
        print("   No se encontró una herramienta adecuada para esta tarea.")

    # Caso 2: Tarea en inglés
    tarea_en = "I need to translate some text from English to Spanish"
    print(f"\n2. Tarea (EN): '{tarea_en}'")
    herramienta_en = find_best_tool(toolbox, tarea_en, language="en")

    if herramienta_en:
        print(f"   Herramienta seleccionada: {herramienta_en.tool_id}")
        print(f"   Descripción: {herramienta_en.description}")
        print(f"   Cuándo usar: {herramienta_en.when_to_use}")
    else:
        print("   No se encontró una herramienta adecuada para esta tarea.")


def ejemplo_detalles_herramienta(toolbox):
    """Ejemplo: Acceder a todos los detalles de una herramienta."""
    print_separator("EJEMPLO: DETALLES DE UNA HERRAMIENTA")

    # Obtener una herramienta específica
    if len(toolbox.tools) > 0:
        herramienta = toolbox.tools[0]  # Obtener la primera herramienta
    else:
        print("No hay herramientas disponibles.")
        return

    print(f"Detalles de la herramienta: {herramienta.tool_id}")
    print(f"Descripción: {herramienta.description}")
    print(f"Cuándo usar: {herramienta.when_to_use}")

    # Mostrar parámetros de entrada
    print("\nParámetros de entrada:")
    for input_param in herramienta.inputs:
        is_required = input_param.get("required", False)
        req_str = "obligatorio" if is_required else "opcional"
        print(f"- {input_param['name']} ({input_param['type']}, {req_str})")
        print(f"  Descripción: {input_param.get('description', 'Sin descripción')}")

    # Mostrar mensajes
    print("\nMensajes:")
    print(f"- Éxito: {herramienta.success_message}")
    if herramienta.failure_messages:
        print("- Errores:")
        for error_msg in herramienta.failure_messages:
            print(f"  * {error_msg}")

    # Mostrar metadatos (si existen)
    if herramienta.metadata:
        print("\nMetadatos:")
        for key, value in herramienta.metadata.items():
            print(f"- {key}: {value}")

    # Mostrar ejemplos (si existen)
    if herramienta.examples:
        print("\nEjemplos:")
        for i, example in enumerate(herramienta.examples, 1):
            print(f"- Ejemplo {i}: {example.get('title', 'Sin título')}")
            print(f"  Descripción: {example.get('description', 'Sin descripción')}")
            if "inputs" in example:
                print("  Entradas:")
                for k, v in example["inputs"].items():
                    print(f"    * {k}: {v}")

    # Mostrar prerrequisitos (si existen)
    if herramienta.prerequisites:
        print("\nPrerrequisitos:")
        for category, items in herramienta.prerequisites.items():
            print(f"- {category}:")
            for item in items:
                print(f"  * {item}")


def ejemplo_esquema_entradas(toolbox):
    """Ejemplo: Generar un esquema JSON para validar entradas."""
    print_separator("EJEMPLO: ESQUEMA DE VALIDACIÓN DE ENTRADAS")

    # Seleccionar una herramienta con entradas
    selected_tool = None
    for tool in toolbox.tools:
        if tool.inputs:
            selected_tool = tool
            break

    if not selected_tool:
        print("No se encontró ninguna herramienta con entradas definidas.")
        return

    print(
        f"Generando esquema de validación para la herramienta: {selected_tool.tool_id}"
    )

    # Obtener el esquema JSON
    esquema = selected_tool.get_input_schema()

    # Mostrar el esquema con formato
    print(json.dumps(esquema, indent=2, ensure_ascii=False))

    print(
        "\nEste esquema puede utilizarse con bibliotecas como 'jsonschema' para validar las entradas."
    )


def ejemplo_soporte_multilingue(toolbox):
    """Ejemplo: Soporte para múltiples idiomas."""
    print_separator("EJEMPLO: SOPORTE MULTILINGÜE")

    # Buscar una herramienta que tenga soporte multilingüe
    multi_tool = None
    for tool in toolbox.tools:
        if len(tool.supported_languages) > 1:
            multi_tool = tool
            break

    if not multi_tool:
        print("No se encontró ninguna herramienta con soporte multilingüe.")
        return

    print(f"Herramienta con soporte multilingüe: {multi_tool.tool_id}")
    print(f"Idiomas disponibles: {', '.join(multi_tool.supported_languages)}")

    # Mostrar descripciones en diferentes idiomas
    print("\nDescripciones en diferentes idiomas:")
    for lang in multi_tool.supported_languages:
        # La propiedad description no es un método, necesitamos acceder de otra manera
        if lang in multi_tool.to_dict().get("localization", {}):
            desc = multi_tool.to_dict()["localization"][lang]["description"]
        else:
            desc = multi_tool.description
        print(f"- {lang.upper()}: {desc}")

    # Mostrar "Cuándo usar" en diferentes idiomas
    print("\n'Cuándo usar' en diferentes idiomas:")
    for lang in multi_tool.supported_languages:
        # La propiedad when_to_use no es un método, necesitamos acceder de otra manera
        if lang in multi_tool.to_dict().get("localization", {}):
            when = multi_tool.to_dict()["localization"][lang]["when_to_use"]
        else:
            when = multi_tool.when_to_use
        print(f"- {lang.upper()}: {when}")


def ejemplo_completo():
    """Ejemplo completo que simula un escenario de uso real."""
    print_separator("EJEMPLO COMPLETO: ESCENARIO DE USO REAL")

    # 1. Cargar todas las herramientas disponibles
    print("1. Cargando herramientas...")
    toolbox = load_toolbox_from_directory("schema/examples", recursive=True)
    print(f"   Se cargaron {len(toolbox)} herramientas")

    # 2. Analizar una petición del usuario
    print("\n2. Procesando petición del usuario...")
    peticion_usuario = (
        "Necesito hacer un agujero en la pared para colgar un cuadro grande"
    )
    idioma_detectado = "es"  # En un caso real, esto se detectaría automáticamente

    print(f"   Petición: '{peticion_usuario}'")
    print(f"   Idioma detectado: {idioma_detectado}")

    # 3. Encontrar la herramienta más adecuada
    print("\n3. Buscando la herramienta más adecuada...")
    herramienta = find_best_tool(toolbox, peticion_usuario, language=idioma_detectado)

    if not herramienta:
        print("   No se encontró una herramienta adecuada para esta tarea.")
        return

    print(f"   Herramienta seleccionada: {herramienta.tool_id}")
    print(f"   Descripción: {herramienta.description}")
    print(f"   Cuándo usar: {herramienta.when_to_use}")

    # 4. Verificar prerrequisitos
    print("\n4. Verificando prerrequisitos...")
    if herramienta.prerequisites:
        for categoria, items in herramienta.prerequisites.items():
            print(f"   - {categoria}:")
            for item in items:
                print(f"     * {item}")
    else:
        print("   No hay prerrequisitos especificados para esta herramienta.")

    # 5. Preparar entradas para la herramienta
    print("\n5. Preparando entradas para la herramienta...")
    entradas = {}

    for input_param in herramienta.inputs:
        nombre = input_param["name"]
        tipo = input_param["type"]
        descripcion = input_param.get("description", "")

        # En un caso real, estas entradas se obtendrían a través de un diálogo con el usuario
        print(f"   Solicitando entrada: {nombre} ({tipo})")
        print(f"   Descripción: {descripcion}")

        # Simular la entrada del usuario (en un caso real, se solicitaría al usuario)
        if nombre == "wall_type":
            entradas[nombre] = "concrete"
            print(f"   Valor proporcionado: {entradas[nombre]}")
        elif nombre == "hole_diameter":
            entradas[nombre] = 10
            print(f"   Valor proporcionado: {entradas[nombre]}")
        elif nombre == "depth":
            entradas[nombre] = 5
            print(f"   Valor proporcionado: {entradas[nombre]}")

    # 6. Validar entradas (simulado)
    print("\n6. Validando entradas...")
    print("   ✓ Todas las entradas son válidas")

    # 7. Ejecutar la herramienta (simulado)
    print("\n7. Ejecutando la herramienta...")
    print(f"   Mensaje de éxito: {herramienta.success_message}")

    # 8. Solicitar retroalimentación (si está disponible)
    print("\n8. Solicitando retroalimentación...")
    if herramienta.feedback:
        print(f"   Preguntas de retroalimentación:")
        for pregunta in herramienta.feedback:
            print(f"   - {pregunta}")
    else:
        print(
            "   No hay preguntas de retroalimentación definidas para esta herramienta."
        )


def main():
    """Función principal que ejecuta todos los ejemplos."""
    # Verificar que estamos en el directorio raíz del proyecto
    if not os.path.exists("schema/examples"):
        print(
            "Error: Este script debe ejecutarse desde el directorio raíz del proyecto."
        )
        print("Por favor, ejecute el script desde la ubicación correcta:")
        print("  python sdk/examples.py")
        return

    print("EJEMPLOS DE USO DEL SDK DE ATDF\n")
    print("Este script muestra diferentes ejemplos de uso del SDK de ATDF.")

    # Cargar herramientas (compartidas entre ejemplos)
    toolbox = ejemplo_cargar_herramientas()

    # Ejecutar ejemplos individuales
    ejemplo_buscar_herramientas(toolbox)
    ejemplo_seleccion_automatica(toolbox)
    ejemplo_detalles_herramienta(toolbox)
    ejemplo_esquema_entradas(toolbox)
    ejemplo_soporte_multilingue(toolbox)

    # Ejecutar el ejemplo completo
    ejemplo_completo()

    print("\n¡Todos los ejemplos se han ejecutado correctamente!")


if __name__ == "__main__":
    main()
