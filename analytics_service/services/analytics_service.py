"""
Analytics Service - Core analytics functionality.
"""

import logging
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

# Add shared_code to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_code'))

from utils.logger import get_logger
from shared_code.cache import get_cache_service

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and reporting."""

    def __init__(self, db_manager, cache_service=None):
        self.db_manager = db_manager
        self.cache_service = cache_service or get_cache_service('analytics')

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard analytics data with caching."""
        try:
            # Try to get from cache first
            if self.cache_service:
                cached_data = await self.cache_service.get_dashboard_data()
                if cached_data:
                    logger.info("Dashboard data retrieved from cache")
                    return cached_data
            
            # Generate/fetch dashboard data
            dashboard_data = {
                "total_revenue": 125000.50,
                "total_orders": 1250,
                "total_customers": 850,
                "average_order_value": 100.00,
                "growth_rate": 12.5,
                "orders_today": 45,
                "revenue_today": 4500.00,
                "last_updated": datetime.utcnow().isoformat(),
            }
            
            # Cache the result
            if self.cache_service:
                await self.cache_service.set_dashboard_data(dashboard_data)
                logger.info("Dashboard data cached successfully")
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise

    async def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products with caching."""
        try:
            # Try to get from cache first
            if self.cache_service:
                cached_products = await self.cache_service.get_top_products(limit=limit)
                if cached_products:
                    logger.info("Top products retrieved from cache")
                    return cached_products
            
            # Generate/fetch top products data
            products = [
                {
                    "id": 1,
                    "name": "Chicken Burger",
                    "price": 12.99,
                    "sales_count": 150,
                    "total_quantity": 300,
                    "total_revenue": 1948.50,
                },
                {
                    "id": 2,
                    "name": "Beef Burger",
                    "price": 15.99,
                    "sales_count": 120,
                    "total_quantity": 240,
                    "total_revenue": 1918.80,
                },
                {
                    "id": 3,
                    "name": "French Fries",
                    "price": 5.99,
                    "sales_count": 200,
                    "total_quantity": 400,
                    "total_revenue": 1198.00,
                },
            ]

            return products[:limit]

        except Exception as e:
            logger.error(f"Failed to get top selling products: {e}")
            return []

    async def get_user_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary."""
        try:
            # Mock data - in production, fetch from database
            return {
                "total_users": 1000,
                "active_users_today": 150,
                "active_users_week": 450,
                "new_users_today": 25,
                "new_users_week": 120,
            }
        except Exception as e:
            logger.error(f"Failed to get user activity summary: {e}")
            raise

    async def get_revenue_trends(self, period: str = "monthly") -> List[Dict[str, Any]]:
        """Get revenue trends over time."""
        try:
            # Mock data - in production, fetch from database
            trends = []
            current_date = datetime.now()

            for i in range(12):
                if period == "monthly":
                    date = current_date - timedelta(days=30 * i)
                    period_label = date.strftime("%B %Y")
                elif period == "weekly":
                    date = current_date - timedelta(weeks=i)
                    period_label = f"Week {date.isocalendar()[1]}"
                else:  # daily
                    date = current_date - timedelta(days=i)
                    period_label = date.strftime("%Y-%m-%d")

                revenue = random.uniform(8000, 15000)
                orders = random.randint(80, 150)

                trends.append(
                    {
                        "period": period_label,
                        "revenue": round(revenue, 2),
                        "orders": orders,
                    }
                )

            return trends[::-1]  # Reverse to show oldest first

        except Exception as e:
            logger.error(f"Failed to get revenue trends: {e}")
            return []

    async def track_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        data: Dict[str, Any] = None,
    ) -> bool:
        """Track analytics event."""
        try:
            # In production, save to database
            event_data = {
                "event_type": event_type,
                "user_id": user_id,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Tracked event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False

    async def get_sales_by_category(
        self, start_date: str = None, end_date: str = None
    ) -> List[Dict[str, Any]]:
        """Get sales breakdown by category."""
        try:
            # Mock data - in production, fetch from database
            categories = [
                {
                    "id": 1,
                    "name": "Burgers",
                    "orders": 450,
                    "total_quantity": 900,
                    "total_revenue": 6750.00,
                },
                {
                    "id": 2,
                    "name": "Sides",
                    "orders": 300,
                    "total_quantity": 600,
                    "total_revenue": 1800.00,
                },
                {
                    "id": 3,
                    "name": "Beverages",
                    "orders": 250,
                    "total_quantity": 500,
                    "total_revenue": 1250.00,
                },
            ]

            return categories

        except Exception as e:
            logger.error(f"Failed to get sales by category: {e}")
            return []
