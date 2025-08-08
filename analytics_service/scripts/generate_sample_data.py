"""
Sample Data Generator for Analytics Service with Elasticsearch.
This script generates sample analytics data for testing purposes.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.elasticsearch_client import es_client
from services.elasticsearch_analytics_service import es_analytics_service
from utils.logger import get_logger

logger = get_logger(__name__)


class SampleDataGenerator:
    """Generates sample data for analytics testing."""

    def __init__(self):
        self.client = es_client
        self.service = es_analytics_service

    async def generate_sample_orders(self, count: int = 1000) -> List[Dict[str, Any]]:
        """Generate sample order data."""
        orders = []
        start_date = datetime.now() - timedelta(days=90)

        products = [
            {"id": "1", "name": "Chicken Burger", "price": 12.99, "category": "Burgers"},
            {"id": "2", "name": "Beef Burger", "price": 15.99, "category": "Burgers"},
            {"id": "3", "name": "French Fries", "price": 5.99, "category": "Sides"},
            {"id": "4", "name": "Onion Rings", "price": 6.99, "category": "Sides"},
            {"id": "5", "name": "Coca Cola", "price": 2.99, "category": "Beverages"},
            {"id": "6", "name": "Orange Juice", "price": 3.99, "category": "Beverages"},
            {"id": "7", "name": "Fish Burger", "price": 13.99, "category": "Burgers"},
            {"id": "8", "name": "Chicken Wings", "price": 8.99, "category": "Sides"},
            {"id": "9", "name": "Milkshake", "price": 4.99, "category": "Beverages"},
            {"id": "10", "name": "Caesar Salad", "price": 9.99, "category": "Salads"},
        ]

        payment_methods = ["credit_card", "debit_card", "paypal", "cash", "mobile_pay"]
        statuses = ["completed", "pending", "cancelled", "refunded"]

        for i in range(count):
            # Random timestamp within last 90 days
            days_ago = random.randint(0, 90)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            order_date = start_date + timedelta(
                days=days_ago, hours=hours_ago, minutes=minutes_ago
            )

            # Random number of items (1-5)
            num_items = random.randint(1, 5)
            items = []
            total_amount = 0

            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                item_price = product["price"] * quantity

                items.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "price": product["price"],
                    "category": product["category"],
                })
                total_amount += item_price

            order = {
                "order_id": f"order_{i+1:06d}",
                "user_id": f"user_{random.randint(1, 500):06d}",
                "total_amount": round(total_amount, 2),
                "currency": "USD",
                "status": random.choice(statuses),
                "payment_method": random.choice(payment_methods),
                "items": items,
                "shipping_address": {
                    "street": f"{random.randint(1, 999)} Sample St",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zip_code": f"{random.randint(10000, 99999)}",
                },
                "timestamp": order_date.isoformat(),
                "created_at": order_date.isoformat(),
                "updated_at": order_date.isoformat(),
            }
            orders.append(order)

        return orders

    async def generate_sample_user_activity(self, count: int = 5000) -> List[Dict[str, Any]]:
        """Generate sample user activity data."""
        activities = []
        start_date = datetime.now() - timedelta(days=30)

        activity_types = [
            "page_view", "product_view", "add_to_cart", "remove_from_cart",
            "checkout_start", "checkout_complete", "search", "login", "logout"
        ]

        pages = [
            "/", "/products", "/cart", "/checkout", "/profile", "/orders",
            "/products/burgers", "/products/sides", "/products/beverages"
        ]

        referrers = [
            "https://google.com", "https://facebook.com", "https://instagram.com",
            "direct", "https://twitter.com", "https://bing.com"
        ]

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
        ]

        cities = [
            {"name": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
            {"name": "Los Angeles", "country": "USA", "lat": 34.0522, "lon": -118.2437},
            {"name": "Chicago", "country": "USA", "lat": 41.8781, "lon": -87.6298},
            {"name": "Houston", "country": "USA", "lat": 29.7604, "lon": -95.3698},
            {"name": "Phoenix", "country": "USA", "lat": 33.4484, "lon": -112.0740},
        ]

        for i in range(count):
            # Random timestamp within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            activity_date = start_date + timedelta(
                days=days_ago, hours=hours_ago, minutes=minutes_ago
            )

            city = random.choice(cities)
            
            activity = {
                "user_id": f"user_{random.randint(1, 500):06d}",
                "session_id": f"session_{random.randint(1, 10000):08d}",
                "activity_type": random.choice(activity_types),
                "page_url": random.choice(pages),
                "referrer": random.choice(referrers),
                "user_agent": random.choice(user_agents),
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "location": {
                    "country": city["country"],
                    "city": city["name"],
                    "coordinates": [city["lon"], city["lat"]],
                },
                "duration_seconds": random.randint(10, 600),
                "timestamp": activity_date.isoformat(),
                "metadata": {
                    "screen_resolution": f"{random.choice([1920, 1366, 1440, 1536])}x{random.choice([1080, 768, 900, 864])}",
                    "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                    "os": random.choice(["Windows", "macOS", "iOS", "Android"]),
                },
            }
            activities.append(activity)

        return activities

    async def generate_sample_products(self) -> List[Dict[str, Any]]:
        """Generate sample product data."""
        products = [
            {
                "product_id": "1",
                "product_name": "Chicken Burger",
                "category": "Burgers",
                "price": 12.99,
                "stock_quantity": 100,
                "sales_count": random.randint(100, 500),
                "view_count": random.randint(1000, 5000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(10, 100),
            },
            {
                "product_id": "2",
                "product_name": "Beef Burger",
                "category": "Burgers",
                "price": 15.99,
                "stock_quantity": 80,
                "sales_count": random.randint(80, 400),
                "view_count": random.randint(800, 4000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(8, 80),
            },
            {
                "product_id": "3",
                "product_name": "French Fries",
                "category": "Sides",
                "price": 5.99,
                "stock_quantity": 200,
                "sales_count": random.randint(200, 800),
                "view_count": random.randint(2000, 8000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(20, 120),
            },
            {
                "product_id": "4",
                "product_name": "Onion Rings",
                "category": "Sides",
                "price": 6.99,
                "stock_quantity": 150,
                "sales_count": random.randint(150, 600),
                "view_count": random.randint(1500, 6000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(15, 90),
            },
            {
                "product_id": "5",
                "product_name": "Coca Cola",
                "category": "Beverages",
                "price": 2.99,
                "stock_quantity": 300,
                "sales_count": random.randint(300, 1000),
                "view_count": random.randint(3000, 10000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(30, 150),
            },
        ]

        for product in products:
            product["timestamp"] = datetime.utcnow().isoformat()
            product["last_updated"] = datetime.utcnow().isoformat()

        return products

    async def initialize_sample_data(self):
        """Initialize Elasticsearch with sample data."""
        try:
            logger.info("Starting sample data generation...")

            # Connect to Elasticsearch
            await self.client.connect()
            
            # Initialize indices
            await self.service.initialize_indices()
            logger.info("Elasticsearch indices initialized")

            # Generate and index orders
            logger.info("Generating sample orders...")
            orders = await self.generate_sample_orders(1000)
            
            logger.info(f"Indexing {len(orders)} orders...")
            success = await self.client.bulk_index(self.service.order_index, orders)
            if success:
                logger.info("Sample orders indexed successfully")
            else:
                logger.error("Failed to index sample orders")

            # Generate and index user activities
            logger.info("Generating sample user activities...")
            activities = await self.generate_sample_user_activity(5000)
            
            logger.info(f"Indexing {len(activities)} user activities...")
            success = await self.client.bulk_index(self.service.user_activity_index, activities)
            if success:
                logger.info("Sample user activities indexed successfully")
            else:
                logger.error("Failed to index sample user activities")

            # Generate and index products
            logger.info("Generating sample products...")
            products = await self.generate_sample_products()
            
            logger.info(f"Indexing {len(products)} products...")
            success = await self.client.bulk_index(self.service.product_index, products)
            if success:
                logger.info("Sample products indexed successfully")
            else:
                logger.error("Failed to index sample products")

            # Generate analytics events
            logger.info("Generating sample analytics events...")
            analytics_events = []
            for order in orders[:100]:  # Generate events for first 100 orders
                event = {
                    "event_type": "order_placed",
                    "user_id": order["user_id"],
                    "revenue": order["total_amount"],
                    "order_count": 1,
                    "metadata": {
                        "order_id": order["order_id"],
                        "payment_method": order["payment_method"],
                        "items_count": len(order["items"]),
                    },
                    "timestamp": order["timestamp"],
                }
                analytics_events.append(event)

            success = await self.client.bulk_index(self.service.analytics_index, analytics_events)
            if success:
                logger.info("Sample analytics events indexed successfully")
            else:
                logger.error("Failed to index sample analytics events")

            logger.info("Sample data generation completed successfully!")

        except Exception as e:
            logger.error(f"Failed to initialize sample data: {e}")
            raise
        finally:
            if self.client.is_connected:
                await self.client.disconnect()


async def main():
    """Main function to run sample data generation."""
    generator = SampleDataGenerator()
    await generator.initialize_sample_data()


if __name__ == "__main__":
    asyncio.run(main())
