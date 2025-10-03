#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo para verificar las funcionalidades de ATDF.

Este script ejecuta una serie de pruebas para verificar que todas las
funcionalidades de ATDF funcionan correctamente, incluyendo:
- Carga de herramientas
- Búsqueda y selección
- Soporte multilingüe
- Conversión entre formatos
- Validación
- Características avanzadas
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atdf_tests")

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

# Importar los módulos necesarios
from sdk.atdf_sdk import (
    ATDFTool,
    ATDFToolbox,
    load_toolbox_from_directory,
    find_best_tool,
)
from improved_loader import (
    load_tools_from_directory,
    select_tool_by_goal,
    detect_language,
)
from tools.converter import convert_to_enhanced, load_tool, save_tool


class ATDFTester:
    """Clase para ejecutar pruebas completas de ATDF."""

    def __init__(self):
        """Inicializar el tester."""
        self.examples_dir = "schema/examples"
        self.success_count = 0
        self.failure_count = 0
        self.test_count = 0

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
        print("\n========== INICIANDO PRUEBAS COMPLETAS DE ATDF ==========\n")

        # Comprobar que exista el directorio de ejemplos
        if not os.path.exists(self.examples_dir):
            logger.error(f"El directorio de ejemplos '{self.examples_dir}' no existe.")
            return False

        # Ejecutar todas las pruebas
        self.test_sdk_loading()
        self.test_improved_loader()
        self.test_language_detection()
        self.test_tool_selection()
        self.test_conversion()
        self.test_advanced_features()
        self.test_multilingual_support()

        # Mostrar resumen
        print(f"\n========== RESUMEN DE PRUEBAS ==========")
        print(f"Total de pruebas: {self.test_count}")
        print(f"Pruebas exitosas: {self.success_count}")
        print(f"Pruebas fallidas: {self.failure_count}")
        print(f"Tasa de éxito: {(self.success_count / self.test_count) * 100:.1f}%\n")

        return self.failure_count == 0

    def test_sdk_loading(self):
        """Probar la carga de herramientas con el SDK."""
        print("\n----- Prueba: Carga de herramientas con SDK -----")

        # Prueba 1: Cargar todas las herramientas
        toolbox = load_toolbox_from_directory(self.examples_dir)
        self._log_result(
            "Carga completa de herramientas",
            len(toolbox) > 0,
            f"Se cargaron {len(toolbox)} herramientas",
        )

        # Prueba 2: Cargar una herramienta específica
        specific_toolbox = ATDFToolbox()
        success = specific_toolbox.load_tool_from_file(
            f"{self.examples_dir}/hole_maker.json"
        )
        self._log_result(
            "Carga de herramienta específica",
            success and len(specific_toolbox) == 1,
            f"Herramienta cargada: {specific_toolbox.tools[0].tool_id if len(specific_toolbox) > 0 else 'ninguna'}",
        )

        # Prueba 3: Acceder a propiedades de herramientas
        if len(toolbox) > 0:
            tool = toolbox.tools[0]
            properties_exist = (
                hasattr(tool, "tool_id")
                and hasattr(tool, "description")
                and hasattr(tool, "when_to_use")
                and hasattr(tool, "inputs")
            )
            self._log_result(
                "Acceso a propiedades de herramientas",
                properties_exist,
                f"Propiedades accesibles para herramienta {tool.tool_id}",
            )

        return toolbox if len(toolbox) > 0 else None

    def test_improved_loader(self):
        """Probar el cargador mejorado."""
        print("\n----- Prueba: Cargador mejorado -----")

        # Prueba 1: Cargar herramientas con el cargador mejorado
        tools = load_tools_from_directory(self.examples_dir)
        self._log_result(
            "Carga con improved_loader",
            len(tools) > 0,
            f"Se cargaron {len(tools)} herramientas",
        )

        return tools if len(tools) > 0 else None

    def test_language_detection(self):
        """Probar la detección de idiomas."""
        print("\n----- Prueba: Detección de idiomas -----")

        # Prueba 1: Español
        es_query = "necesito hacer un agujero en la pared"
        es_lang = detect_language(es_query)
        self._log_result(
            "Detección de español",
            es_lang == "es",
            f"Consulta en español detectada como '{es_lang}'",
        )

        # Prueba 2: Inglés
        en_query = "I need to translate some text"
        en_lang = detect_language(en_query)
        self._log_result(
            "Detección de inglés",
            en_lang == "en",
            f"Consulta en inglés detectada como '{en_lang}'",
        )

        # Prueba 3: Portugués
        pt_query = "preciso criar um furo na parede"
        pt_lang = detect_language(pt_query)
        self._log_result(
            "Detección de portugués",
            pt_lang == "pt",
            f"Consulta en portugués detectada como '{pt_lang}'",
        )

    def test_tool_selection(self):
        """Probar la selección de herramientas."""
        print("\n----- Prueba: Selección de herramientas -----")

        # Cargar herramientas con ambos métodos
        sdk_toolbox = load_toolbox_from_directory(self.examples_dir)
        imp_tools = load_tools_from_directory(self.examples_dir)

        # Pruebas con SDK
        if len(sdk_toolbox) > 0:
            # Prueba 1: Selección para perforar (español)
            es_query = "hacer un agujero"
            tool_es = find_best_tool(sdk_toolbox, es_query, language="es")
            self._log_result(
                "SDK: Selección para 'hacer un agujero'",
                tool_es is not None and "hole" in tool_es.tool_id.lower(),
                f"Herramienta seleccionada: {tool_es.tool_id if tool_es else 'ninguna'}",
            )

            # Prueba 2: Selección para traducir (inglés)
            en_query = "translate text"
            tool_en = find_best_tool(sdk_toolbox, en_query, language="en")
            self._log_result(
                "SDK: Selección para 'translate text'",
                tool_en is not None and "translator" in tool_en.tool_id.lower(),
                f"Herramienta seleccionada: {tool_en.tool_id if tool_en else 'ninguna'}",
            )

        # Pruebas con improved_loader
        if len(imp_tools) > 0:
            # Prueba 3: Selección para perforar (español)
            es_query = "hacer un agujero"
            tool_es = select_tool_by_goal(imp_tools, es_query)
            self._log_result(
                "Improved: Selección para 'hacer un agujero'",
                tool_es is not None and "hole" in tool_es["tool_id"].lower(),
                f"Herramienta seleccionada: {tool_es['tool_id'] if tool_es else 'ninguna'}",
            )

            # Prueba 4: Selección para traducir (portugués)
            pt_query = "preciso traduzir texto"
            tool_pt = select_tool_by_goal(imp_tools, pt_query)
            self._log_result(
                "Improved: Selección para 'preciso traduzir texto'",
                tool_pt is not None and "translator" in tool_pt["tool_id"].lower(),
                f"Herramienta seleccionada: {tool_pt['tool_id'] if tool_pt else 'ninguna'}",
            )

    def test_conversion(self):
        """Probar la conversión entre formatos."""
        print("\n----- Prueba: Conversión entre formatos -----")

        # Cargar una herramienta básica
        basic_tool_path = f"{self.examples_dir}/hole_maker.json"
        basic_tool = load_tool(basic_tool_path)

        if basic_tool:
            # Convertir a formato mejorado
            enhanced_tool = convert_to_enhanced(basic_tool, author="ATDF Tester")

            # Verificar que se añadieron campos adicionales
            has_metadata = "metadata" in enhanced_tool
            has_examples = "examples" in enhanced_tool

            self._log_result(
                "Conversión básica a mejorada",
                has_metadata and has_examples,
                f"Campos añadidos: metadatos={has_metadata}, ejemplos={has_examples}",
            )

            # Guardar y volver a cargar
            temp_path = "tests/temp_converted.json"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            save_success = save_tool(enhanced_tool, temp_path)

            if save_success:
                # Cargar con SDK para verificar compatibilidad
                temp_toolbox = ATDFToolbox()
                load_success = temp_toolbox.load_tool_from_file(temp_path)

                self._log_result(
                    "Compatibilidad de herramienta convertida",
                    load_success and len(temp_toolbox) == 1,
                    f"Carga con SDK: {load_success}",
                )

                # Limpiar archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def test_advanced_features(self):
        """Probar características avanzadas."""
        print("\n----- Prueba: Características avanzadas -----")

        # Buscar una herramienta con características avanzadas
        advanced_tool_path = f"{self.examples_dir}/enhanced_hole_maker.json"

        if os.path.exists(advanced_tool_path):
            # Cargar con SDK
            toolbox = ATDFToolbox()
            success = toolbox.load_tool_from_file(advanced_tool_path)

            if success and len(toolbox) > 0:
                tool = toolbox.tools[0]

                # Verificar metadatos
                has_metadata = tool.metadata is not None and len(tool.metadata) > 0
                self._log_result(
                    "Metadatos",
                    has_metadata,
                    f"Metadatos presentes: {list(tool.metadata.keys()) if has_metadata else 'ninguno'}",
                )

                # Verificar ejemplos
                has_examples = tool.examples is not None and len(tool.examples) > 0
                self._log_result(
                    "Ejemplos",
                    has_examples,
                    f"Número de ejemplos: {len(tool.examples) if has_examples else 0}",
                )

                # Verificar prerrequisitos
                has_prerequisites = (
                    tool.prerequisites is not None and len(tool.prerequisites) > 0
                )
                self._log_result(
                    "Prerrequisitos",
                    has_prerequisites,
                    f"Categorías de prerrequisitos: {list(tool.prerequisites.keys()) if has_prerequisites else 'ninguna'}",
                )

                # Verificar feedback
                has_feedback = tool.feedback is not None and len(tool.feedback) > 0
                self._log_result(
                    "Feedback",
                    has_feedback,
                    f"Tipos de feedback: {list(tool.feedback.keys()) if has_feedback else 'ninguno'}",
                )

                # Verificar esquema de entrada
                schema = tool.get_input_schema()
                has_schema = schema and "properties" in schema
                self._log_result(
                    "Esquema de entrada",
                    has_schema,
                    f"Propiedades en esquema: {list(schema['properties'].keys()) if has_schema else 'ninguna'}",
                )

        return toolbox if "toolbox" in locals() and len(toolbox) > 0 else None

    def test_multilingual_support(self):
        """Probar soporte multilingüe."""
        print("\n----- Prueba: Soporte multilingüe -----")

        # Buscar herramientas en diferentes idiomas
        es_files = [f for f in os.listdir(self.examples_dir) if f.endswith("_es.json")]
        en_files = [f for f in os.listdir(self.examples_dir) if f.endswith("_en.json")]
        pt_files = [f for f in os.listdir(self.examples_dir) if f.endswith("_pt.json")]

        self._log_result(
            "Archivos en diferentes idiomas",
            len(es_files) > 0 and len(en_files) > 0 and len(pt_files) > 0,
            f"ES: {len(es_files)}, EN: {len(en_files)}, PT: {len(pt_files)}",
        )

        # Cargar una herramienta avanzada con localización
        advanced_tool_path = f"{self.examples_dir}/enhanced_hole_maker.json"

        if os.path.exists(advanced_tool_path):
            with open(advanced_tool_path, "r", encoding="utf-8") as f:
                tool_data = json.load(f)

                # Verificar soporte de localización
                has_localization = "localization" in tool_data
                langs = list(tool_data.get("localization", {}).keys())

                self._log_result(
                    "Localización en herramienta avanzada",
                    has_localization and len(langs) > 1,
                    f"Idiomas soportados: {langs if has_localization else 'ninguno'}",
                )

                # Verificar consistencia entre idiomas
                if has_localization and len(langs) > 1:
                    fields_consistent = True
                    for lang in langs:
                        if (
                            "description" not in tool_data["localization"][lang]
                            or "when_to_use" not in tool_data["localization"][lang]
                        ):
                            fields_consistent = False
                            break

                    self._log_result(
                        "Consistencia entre idiomas",
                        fields_consistent,
                        "Todos los idiomas tienen campos obligatorios",
                    )


# Ejecutar pruebas si se ejecuta como script
if __name__ == "__main__":
    tester = ATDFTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
