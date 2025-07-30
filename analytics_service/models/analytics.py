"""
Analytics Models - Data models for analytics service.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SalesData(BaseModel):
    """Model for sales data points."""

    date: datetime
    amount: float
    order_count: int
    customer_count: int


class ProductSalesData(BaseModel):
    """Model for product sales data."""

    product_id: str
    product_name: str
    quantity_sold: int
    revenue: float
    category: str


class CategorySalesData(BaseModel):
    """Model for category sales data."""

    category: str
    total_sales: float
    order_count: int
    product_count: int


class UserActivityData(BaseModel):
    """Model for user activity data."""

    user_id: str
    login_count: int
    last_login: datetime
    total_orders: int
    total_spent: float


class RevenueTrendData(BaseModel):
    """Model for revenue trend data."""

    period: str
    revenue: float
    growth_rate: float
    previous_period_revenue: float


class DashboardMetrics(BaseModel):
    """Model for dashboard metrics."""

    total_revenue: float
    total_orders: int
    total_customers: int
    average_order_value: float
    top_selling_products: List[ProductSalesData]
    category_sales: List[CategorySalesData]


class SalesReport(BaseModel):
    """Model for sales report."""

    report_id: str
    generated_at: datetime
    start_date: datetime
    end_date: datetime
    total_revenue: float
    total_orders: int
    daily_sales: List[SalesData]
    top_products: List[ProductSalesData]
    category_breakdown: List[CategorySalesData]


class AnalyticsEvent(BaseModel):
    """Model for analytics events."""

    event_id: str
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsConfig(BaseModel):
    """Model for analytics configuration."""

    tracking_enabled: bool = True
    data_retention_days: int = 365
    real_time_tracking: bool = True
    export_formats: List[str] = Field(default_factory=lambda: ["json", "csv", "excel"])
