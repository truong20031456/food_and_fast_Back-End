#!/usr/bin/env python3
"""
Load Testing Integration for Food Fast E-commerce
Automated performance testing using Locust
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
import yaml


class LoadTestManager:
    """Manages load testing operations for all microservices"""

    def __init__(self, environment: str = "staging"):
        self.environment = environment
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "load_tests" / "results"
        self.scripts_dir = self.base_dir / "load_tests" / "scripts"
        self.config_file = self.base_dir / "load_tests" / "config.yaml"

        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load load testing configuration"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            return {
                "environments": {
                    "development": {
                        "api_gateway": "http://localhost:8000",
                        "auth_service": "http://localhost:8001",
                        "user_service": "http://localhost:8002",
                        "product_service": "http://localhost:8003",
                        "order_service": "http://localhost:8004",
                        "payment_service": "http://localhost:8005",
                        "notification_service": "http://localhost:8006",
                        "analytics_service": "http://localhost:8007",
                    },
                    "staging": {
                        "api_gateway": "https://staging-api.foodfast.com",
                        "auth_service": "https://staging-auth.foodfast.com",
                        "user_service": "https://staging-user.foodfast.com",
                        "product_service": "https://staging-product.foodfast.com",
                        "order_service": "https://staging-order.foodfast.com",
                        "payment_service": "https://staging-payment.foodfast.com",
                        "notification_service": "https://staging-notification.foodfast.com",
                        "analytics_service": "https://staging-analytics.foodfast.com",
                    },
                },
                "test_scenarios": {
                    "smoke": {"users": 5, "spawn_rate": 1, "duration": "2m"},
                    "load": {"users": 50, "spawn_rate": 5, "duration": "10m"},
                    "stress": {"users": 200, "spawn_rate": 10, "duration": "15m"},
                    "spike": {"users": 500, "spawn_rate": 50, "duration": "5m"},
                },
                "thresholds": {
                    "response_time_95": 2000,  # milliseconds
                    "response_time_avg": 500,  # milliseconds
                    "error_rate": 0.01,  # 1%
                    "rps_min": 10,  # requests per second
                },
            }

    def generate_locust_script(self, service_name: str) -> str:
        """Generate Locust script for a specific service"""

        service_scripts = {
            "api_gateway": """
from locust import HttpUser, task, between
import random
import json

class APIGatewayUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Health check on start
        self.client.get("/health")
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def metrics_endpoint(self):
        self.client.get("/metrics")
    
    @task(1)
    def docs_endpoint(self):
        self.client.get("/docs")
""",
            "auth_service": """
from locust import HttpUser, task, between
import random
import json

class AuthServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.test_user_data = {
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        # Register test user
        self.register_user()
    
    def register_user(self):
        response = self.client.post("/auth/register", json=self.test_user_data)
        if response.status_code == 201:
            self.access_token = response.json().get("access_token")
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def login(self):
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        self.client.post("/auth/login", json=login_data)
    
    @task(1)
    def verify_token(self):
        if hasattr(self, 'access_token'):
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self.client.get("/auth/verify", headers=headers)
""",
            "product_service": """
from locust import HttpUser, task, between
import random

class ProductServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(5)
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def list_products(self):
        params = {
            "page": random.randint(1, 5),
            "size": random.choice([10, 20, 50])
        }
        self.client.get("/products", params=params)
    
    @task(2)
    def search_products(self):
        search_terms = ["pizza", "burger", "salad", "pasta", "sushi"]
        params = {"q": random.choice(search_terms)}
        self.client.get("/products/search", params=params)
    
    @task(1)
    def get_product_details(self):
        product_id = random.randint(1, 100)
        self.client.get(f"/products/{product_id}")
    
    @task(1)
    def get_categories(self):
        self.client.get("/categories")
""",
            "order_service": """
from locust import HttpUser, task, between
import random
import json

class OrderServiceUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        # Simulate user authentication
        self.user_id = random.randint(1, 1000)
        self.headers = {"X-User-ID": str(self.user_id)}
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def list_orders(self):
        self.client.get("/orders", headers=self.headers)
    
    @task(1)
    def create_order(self):
        order_data = {
            "items": [
                {
                    "product_id": random.randint(1, 50),
                    "quantity": random.randint(1, 3),
                    "price": round(random.uniform(10.0, 50.0), 2)
                }
            ],
            "delivery_address": "123 Test Street, Test City"
        }
        self.client.post("/orders", json=order_data, headers=self.headers)
    
