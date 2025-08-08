"""
Elasticsearch Analytics Service - Specialized service for analytics data operations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.elasticsearch_client import es_client
from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ElasticsearchAnalyticsService:
    """Service for analytics operations using Elasticsearch."""

    def __init__(self):
        self.client = es_client
        self.analytics_index = settings.elasticsearch.analytics_index
        self.order_index = settings.elasticsearch.order_index
        self.user_activity_index = settings.elasticsearch.user_activity_index
        self.product_index = settings.elasticsearch.product_index

    async def initialize_indices(self):
        """Initialize all required indices with mappings."""
        await self._create_analytics_index()
        await self._create_order_index()
        await self._create_user_activity_index()
        await self._create_product_index()

    async def _create_analytics_index(self):
        """Create analytics index with mapping."""
        mapping = {
            "properties": {
                "timestamp": {"type": "date"},
                "event_type": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "session_id": {"type": "keyword"},
                "revenue": {"type": "double"},
                "order_count": {"type": "integer"},
                "customer_count": {"type": "integer"},
                "product_id": {"type": "keyword"},
                "category": {"type": "keyword"},
                "metadata": {"type": "object"},
            }
        }
        await self.client.create_index(self.analytics_index, mapping)

    async def _create_order_index(self):
        """Create order index with mapping."""
        mapping = {
            "properties": {
                "timestamp": {"type": "date"},
                "order_id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "total_amount": {"type": "double"},
                "currency": {"type": "keyword"},
                "status": {"type": "keyword"},
                "payment_method": {"type": "keyword"},
                "items": {
                    "type": "nested",
                    "properties": {
                        "product_id": {"type": "keyword"},
                        "product_name": {"type": "text"},
                        "quantity": {"type": "integer"},
                        "price": {"type": "double"},
                        "category": {"type": "keyword"},
                    },
                },
                "shipping_address": {"type": "object"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
        await self.client.create_index(self.order_index, mapping)

    async def _create_user_activity_index(self):
        """Create user activity index with mapping."""
        mapping = {
            "properties": {
                "timestamp": {"type": "date"},
                "user_id": {"type": "keyword"},
                "session_id": {"type": "keyword"},
                "activity_type": {"type": "keyword"},
                "page_url": {"type": "keyword"},
                "referrer": {"type": "keyword"},
                "user_agent": {"type": "text"},
                "ip_address": {"type": "ip"},
                "location": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "keyword"},
                        "city": {"type": "keyword"},
                        "coordinates": {"type": "geo_point"},
                    },
                },
                "duration_seconds": {"type": "integer"},
                "metadata": {"type": "object"},
            }
        }
        await self.client.create_index(self.user_activity_index, mapping)

    async def _create_product_index(self):
        """Create product index with mapping."""
        mapping = {
            "properties": {
                "timestamp": {"type": "date"},
                "product_id": {"type": "keyword"},
                "product_name": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "double"},
                "stock_quantity": {"type": "integer"},
                "sales_count": {"type": "integer"},
                "view_count": {"type": "integer"},
                "rating": {"type": "float"},
                "reviews_count": {"type": "integer"},
                "last_updated": {"type": "date"},
            }
        }
        await self.client.create_index(self.product_index, mapping)

    async def index_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Index order data for analytics."""
        try:
            # Ensure timestamp is present
            if "timestamp" not in order_data:
                order_data["timestamp"] = datetime.utcnow().isoformat()

            result = await self.client.index_document(
                self.order_index, order_data, order_data.get("order_id")
            )

            # Also create analytics event
            analytics_event = {
                "timestamp": order_data["timestamp"],
                "event_type": "order_placed",
                "user_id": order_data.get("user_id"),
                "revenue": order_data.get("total_amount", 0),
                "order_count": 1,
                "metadata": {
                    "order_id": order_data.get("order_id"),
                    "payment_method": order_data.get("payment_method"),
                    "items_count": len(order_data.get("items", [])),
                },
            }

            await self.client.index_document(self.analytics_index, analytics_event)
            return result

        except Exception as e:
            logger.error(f"Failed to index order data: {e}")
            return False

    async def index_user_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Index user activity data."""
        try:
            if "timestamp" not in activity_data:
                activity_data["timestamp"] = datetime.utcnow().isoformat()

            return await self.client.index_document(
                self.user_activity_index, activity_data
            )

        except Exception as e:
            logger.error(f"Failed to index user activity: {e}")
            return False

    async def index_product_data(self, product_data: Dict[str, Any]) -> bool:
        """Index or update product data."""
        try:
            if "timestamp" not in product_data:
                product_data["timestamp"] = datetime.utcnow().isoformat()

            return await self.client.index_document(
                self.product_index, product_data, product_data.get("product_id")
            )

        except Exception as e:
            logger.error(f"Failed to index product data: {e}")
            return False

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get real-time dashboard metrics from Elasticsearch."""
        try:
            # Get date range for today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_iso = today.isoformat()

            # Aggregation query for dashboard metrics
            aggs = {
                "total_revenue": {
                    "sum": {"field": "total_amount"}
                },
                "total_orders": {
                    "cardinality": {"field": "order_id"}
                },
                "total_customers": {
                    "cardinality": {"field": "user_id"}
                },
                "avg_order_value": {
                    "avg": {"field": "total_amount"}
                },
                "today_revenue": {
                    "filter": {
                        "range": {
                            "timestamp": {"gte": today_iso}
                        }
                    },
                    "aggs": {
                        "revenue": {"sum": {"field": "total_amount"}}
                    }
                },
                "today_orders": {
                    "filter": {
                        "range": {
                            "timestamp": {"gte": today_iso}
                        }
                    },
                    "aggs": {
                        "count": {"cardinality": {"field": "order_id"}}
                    }
                }
            }

            result = await self.client.aggregate(self.order_index, aggs)

            return {
                "total_revenue": result.get("total_revenue", {}).get("value", 0),
                "total_orders": result.get("total_orders", {}).get("value", 0),
                "total_customers": result.get("total_customers", {}).get("value", 0),
                "average_order_value": result.get("avg_order_value", {}).get("value", 0),
                "today_revenue": result.get("today_revenue", {}).get("revenue", {}).get("value", 0),
                "today_orders": result.get("today_orders", {}).get("count", {}).get("value", 0),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}

    async def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products from Elasticsearch."""
        try:
            # Aggregation to get top selling products
            aggs = {
                "top_products": {
                    "terms": {
                        "field": "items.product_id",
                        "size": limit
                    },
                    "aggs": {
                        "total_quantity": {
                            "sum": {"field": "items.quantity"}
                        },
                        "total_revenue": {
                            "sum": {
                                "script": {
                                    "source": "doc['items.quantity'].value * doc['items.price'].value"
                                }
                            }
                        },
                        "product_details": {
                            "top_hits": {
                                "size": 1,
                                "_source": ["items.product_name", "items.price", "items.category"]
                            }
                        }
                    }
                }
            }

            result = await self.client.aggregate(self.order_index, aggs)
            products = []

            for bucket in result.get("top_products", {}).get("buckets", []):
                product_hit = bucket["product_details"]["hits"]["hits"]
                if product_hit:
                    source = product_hit[0]["_source"]["items"]
                    products.append({
                        "product_id": bucket["key"],
                        "name": source.get("product_name", "Unknown"),
                        "price": source.get("price", 0),
                        "category": source.get("category", "Unknown"),
                        "sales_count": bucket["doc_count"],
                        "total_quantity": bucket["total_quantity"]["value"],
                        "total_revenue": bucket["total_revenue"]["value"],
                    })

            return products

        except Exception as e:
            logger.error(f"Failed to get top selling products: {e}")
            return []

    async def get_revenue_trends(self, period: str = "monthly", periods: int = 12) -> List[Dict[str, Any]]:
        """Get revenue trends over time."""
        try:
            # Determine date interval based on period
            if period == "daily":
                interval = "1d"
                date_format = "yyyy-MM-dd"
            elif period == "weekly":
                interval = "1w"
                date_format = "yyyy-'W'ww"
            else:  # monthly
                interval = "1M"
                date_format = "yyyy-MM"

            # Calculate start date
            end_date = datetime.now()
            if period == "daily":
                start_date = end_date - timedelta(days=periods)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=periods)
            else:  # monthly
                start_date = end_date - timedelta(days=30 * periods)

            aggs = {
                "revenue_over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": interval,
                        "format": date_format,
                        "min_doc_count": 0,
                        "extended_bounds": {
                            "min": start_date.isoformat(),
                            "max": end_date.isoformat()
                        }
                    },
                    "aggs": {
                        "revenue": {"sum": {"field": "total_amount"}},
                        "orders": {"cardinality": {"field": "order_id"}}
                    }
                }
            }

            query = {
                "range": {
                    "timestamp": {
                        "gte": start_date.isoformat(),
                        "lte": end_date.isoformat()
                    }
                }
            }

            result = await self.client.aggregate(self.order_index, aggs, query)
            trends = []

            for bucket in result.get("revenue_over_time", {}).get("buckets", []):
                trends.append({
                    "period": bucket["key_as_string"],
                    "revenue": bucket["revenue"]["value"],
                    "orders": bucket["orders"]["value"],
                    "timestamp": bucket["key"]
                })

            return trends

        except Exception as e:
            logger.error(f"Failed to get revenue trends: {e}")
            return []

    async def get_user_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary from Elasticsearch."""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)

            aggs = {
                "total_users": {
                    "cardinality": {"field": "user_id"}
                },
                "active_today": {
                    "filter": {
                        "range": {
                            "timestamp": {"gte": today.isoformat()}
                        }
                    },
                    "aggs": {
                        "users": {"cardinality": {"field": "user_id"}}
                    }
                },
                "active_week": {
                    "filter": {
                        "range": {
                            "timestamp": {"gte": week_ago.isoformat()}
                        }
                    },
                    "aggs": {
                        "users": {"cardinality": {"field": "user_id"}}
                    }
                }
            }

            result = await self.client.aggregate(self.user_activity_index, aggs)

            return {
                "total_users": result.get("total_users", {}).get("value", 0),
                "active_users_today": result.get("active_today", {}).get("users", {}).get("value", 0),
                "active_users_week": result.get("active_week", {}).get("users", {}).get("value", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get user activity summary: {e}")
            return {}

    async def search_analytics(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        date_range: Optional[Dict[str, str]] = None,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """Search analytics data with filters."""
        try:
            # Build search query
            search_query = {"match_all": {}}
            
            if query:
                search_query = {
                    "multi_match": {
                        "query": query,
                        "fields": ["event_type", "metadata.*"]
                    }
                }

            # Add filters
            filter_conditions = []
            
            if filters:
                for field, value in filters.items():
                    filter_conditions.append({"term": {field: value}})

            if date_range:
                range_filter = {"range": {"timestamp": {}}}
                if date_range.get("start"):
                    range_filter["range"]["timestamp"]["gte"] = date_range["start"]
                if date_range.get("end"):
                    range_filter["range"]["timestamp"]["lte"] = date_range["end"]
                filter_conditions.append(range_filter)

            if filter_conditions:
                search_query = {
                    "bool": {
                        "must": [search_query],
                        "filter": filter_conditions
                    }
                }

            result = await self.client.search(
                self.analytics_index,
                search_query,
                size=size,
                sort=[{"timestamp": {"order": "desc"}}]
            )

            return [hit["_source"] for hit in result["hits"]["hits"]]

        except Exception as e:
            logger.error(f"Failed to search analytics: {e}")
            return []


# Global Elasticsearch analytics service instance
es_analytics_service = ElasticsearchAnalyticsService()
