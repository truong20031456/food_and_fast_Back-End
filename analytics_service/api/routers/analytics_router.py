"""
Analytics Router - Simplified function-based routes for analytics.
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
    DailySalesReportResponse,
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# Initialize services
analytics_service = AnalyticsService()
sales_report_service = SalesReportService()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data():
    """Get dashboard analytics data."""
    try:
        data = await analytics_service.get_dashboard_data()
        return DashboardResponse(**data)
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve dashboard data"
        )


@router.get("/sales/summary", response_model=SalesSummaryResponse)
async def get_sales_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
):
    """Get sales summary analytics."""
    try:
        summary = await sales_report_service.get_sales_summary(
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
    limit: int = Query(
        10, description="Number of products to return", ge=1, le=100
    ),
):
    """Get top selling products."""
    try:
        products = await analytics_service.get_top_selling_products(limit)
        return TopProductsResponse(products=products)
    except Exception as e:
        logger.error(f"Failed to get top selling products: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve top selling products"
        )


@router.get("/users/activity", response_model=UserActivityResponse)
async def get_user_activity(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    """Get user activity analytics."""
    try:
        activity = await analytics_service.get_user_activity(start_date, end_date)
        return UserActivityResponse(**activity)
    except Exception as e:
        logger.error(f"Failed to get user activity: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve user activity"
        )


@router.get("/revenue/trends", response_model=RevenueTrendsResponse)
async def get_revenue_trends(
    period: str = Query("monthly", description="Period: daily, weekly, monthly"),
    months: int = Query(12, description="Number of months", ge=1, le=24),
):
    """Get revenue trends."""
    try:
        trends = await analytics_service.get_revenue_trends(period, months)
        return RevenueTrendsResponse(**trends)
    except Exception as e:
        logger.error(f"Failed to get revenue trends: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve revenue trends"
        )


@router.get("/reports/daily-sales", response_model=DailySalesReportResponse)
async def get_daily_sales_report(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)"),
):
    """Get daily sales report."""
    try:
        report = await sales_report_service.get_daily_sales_report(date)
        return DailySalesReportResponse(**report)
    except Exception as e:
        logger.error(f"Failed to get daily sales report: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve daily sales report"
        )


@router.get("/export/sales")
async def export_sales_data(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("csv", description="Export format: csv, excel"),
):
    """Export sales data."""
    try:
        file_data = await analytics_service.export_sales_data(
            start_date, end_date, format
        )
        return {"download_url": file_data["url"], "expires_at": file_data["expires"]}
    except Exception as e:
        logger.error(f"Failed to export sales data: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to export sales data"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "analytics_service"}
