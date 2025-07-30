"""
Analytics Controller - Handles HTTP requests for analytics endpoints.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
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
    DailySalesReportResponse
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class AnalyticsController:
    """Controller for analytics endpoints."""
    
    def __init__(self, analytics_service: AnalyticsService, sales_report_service: SalesReportService):
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
            raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")
    
    @router.get("/sales/summary", response_model=SalesSummaryResponse)
    async def get_sales_summary(
        self,
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        period: str = Query("daily", description="Period: daily, weekly, monthly")
    ):
        """Get sales summary analytics."""
        try:
            summary = await self.sales_report_service.get_sales_summary(start_date, end_date, period)
            return SalesSummaryResponse(**summary)
        except Exception as e:
            logger.error(f"Failed to get sales summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve sales summary")
    
    @router.get("/products/top-selling", response_model=TopProductsResponse)
    async def get_top_selling_products(
        self,
        limit: int = Query(10, description="Number of products to return", ge=1, le=100)
    ):
        """Get top selling products."""
        try:
            products = await self.analytics_service.get_top_selling_products(limit)
            return TopProductsResponse(products=products)
        except Exception as e:
            logger.error(f"Failed to get top selling products: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve top selling products")
    
    @router.get("/users/activity", response_model=UserActivityResponse)
    async def get_user_activity_summary(self):
        """Get user activity summary."""
        try:
            activity = await self.analytics_service.get_user_activity_summary()
            return UserActivityResponse(**activity)
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user activity")
    
    @router.get("/revenue/trends", response_model=RevenueTrendsResponse)
    async def get_revenue_trends(
        self,
        period: str = Query("monthly", description="Period: daily, weekly, monthly")
    ):
        """Get revenue trends."""
        try:
            trends = await self.analytics_service.get_revenue_trends(period)
            return RevenueTrendsResponse(trends=trends)
        except Exception as e:
            logger.error(f"Failed to get revenue trends: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve revenue trends")
    
    @router.get("/sales/daily-report")
    async def get_daily_sales_report(
        self,
        date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)")
    ):
        """Get detailed daily sales report."""
        try:
            report = await self.sales_report_service.get_daily_sales_report(date)
            return report
        except Exception as e:
            logger.error(f"Failed to get daily sales report: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve daily sales report")