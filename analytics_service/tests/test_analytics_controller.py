"""
Tests for Analytics Controller.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestAnalyticsController:
    """Test cases for analytics controller endpoints."""
    
    def test_get_dashboard_data(self, client: TestClient):
        """Test dashboard data endpoint."""
        with patch('controllers.analytics_controller.AnalyticsService') as mock_service:
            mock_service.return_value.get_dashboard_data.return_value = {
                "total_revenue": 10000.0,
                "total_orders": 100,
                "total_customers": 50,
                "average_order_value": 100.0,
                "top_selling_products": [],
                "category_sales": []
            }
            
            response = client.get("/api/v1/analytics/dashboard")
            assert response.status_code == 200
            data = response.json()
            assert "total_revenue" in data
            assert "total_orders" in data
    
    def test_get_sales_summary(self, client: TestClient):
        """Test sales summary endpoint."""
        with patch('controllers.analytics_controller.AnalyticsService') as mock_service:
            mock_service.return_value.get_sales_summary.return_value = {
                "period": "daily",
                "data": [
                    {
                        "date": "2024-01-01",
                        "revenue": 1000.0,
                        "orders": 10,
                        "customers": 8
                    }
                ]
            }
            
            response = client.get("/api/v1/analytics/sales/summary?period=daily")
            assert response.status_code == 200
            data = response.json()
            assert "period" in data
            assert "data" in data
    
    def test_get_top_selling_products(self, client: TestClient):
        """Test top selling products endpoint."""
        with patch('controllers.analytics_controller.AnalyticsService') as mock_service:
            mock_service.return_value.get_top_selling_products.return_value = {
                "products": [
                    {
                        "product_id": "prod_001",
                        "product_name": "Test Product",
                        "quantity_sold": 50,
                        "revenue": 500.0,
                        "category": "Electronics"
                    }
                ]
            }
            
            response = client.get("/api/v1/analytics/products/top-selling?limit=10")
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
    
    def test_get_user_activity_summary(self, client: TestClient):
        """Test user activity summary endpoint."""
        with patch('controllers.analytics_controller.AnalyticsService') as mock_service:
            mock_service.return_value.get_user_activity_summary.return_value = {
                "total_users": 100,
                "active_users": 75,
                "new_users": 10,
                "user_activity": [
                    {
                        "user_id": "user_001",
                        "login_count": 5,
                        "last_login": "2024-01-01T10:00:00",
                        "total_orders": 3,
                        "total_spent": 150.0
                    }
                ]
            }
            
            response = client.get("/api/v1/analytics/users/activity")
            assert response.status_code == 200
            data = response.json()
            assert "total_users" in data
            assert "active_users" in data
    
    def test_get_revenue_trends(self, client: TestClient):
        """Test revenue trends endpoint."""
        with patch('controllers.analytics_controller.AnalyticsService') as mock_service:
            mock_service.return_value.get_revenue_trends.return_value = {
                "period": "monthly",
                "trends": [
                    {
                        "period": "2024-01",
                        "revenue": 10000.0,
                        "growth_rate": 0.15,
                        "previous_period_revenue": 8700.0
                    }
                ]
            }
            
            response = client.get("/api/v1/analytics/revenue/trends?period=monthly")
            assert response.status_code == 200
            data = response.json()
            assert "period" in data
            assert "trends" in data
    
    def test_get_daily_sales_report(self, client: TestClient):
        """Test daily sales report endpoint."""
        with patch('controllers.analytics_controller.SalesReportService') as mock_service:
            mock_service.return_value.generate_daily_report.return_value = {
                "date": "2024-01-01",
                "total_revenue": 1000.0,
                "total_orders": 10,
                "total_customers": 8,
                "top_products": [],
                "category_breakdown": []
            }
            
            response = client.get("/api/v1/analytics/sales/daily-report?date=2024-01-01")
            assert response.status_code == 200
            data = response.json()
            assert "date" in data
            assert "total_revenue" in data
    
    def test_invalid_date_format(self, client: TestClient):
        """Test invalid date format handling."""
        response = client.get("/api/v1/analytics/sales/summary?start_date=invalid-date")
        assert response.status_code == 400
    
    def test_invalid_period(self, client: TestClient):
        """Test invalid period parameter handling."""
        response = client.get("/api/v1/analytics/sales/summary?period=invalid")
        assert response.status_code == 400
    
    def test_invalid_limit(self, client: TestClient):
        """Test invalid limit parameter handling."""
        response = client.get("/api/v1/analytics/products/top-selling?limit=0")
        assert response.status_code == 400
        
        response = client.get("/api/v1/analytics/products/top-selling?limit=101")
        assert response.status_code == 400