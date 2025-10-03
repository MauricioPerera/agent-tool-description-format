#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agente trilingüe de demostración para ATDF (Agent Tool Description Format).
Este módulo simula un agente que puede entender consultas en español, inglés y portugués,
y seleccionar la herramienta ATDF adecuada basándose en la consulta.
"""

import json
import os
import re
import sys
from pathlib import Path


class ATDFTrilingualAgent:
    """
    Agente trilingüe que demuestra la capacidad multilingüe de ATDF.
    """

    def __init__(self, tools_dir=None):
        """
        Inicializa el agente trilingüe cargando las herramientas ATDF disponibles.

        Args:
            tools_dir: Directorio que contiene las herramientas ATDF.
                      Si es None, se usa el directorio por defecto.
        """
        if tools_dir is None:
            # Detectar el directorio del proyecto
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            tools_dir = project_root / "schema" / "examples"

        self.tools = self._load_tools(tools_dir)
        self.languages = {"es": "Español", "en": "English", "pt": "Português"}

    def _load_tools(self, tools_dir):
        """
        Carga las herramientas ATDF desde el directorio especificado.

        Args:
            tools_dir: Directorio que contiene las herramientas ATDF.

        Returns:
            Un diccionario de herramientas organizadas por idioma y tipo.
        """
        tools = {}

        try:
            # Cargar todas las herramientas del directorio
            for file in os.listdir(tools_dir):
                if file.endswith(".json"):
                    with open(
                        os.path.join(tools_dir, file), "r", encoding="utf-8"
                    ) as f:
                        try:
                            tool_data = json.load(f)

                            # Detectar el idioma y el tipo de herramienta
                            lang = "en"  # Por defecto en inglés
                            tool_type = file.split(".")[0]

                            # Verificar si hay código de idioma en el nombre
                            if "_es." in file:
                                lang = "es"
                            elif "_pt." in file:
                                lang = "pt"
                            elif "_en." in file:
                                lang = "en"

                            # Simplificar el tipo de herramienta
                            if "hole_maker" in tool_type:
                                tool_type = "hole_maker"
                            elif "text_translator" in tool_type:
                                tool_type = "text_translator"
                            elif "paint_brush" in tool_type:
                                tool_type = "paint_brush"

                            # Inicializar las estructuras según sea necesario
                            if lang not in tools:
                                tools[lang] = {}

                            tools[lang][tool_type] = tool_data

                        except json.JSONDecodeError:
                            print(f"Error al decodificar JSON en archivo: {file}")

        except Exception as e:
            print(f"Error al cargar herramientas: {str(e)}")

        return tools

    def select_tool(self, query, language=None):
        """
        Selecciona la herramienta ATDF apropiada basándose en la consulta del usuario.

        Args:
            query: Consulta del usuario.
            language: Código de idioma (es, en, pt). Si es None, se detecta automáticamente.

        Returns:
            La herramienta seleccionada y su puntuación de coincidencia.
        """
        if language is None:
            language = self._detect_language(query)

        if language not in self.tools:
            return None, 0, "Idioma no soportado"

        best_match = None
        best_score = 0
        match_reason = ""

        # Para cada herramienta en el idioma detectado
        for tool_name, tool_data in self.tools[language].items():
            # Verificar si hay coincidencia con los casos de uso
            use_cases = tool_data.get("when_to_use", [])
            if isinstance(use_cases, str):
                use_cases = [use_cases]

            # Calcular puntuación para esta herramienta
            score = 0
            current_reason = ""

            # Verificar coincidencias en casos de uso
            for case in use_cases:
                if self._has_match(query, case):
                    score += 0.5
                    current_reason = f"Coincide con caso de uso: '{case}'"

            # Verificar coincidencias en la descripción
            description = tool_data.get("description", "")
            if self._has_match(query, description):
                score += 0.3
                if current_reason:
                    current_reason += " y "
                current_reason += f"coincide con descripción"

            # Si esta herramienta tiene mejor puntuación que la actual mejor
            if score > best_score:
                best_match = tool_data
                best_score = score
                match_reason = current_reason

        return best_match, best_score, match_reason

    def _detect_language(self, text):
        """
        Detecta el idioma del texto basado en palabras clave.

        Args:
            text: Texto a analizar.

        Returns:
            Código del idioma detectado (es, en, pt).
        """
        # Palabras clave para cada idioma
        keywords = {
            "es": [
                "hacer",
                "agujero",
                "traducir",
                "español",
                "herramienta",
                "para",
                "necesito",
                "quiero",
                "perforar",
            ],
            "en": [
                "make",
                "hole",
                "translate",
                "english",
                "tool",
                "for",
                "need",
                "want",
                "drill",
            ],
            "pt": [
                "fazer",
                "furo",
                "traduzir",
                "português",
                "ferramenta",
                "para",
                "preciso",
                "quero",
                "perfurar",
            ],
        }

        # Convertir a minúsculas
        text = text.lower()

        # Contar coincidencias para cada idioma
        scores = {lang: 0 for lang in keywords}
        for lang, words in keywords.items():
            for word in words:
                if re.search(r"\b" + word + r"\b", text):
                    scores[lang] += 1

        # Determinar el idioma con más coincidencias
        max_score = 0
        detected_lang = "en"  # Valor por defecto

        for lang, score in scores.items():
            if score > max_score:
                max_score = score
                detected_lang = lang

        return detected_lang

    def _has_match(self, query, text):
        """
        Verifica si hay coincidencia entre la consulta y el texto.

        Args:
            query: Consulta del usuario.
            text: Texto a comparar.

        Returns:
            True si hay coincidencia, False en caso contrario.
        """
        # Convertir a minúsculas
        query = query.lower()
        text = text.lower()

        # Dividir en palabras
        query_words = set(re.findall(r"\b\w+\b", query))
        text_words = set(re.findall(r"\b\w+\b", text))

        # Contar palabras comunes
        common_words = query_words.intersection(text_words)

        # Si hay al menos 2 palabras en común, consideramos que hay coincidencia
        if len(common_words) >= 2:
            return True

        # Verificar si hay una frase completa que coincide
        for phrase in text.split("."):
            phrase = phrase.strip()
            if len(phrase) > 5 and phrase in query:
                return True

        return False

    def get_language_name(self, lang_code):
        """
        Obtiene el nombre del idioma a partir de su código.

        Args:
            lang_code: Código del idioma (es, en, pt).

        Returns:
            Nombre del idioma.
        """
        return self.languages.get(lang_code, "Desconocido")

    def get_available_languages(self):
        """
        Obtiene los idiomas disponibles en las herramientas cargadas.

        Returns:
            Lista de códigos de idioma disponibles.
        """
        return list(self.tools.keys())

    def get_tools_by_language(self, language):
        """
        Obtiene las herramientas disponibles para un idioma específico.

        Args:
            language: Código del idioma.

        Returns:
            Diccionario de herramientas para el idioma especificado.
        """
        if language in self.tools:
            return self.tools[language]
        return {}


# Prueba simple si se ejecuta directamente
if __name__ == "__main__":
    agent = ATDFTrilingualAgent()

    # Ejemplos de consultas en diferentes idiomas
    queries = [
        "Necesito hacer un agujero en la pared",
        "I need to translate some text",
        "Preciso de uma ferramenta para fazer um furo",
    ]

    print("Demostración del Agente Trilingüe ATDF")
    print("======================================\n")

    for query in queries:
        print(f"Consulta: '{query}'")

        language = agent._detect_language(query)
        print(f"Idioma detectado: {agent.get_language_name(language)}")

        tool, score, reason = agent.select_tool(query)

        if tool:
            print(f"Herramienta seleccionada: {tool.get('tool_id', 'Desconocido')}")
            print(f"Puntuación: {score:.2f}")
            print(f"Razón: {reason}")
        else:
            print("No se encontró una herramienta adecuada.")

        print("\n" + "-" * 50 + "\n")
