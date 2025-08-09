"""
Tests for Notification Service Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json


class TestNotificationEndpoints:
    """Test cases for notification service endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "notification-service"

    def test_send_notification_success(self, client: TestClient, sample_notification_data):
        """Test successful notification sending."""
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            # Mock successful notification sending
            mock_service.return_value.send_notification = AsyncMock(return_value={
                "id": "notif_123",
                "status": "sent",
                "message": "Notification sent successfully"
            })
            
            response = client.post("/notifications/send", json=sample_notification_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "notif_123"
            assert data["status"] == "sent"

    def test_send_notification_invalid_data(self, client: TestClient):
        """Test notification sending with invalid data."""
        invalid_data = {
            "user_id": "",  # Empty user_id
            "type": "invalid_type",  # Invalid type
            "template": "",  # Empty template
        }
        
        response = client.post("/notifications/send", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_send_bulk_notifications_success(self, client: TestClient, sample_bulk_notification_data):
        """Test successful bulk notification sending."""
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.send_bulk_notifications = AsyncMock(return_value={
                "sent": 2,
                "failed": 0,
                "results": [
                    {"id": "notif_456", "status": "sent"},
                    {"id": "notif_789", "status": "sent"}
                ]
            })
            
            response = client.post("/notifications/bulk", json=sample_bulk_notification_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["sent"] == 2
            assert data["failed"] == 0

    def test_get_notification_status(self, client: TestClient):
        """Test getting notification status."""
        notification_id = "notif_123"
        
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.get_notification_status = AsyncMock(return_value={
                "id": notification_id,
                "status": "delivered",
                "sent_at": "2025-08-09T10:00:00Z",
                "delivered_at": "2025-08-09T10:00:05Z"
            })
            
            response = client.get(f"/notifications/{notification_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == notification_id
            assert data["status"] == "delivered"

    def test_get_notification_status_not_found(self, client: TestClient):
        """Test getting status for non-existent notification."""
        notification_id = "invalid_id"
        
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.get_notification_status = AsyncMock(return_value=None)
            
            response = client.get(f"/notifications/{notification_id}/status")
            assert response.status_code == 404

    def test_get_user_notifications(self, client: TestClient):
        """Test getting user notifications."""
        user_id = "user_123"
        
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.get_user_notifications = AsyncMock(return_value=[
                {
                    "id": "notif_123",
                    "type": "email",
                    "template": "order_confirmation",
                    "status": "delivered",
                    "sent_at": "2025-08-09T10:00:00Z"
                },
                {
                    "id": "notif_456",
                    "type": "sms",
                    "template": "promotion",
                    "status": "sent",
                    "sent_at": "2025-08-09T09:00:00Z"
                }
            ])
            
            response = client.get(f"/notifications/user/{user_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["id"] == "notif_123"

    def test_notification_templates_list(self, client: TestClient):
        """Test getting available notification templates."""
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.get_templates = AsyncMock(return_value=[
                {
                    "id": "order_confirmation",
                    "name": "Order Confirmation",
                    "type": "email",
                    "variables": ["order_id", "customer_name", "total_amount"]
                },
                {
                    "id": "promotion",
                    "name": "Promotional Offer",
                    "type": "email",
                    "variables": ["discount", "code", "expiry_date"]
                }
            ])
            
            response = client.get("/notifications/templates")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["id"] == "order_confirmation"

    def test_notification_service_error_handling(self, client: TestClient, sample_notification_data):
        """Test error handling when notification service fails."""
        with patch("api.routers.notification_router.NotificationService") as mock_service:
            mock_service.return_value.send_notification = AsyncMock(
                side_effect=Exception("Service unavailable")
            )
            
            response = client.post("/notifications/send", json=sample_notification_data)
            assert response.status_code == 500
