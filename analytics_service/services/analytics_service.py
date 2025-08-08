"""
Analytics Service - Core analytics functionality with Elasticsearch integration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

from utils.logger import get_logger
from services.elasticsearch_analytics_service import es_analytics_service

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and reporting with Elasticsearch integration."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.es_service = es_analytics_service

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard analytics data from Elasticsearch or fallback to mock data."""
        try:
            # Try to get real data from Elasticsearch first
            es_data = await self.es_service.get_dashboard_metrics()
            
            if es_data:
                logger.info("Retrieved dashboard data from Elasticsearch")
                return es_data
            
            # Fallback to mock data if Elasticsearch is not available
            logger.warning("Elasticsearch unavailable, using mock data")
            return {
                "total_revenue": 125000.50,
                "total_orders": 1250,
                "total_customers": 850,
                "average_order_value": 100.00,
                "today_revenue": 5432.10,
                "today_orders": 45,
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise

    async def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products from Elasticsearch or fallback to mock data."""
        try:
            # Try to get real data from Elasticsearch first
            es_data = await self.es_service.get_top_selling_products(limit)
            
            if es_data:
                logger.info("Retrieved top selling products from Elasticsearch")
                return es_data
            
            # Fallback to mock data if Elasticsearch is not available
            logger.warning("Elasticsearch unavailable, using mock data for top selling products")
            products = [
                {
                    "product_id": "1",
                    "name": "Chicken Burger",
                    "price": 12.99,
                    "category": "Burgers",
                    "sales_count": 150,
                    "total_quantity": 300,
                    "total_revenue": 1948.50,
                },
                {
                    "product_id": "2",
                    "name": "Beef Burger",
                    "price": 15.99,
                    "category": "Burgers",
                    "sales_count": 120,
                    "total_quantity": 240,
                    "total_revenue": 1918.80,
                },
                {
                    "product_id": "3",
                    "name": "French Fries",
                    "price": 5.99,
                    "category": "Sides",
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
        """Get user activity summary from Elasticsearch or fallback to mock data."""
        try:
            # Try to get real data from Elasticsearch first
            es_data = await self.es_service.get_user_activity_summary()
            
            if es_data:
                logger.info("Retrieved user activity summary from Elasticsearch")
                # Add mock data for fields not available in ES
                es_data.update({
                    "new_users_today": 25,
                    "new_users_week": 120,
                })
                return es_data
            
            # Fallback to mock data if Elasticsearch is not available
            logger.warning("Elasticsearch unavailable, using mock data for user activity")
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
        """Get revenue trends over time from Elasticsearch or fallback to mock data."""
        try:
            # Try to get real data from Elasticsearch first
            periods_count = 12 if period == "monthly" else 7 if period == "weekly" else 30
            es_data = await self.es_service.get_revenue_trends(period, periods_count)
            
            if es_data:
                logger.info(f"Retrieved {period} revenue trends from Elasticsearch")
                return es_data
            
            # Fallback to mock data if Elasticsearch is not available
            logger.warning("Elasticsearch unavailable, using mock data for revenue trends")
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
                        "timestamp": date.isoformat(),
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
        """Track analytics event to Elasticsearch."""
        try:
            # Try to index to Elasticsearch first
            event_data = {
                "event_type": event_type,
                "user_id": user_id,
                "metadata": data or {},
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            es_success = await self.es_service.client.index_document(
                self.es_service.analytics_index, event_data
            )
            
            if es_success:
                logger.info(f"Tracked event to Elasticsearch: {event_type}")
            else:
                logger.warning(f"Failed to track event to Elasticsearch: {event_type}")
            
            # Also save to traditional database if available
            # In production, implement database storage here
            
            return True

        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False

    async def index_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Index order data to Elasticsearch for analytics."""
        try:
            return await self.es_service.index_order_data(order_data)
        except Exception as e:
            logger.error(f"Failed to index order data: {e}")
            return False

    async def index_user_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Index user activity data to Elasticsearch."""
        try:
            return await self.es_service.index_user_activity(activity_data)
        except Exception as e:
            logger.error(f"Failed to index user activity: {e}")
            return False

    async def search_analytics(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        date_range: Optional[Dict[str, str]] = None,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """Search analytics data using Elasticsearch."""
        try:
            return await self.es_service.search_analytics(query, filters, date_range, size)
        except Exception as e:
            logger.error(f"Failed to search analytics: {e}")
            return []

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
