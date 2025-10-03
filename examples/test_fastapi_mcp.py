#!/usr/bin/env python3
"""
Comprehensive test script for FastAPI MCP Integration with ATDF error handling
"""

import json
import time
from datetime import datetime, timedelta

from http_client import get as http_get
from http_client import post as http_post

BASE_URL = "http://127.0.0.1:8000"


def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    try:
        response = http_get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_tools_endpoint():
    """Test the MCP tools endpoint"""
    print("\nTesting tools endpoint...")
    try:
        response = http_get(f"{BASE_URL}/tools")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Tools found: {len(data.get('tools', []))}")
        for tool in data.get("tools", []):
            print(f"  - {tool['name']}: {tool['description']}")
        return response.status_code == 200 and len(data.get("tools", [])) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_hotel_reservation_success():
    """Test successful hotel reservation"""
    print("\nTesting successful hotel reservation...")
    try:
        data = {
            "guest_name": "John Doe",
            "email": "john.doe@example.com",
            "check_in": (datetime.now() + timedelta(days=1)).isoformat(),
            "check_out": (datetime.now() + timedelta(days=3)).isoformat(),
            "room_type": "double",
            "guests": 2,
        }
        response = http_post(f"{BASE_URL}/api/hotel/reserve", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200 and "reservation_id" in result
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_hotel_reservation_validation_errors():
    """Test hotel reservation validation errors with ATDF responses"""
    print("\nTesting hotel reservation validation errors...")

    # Test past check-in date
    print("  Testing past check-in date...")
    try:
        data = {
            "guest_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "check_in": (datetime.now() - timedelta(days=1)).isoformat(),
            "check_out": (datetime.now() + timedelta(days=1)).isoformat(),
            "room_type": "single",
            "guests": 1,
        }
        response = http_post(f"{BASE_URL}/api/hotel/reserve", json=data)
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    ATDF Error: {json.dumps(result, indent=2)}")
        if response.status_code != 400:
            print("    La API no devolvió el código esperado (400)")
            return False
        if "errors" not in result:
            print("    La respuesta no incluyó errores ATDF")
            return False
        if result["errors"][0].get("tool_name") != "hotel_reservation":
            print("    El error no corresponde a hotel_reservation")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

    # Test invalid stay duration
    print("  Testing invalid stay duration...")
    try:
        data = {
            "guest_name": "Bob Smith",
            "email": "bob.smith@example.com",
            "check_in": (datetime.now() + timedelta(hours=1)).isoformat(),
            "check_out": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "room_type": "suite",
            "guests": 3,
        }
        response = http_post(f"{BASE_URL}/api/hotel/reserve", json=data)
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    ATDF Error: {json.dumps(result, indent=2)}")
        if response.status_code != 400 or "errors" not in result:
            print("    La API no retornó el envelope ATDF esperado")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

    return True


def test_flight_booking_success():
    """Test successful flight booking"""
    print("\nTesting successful flight booking...")
    try:
        data = {
            "passenger_name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "departure_city": "New York",
            "arrival_city": "Los Angeles",
            "departure_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "seat_class": "economy",
        }
        response = http_post(f"{BASE_URL}/api/flight/book", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200 and "booking_id" in result
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_flight_booking_validation_errors():
    """Test flight booking validation errors with ATDF responses"""
    print("\nTesting flight booking validation errors...")

    # Test past departure date
    print("  Testing past departure date...")
    try:
        data = {
            "passenger_name": "Charlie Brown",
            "email": "charlie.brown@example.com",
            "departure_city": "Chicago",
            "arrival_city": "Miami",
            "departure_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "seat_class": "business",
        }
        response = http_post(f"{BASE_URL}/api/flight/book", json=data)
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    ATDF Error: {json.dumps(result, indent=2)}")
        if response.status_code != 400:
            print("    La API no devolvió el código esperado (400)")
            return False
        if "errors" not in result:
            print("    La respuesta no incluyó errores ATDF")
            return False
        if result["errors"][0].get("tool_name") != "flight_booking":
            print("    El error no corresponde a flight_booking")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

    # Test same departure and arrival city
    print("  Testing same departure and arrival city...")
    try:
        data = {
            "passenger_name": "David Wilson",
            "email": "david.wilson@example.com",
            "departure_city": "Boston",
            "arrival_city": "Boston",
            "departure_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "seat_class": "first",
        }
        response = http_post(f"{BASE_URL}/api/flight/book", json=data)
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    ATDF Error: {json.dumps(result, indent=2)}")
        if response.status_code != 400 or "errors" not in result:
            print("    La API no retornó el envelope ATDF esperado")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

    return True


def test_list_endpoints():
    """Test list endpoints"""
    print("\nTesting list endpoints...")

    # Test hotel reservations list
    print("  Testing hotel reservations list...")
    try:
        response = http_get(f"{BASE_URL}/api/hotel/reservations")
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    Reservations: {len(result.get('reservations', []))}")
    except Exception as e:
        print(f"    Error: {e}")
        return False

    # Test flight bookings list
    print("  Testing flight bookings list...")
    try:
        response = http_get(f"{BASE_URL}/api/flight/bookings")
        print(f"    Status: {response.status_code}")
        result = response.json()
        print(f"    Bookings: {len(result.get('bookings', []))}")
    except Exception as e:
        print(f"    Error: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("FastAPI MCP Integration Test Suite")
    print("=" * 60)

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)

    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Tools Endpoint", test_tools_endpoint),
        ("Hotel Reservation Success", test_hotel_reservation_success),
        (
            "Hotel Reservation Validation Errors",
            test_hotel_reservation_validation_errors,
        ),
        ("Flight Booking Success", test_flight_booking_success),
        ("Flight Booking Validation Errors", test_flight_booking_validation_errors),
        ("List Endpoints", test_list_endpoints),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ERROR - {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! FastAPI MCP integration is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    main()
