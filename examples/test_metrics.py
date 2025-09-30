#!/usr/bin/env python3
"""
Test script to generate metrics for ATDF FastAPI application.
This script sends various requests to test the monitoring and metrics collection.
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

# Configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_REQUESTS = 5
TEST_DURATION = 60  # seconds

class MetricsTestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request and return response data"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
        except Exception as e:
            return {
                "status": 500,
                "error": str(e)
            }
    
    async def test_hotel_reservation_success(self) -> Dict[str, Any]:
        """Test successful hotel reservation"""
        check_in = datetime.now() + timedelta(days=random.randint(1, 30))
        check_out = check_in + timedelta(days=random.randint(1, 7))
        
        data = {
            "guest_name": f"Test Guest {random.randint(1, 1000)}",
            "email": f"test{random.randint(1, 1000)}@example.com",
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "room_type": random.choice(["single", "double", "suite"]),
            "guests": random.randint(1, 4)
        }
        
        return await self.make_request("POST", "/api/hotel/reserve", data)
    
    async def test_hotel_reservation_error(self) -> Dict[str, Any]:
        """Test hotel reservation with validation error"""
        # Use past date to trigger validation error
        check_in = datetime.now() - timedelta(days=1)
        check_out = check_in + timedelta(days=1)
        
        data = {
            "guest_name": "Error Test",
            "email": "error@example.com",
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "room_type": "single",
            "guests": 1
        }
        
        return await self.make_request("POST", "/api/hotel/reserve", data)
    
    async def test_flight_booking_success(self) -> Dict[str, Any]:
        """Test successful flight booking"""
        departure_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        cities = ["New York", "Los Angeles", "Chicago", "Miami", "Seattle", "Boston"]
        departure_city = random.choice(cities)
        arrival_city = random.choice([c for c in cities if c != departure_city])
        
        data = {
            "passenger_name": f"Test Passenger {random.randint(1, 1000)}",
            "email": f"passenger{random.randint(1, 1000)}@example.com",
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "departure_date": departure_date.isoformat(),
            "seat_class": random.choice(["economy", "business", "first"])
        }
        
        return await self.make_request("POST", "/api/flight/book", data)
    
    async def test_flight_booking_error(self) -> Dict[str, Any]:
        """Test flight booking with validation error"""
        # Use same city for departure and arrival to trigger error
        data = {
            "passenger_name": "Error Test",
            "email": "error@example.com",
            "departure_city": "New York",
            "arrival_city": "New York",  # Same city - will cause error
            "departure_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "seat_class": "economy"
        }
        
        return await self.make_request("POST", "/api/flight/book", data)
    
    async def test_endpoints(self) -> Dict[str, Any]:
        """Test various endpoints"""
        endpoints = [
            ("GET", "/"),
            ("GET", "/tools"),
            ("GET", "/health"),
            ("GET", "/api/hotel/reservations"),
            ("GET", "/api/flight/bookings"),
            ("GET", "/metrics")
        ]
        
        results = {}
        for method, endpoint in endpoints:
            result = await self.make_request(method, endpoint)
            results[f"{method} {endpoint}"] = result
        
        return results

async def run_load_test(client: MetricsTestClient, duration: int):
    """Run load test for specified duration"""
    print(f"Starting load test for {duration} seconds...")
    
    start_time = time.time()
    request_count = 0
    error_count = 0
    
    while time.time() - start_time < duration:
        # Create tasks for concurrent requests
        tasks = []
        
        for _ in range(CONCURRENT_REQUESTS):
            # Randomly choose test type
            test_type = random.choice([
                "hotel_success",
                "hotel_error", 
                "flight_success",
                "flight_error",
                "endpoints"
            ])
            
            if test_type == "hotel_success":
                tasks.append(client.test_hotel_reservation_success())
            elif test_type == "hotel_error":
                tasks.append(client.test_hotel_reservation_error())
            elif test_type == "flight_success":
                tasks.append(client.test_flight_booking_success())
            elif test_type == "flight_error":
                tasks.append(client.test_flight_booking_error())
            elif test_type == "endpoints":
                tasks.append(client.test_endpoints())
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in results:
            request_count += 1
            if isinstance(result, Exception) or (isinstance(result, dict) and result.get("status", 200) >= 400):
                error_count += 1
        
        # Small delay between batches
        await asyncio.sleep(0.1)
    
    elapsed_time = time.time() - start_time
    print(f"Load test completed:")
    print(f"  Duration: {elapsed_time:.2f} seconds")
    print(f"  Total requests: {request_count}")
    print(f"  Errors: {error_count}")
    print(f"  Request rate: {request_count / elapsed_time:.2f} req/sec")
    print(f"  Error rate: {(error_count / request_count * 100):.2f}%")

async def test_metrics_endpoint(client: MetricsTestClient):
    """Test the metrics endpoint"""
    print("Testing metrics endpoint...")
    
    result = await client.make_request("GET", "/metrics")
    
    if result["status"] == 200:
        metrics_data = result["data"]
        print("✅ Metrics endpoint is working")
        print(f"Metrics data length: {len(metrics_data)} characters")
        
        # Check for expected metrics
        expected_metrics = [
            "atdf_requests_total",
            "atdf_request_duration_seconds",
            "atdf_tool_executions_total",
            "atdf_tool_execution_duration_seconds",
            "atdf_active_connections",
            "atdf_errors_total"
        ]
        
        for metric in expected_metrics:
            if metric in metrics_data:
                print(f"✅ Found metric: {metric}")
            else:
                print(f"❌ Missing metric: {metric}")
    else:
        print(f"❌ Metrics endpoint failed with status: {result['status']}")

async def main():
    """Main test function"""
    print("ATDF Metrics Test Script")
    print("=" * 50)
    
    async with MetricsTestClient(BASE_URL) as client:
        # Test basic connectivity
        print("Testing basic connectivity...")
        health_result = await client.make_request("GET", "/health")
        
        if health_result["status"] != 200:
            print(f"❌ Health check failed: {health_result}")
            return
        
        print("✅ Application is healthy")
        
        # Test metrics endpoint
        await test_metrics_endpoint(client)
        
        # Run some sample requests
        print("\nRunning sample requests...")
        
        # Test successful operations
        hotel_result = await client.test_hotel_reservation_success()
        print(f"Hotel reservation: {hotel_result['status']}")
        
        flight_result = await client.test_flight_booking_success()
        print(f"Flight booking: {flight_result['status']}")
        
        # Test error cases
        hotel_error = await client.test_hotel_reservation_error()
        print(f"Hotel error test: {hotel_error['status']}")
        
        flight_error = await client.test_flight_booking_error()
        print(f"Flight error test: {flight_error['status']}")
        
        # Run load test
        print(f"\nRunning load test for {TEST_DURATION} seconds...")
        await run_load_test(client, TEST_DURATION)
        
        # Final metrics check
        print("\nFinal metrics check...")
        await test_metrics_endpoint(client)
        
        print("\n✅ Test completed! Check Grafana dashboard for metrics visualization.")
        print(f"Grafana URL: http://localhost:3000")
        print(f"Prometheus URL: http://localhost:9090")

if __name__ == "__main__":
    asyncio.run(main())