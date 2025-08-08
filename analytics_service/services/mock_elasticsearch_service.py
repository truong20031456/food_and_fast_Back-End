"""
Mock Elasticsearch Service for Demo Purposes
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class MockElasticsearchService:
    """Mock Elasticsearch service for demo when cloud connection not available."""
    
    def __init__(self):
        self.is_connected = False
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, List[Dict]]:
        """Generate mock analytics data for demonstration."""
        base_date = datetime.now() - timedelta(days=30)
        
        # Mock orders data
        orders = []
        for i in range(100):
            order_date = base_date + timedelta(days=i % 30, hours=i % 24)
            orders.append({
                "order_id": f"ORD-{1000 + i}",
                "user_id": f"USER-{100 + (i % 20)}",
                "total_amount": round(50 + (i % 200), 2),
                "status": ["pending", "completed", "cancelled"][i % 3],
                "created_at": order_date.isoformat(),
                "products": [
                    {
                        "product_id": f"PROD-{200 + (i % 50)}",
                        "name": f"Product {(i % 50) + 1}",
                        "price": round(10 + (i % 50), 2),
                        "quantity": 1 + (i % 3)
                    }
                ]
            })
        
        # Mock user activity data
        activities = []
        for i in range(200):
            activity_date = base_date + timedelta(days=i % 30, hours=i % 24, minutes=i % 60)
            activities.append({
                "user_id": f"USER-{100 + (i % 20)}",
                "action": ["view", "add_to_cart", "purchase", "search"][i % 4],
                "product_id": f"PROD-{200 + (i % 50)}",
                "timestamp": activity_date.isoformat(),
                "session_id": f"SESSION-{i // 10}",
                "page": f"/product/{200 + (i % 50)}"
            })
        
        return {
            "orders": orders,
            "user_activities": activities
        }
    
    async def connect(self):
        """Mock connection."""
        logger.info("🚀 Using Mock Elasticsearch Service (Demo Mode)")
        self.is_connected = True
        return True
    
    async def disconnect(self):
        """Mock disconnection."""
        self.is_connected = False
        logger.info("📴 Disconnected from Mock Elasticsearch Service")
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return self.is_connected
    
    async def get_dashboard_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get dashboard metrics from mock data."""
        logger.info(f"📊 Getting dashboard metrics (Mock): {start_date} to {end_date}")
        
        # Filter orders by date range
        orders = [
            order for order in self.mock_data["orders"]
            if start_date <= datetime.fromisoformat(order["created_at"]) <= end_date
        ]
        
        total_revenue = sum(order["total_amount"] for order in orders)
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o["status"] == "completed"])
        unique_customers = len(set(order["user_id"] for order in orders))
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "conversion_rate": round((completed_orders / total_orders * 100) if total_orders > 0 else 0, 2),
            "unique_customers": unique_customers,
            "average_order_value": round(total_revenue / total_orders if total_orders > 0 else 0, 2),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_top_selling_products(self, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get top selling products from mock data."""
        logger.info(f"🏆 Getting top {limit} selling products (Mock)")
        
        # Count product sales
        product_sales = {}
        for order in self.mock_data["orders"]:
            order_date = datetime.fromisoformat(order["created_at"])
            if start_date and order_date < start_date:
                continue
            if end_date and order_date > end_date:
                continue
                
            for product in order["products"]:
                product_id = product["product_id"]
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        "product_id": product_id,
                        "name": product["name"],
                        "total_quantity": 0,
                        "total_revenue": 0
                    }
                
                product_sales[product_id]["total_quantity"] += product["quantity"]
                product_sales[product_id]["total_revenue"] += product["price"] * product["quantity"]
        
        # Sort by total quantity and take top N
        top_products = sorted(
            product_sales.values(),
            key=lambda x: x["total_quantity"],
            reverse=True
        )[:limit]
        
        return top_products
    
    async def get_revenue_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get revenue trends from mock data."""
        logger.info(f"📈 Getting revenue trends for last {days} days (Mock)")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Group orders by date
        daily_revenue = {}
        for order in self.mock_data["orders"]:
            order_date = datetime.fromisoformat(order["created_at"])
            if start_date <= order_date <= end_date:
                date_key = order_date.strftime("%Y-%m-%d")
                if date_key not in daily_revenue:
                    daily_revenue[date_key] = {
                        "date": date_key,
                        "revenue": 0,
                        "orders": 0
                    }
                
                daily_revenue[date_key]["revenue"] += order["total_amount"]
                daily_revenue[date_key]["orders"] += 1
        
        # Fill missing dates with zero
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            if date_key not in daily_revenue:
                daily_revenue[date_key] = {
                    "date": date_key,
                    "revenue": 0,
                    "orders": 0
                }
            current_date += timedelta(days=1)
        
        # Sort by date
        trends = sorted(daily_revenue.values(), key=lambda x: x["date"])
        return trends
    
    async def get_user_activity_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user activity statistics from mock data."""
        logger.info(f"👥 Getting user activity stats (Mock): {start_date} to {end_date}")
        
        # Filter activities by date range
        activities = [
            activity for activity in self.mock_data["user_activities"]
            if start_date <= datetime.fromisoformat(activity["timestamp"]) <= end_date
        ]
        
        # Count actions
        action_counts = {}
        unique_users = set()
        unique_sessions = set()
        
        for activity in activities:
            action = activity["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
            unique_users.add(activity["user_id"])
            unique_sessions.add(activity["session_id"])
        
        return {
            "total_activities": len(activities),
            "unique_users": len(unique_users),
            "unique_sessions": len(unique_sessions),
            "action_breakdown": action_counts,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

# Global mock service instance
mock_elasticsearch_service = MockElasticsearchService()
