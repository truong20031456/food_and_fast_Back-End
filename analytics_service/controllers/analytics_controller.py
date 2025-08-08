"""
Analytics Controller - Handles HTTP requests for analytics endpoints.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse

from services.analytics_service import AnalyticsService
from services.sales_report import SalesReportService
from schemas.analytics import (
    DashboardResponse,
    SalesSummaryRequest,
    SalesSummaryResponse,
    TopProductsResponse,
    UserActivityResponse,
    RevenueTrendsResponse,
    DailySalesReportResponse,
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class AnalyticsController:
    """Controller for analytics endpoints."""

    def __init__(
        self,
        analytics_service: AnalyticsService,
        sales_report_service: SalesReportService,
    ):
        self.analytics_service = analytics_service
        self.sales_report_service = sales_report_service

    @router.get("/dashboard", response_model=DashboardResponse)
    async def get_dashboard_data(self):
        """Get dashboard analytics data."""
        try:
            data = await self.analytics_service.get_dashboard_data()
            return DashboardResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve dashboard data"
            )

    @router.get("/sales/summary", response_model=SalesSummaryResponse)
    async def get_sales_summary(
        self,
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        period: str = Query("daily", description="Period: daily, weekly, monthly"),
    ):
        """Get sales summary analytics."""
        try:
            summary = await self.sales_report_service.get_sales_summary(
                start_date, end_date, period
            )
            return SalesSummaryResponse(**summary)
        except Exception as e:
            logger.error(f"Failed to get sales summary: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve sales summary"
            )

    @router.get("/products/top-selling", response_model=TopProductsResponse)
    async def get_top_selling_products(
        self,
        limit: int = Query(
            10, description="Number of products to return", ge=1, le=100
        ),
    ):
        """Get top selling products."""
        try:
            products = await self.analytics_service.get_top_selling_products(limit)
            return TopProductsResponse(products=products)
        except Exception as e:
            logger.error(f"Failed to get top selling products: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve top selling products"
            )

    @router.get("/users/activity", response_model=UserActivityResponse)
    async def get_user_activity_summary(self):
        """Get user activity summary."""
        try:
            activity = await self.analytics_service.get_user_activity_summary()
            return UserActivityResponse(**activity)
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve user activity"
            )

    @router.get("/revenue/trends", response_model=RevenueTrendsResponse)
    async def get_revenue_trends(
        self,
        period: str = Query("monthly", description="Period: daily, weekly, monthly"),
    ):
        """Get revenue trends."""
        try:
            trends = await self.analytics_service.get_revenue_trends(period)
            return RevenueTrendsResponse(trends=trends)
        except Exception as e:
            logger.error(f"Failed to get revenue trends: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve revenue trends"
            )

    @router.get("/sales/daily-report")
    async def get_daily_sales_report(
        self, date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)")
    ):
        """Get detailed daily sales report."""
        try:
            report = await self.sales_report_service.get_daily_sales_report(date)
            return report
        except Exception as e:
            logger.error(f"Failed to get daily sales report: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve daily sales report"
            )

    @router.post("/events/track")
    async def track_event(
        self,
        event_data: Dict[str, Any] = Body(..., description="Event data to track")
    ):
        """Track analytics event to Elasticsearch."""
        try:
            event_type = event_data.get("event_type")
            user_id = event_data.get("user_id")
            metadata = event_data.get("data", {})

            if not event_type:
                raise HTTPException(status_code=400, detail="event_type is required")

            success = await self.analytics_service.track_event(event_type, user_id, metadata)
            
            if success:
                return {"status": "success", "message": "Event tracked successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to track event")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            raise HTTPException(status_code=500, detail="Failed to track event")

    @router.post("/orders/index")
    async def index_order_data(
        self,
        order_data: Dict[str, Any] = Body(..., description="Order data to index")
    ):
        """Index order data to Elasticsearch for analytics."""
        try:
            success = await self.analytics_service.index_order_data(order_data)
            
            if success:
                return {"status": "success", "message": "Order data indexed successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to index order data")

        except Exception as e:
            logger.error(f"Failed to index order data: {e}")
            raise HTTPException(status_code=500, detail="Failed to index order data")

    @router.post("/user-activity/index")
    async def index_user_activity(
        self,
        activity_data: Dict[str, Any] = Body(..., description="User activity data to index")
    ):
        """Index user activity data to Elasticsearch."""
        try:
            success = await self.analytics_service.index_user_activity(activity_data)
            
            if success:
                return {"status": "success", "message": "User activity indexed successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to index user activity")

        except Exception as e:
            logger.error(f"Failed to index user activity: {e}")
            raise HTTPException(status_code=500, detail="Failed to index user activity")

    @router.get("/search")
    async def search_analytics(
        self,
        query: str = Query(..., description="Search query"),
        filters: Optional[str] = Query(None, description="JSON string of filters"),
        date_start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        date_end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        size: int = Query(100, description="Number of results to return", ge=1, le=1000)
    ):
        """Search analytics data using Elasticsearch."""
        try:
            # Parse filters if provided
            parsed_filters = None
            if filters:
                import json
                try:
                    parsed_filters = json.loads(filters)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid filters JSON")

            # Build date range if provided
            date_range = None
            if date_start or date_end:
                date_range = {}
                if date_start:
                    date_range["start"] = date_start
                if date_end:
                    date_range["end"] = date_end

            results = await self.analytics_service.search_analytics(
                query, parsed_filters, date_range, size
            )
            
            return {
                "status": "success",
                "results": results,
                "total": len(results)
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to search analytics: {e}")
            raise HTTPException(status_code=500, detail="Failed to search analytics")

    @router.get("/health/elasticsearch")
    async def elasticsearch_health(self):
        """Check Elasticsearch health status."""
        try:
            from services.elasticsearch_analytics_service import es_analytics_service
            
            # Check if Elasticsearch client is connected
            is_connected = es_analytics_service.client.is_connected
            health_status = await es_analytics_service.client.health_check()
            
            return {
                "status": "healthy" if health_status else "unhealthy",
                "connected": is_connected,
                "elasticsearch": "available" if health_status else "unavailable"
            }

        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "connected": False,
                    "elasticsearch": "unavailable",
                    "error": str(e)
                }
            )
