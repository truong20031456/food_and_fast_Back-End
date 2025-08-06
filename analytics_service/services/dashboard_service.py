"""
Advanced Analytics Dashboard Service
Provides comprehensive analytics and visualization capabilities
"""

import json
import logging
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

from services.data_pipeline import DataPipelineService
from shared_code.utils.redis import get_redis_manager
from shared_code.utils.logging import get_logger

logger = get_logger(__name__)


class AnalyticsDashboard:
    """Advanced analytics dashboard with visualizations."""

    def __init__(self, data_pipeline: DataPipelineService, redis_manager=None):
        self.data_pipeline = data_pipeline
        self.redis = redis_manager or get_redis_manager()

    async def generate_revenue_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive revenue dashboard.

        Args:
            days: Number of days to analyze

        Returns:
            Dashboard data with charts and metrics
        """
        try:
            logger.info(f"Generating revenue dashboard for {days} days")

            # Get data from pipeline
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            events = await self.data_pipeline.collect_order_events(start_date, end_date)
            metrics = await self.data_pipeline.process_sales_metrics(events)

            if not metrics:
                return {"error": "No data available for the specified period"}

            dashboard_data = {
                "title": "Revenue Analytics Dashboard",
                "period": f"{days} days",
                "generated_at": datetime.now().isoformat(),
                "summary": metrics.get("summary", {}),
                "charts": {},
                "insights": [],
            }

            # Generate charts
            daily_metrics = metrics.get("daily_metrics", {})
            if daily_metrics:
                # Revenue trend chart
                revenue_chart = await self._create_revenue_trend_chart(daily_metrics)
                dashboard_data["charts"]["revenue_trend"] = revenue_chart

                # Order volume chart
                orders_chart = await self._create_orders_chart(daily_metrics)
                dashboard_data["charts"]["orders_volume"] = orders_chart

                # Growth metrics chart
                growth_chart = await self._create_growth_chart(daily_metrics)
                dashboard_data["charts"]["growth_metrics"] = growth_chart

            # Restaurant performance
            restaurant_metrics = metrics.get("restaurant_metrics", {})
            if restaurant_metrics:
                restaurant_chart = await self._create_restaurant_performance_chart(
                    restaurant_metrics
                )
                dashboard_data["charts"]["restaurant_performance"] = restaurant_chart

            # Customer segments
            user_segments = metrics.get("user_segments", {})
            if user_segments:
                segments_chart = await self._create_customer_segments_chart(
                    user_segments
                )
                dashboard_data["charts"]["customer_segments"] = segments_chart

            # Generate insights
            insights = await self._generate_revenue_insights(metrics)
            dashboard_data["insights"] = insights

            logger.info("Revenue dashboard generated successfully")
            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating revenue dashboard: {str(e)}")
            return {"error": str(e)}

    async def _create_revenue_trend_chart(self, daily_metrics: Dict) -> Dict[str, Any]:
        """Create revenue trend line chart."""
        try:
            dates = list(daily_metrics.keys())
            revenues = [data["total_revenue"] for data in daily_metrics.values()]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=revenues,
                    mode="lines+markers",
                    name="Daily Revenue",
                    line=dict(color="#1f77b4", width=3),
                    marker=dict(size=8),
                )
            )

            fig.update_layout(
                title="Daily Revenue Trend",
                xaxis_title="Date",
                yaxis_title="Revenue ($)",
                template="plotly_white",
                height=400,
            )

            return {
                "type": "line_chart",
                "data": fig.to_json(),
                "title": "Daily Revenue Trend",
            }

        except Exception as e:
            logger.error(f"Error creating revenue trend chart: {str(e)}")
            return {}

    async def _create_orders_chart(self, daily_metrics: Dict) -> Dict[str, Any]:
        """Create orders volume chart."""
        try:
            dates = list(daily_metrics.keys())
            orders = [data["total_orders"] for data in daily_metrics.values()]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=dates, y=orders, name="Daily Orders", marker_color="#ff7f0e")
            )

            fig.update_layout(
                title="Daily Orders Volume",
                xaxis_title="Date",
                yaxis_title="Number of Orders",
                template="plotly_white",
                height=400,
            )

            return {
                "type": "bar_chart",
                "data": fig.to_json(),
                "title": "Daily Orders Volume",
            }

        except Exception as e:
            logger.error(f"Error creating orders chart: {str(e)}")
            return {}

    async def _create_growth_chart(self, daily_metrics: Dict) -> Dict[str, Any]:
        """Create growth metrics chart."""
        try:
            dates = list(daily_metrics.keys())
            revenue_growth = [
                data.get("revenue_growth", 0) for data in daily_metrics.values()
            ]
            order_growth = [
                data.get("order_growth", 0) for data in daily_metrics.values()
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=revenue_growth,
                    mode="lines+markers",
                    name="Revenue Growth %",
                    line=dict(color="#2ca02c"),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=order_growth,
                    mode="lines+markers",
                    name="Order Growth %",
                    line=dict(color="#d62728"),
                    yaxis="y2",
                )
            )

            fig.update_layout(
                title="Growth Metrics",
                xaxis_title="Date",
                yaxis_title="Revenue Growth (%)",
                yaxis2=dict(title="Order Growth (%)", overlaying="y", side="right"),
                template="plotly_white",
                height=400,
            )

            return {
                "type": "dual_axis_chart",
                "data": fig.to_json(),
                "title": "Growth Metrics",
            }

        except Exception as e:
            logger.error(f"Error creating growth chart: {str(e)}")
            return {}

    async def _create_restaurant_performance_chart(
        self, restaurant_metrics: Dict
    ) -> Dict[str, Any]:
        """Create restaurant performance chart."""
        try:
            restaurants = list(restaurant_metrics.keys())[:10]  # Top 10
            revenues = [restaurant_metrics[r]["revenue"] for r in restaurants]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=restaurants,
                    y=revenues,
                    name="Restaurant Revenue",
                    marker_color="#9467bd",
                )
            )

            fig.update_layout(
                title="Top 10 Restaurant Performance",
                xaxis_title="Restaurant",
                yaxis_title="Revenue ($)",
                template="plotly_white",
                height=400,
                xaxis_tickangle=-45,
            )

            return {
                "type": "bar_chart",
                "data": fig.to_json(),
                "title": "Restaurant Performance",
            }

        except Exception as e:
            logger.error(f"Error creating restaurant performance chart: {str(e)}")
            return {}

    async def _create_customer_segments_chart(
        self, user_segments: Dict
    ) -> Dict[str, Any]:
        """Create customer segments pie chart."""
        try:
            labels = list(user_segments.keys())
            values = list(user_segments.values())

            fig = go.Figure()
            fig.add_trace(
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker_colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"],
                )
            )

            fig.update_layout(
                title="Customer Segments Distribution",
                template="plotly_white",
                height=400,
            )

            return {
                "type": "pie_chart",
                "data": fig.to_json(),
                "title": "Customer Segments",
            }

        except Exception as e:
            logger.error(f"Error creating customer segments chart: {str(e)}")
            return {}

    async def _generate_revenue_insights(self, metrics: Dict) -> List[Dict[str, Any]]:
        """Generate business insights from revenue data."""
        insights = []

        try:
            summary = metrics.get("summary", {})
            daily_metrics = metrics.get("daily_metrics", {})

            # Revenue insights
            total_revenue = summary.get("total_revenue", 0)
            avg_order_value = summary.get("avg_order_value", 0)

            if total_revenue > 100000:
                insights.append(
                    {
                        "type": "positive",
                        "title": "Strong Revenue Performance",
                        "message": f"Total revenue of ${total_revenue:,.2f} indicates strong business performance",
                        "priority": "high",
                    }
                )

            if avg_order_value > 50:
                insights.append(
                    {
                        "type": "positive",
                        "title": "High Average Order Value",
                        "message": f"AOV of ${avg_order_value:.2f} suggests premium customer behavior",
                        "priority": "medium",
                    }
                )

            # Growth insights
            if daily_metrics:
                recent_growth = []
                for date, data in list(daily_metrics.items())[-7:]:  # Last 7 days
                    growth = data.get("revenue_growth", 0)
                    if growth is not None and not pd.isna(growth):
                        recent_growth.append(growth)

                if recent_growth:
                    avg_growth = sum(recent_growth) / len(recent_growth)
                    if avg_growth > 5:
                        insights.append(
                            {
                                "type": "positive",
                                "title": "Strong Growth Trend",
                                "message": f"Average daily growth of {avg_growth:.1f}% over the last week",
                                "priority": "high",
                            }
                        )
                    elif avg_growth < -5:
                        insights.append(
                            {
                                "type": "warning",
                                "title": "Declining Revenue Trend",
                                "message": f"Revenue declining at {abs(avg_growth):.1f}% daily - investigate causes",
                                "priority": "critical",
                            }
                        )

            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []

    async def generate_operational_dashboard(self) -> Dict[str, Any]:
        """Generate operational metrics dashboard."""
        try:
            logger.info("Generating operational dashboard")

            dashboard_data = {
                "title": "Operational Dashboard",
                "generated_at": datetime.now().isoformat(),
                "metrics": {},
                "charts": {},
                "alerts": [],
            }

            # Get real-time metrics
            operational_metrics = await self._get_operational_metrics()
            dashboard_data["metrics"] = operational_metrics

            # Delivery performance chart
            delivery_chart = await self._create_delivery_performance_chart()
            dashboard_data["charts"]["delivery_performance"] = delivery_chart

            # Order status distribution
            status_chart = await self._create_order_status_chart()
            dashboard_data["charts"]["order_status"] = status_chart

            # System health metrics
            health_chart = await self._create_system_health_chart()
            dashboard_data["charts"]["system_health"] = health_chart

            # Generate operational alerts
            alerts = await self._generate_operational_alerts(operational_metrics)
            dashboard_data["alerts"] = alerts

            logger.info("Operational dashboard generated successfully")
            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating operational dashboard: {str(e)}")
            return {"error": str(e)}

    async def _get_operational_metrics(self) -> Dict[str, Any]:
        """Get current operational metrics."""
        try:
            # In a real system, these would come from various services
            return {
                "active_orders": 156,
                "average_delivery_time": 28.5,
                "driver_utilization": 78.2,
                "order_fulfillment_rate": 96.8,
                "customer_satisfaction": 4.3,
                "system_uptime": 99.7,
                "active_restaurants": 45,
                "peak_hour_orders": 234,
            }

        except Exception as e:
            logger.error(f"Error getting operational metrics: {str(e)}")
            return {}

    async def _create_delivery_performance_chart(self) -> Dict[str, Any]:
        """Create delivery performance chart."""
        try:
            # Mock data for demonstration
            time_ranges = ["0-15 min", "15-30 min", "30-45 min", "45-60 min", "60+ min"]
            delivery_counts = [45, 120, 85, 25, 8]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=time_ranges,
                    y=delivery_counts,
                    name="Delivery Times",
                    marker_color="#17becf",
                )
            )

            fig.update_layout(
                title="Delivery Time Distribution",
                xaxis_title="Delivery Time Range",
                yaxis_title="Number of Orders",
                template="plotly_white",
                height=400,
            )

            return {
                "type": "bar_chart",
                "data": fig.to_json(),
                "title": "Delivery Performance",
            }

        except Exception as e:
            logger.error(f"Error creating delivery performance chart: {str(e)}")
            return {}

    async def _create_order_status_chart(self) -> Dict[str, Any]:
        """Create order status distribution chart."""
        try:
            statuses = ["Pending", "Preparing", "Ready", "Delivering", "Completed"]
            counts = [23, 45, 12, 67, 189]

            fig = go.Figure()
            fig.add_trace(go.Pie(labels=statuses, values=counts, hole=0.4))

            fig.update_layout(
                title="Current Order Status Distribution",
                template="plotly_white",
                height=400,
            )

            return {"type": "pie_chart", "data": fig.to_json(), "title": "Order Status"}

        except Exception as e:
            logger.error(f"Error creating order status chart: {str(e)}")
            return {}

    async def _create_system_health_chart(self) -> Dict[str, Any]:
        """Create system health metrics chart."""
        try:
            services = [
                "API Gateway",
                "Auth Service",
                "Order Service",
                "Payment Service",
                "Notification",
            ]
            uptime = [99.9, 99.8, 98.5, 99.2, 97.8]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=services,
                    y=uptime,
                    name="Service Uptime %",
                    marker_color=[
                        "#2ca02c" if x >= 99 else "#ff7f0e" if x >= 98 else "#d62728"
                        for x in uptime
                    ],
                )
            )

            fig.update_layout(
                title="Service Health Status",
                xaxis_title="Service",
                yaxis_title="Uptime (%)",
                template="plotly_white",
                height=400,
                yaxis=dict(range=[95, 100]),
            )

            return {
                "type": "bar_chart",
                "data": fig.to_json(),
                "title": "System Health",
            }

        except Exception as e:
            logger.error(f"Error creating system health chart: {str(e)}")
            return {}

    async def _generate_operational_alerts(self, metrics: Dict) -> List[Dict[str, Any]]:
        """Generate operational alerts based on metrics."""
        alerts = []

        try:
            # Delivery time alert
            avg_delivery_time = metrics.get("average_delivery_time", 0)
            if avg_delivery_time > 35:
                alerts.append(
                    {
                        "type": "warning",
                        "title": "High Delivery Times",
                        "message": f"Average delivery time is {avg_delivery_time} minutes",
                        "action": "Check driver availability and optimize routes",
                    }
                )

            # Fulfillment rate alert
            fulfillment_rate = metrics.get("order_fulfillment_rate", 100)
            if fulfillment_rate < 95:
                alerts.append(
                    {
                        "type": "critical",
                        "title": "Low Fulfillment Rate",
                        "message": f"Order fulfillment rate is {fulfillment_rate}%",
                        "action": "Investigate order processing bottlenecks",
                    }
                )

            # System uptime alert
            uptime = metrics.get("system_uptime", 100)
            if uptime < 99:
                alerts.append(
                    {
                        "type": "warning",
                        "title": "System Uptime Issue",
                        "message": f"System uptime is {uptime}%",
                        "action": "Check service health and infrastructure",
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Error generating operational alerts: {str(e)}")
            return []

    async def export_dashboard_data(
        self, dashboard_data: Dict, format_type: str = "json"
    ) -> str:
        """
        Export dashboard data in various formats.

        Args:
            dashboard_data: Dashboard data to export
            format_type: Export format (json, csv, pdf)

        Returns:
            Exported data as string or file path
        """
        try:
            if format_type == "json":
                return json.dumps(dashboard_data, indent=2, default=str)

            elif format_type == "csv":
                # Convert summary data to CSV
                summary = dashboard_data.get("summary", {})
                df = pd.DataFrame([summary])
                return df.to_csv(index=False)

            else:
                return json.dumps(dashboard_data, default=str)

        except Exception as e:
            logger.error(f"Error exporting dashboard data: {str(e)}")
            return ""
