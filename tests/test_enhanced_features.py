#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de las Características Mejoradas de ATDF (v0.2.0).

Este script verifica el correcto funcionamiento de las características
avanzadas añadidas en la versión mejorada del formato ATDF (v0.2.0).
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enhanced_features_tests')

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

# Importar módulos necesarios
from tools.converter import convert_to_enhanced, load_tool, save_tool
from tools.validator import validate_tool

class EnhancedFeaturesTester:
    """Clase para probar las características mejoradas de ATDF."""
    
    def __init__(self):
        """Inicializar el tester."""
        self.examples_dir = "schema/examples"
        self.basic_schema = "schema/atdf_schema.json"
        self.enhanced_schema = "schema/enhanced_atdf_schema.json"
        self.temp_dir = "tests/temp"
        
        # Crear directorio temporal si no existe
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Contadores para el resumen
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
        print("\n========== INICIANDO PRUEBAS DE CARACTERÍSTICAS MEJORADAS ==========\n")
        
        # Verificar que existan los esquemas
        if not os.path.exists(self.basic_schema):
            logger.error(f"El esquema básico '{self.basic_schema}' no existe.")
            return False
        
        if not os.path.exists(self.enhanced_schema):
            logger.error(f"El esquema mejorado '{self.enhanced_schema}' no existe.")
            return False
        
        # Ejecutar pruebas
        self.test_basic_validation()
        self.test_enhanced_validation()
        self.test_conversion_metadata()
        self.test_conversion_examples()
        self.test_conversion_localization()
        self.test_conversion_prerequisites()
        self.test_conversion_feedback()
        self.test_schema_compatibility()
        
        # Limpiar directorio temporal
        self._cleanup()
        
        # Mostrar resumen
        print(f"\n========== RESUMEN DE PRUEBAS DE CARACTERÍSTICAS MEJORADAS ==========")
        print(f"Total de pruebas: {self.test_count}")
        print(f"Pruebas exitosas: {self.success_count}")
        print(f"Pruebas fallidas: {self.failure_count}")
        print(f"Tasa de éxito: {(self.success_count / self.test_count) * 100:.1f}%\n")
        
        return self.failure_count == 0
    
    def _cleanup(self):
        """Limpiar archivos temporales."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Directorio temporal '{self.temp_dir}' eliminado correctamente.")
        except Exception as e:
            logger.warning(f"No se pudo limpiar el directorio temporal: {e}")
    
    def test_basic_validation(self):
        """Probar la validación de herramientas en formato básico."""
        print("\n----- Prueba: Validación Básica -----")
        
        # Buscar herramientas en formato básico
        basic_tools = ["hole_maker.json", "text_translator.json"]
        
        for tool_name in basic_tools:
            tool_path = os.path.join(self.examples_dir, tool_name)
            
            if os.path.exists(tool_path):
                # Validar contra el esquema básico
                is_valid = validate_tool(tool_path, self.basic_schema)
                
                self._log_result(
                    f"Validación básica de '{tool_name}'",
                    is_valid,
                    "Herramienta válida según esquema básico"
                )
    
    def test_enhanced_validation(self):
        """Probar la validación de herramientas en formato mejorado."""
        print("\n----- Prueba: Validación Mejorada -----")
        
        # Buscar herramientas en formato mejorado
        enhanced_tools = ["enhanced_hole_maker.json"]
        
        for tool_name in enhanced_tools:
            tool_path = os.path.join(self.examples_dir, tool_name)
            
            if os.path.exists(tool_path):
                # Validar contra el esquema mejorado
                is_valid = validate_tool(tool_path, self.enhanced_schema)
                
                self._log_result(
                    f"Validación mejorada de '{tool_name}'",
                    is_valid,
                    "Herramienta válida según esquema mejorado"
                )
    
    def test_conversion_metadata(self):
        """Probar la conversión y generación de metadatos."""
        print("\n----- Prueba: Conversión y Metadatos -----")
        
        # Cargar una herramienta básica
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de metadatos",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir con metadatos personalizados
        enhanced_tool = convert_to_enhanced(
            basic_tool, 
            author="Test Author",
            extract_language=True
        )
        
        # Verificar metadatos
        has_metadata = 'metadata' in enhanced_tool
        has_author = has_metadata and enhanced_tool['metadata'].get('author') == "Test Author"
        has_tags = has_metadata and 'tags' in enhanced_tool['metadata'] and len(enhanced_tool['metadata']['tags']) > 0
        has_category = has_metadata and 'category' in enhanced_tool['metadata']
        
        # Guardar para pruebas posteriores
        temp_path = os.path.join(self.temp_dir, "metadata_test.json")
        save_tool(enhanced_tool, temp_path)
        
        self._log_result(
            "Generación de metadatos",
            has_metadata and has_author and has_tags and has_category,
            f"Metadatos: autor={has_author}, etiquetas={has_tags}, categoría={has_category}"
        )
    
    def test_conversion_examples(self):
        """Probar la conversión y generación de ejemplos."""
        print("\n----- Prueba: Conversión y Ejemplos -----")
        
        # Cargar una herramienta básica
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de ejemplos",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir
        enhanced_tool = convert_to_enhanced(basic_tool)
        
        # Verificar ejemplos
        has_examples = 'examples' in enhanced_tool and len(enhanced_tool['examples']) > 0
        example_structure = False
        
        if has_examples and len(enhanced_tool['examples']) > 0:
            first_example = enhanced_tool['examples'][0]
            example_structure = (
                'title' in first_example and
                'description' in first_example and
                'inputs' in first_example and
                'expected_output' in first_example
            )
        
        # Guardar para pruebas posteriores
        temp_path = os.path.join(self.temp_dir, "examples_test.json")
        save_tool(enhanced_tool, temp_path)
        
        self._log_result(
            "Generación de ejemplos",
            has_examples and example_structure,
            f"Ejemplos generados: {len(enhanced_tool.get('examples', []))}, estructura correcta: {example_structure}"
        )
    
    def test_conversion_localization(self):
        """Probar la conversión y generación de localización."""
        print("\n----- Prueba: Conversión y Localización -----")
        
        # Cargar una herramienta básica
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de localización",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir con localización
        enhanced_tool = convert_to_enhanced(basic_tool, extract_language=True)
        
        # Verificar localización
        has_localization = 'localization' in enhanced_tool
        languages = list(enhanced_tool.get('localization', {}).keys())
        has_multiple_langs = len(languages) > 0
        
        # Verificar estructura de localización
        localization_structure = False
        if has_localization and has_multiple_langs:
            lang = languages[0]
            localization_structure = (
                'description' in enhanced_tool['localization'][lang] and
                'when_to_use' in enhanced_tool['localization'][lang]
            )
        
        # Guardar para pruebas posteriores
        temp_path = os.path.join(self.temp_dir, "localization_test.json")
        save_tool(enhanced_tool, temp_path)
        
        self._log_result(
            "Generación de localización",
            has_localization and has_multiple_langs and localization_structure,
            f"Idiomas: {languages}, estructura correcta: {localization_structure}"
        )
    
    def test_conversion_prerequisites(self):
        """Probar la conversión y generación de prerrequisitos."""
        print("\n----- Prueba: Conversión y Prerrequisitos -----")
        
        # Cargar una herramienta básica (que parezca física)
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de prerrequisitos",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir
        enhanced_tool = convert_to_enhanced(basic_tool)
        
        # Verificar prerrequisitos
        has_prerequisites = 'prerequisites' in enhanced_tool
        
        prerequisites_structure = False
        if has_prerequisites:
            prerequisites_structure = (
                'tools' in enhanced_tool['prerequisites'] and
                'conditions' in enhanced_tool['prerequisites'] and
                'permissions' in enhanced_tool['prerequisites']
            )
        
        # Guardar para pruebas posteriores
        temp_path = os.path.join(self.temp_dir, "prerequisites_test.json")
        save_tool(enhanced_tool, temp_path)
        
        self._log_result(
            "Generación de prerrequisitos",
            has_prerequisites and prerequisites_structure,
            f"Prerrequisitos generados: {has_prerequisites}, estructura correcta: {prerequisites_structure}"
        )
    
    def test_conversion_feedback(self):
        """Probar la conversión y generación de feedback."""
        print("\n----- Prueba: Conversión y Feedback -----")
        
        # Cargar una herramienta básica (que parezca física)
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de feedback",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir
        enhanced_tool = convert_to_enhanced(basic_tool)
        
        # Verificar feedback
        has_feedback = 'feedback' in enhanced_tool
        
        feedback_structure = False
        if has_feedback:
            feedback_structure = (
                'progress_indicators' in enhanced_tool['feedback'] and
                'completion_signals' in enhanced_tool['feedback']
            )
        
        # Guardar para pruebas posteriores
        temp_path = os.path.join(self.temp_dir, "feedback_test.json")
        save_tool(enhanced_tool, temp_path)
        
        self._log_result(
            "Generación de feedback",
            has_feedback and feedback_structure,
            f"Feedback generado: {has_feedback}, estructura correcta: {feedback_structure}"
        )
    
    def test_schema_compatibility(self):
        """Probar que las herramientas mejoradas sigan siendo compatibles con el esquema básico."""
        print("\n----- Prueba: Compatibilidad de Esquemas -----")
        
        # Cargar una herramienta básica
        basic_tool_path = os.path.join(self.examples_dir, "hole_maker.json")
        basic_tool = load_tool(basic_tool_path)
        
        if not basic_tool:
            self._log_result(
                "Carga de herramienta básica para prueba de compatibilidad",
                False,
                f"No se pudo cargar '{basic_tool_path}'"
            )
            return
        
        # Convertir a formato mejorado
        enhanced_tool = convert_to_enhanced(basic_tool)
        
        # Guardar versión mejorada
        temp_path = os.path.join(self.temp_dir, "compatibility_test.json")
        save_tool(enhanced_tool, temp_path)
        
        # Validar contra esquema básico
        basic_valid = validate_tool(temp_path, self.basic_schema)
        
        # Validar contra esquema mejorado
        enhanced_valid = validate_tool(temp_path, self.enhanced_schema)
        
        self._log_result(
            "Compatibilidad de esquemas",
            basic_valid and enhanced_valid,
            f"Válido contra esquema básico: {basic_valid}, válido contra esquema mejorado: {enhanced_valid}"
        )

# Ejecutar pruebas si se ejecuta como script
if __name__ == "__main__":
    tester = EnhancedFeaturesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 