    @task(1)
    def get_order_status(self):
        order_id = random.randint(1, 100)
        self.client.get(f"/orders/{order_id}/status", headers=self.headers)
""",
        }

        script_content = service_scripts.get(
            service_name, service_scripts["api_gateway"]
        )

        script_path = self.scripts_dir / f"{service_name}_locust.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        return str(script_path)

    def run_health_check(self, service_name: str) -> bool:
        """Run health check before load testing"""
        if service_name in self.config["environments"][self.environment]:
            url = self.config["environments"][self.environment][service_name]
            health_url = f"{url}/health"

            try:
                response = requests.get(health_url, timeout=10)
                return response.status_code == 200
            except:
                return False
        return False

    def run_load_test(self, service_name: str, scenario: str = "load") -> Dict:
        """Run load test for a specific service"""

        print(f"🚀 Starting {scenario} test for {service_name}")

        # Health check first
        if not self.run_health_check(service_name):
            print(f"❌ Health check failed for {service_name}")
            return {"success": False, "error": "Health check failed"}

        # Generate Locust script
        script_path = self.generate_locust_script(service_name)

        # Get test parameters
        test_config = self.config["test_scenarios"][scenario]
        base_url = self.config["environments"][self.environment][service_name]

        # Prepare results file
        timestamp = int(time.time())
        results_file = self.results_dir / f"{service_name}_{scenario}_{timestamp}.json"

        # Build Locust command
        cmd = [
            "locust",
            "-f",
            script_path,
            "--host",
            base_url,
            "--users",
            str(test_config["users"]),
            "--spawn-rate",
            str(test_config["spawn_rate"]),
            "--run-time",
            test_config["duration"],
            "--headless",
            "--json",
            "--html",
            str(self.results_dir / f"{service_name}_{scenario}_{timestamp}.html"),
        ]

        try:
            # Run Locust
            print(f"📊 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

            # Parse results
            if result.returncode == 0:
                # Save detailed results
                results_data = {
                    "service": service_name,
                    "scenario": scenario,
                    "timestamp": timestamp,
                    "config": test_config,
                    "stdout": result.stdout,
                    "success": True,
                }

                with open(results_file, "w") as f:
                    json.dump(results_data, f, indent=2)

                print(f"✅ Load test completed for {service_name}")
                print(f"📊 Results saved to: {results_file}")

                return results_data
            else:
                print(f"❌ Load test failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            print(f"⏰ Load test timed out for {service_name}")
            return {"success": False, "error": "Test timed out"}
        except Exception as e:
            print(f"❌ Error running load test: {e}")
            return {"success": False, "error": str(e)}

    def run_full_test_suite(self, scenario: str = "load") -> Dict:
        """Run load tests for all services"""

        print(f"🎯 Running full {scenario} test suite")

        services = list(self.config["environments"][self.environment].keys())
        results = {}

        for service in services:
            print(f"\n{'=' * 50}")
            print(f"Testing {service}")
            print(f"{'=' * 50}")

            results[service] = self.run_load_test(service, scenario)

            # Wait between tests
            time.sleep(10)

        # Generate summary report
        self.generate_summary_report(results, scenario)

        return results

    def generate_summary_report(self, results: Dict, scenario: str):
        """Generate summary report for test results"""

        timestamp = int(time.time())
        report_file = self.results_dir / f"summary_{scenario}_{timestamp}.html"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Summary - {scenario.title()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .service {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background: #d4edda; border-color: #c3e6cb; }}
        .failure {{ background: #f8d7da; border-color: #f5c6cb; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Food Fast E-commerce Load Test Results</h1>
        <p>Scenario: {scenario.title()} | Environment: {self.environment.title()} | Date: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <h2>📊 Test Summary</h2>
"""

        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)

        html_content += f"""
    <div class="metric">
        <strong>Total Services:</strong> {total_count}
    </div>
    <div class="metric">
        <strong>Successful Tests:</strong> {success_count}
    </div>
    <div class="metric">
        <strong>Failed Tests:</strong> {total_count - success_count}
    </div>
    <div class="metric">
        <strong>Success Rate:</strong> {success_count / total_count * 100:.1f}%
    </div>
    
    <h2>🔍 Service Details</h2>
"""

        for service, result in results.items():
            status_class = "success" if result.get("success", False) else "failure"
            status_icon = "✅" if result.get("success", False) else "❌"

            html_content += f"""
    <div class="service {status_class}">
        <h3>{status_icon} {service.replace("_", " ").title()}</h3>
        <p><strong>Status:</strong> {"Passed" if result.get("success", False) else "Failed"}</p>
        {f"<p><strong>Error:</strong> {result.get('error', '')}</p>" if not result.get("success", False) else ""}
    </div>
"""

        html_content += """
</body>
</html>
"""

        with open(report_file, "w") as f:
            f.write(html_content)

        print(f"\n📋 Summary report generated: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Food Fast E-commerce Load Testing")
    parser.add_argument(
        "--environment",
        "-e",
        default="staging",
        choices=["development", "staging", "production"],
    )
    parser.add_argument(
        "--service", "-s", default="all", help="Service to test (default: all)"
    )
    parser.add_argument(
        "--scenario",
        "-sc",
        default="load",
        choices=["smoke", "load", "stress", "spike"],
    )
    parser.add_argument("--config", "-c", help="Custom config file path")

    args = parser.parse_args()

    load_tester = LoadTestManager(args.environment)

    if args.service == "all":
        results = load_tester.run_full_test_suite(args.scenario)
    else:
        results = load_tester.run_load_test(args.service, args.scenario)

    print("\n🎉 Load testing completed!")


if __name__ == "__main__":
    main()
