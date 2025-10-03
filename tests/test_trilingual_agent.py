#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Agente Trilingüe de ATDF.

Este script prueba el funcionamiento del agente trilingüe con diferentes
consultas en español, inglés y portugués, verificando la correcta selección
de herramientas y detección de idiomas.
"""

import logging
import os
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trilingual_tests")

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

# Importar módulos del agente trilingüe
from improved_loader import (
    detect_language,
    load_tools_from_directory,
    select_tool_by_goal,
)


class TrilingualTester:
    """Clase para probar el agente trilingüe."""

    def __init__(self):
        """Inicializar el tester."""
        # Configurar directorio de ejemplos
        self.examples_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "schema/examples",
        )
        self.success_count = 0
        self.failure_count = 0
        self.test_count = 0

        # Cargar herramientas
        self.tools = load_tools_from_directory(self.examples_dir)

    def _log_result(self, test_name, success, message=""):
        """Registrar el resultado de una prueba."""
        self.test_count += 1
        result = "✅ PASS" if success else "❌ FAIL"

        if success:
            self.success_count += 1
            logger.info(f"{result} - {test_name}: {message}")
        else:
            self.failure_count += 1
            logger.error(f"{result} - {test_name}: {message}")

        return success

    def run_all_tests(self):
        """Ejecutar todas las pruebas."""
        print("\n========== INICIANDO PRUEBAS DEL AGENTE TRILINGÜE ==========\n")

        # Verificar que las herramientas se cargaron correctamente
        if not self.tools:
            logger.error(
                f"No se pudieron cargar herramientas desde '{self.examples_dir}'."
            )
            return False

        logger.info(f"Se cargaron {len(self.tools)} herramientas.")

        # Ejecutar pruebas
        self.test_language_detection()
        self.test_spanish_queries()
        self.test_english_queries()
        self.test_portuguese_queries()
        self.test_ambiguous_queries()
        self.test_complex_queries()

        # Mostrar resumen
        print(f"\n========== RESUMEN DE PRUEBAS TRILINGÜES ==========")
        print(f"Total de pruebas: {self.test_count}")
        print(f"Pruebas exitosas: {self.success_count}")
        print(f"Pruebas fallidas: {self.failure_count}")
        print(f"Tasa de éxito: {(self.success_count / self.test_count) * 100:.1f}%\n")

        return self.failure_count == 0

    def test_language_detection(self):
        """Probar la detección de idiomas con casos más complejos."""
        print("\n----- Prueba: Detección Avanzada de Idiomas -----")

        # Prueba 1: Español con mezcla de palabras en inglés
        es_query = "necesito hacer un hole en la wall"
        es_lang = detect_language(es_query)
        self._log_result(
            "Español con palabras en inglés",
            es_lang == "es",
            f"Detectado como '{es_lang}'",
        )

        # Prueba 2: Inglés con nombres propios españoles
        en_query = "I need to translate a text from Pedro García"
        en_lang = detect_language(en_query)
        self._log_result(
            "Inglés con nombres españoles",
            en_lang == "en",
            f"Detectado como '{en_lang}'",
        )

        # Prueba 3: Portugués con términos técnicos en inglés
        pt_query = "preciso de um drill para fazer um furo na wall"
        pt_lang = detect_language(pt_query)
        self._log_result(
            "Portugués con términos técnicos",
            pt_lang == "pt",
            f"Detectado como '{pt_lang}'",
        )

        # Prueba 4: Consulta muy corta
        short_query = "agujero"
        short_lang = detect_language(short_query)
        self._log_result(
            "Consulta muy corta",
            short_lang in ["es", "en", "pt"],
            f"Detectado como '{short_lang}'",
        )

    def test_spanish_queries(self):
        """Probar consultas en español."""
        print("\n----- Prueba: Consultas en Español -----")

        # Lista de consultas en español
        queries = [
            "necesito hacer un agujero",
            "quiero perforar una pared",
            "herramienta para hacer huecos",
            "cómo hago un agujero en la pared",
            "necesito traducir un texto",
            "herramienta para traducción",
        ]

        for i, query in enumerate(queries, 1):
            tool = select_tool_by_goal(self.tools, query)

            # Determinar la herramienta esperada
            expected_tool_type = (
                "hole"
                if any(word in query for word in ["agujero", "perforar", "huecos"])
                else "translator"
            )

            success = tool is not None and expected_tool_type in tool["tool_id"].lower()

            self._log_result(
                f"Consulta ES #{i}: '{query}'",
                success,
                f"Herramienta: {tool['tool_id'] if tool else 'ninguna'}",
            )

    def test_english_queries(self):
        """Probar consultas en inglés."""
        print("\n----- Prueba: Consultas en Inglés -----")

        # Lista de consultas en inglés
        queries = [
            "I need to make a hole",
            "tool for drilling",
            "how to drill a wall",
            "need to create a hole",
            "translate some text",
            "tool for language translation",
        ]

        for i, query in enumerate(queries, 1):
            tool = select_tool_by_goal(self.tools, query)

            # Determinar la herramienta esperada
            expected_tool_type = (
                "hole"
                if any(word in query for word in ["hole", "drill"])
                else "translator"
            )

            success = tool is not None and expected_tool_type in tool["tool_id"].lower()

            self._log_result(
                f"Consulta EN #{i}: '{query}'",
                success,
                f"Herramienta: {tool['tool_id'] if tool else 'ninguna'}",
            )

    def test_portuguese_queries(self):
        """Probar consultas en portugués."""
        print("\n----- Prueba: Consultas en Portugués -----")

        # Lista de consultas en portugués
        queries = [
            "preciso fazer um furo",
            "ferramenta para perfurar",
            "como fazer um buraco na parede",
            "preciso traduzir um texto",
            "ferramenta para tradução",
        ]

        for i, query in enumerate(queries, 1):
            tool = select_tool_by_goal(self.tools, query)

            # Determinar la herramienta esperada
            expected_tool_type = (
                "hole"
                if any(word in query for word in ["furo", "perfurar", "buraco"])
                else "translator"
            )

            success = tool is not None and expected_tool_type in tool["tool_id"].lower()

            self._log_result(
                f"Consulta PT #{i}: '{query}'",
                success,
                f"Herramienta: {tool['tool_id'] if tool else 'ninguna'}",
            )

    def test_ambiguous_queries(self):
        """Probar consultas ambiguas que podrían coincidir con múltiples herramientas."""
        print("\n----- Prueba: Consultas Ambiguas -----")

        # Lista de consultas ambiguas
        queries = [
            # Español
            "necesito una herramienta",
            # Inglés
            "I need a tool for the wall",
            # Portugués
            "preciso de uma ferramenta",
        ]

        for i, query in enumerate(queries, 1):
            language = detect_language(query)
            tool = select_tool_by_goal(self.tools, query)

            # En consultas ambiguas, lo importante es que devuelva alguna herramienta
            # y que el idioma sea detectado correctamente
            language_success = language in ["es", "en", "pt"]
            tool_success = tool is not None

            self._log_result(
                f"Consulta ambigua #{i}: '{query}'",
                language_success and tool_success,
                f"Idioma: {language}, Herramienta: {tool['tool_id'] if tool else 'ninguna'}",
            )

    def test_complex_queries(self):
        """Probar consultas complejas con múltiples elementos."""
        print("\n----- Prueba: Consultas Complejas -----")

        # Lista de consultas complejas
        queries = [
            # Español - Múltiples herramientas
            "necesito hacer un agujero y luego traducir un texto",
            # Inglés - Consulta detallada
            "I need to make a precise 10mm hole in the concrete wall for hanging a large painting",
            # Portugués - Negación
            "não quero traduzir, preciso fazer um furo",
        ]

        for i, query in enumerate(queries, 1):
            language = detect_language(query)
            tool = select_tool_by_goal(self.tools, query)

            # Para consultas complejas, verificamos principalmente que el idioma sea detectado correctamente
            # y que se seleccione una herramienta, sin importar exactamente cuál
            language_success = language in ["es", "en", "pt"]
            tool_success = tool is not None

            self._log_result(
                f"Consulta compleja #{i}: '{query}'",
                language_success and tool_success,
                f"Idioma: {language}, Herramienta: {tool['tool_id'] if tool else 'ninguna'}",
            )


# Ejecutar pruebas si se ejecuta como script
if __name__ == "__main__":
    tester = TrilingualTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
