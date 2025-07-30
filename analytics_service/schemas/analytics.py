"""
Analytics Schemas - Pydantic models for data validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DashboardResponse(BaseModel):
    """Dashboard data response schema."""

    total_revenue: float = Field(..., description="Total revenue")
    total_orders: int = Field(..., description="Total number of orders")
    total_customers: int = Field(..., description="Total number of customers")
    average_order_value: float = Field(..., description="Average order value")
    last_updated: str = Field(..., description="Last update timestamp")


class SalesSummaryRequest(BaseModel):
    """Sales summary request schema."""

    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    period: str = Field("daily", description="Period: daily, weekly, monthly")


class SalesPeriodData(BaseModel):
    """Sales data for a specific period."""

    period: str = Field(..., description="Period identifier")
    sales: float = Field(..., description="Sales amount")
    orders: int = Field(..., description="Number of orders")


class TopProductData(BaseModel):
    """Top selling product data."""

    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    sales_count: int = Field(..., description="Number of sales")
    total_quantity: int = Field(..., description="Total quantity sold")
    total_revenue: float = Field(..., description="Total revenue from this product")


class CategorySalesData(BaseModel):
    """Sales data by category."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    orders: int = Field(..., description="Number of orders")
    total_quantity: int = Field(..., description="Total quantity sold")
    total_revenue: float = Field(..., description="Total revenue from this category")


class SalesSummaryResponse(BaseModel):
    """Sales summary response schema."""

    period: str = Field(..., description="Analysis period")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    total_sales: float = Field(..., description="Total sales amount")
    total_orders: int = Field(..., description="Total number of orders")
    average_order_value: float = Field(..., description="Average order value")
    sales_by_period: List[SalesPeriodData] = Field(
        ..., description="Sales breakdown by period"
    )
    top_products: List[TopProductData] = Field(..., description="Top selling products")
    sales_by_category: List[CategorySalesData] = Field(
        ..., description="Sales by category"
    )
    generated_at: str = Field(..., description="Report generation timestamp")


class TopProductsResponse(BaseModel):
    """Top products response schema."""

    products: List[Dict[str, Any]] = Field(
        ..., description="List of top selling products"
    )


class UserActivityResponse(BaseModel):
    """User activity response schema."""

    total_users: int = Field(..., description="Total number of users")
    active_users_today: int = Field(..., description="Active users today")
    active_users_week: int = Field(..., description="Active users this week")
    new_users_today: int = Field(..., description="New users today")


class RevenueTrendData(BaseModel):
    """Revenue trend data for a period."""

    period: str = Field(..., description="Period identifier")
    revenue: float = Field(..., description="Revenue amount")
    orders: int = Field(..., description="Number of orders")


class RevenueTrendsResponse(BaseModel):
    """Revenue trends response schema."""

    trends: List[RevenueTrendData] = Field(..., description="Revenue trends over time")


class DailySalesReportResponse(BaseModel):
    """Daily sales report response schema."""

    date: str = Field(..., description="Report date")
    total_orders: int = Field(..., description="Total orders for the day")
    total_revenue: float = Field(..., description="Total revenue for the day")
    average_order_value: float = Field(..., description="Average order value")
    unique_customers: int = Field(..., description="Number of unique customers")
    hourly_breakdown: List[Dict[str, Any]] = Field(
        ..., description="Hourly sales breakdown"
    )
    generated_at: str = Field(..., description="Report generation timestamp")
