#!/usr/bin/env python3
"""
ATDF Error Handling Demonstration Script

Este script demuestra todas las capacidades de manejo de errores ATDF
implementadas en la integración FastAPI MCP.

Ejecutar con: python examples/demo_atdf_errors.py
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuración
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}


def print_section(title: str):
    """Imprime una sección con formato."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Imprime una subsección con formato."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def make_request(
    method: str, endpoint: str, data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Realiza una petición HTTP y retorna la respuesta."""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json() if response.content else None,
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "No se pudo conectar al servidor. Asegúrate de que esté ejecutándose en http://127.0.0.1:8000"
        }
    except Exception as e:
        return {"error": f"Error en la petición: {str(e)}"}


def demo_api_info():
    """Demuestra la información básica de la API."""
    print_section("INFORMACIÓN DE LA API")

    response = make_request("GET", "/")

    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False

    print(f"✅ Status: {response['status_code']}")
    print(f"📋 Información de la API:")
    print(json.dumps(response["body"], indent=2, ensure_ascii=False))
    return True


def demo_mcp_tools():
    """Demuestra el endpoint de herramientas MCP."""
    print_section("HERRAMIENTAS MCP")

    response = make_request("GET", "/tools")

    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False

    print(f"✅ Status: {response['status_code']}")
    print(f"🔧 Herramientas disponibles:")

    tools = response["body"]["tools"]
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']}: {tool['description']}")
        print(
            f"     Esquema de entrada: {len(tool['inputSchema']['properties'])} propiedades"
        )

    return True


def demo_hotel_reservation_success():
    """Demuestra una reserva de hotel exitosa."""
    print_section("RESERVA DE HOTEL EXITOSA")

    # Datos válidos para reserva
    check_in = datetime.now() + timedelta(days=7)
    check_out = check_in + timedelta(days=2)

    data = {
        "guest_name": "María García",
        "email": "maria.garcia@example.com",
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "room_type": "double",
        "guests": 2,
    }

    response = make_request("POST", "/api/hotel/reserve", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False

    print(f"✅ Status: {response['status_code']}")
    print(f"🏨 Reserva creada exitosamente:")
    print(json.dumps(response["body"], indent=2, ensure_ascii=False))
    return True


def demo_hotel_validation_errors():
    """Demuestra errores de validación en reservas de hotel."""
    print_section("ERRORES DE VALIDACIÓN - HOTEL")

    # 1. Fecha de check-in en el pasado
    print_subsection("1. Fecha de Check-in en el Pasado")
    past_date = datetime.now() - timedelta(days=1)
    future_date = datetime.now() + timedelta(days=5)

    data = {
        "guest_name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "check_in": past_date.isoformat(),
        "check_out": future_date.isoformat(),
        "room_type": "single",
        "guests": 1,
    }

    response = make_request("POST", "/api/hotel/reserve", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"📋 Status: {response['status_code']}")
        print(f"🚨 Error ATDF (fecha en el pasado):")
        print(json.dumps(response["body"], indent=2, ensure_ascii=False))

    # 2. Check-out antes del check-in
    print_subsection("2. Check-out Antes del Check-in")
    check_in = datetime.now() + timedelta(days=5)
    check_out = check_in - timedelta(days=1)  # Antes del check-in

    data = {
        "guest_name": "Ana López",
        "email": "ana.lopez@example.com",
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "room_type": "suite",
        "guests": 3,
    }

    response = make_request("POST", "/api/hotel/reserve", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"📋 Status: {response['status_code']}")
        print(f"🚨 Error ATDF (validación Pydantic):")
        print(json.dumps(response["body"], indent=2, ensure_ascii=False))


def demo_flight_booking_success():
    """Demuestra una reserva de vuelo exitosa."""
    print_section("RESERVA DE VUELO EXITOSA")

    departure_date = datetime.now() + timedelta(days=14)

    data = {
        "passenger_name": "Carlos Rodríguez",
        "email": "carlos.rodriguez@example.com",
        "departure_city": "Madrid",
        "arrival_city": "Barcelona",
        "departure_date": departure_date.isoformat(),
        "seat_class": "economy",
    }

    response = make_request("POST", "/api/flight/book", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False

    print(f"✅ Status: {response['status_code']}")
    print(f"✈️ Vuelo reservado exitosamente:")
    print(json.dumps(response["body"], indent=2, ensure_ascii=False))
    return True


def demo_flight_validation_errors():
    """Demuestra errores de validación en reservas de vuelo."""
    print_section("ERRORES DE VALIDACIÓN - VUELO")

    # 1. Fecha de salida en el pasado
    print_subsection("1. Fecha de Salida en el Pasado")
    past_date = datetime.now() - timedelta(days=1)

    data = {
        "passenger_name": "Laura Martín",
        "email": "laura.martin@example.com",
        "departure_city": "Valencia",
        "arrival_city": "Sevilla",
        "departure_date": past_date.isoformat(),
        "seat_class": "business",
    }

    response = make_request("POST", "/api/flight/book", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"📋 Status: {response['status_code']}")
        print(f"🚨 Error ATDF (fecha en el pasado):")
        print(json.dumps(response["body"], indent=2, ensure_ascii=False))

    # 2. Misma ciudad de origen y destino
    print_subsection("2. Misma Ciudad de Origen y Destino")
    future_date = datetime.now() + timedelta(days=10)

    data = {
        "passenger_name": "Pedro Sánchez",
        "email": "pedro.sanchez@example.com",
        "departure_city": "Bilbao",
        "arrival_city": "Bilbao",  # Misma ciudad
        "departure_date": future_date.isoformat(),
        "seat_class": "first",
    }

    response = make_request("POST", "/api/flight/book", data)

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"📋 Status: {response['status_code']}")
        print(f"🚨 Error ATDF (ruta inválida):")
        print(json.dumps(response["body"], indent=2, ensure_ascii=False))


def demo_list_endpoints():
    """Demuestra los endpoints de listado."""
    print_section("ENDPOINTS DE LISTADO")

    # Listar reservas de hotel
    print_subsection("Reservas de Hotel")
    response = make_request("GET", "/api/hotel/reservations")

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"✅ Status: {response['status_code']}")
        reservations = response["body"]["reservations"]
        print(f"🏨 Reservas encontradas: {len(reservations)}")
        for i, reservation in enumerate(reservations, 1):
            print(
                f"  {i}. {reservation['guest_name']} - {reservation['room_type']} - {reservation['status']}"
            )

    # Listar reservas de vuelo
    print_subsection("Reservas de Vuelo")
    response = make_request("GET", "/api/flight/bookings")

    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(f"✅ Status: {response['status_code']}")
        bookings = response["body"]["bookings"]
        print(f"✈️ Reservas encontradas: {len(bookings)}")
        for i, booking in enumerate(bookings, 1):
            print(
                f"  {i}. {booking['passenger_name']} - {booking['departure_city']} → {booking['arrival_city']} - {booking['status']}"
            )


def demo_atdf_error_analysis():
    """Analiza y explica el formato ATDF de errores."""
    print_section("ANÁLISIS DEL FORMATO ATDF")

    print(
        """
🎯 **Formato ATDF (Agent Tool Description Format)**

El formato ATDF proporciona respuestas de error estandarizadas que incluyen:

📋 **Campos Principales:**
• type: URI que identifica el tipo de error
• title: Título legible del error
• detail: Descripción detallada del problema
• instance: ID único de la instancia de error

🔧 **Campos Específicos para Agentes de IA:**
• tool_name: Nombre de la herramienta que generó el error
• parameter_name: Parámetro específico que causó el error
• suggested_value: Valor sugerido para corregir el error
• context: Información adicional de contexto

💡 **Beneficios para Agentes de IA:**
1. **Corrección Automática**: Los valores sugeridos permiten corrección inmediata
2. **Contexto Enriquecido**: Información detallada para mejor debugging
3. **Seguimiento**: IDs únicos para monitoreo y análisis
4. **Estandarización**: Formato consistente en todas las herramientas

🔄 **Flujo de Corrección:**
1. Agente recibe error ATDF
2. Identifica el parámetro problemático
3. Aplica el valor sugerido (si está disponible)
4. Reintenta la operación
5. Monitorea el resultado
"""
    )


def main():
    """Función principal que ejecuta todas las demostraciones."""
    print("🚀 DEMOSTRACIÓN COMPLETA - ATDF FastAPI MCP Integration")
    print("=" * 70)
    print("Este script demuestra todas las capacidades de manejo de errores ATDF")
    print("implementadas en la integración FastAPI MCP.")
    print("=" * 70)

    # Verificar que el servidor esté ejecutándose
    print("\n🔍 Verificando conexión con el servidor...")
    test_response = make_request("GET", "/")
    if "error" in test_response:
        print(f"❌ {test_response['error']}")
        print("\n💡 Para ejecutar esta demostración:")
        print("   1. Asegúrate de que el servidor esté ejecutándose:")
        print("      uvicorn examples.fastapi_mcp_integration:app --reload --port 8000")
        print("   2. Ejecuta este script nuevamente:")
        print("      python examples/demo_atdf_errors.py")
        return

    print("✅ Servidor conectado correctamente!")

    # Ejecutar todas las demostraciones
    demos = [
        ("Información de la API", demo_api_info),
        ("Herramientas MCP", demo_mcp_tools),
        ("Reserva de Hotel Exitosa", demo_hotel_reservation_success),
        ("Errores de Validación - Hotel", demo_hotel_validation_errors),
        ("Reserva de Vuelo Exitosa", demo_flight_booking_success),
        ("Errores de Validación - Vuelo", demo_flight_validation_errors),
        ("Endpoints de Listado", demo_list_endpoints),
        ("Análisis del Formato ATDF", demo_atdf_error_analysis),
    ]

    results = []
    for title, demo_func in demos:
        try:
            result = demo_func()
            results.append((title, result))
        except Exception as e:
            print(f"❌ Error en {title}: {str(e)}")
            results.append((title, False))

    # Resumen final
    print_section("RESUMEN DE LA DEMOSTRACIÓN")

    successful = sum(1 for _, result in results if result)
    total = len(results)

    print(f"📊 Resultados: {successful}/{total} demostraciones exitosas")

    if successful == total:
        print("🎉 ¡Todas las demostraciones fueron exitosas!")
        print(
            "✅ La integración FastAPI MCP con manejo de errores ATDF está funcionando correctamente."
        )
    else:
        print("⚠️ Algunas demostraciones fallaron. Revisa los errores anteriores.")

    print("\n🔗 Recursos adicionales:")
    print("   • README.md - Documentación completa del proyecto")
    print("   • IMPLEMENTATION_SUMMARY.md - Resumen técnico de implementación")
    print("   • test_fastapi_mcp.py - Suite de pruebas automatizadas")

    print("\n🚀 ¡La integración está lista para uso en producción!")


if __name__ == "__main__":
    main()
