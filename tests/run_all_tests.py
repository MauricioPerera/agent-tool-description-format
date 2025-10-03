#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de todas las pruebas de ATDF.

Este script ejecuta todas las pruebas disponibles para verificar el funcionamiento
completo del formato ATDF y todas sus características.
"""

import logging
import os
import sys
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("all_tests")

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

# Importar todas las pruebas
try:
    from tests.test_atdf_complete import ATDFTester
    from tests.test_enhanced_features import EnhancedFeaturesTester
    from tests.test_trilingual_agent import TrilingualTester
except ImportError as e:
    logger.error(f"Error al importar módulos de prueba: {e}")
    sys.exit(1)


def run_all_tests():
    """Ejecutar todas las pruebas disponibles."""
    print("\n==========================================================")
    print("                PRUEBAS COMPLETAS DE ATDF                 ")
    print("==========================================================\n")

    # Lista para almacenar resultados
    results = []

    # Medir tiempo total
    start_time = time.time()

    # 1. Pruebas completas del SDK y funcionalidades básicas
    print("\n\n==========================================================")
    print("           INICIANDO PRUEBAS COMPLETAS DE ATDF            ")
    print("==========================================================\n")

    try:
        atdf_tester = ATDFTester()
        atdf_success = atdf_tester.run_all_tests()
        results.append(
            (
                "Pruebas completas de ATDF",
                atdf_success,
                atdf_tester.success_count,
                atdf_tester.failure_count,
                atdf_tester.test_count,
            )
        )
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas completas de ATDF: {e}")
        results.append(("Pruebas completas de ATDF", False, 0, 1, 1))

    # 2. Pruebas del agente trilingüe
    print("\n\n==========================================================")
    print("           INICIANDO PRUEBAS DEL AGENTE TRILINGÜE        ")
    print("==========================================================\n")

    try:
        trilingual_tester = TrilingualTester()
        trilingual_success = trilingual_tester.run_all_tests()
        results.append(
            (
                "Pruebas del agente trilingüe",
                trilingual_success,
                trilingual_tester.success_count,
                trilingual_tester.failure_count,
                trilingual_tester.test_count,
            )
        )
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas del agente trilingüe: {e}")
        results.append(("Pruebas del agente trilingüe", False, 0, 1, 1))

    # 3. Pruebas de características mejoradas
    print("\n\n==========================================================")
    print("         INICIANDO PRUEBAS DE CARACTERÍSTICAS MEJORADAS   ")
    print("==========================================================\n")

    try:
        enhanced_tester = EnhancedFeaturesTester()
        enhanced_success = enhanced_tester.run_all_tests()
        results.append(
            (
                "Pruebas de características mejoradas",
                enhanced_success,
                enhanced_tester.success_count,
                enhanced_tester.failure_count,
                enhanced_tester.test_count,
            )
        )
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas de características mejoradas: {e}")
        results.append(("Pruebas de características mejoradas", False, 0, 1, 1))

    # Calcular tiempo total
    total_time = time.time() - start_time

    # Calcular totales
    total_success = sum(result[2] for result in results)
    total_failure = sum(result[3] for result in results)
    total_tests = sum(result[4] for result in results)

    # Mostrar resumen global
    print("\n\n==========================================================")
    print("                 RESUMEN GLOBAL DE PRUEBAS                ")
    print("==========================================================\n")

    # Mostrar resultados por categoría
    for name, success, passed, failed, total in results:
        status = "✅ PASS" if success else "❌ FAIL"
        if total > 0:
            success_rate = (passed / total) * 100
            print(
                f"{status} - {name}: {passed}/{total} pruebas exitosas ({success_rate:.1f}%)"
            )
        else:
            print(f"{status} - {name}: No se ejecutaron pruebas")

    # Mostrar resumen total
    print("\n==========================================================")
    print(f"Total de pruebas: {total_tests}")
    print(f"Pruebas exitosas: {total_success}")
    print(f"Pruebas fallidas: {total_failure}")
    if total_tests > 0:
        success_rate = (total_success / total_tests) * 100
        print(f"Tasa de éxito global: {success_rate:.1f}%")
    else:
        print("Tasa de éxito global: N/A (no se ejecutaron pruebas)")
    print(f"Tiempo total: {total_time:.2f} segundos")
    print("==========================================================\n")

    # Determinar el resultado final
    overall_success = all(result[1] for result in results)
    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
