#!/usr/bin/env python3
"""
Test script for Enhanced ATDF Metadata Implementation

Este script valida que todos los campos de metadata del enhancement_proposal.md
estén correctamente implementados en la integración FastAPI.

Ejecutar con: python examples/test_metadata_implementation.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}


def test_metadata_fields():
    """Prueba que todos los campos de metadata estén presentes"""
    print("🔍 Probando campos de metadata...")

    try:
        response = requests.get(f"{BASE_URL}/tools", headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        tools = data.get("tools", [])

        if not tools:
            print("❌ No se encontraron herramientas")
            return False

        for tool in tools:
            tool_id = tool.get("tool_id", "unknown")
            print(f"\n📋 Validando herramienta: {tool_id}")

            # Validar campos básicos
            required_fields = ["tool_id", "description", "when_to_use", "inputSchema"]
            for field in required_fields:
                if field not in tool:
                    print(f"❌ Campo requerido faltante: {field}")
                    return False
                print(f"✅ {field}: presente")

            # Validar metadata
            metadata = tool.get("metadata")
            if not metadata:
                print("❌ Campo metadata faltante")
                return False

            metadata_fields = [
                "version",
                "author",
                "tags",
                "category",
                "created_at",
                "updated_at",
            ]
            for field in metadata_fields:
                if field not in metadata:
                    print(f"❌ Campo metadata.{field} faltante")
                    return False
                print(f"✅ metadata.{field}: {metadata[field]}")

            # Validar localización
            localization = tool.get("localization")
            if not localization:
                print("❌ Campo localization faltante")
                return False

            for lang in ["es", "en"]:
                if lang not in localization:
                    print(f"❌ Localización {lang} faltante")
                    return False

                lang_data = localization[lang]
                for field in ["description", "when_to_use"]:
                    if field not in lang_data:
                        print(f"❌ Campo localization.{lang}.{field} faltante")
                        return False
                    print(f"✅ localization.{lang}.{field}: presente")

            # Validar ejemplos
            examples = tool.get("examples")
            if not examples or not isinstance(examples, list):
                print("❌ Campo examples faltante o no es una lista")
                return False

            for i, example in enumerate(examples):
                example_fields = ["goal", "input_values", "expected_result"]
                for field in example_fields:
                    if field not in example:
                        print(f"❌ Campo examples[{i}].{field} faltante")
                        return False
                    print(f"✅ examples[{i}].{field}: presente")

            # Validar prerrequisitos
            prerequisites = tool.get("prerequisites")
            if not prerequisites:
                print("❌ Campo prerequisites faltante")
                return False

            prereq_fields = ["tools", "permissions", "environment"]
            for field in prereq_fields:
                if field not in prerequisites:
                    print(f"❌ Campo prerequisites.{field} faltante")
                    return False
                print(f"✅ prerequisites.{field}: {prerequisites[field]}")

        print("\n🎉 Todos los campos de metadata están correctamente implementados!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_schema_compliance():
    """Prueba que la estructura cumpla con el enhanced_atdf_schema.json"""
    print("\n🔍 Probando cumplimiento del esquema enhanced ATDF...")

    try:
        response = requests.get(f"{BASE_URL}/tools", headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        tools = data.get("tools", [])

        for tool in tools:
            tool_id = tool.get("tool_id")

            # Validar tipos de datos
            metadata = tool.get("metadata", {})

            # Version debe ser string
            if not isinstance(metadata.get("version"), str):
                print(f"❌ {tool_id}: metadata.version debe ser string")
                return False

            # Tags debe ser lista
            if not isinstance(metadata.get("tags"), list):
                print(f"❌ {tool_id}: metadata.tags debe ser lista")
                return False

            # Created_at y updated_at deben ser strings de fecha
            for date_field in ["created_at", "updated_at"]:
                date_value = metadata.get(date_field)
                if not isinstance(date_value, str):
                    print(f"❌ {tool_id}: metadata.{date_field} debe ser string")
                    return False

                try:
                    datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                except ValueError:
                    print(f"❌ {tool_id}: metadata.{date_field} no es una fecha válida")
                    return False

            # Examples debe ser lista de objetos con campos requeridos
            examples = tool.get("examples", [])
            for example in examples:
                if not isinstance(example.get("input_values"), dict):
                    print(f"❌ {tool_id}: example.input_values debe ser objeto")
                    return False

        print("✅ Esquema enhanced ATDF cumplido correctamente!")
        return True

    except Exception as e:
        print(f"❌ Error validando esquema: {e}")
        return False


def test_localization_content():
    """Prueba que el contenido de localización sea diferente entre idiomas"""
    print("\n🔍 Probando contenido de localización...")

    try:
        response = requests.get(f"{BASE_URL}/tools", headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        tools = data.get("tools", [])

        for tool in tools:
            tool_id = tool.get("tool_id")
            localization = tool.get("localization", {})

            es_desc = localization.get("es", {}).get("description", "")
            en_desc = localization.get("en", {}).get("description", "")

            if es_desc == en_desc:
                print(
                    f"⚠️  {tool_id}: Las descripciones en español e inglés son idénticas"
                )
            else:
                print(f"✅ {tool_id}: Localización diferenciada correctamente")
                print(f"   ES: {es_desc[:50]}...")
                print(f"   EN: {en_desc[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error validando localización: {e}")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de implementación de metadata ATDF")
    print("=" * 60)

    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Servidor FastAPI ejecutándose en {BASE_URL}")
    except:
        print(f"❌ Servidor FastAPI no disponible en {BASE_URL}")
        print("   Asegúrate de ejecutar: python fastapi_mcp_integration.py")
        return

    # Ejecutar pruebas
    tests = [
        ("Campos de Metadata", test_metadata_fields),
        ("Cumplimiento de Esquema", test_schema_compliance),
        ("Contenido de Localización", test_localization_content),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nResultado: {passed}/{len(tests)} pruebas pasaron")

    if passed == len(tests):
        print("🎉 ¡Implementación de metadata ATDF completamente exitosa!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar implementación.")


if __name__ == "__main__":
    main()
