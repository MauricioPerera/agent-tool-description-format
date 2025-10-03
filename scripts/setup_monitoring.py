#!/usr/bin/env python3
"""
Setup script for ATDF monitoring infrastructure.
This script helps configure and verify the monitoring setup.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests


class MonitoringSetup:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.env_file = self.project_root / ".env"

    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        print("Checking prerequisites...")

        required_tools = ["docker", "docker-compose"]
        missing_tools = []

        for tool in required_tools:
            try:
                result = subprocess.run(
                    [tool, "--version"], capture_output=True, text=True, check=True
                )
                print(f"✅ {tool}: {result.stdout.strip().split()[0]}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
                print(f"❌ {tool}: Not found")

        if missing_tools:
            print(f"\nMissing required tools: {', '.join(missing_tools)}")
            print("Please install Docker and Docker Compose before continuing.")
            return False

        return True

    def check_files(self) -> bool:
        """Check if required configuration files exist"""
        print("\nChecking configuration files...")

        required_files = [
            "docker-compose.yml",
            "Dockerfile",
            "prometheus.yml",
            "grafana/provisioning/datasources/prometheus.yml",
            "grafana/provisioning/dashboards/dashboard.yml",
            "grafana/dashboards/atdf-dashboard.json",
            "alert_rules.yml",
        ]

        missing_files = []

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"❌ {file_path}")

        if missing_files:
            print(f"\nMissing configuration files: {', '.join(missing_files)}")
            return False

        return True

    def setup_environment(self) -> bool:
        """Setup environment variables"""
        print("\nSetting up environment...")

        if not self.env_file.exists():
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                print("Copying .env.example to .env...")
                with open(env_example, "r") as src, open(self.env_file, "w") as dst:
                    dst.write(src.read())
                print("✅ Environment file created")
            else:
                print("❌ .env.example not found")
                return False
        else:
            print("✅ Environment file already exists")

        return True

    def start_services(self) -> bool:
        """Start monitoring services"""
        print("\nStarting monitoring services...")

        try:
            # Start services
            cmd = [
                "docker-compose",
                "up",
                "-d",
                "prometheus",
                "grafana",
                "postgres",
                "redis",
            ]
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, check=True
            )

            print("✅ Services started successfully")
            print("Waiting for services to be ready...")
            time.sleep(10)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
            print(f"Error output: {e.stderr}")
            return False

    def verify_services(self) -> Dict[str, bool]:
        """Verify that services are running and accessible"""
        print("\nVerifying services...")

        services = {
            "Prometheus": "http://localhost:9090/-/healthy",
            "Grafana": "http://localhost:3000/api/health",
        }

        results = {}

        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {service_name}: Running")
                    results[service_name] = True
                else:
                    print(f"❌ {service_name}: HTTP {response.status_code}")
                    results[service_name] = False
            except requests.RequestException as e:
                print(f"❌ {service_name}: Connection failed - {e}")
                results[service_name] = False

        return results

    def setup_grafana(self) -> bool:
        """Setup Grafana dashboards and datasources"""
        print("\nSetting up Grafana...")

        # Wait for Grafana to be fully ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:3000/api/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass

            if i < max_retries - 1:
                print(f"Waiting for Grafana... ({i+1}/{max_retries})")
                time.sleep(2)
        else:
            print("❌ Grafana did not become ready in time")
            return False

        print("✅ Grafana is ready")

        # Grafana should auto-provision datasources and dashboards
        # from the configuration files we created
        print("✅ Grafana auto-provisioning configured")

        return True

    def start_application(self) -> bool:
        """Start the ATDF application"""
        print("\nStarting ATDF application...")

        try:
            cmd = ["docker-compose", "up", "-d", "atdf-api"]
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, check=True
            )

            print("✅ ATDF application started")

            # Wait for application to be ready
            print("Waiting for application to be ready...")
            max_retries = 30

            for i in range(max_retries):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ ATDF application is ready")
                        return True
                except requests.RequestException:
                    pass

                if i < max_retries - 1:
                    print(f"Waiting for application... ({i+1}/{max_retries})")
                    time.sleep(2)

            print("❌ Application did not become ready in time")
            return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start application: {e}")
            return False

    def verify_metrics(self) -> bool:
        """Verify that metrics are being collected"""
        print("\nVerifying metrics collection...")

        try:
            # Check application metrics endpoint
            response = requests.get("http://localhost:8000/metrics", timeout=10)
            if response.status_code == 200:
                metrics_data = response.text

                # Check for expected metrics
                expected_metrics = [
                    "atdf_requests_total",
                    "atdf_request_duration_seconds",
                    "atdf_tool_executions_total",
                ]

                found_metrics = []
                for metric in expected_metrics:
                    if metric in metrics_data:
                        found_metrics.append(metric)

                print(f"✅ Application metrics endpoint working")
                print(
                    f"✅ Found {len(found_metrics)}/{len(expected_metrics)} expected metrics"
                )

                # Check if Prometheus can scrape metrics
                time.sleep(5)  # Wait for Prometheus to scrape

                prom_response = requests.get(
                    "http://localhost:9090/api/v1/query?query=up", timeout=10
                )
                if prom_response.status_code == 200:
                    print("✅ Prometheus is collecting metrics")
                    return True
                else:
                    print("❌ Prometheus query failed")
                    return False
            else:
                print(f"❌ Metrics endpoint returned HTTP {response.status_code}")
                return False

        except requests.RequestException as e:
            print(f"❌ Failed to verify metrics: {e}")
            return False

    def print_summary(self):
        """Print setup summary and next steps"""
        print("\n" + "=" * 60)
        print("MONITORING SETUP COMPLETE")
        print("=" * 60)
        print("\nServices URLs:")
        print("🌐 ATDF Application: http://localhost:8000")
        print("📊 Grafana Dashboard: http://localhost:3000")
        print("   - Username: admin")
        print("   - Password: admin")
        print("📈 Prometheus: http://localhost:9090")
        print("📋 Application Metrics: http://localhost:8000/metrics")
        print("🏥 Health Check: http://localhost:8000/health")

        print("\nNext Steps:")
        print("1. Open Grafana at http://localhost:3000")
        print("2. Login with admin/admin")
        print("3. Navigate to the ATDF Dashboard")
        print("4. Run the metrics test script:")
        print("   python examples/test_metrics.py")
        print("5. Watch the metrics in real-time!")

        print("\nUseful Commands:")
        print("• View logs: docker-compose logs -f atdf-api")
        print("• Stop services: docker-compose down")
        print("• Restart services: docker-compose restart")
        print("• View metrics: curl http://localhost:8000/metrics")


def main():
    """Main setup function"""
    print("ATDF Monitoring Setup")
    print("=" * 50)

    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setup = MonitoringSetup(project_root)

    # Run setup steps
    steps = [
        ("Checking prerequisites", setup.check_prerequisites),
        ("Checking configuration files", setup.check_files),
        ("Setting up environment", setup.setup_environment),
        ("Starting monitoring services", setup.start_services),
        ("Verifying services", lambda: all(setup.verify_services().values())),
        ("Setting up Grafana", setup.setup_grafana),
        ("Starting ATDF application", setup.start_application),
        ("Verifying metrics collection", setup.verify_metrics),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")

        try:
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
            else:
                print(f"✅ {step_name} completed")
        except Exception as e:
            failed_steps.append(step_name)
            print(f"❌ {step_name} failed with error: {e}")

    # Print results
    if failed_steps:
        print(f"\n❌ Setup completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease check the errors above and try again.")
        sys.exit(1)
    else:
        print(f"\n✅ All setup steps completed successfully!")
        setup.print_summary()


if __name__ == "__main__":
    main()
