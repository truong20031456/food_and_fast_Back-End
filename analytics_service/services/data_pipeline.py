"""
Data Pipeline Service for Analytics
Handles data collection, processing, and aggregation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from core.database import get_db_session
from models.analytics import AnalyticsEvent, SalesMetric, UserMetric
from utils.logger import get_logger

logger = get_logger(__name__)


class DataPipelineService:
    """Service for processing analytics data pipelines."""

    def __init__(self, db_session, redis_manager=None):
        self.db = db_session
        self.redis = redis_manager

    async def collect_order_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Collect order events from the database.

        Args:
            start_date: Start date for data collection
            end_date: End date for data collection

        Returns:
            List of order events
        """
        try:
            # In a real implementation, this would query the order service
            # For now, we'll simulate data collection

            logger.info(f"Collecting order events from {start_date} to {end_date}")

            # Simulate order data
            order_events = []
            current_date = start_date

            while current_date <= end_date:
                # Generate mock order events for each day
                daily_orders = np.random.poisson(50)  # Average 50 orders per day

                for _ in range(daily_orders):
                    event = {
                        "event_type": "order_completed",
                        "timestamp": current_date
                        + timedelta(
                            hours=np.random.randint(0, 24),
                            minutes=np.random.randint(0, 60),
                        ),
                        "order_id": f"order_{np.random.randint(10000, 99999)}",
                        "user_id": f"user_{np.random.randint(1, 1000)}",
                        "total_amount": round(np.random.uniform(15.0, 150.0), 2),
                        "items_count": np.random.randint(1, 8),
                        "restaurant_id": f"restaurant_{np.random.randint(1, 50)}",
                        "delivery_time": np.random.randint(20, 60),  # minutes
                    }
                    order_events.append(event)

                current_date += timedelta(days=1)

            logger.info(f"Collected {len(order_events)} order events")
            return order_events

        except Exception as e:
            logger.error(f"Error collecting order events: {str(e)}")
            return []

    async def process_sales_metrics(self, events: List[Dict]) -> Dict[str, Any]:
        """
        Process sales metrics from order events.

        Args:
            events: List of order events

        Returns:
            Processed sales metrics
        """
        try:
            if not events:
                return {}

            logger.info("Processing sales metrics...")

            # Convert to DataFrame for easier processing
            df = pd.DataFrame(events)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date

            # Calculate daily metrics
            daily_metrics = (
                df.groupby("date")
                .agg(
                    {
                        "total_amount": ["sum", "mean", "count"],
                        "items_count": "sum",
                        "delivery_time": "mean",
                    }
                )
                .round(2)
            )

            # Flatten column names
            daily_metrics.columns = [
                "total_revenue",
                "avg_order_value",
                "total_orders",
                "total_items",
                "avg_delivery_time",
            ]

            # Calculate growth rates
            daily_metrics["revenue_growth"] = (
                daily_metrics["total_revenue"].pct_change() * 100
            )
            daily_metrics["order_growth"] = (
                daily_metrics["total_orders"].pct_change() * 100
            )

            # Restaurant performance
            restaurant_metrics = (
                df.groupby("restaurant_id")
                .agg({"total_amount": ["sum", "count"], "delivery_time": "mean"})
                .round(2)
            )

            restaurant_metrics.columns = ["revenue", "orders", "avg_delivery_time"]
            restaurant_metrics = restaurant_metrics.sort_values(
                "revenue", ascending=False
            )

            # User behavior metrics
            user_metrics = (
                df.groupby("user_id")
                .agg({"total_amount": ["sum", "count"], "items_count": "mean"})
                .round(2)
            )

            user_metrics.columns = ["total_spent", "order_count", "avg_items_per_order"]

            # Calculate customer segments
            user_metrics["customer_segment"] = pd.cut(
                user_metrics["total_spent"],
                bins=[0, 50, 200, 500, float("inf")],
                labels=["Low Value", "Medium Value", "High Value", "VIP"],
            )

            segment_distribution = (
                user_metrics["customer_segment"].value_counts().to_dict()
            )

            metrics = {
                "daily_metrics": daily_metrics.to_dict("index"),
                "restaurant_metrics": restaurant_metrics.head(10).to_dict("index"),
                "user_segments": segment_distribution,
                "summary": {
                    "total_revenue": df["total_amount"].sum(),
                    "total_orders": len(df),
                    "avg_order_value": df["total_amount"].mean(),
                    "avg_delivery_time": df["delivery_time"].mean(),
                    "unique_customers": df["user_id"].nunique(),
                    "unique_restaurants": df["restaurant_id"].nunique(),
                },
            }

            logger.info("Sales metrics processed successfully")
            return metrics

        except Exception as e:
            logger.error(f"Error processing sales metrics: {str(e)}")
            return {}

    async def store_metrics(self, metrics: Dict[str, Any], metric_type: str = "sales"):
        """
        Store processed metrics in database and cache.

        Args:
            metrics: Processed metrics data
            metric_type: Type of metrics (sales, user, etc.)
        """
        try:
            # Store in database
            if metric_type == "sales" and "summary" in metrics:
                summary = metrics["summary"]

                sales_metric = SalesMetric(
                    date=datetime.now().date(),
                    total_revenue=summary["total_revenue"],
                    total_orders=summary["total_orders"],
                    avg_order_value=summary["avg_order_value"],
                    unique_customers=summary["unique_customers"],
                    avg_delivery_time=summary["avg_delivery_time"],
                )

                self.db.add(sales_metric)
                await self.db.commit()

                logger.info("Sales metrics stored in database")

            # Cache in Redis for quick access
            if self.redis:
                cache_key = (
                    f"analytics:{metric_type}:{datetime.now().strftime('%Y-%m-%d')}"
                )
                await self.redis.setex(
                    cache_key, 3600, str(metrics)
                )  # Cache for 1 hour
                logger.info(f"Metrics cached with key: {cache_key}")

        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")

    async def generate_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate business insights from metrics.

        Args:
            metrics: Processed metrics data

        Returns:
            Business insights and recommendations
        """
        try:
            insights = {"insights": [], "recommendations": [], "alerts": []}

            if "summary" in metrics:
                summary = metrics["summary"]

                # Revenue insights
                if summary["avg_order_value"] > 75:
                    insights["insights"].append(
                        "High average order value indicates premium customer behavior"
                    )
                    insights["recommendations"].append(
                        "Consider upselling premium items"
                    )

                # Delivery time insights
                if summary["avg_delivery_time"] > 45:
                    insights["alerts"].append(
                        "Average delivery time exceeds target (45 minutes)"
                    )
                    insights["recommendations"].append(
                        "Optimize delivery routes and restaurant partnerships"
                    )

                # Customer insights
                if "user_segments" in metrics:
                    segments = metrics["user_segments"]
                    high_value_ratio = (
                        segments.get("High Value", 0) + segments.get("VIP", 0)
                    ) / sum(segments.values())

                    if high_value_ratio > 0.3:
                        insights["insights"].append(
                            "Strong high-value customer base (30%+)"
                        )
                        insights["recommendations"].append(
                            "Implement loyalty program to retain VIP customers"
                        )

                # Restaurant performance insights
                if "restaurant_metrics" in metrics:
                    restaurant_data = metrics["restaurant_metrics"]
                    if len(restaurant_data) > 0:
                        top_restaurant = list(restaurant_data.keys())[0]
                        insights["insights"].append(
                            f"Top performing restaurant: {top_restaurant}"
                        )

            logger.info("Business insights generated successfully")
            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {"insights": [], "recommendations": [], "alerts": []}

    async def run_daily_pipeline(self):
        """
        Run the complete daily analytics pipeline.
        This should be scheduled to run daily.
        """
        try:
            logger.info("Starting daily analytics pipeline...")

            # Define date range (yesterday)
            end_date = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            ) - timedelta(days=1)
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

            # Step 1: Collect data
            events = await self.collect_order_events(start_date, end_date)

            if not events:
                logger.warning("No events collected for processing")
                return

            # Step 2: Process metrics
            metrics = await self.process_sales_metrics(events)

            # Step 3: Store metrics
            await self.store_metrics(metrics, "sales")

            # Step 4: Generate insights
            insights = await self.generate_insights(metrics)
            await self.store_metrics(insights, "insights")

            logger.info("Daily analytics pipeline completed successfully")

        except Exception as e:
            logger.error(f"Error in daily pipeline: {str(e)}")

    async def run_real_time_pipeline(self, event_data: Dict[str, Any]):
        """
        Process real-time events as they come in.

        Args:
            event_data: Real-time event data
        """
        try:
            logger.info(f"Processing real-time event: {event_data.get('event_type')}")

            # Store event
            analytics_event = AnalyticsEvent(
                event_type=event_data.get("event_type"),
                timestamp=datetime.now(),
                data=event_data,
            )

            self.db.add(analytics_event)
            await self.db.commit()

            # Update real-time metrics in cache
            if self.redis:
                cache_key = f"realtime:events:{datetime.now().strftime('%Y-%m-%d-%H')}"
                await self.redis.incr(cache_key)
                await self.redis.expire(cache_key, 86400)  # Expire after 24 hours

            logger.info("Real-time event processed successfully")

        except Exception as e:
            logger.error(f"Error processing real-time event: {str(e)}")


# Scheduled task function
async def run_scheduled_analytics():
    """Function to be called by scheduler for daily analytics."""
    try:
        # This would typically be called by a scheduler like Celery or APScheduler
        db_session = get_db_session()
        pipeline = DataPipelineService(db_session)
        await pipeline.run_daily_pipeline()

    except Exception as e:
        logger.error(f"Error in scheduled analytics: {str(e)}")
    finally:
        if db_session:
            await db_session.close()
