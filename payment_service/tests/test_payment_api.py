"""
Tests for Payment Service Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json


class TestPaymentEndpoints:
    """Test cases for payment service endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "payment-service"

    def test_create_payment_intent_success(self, client: TestClient, sample_payment_data):
        """Test successful payment intent creation."""
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.create_payment_intent = AsyncMock(return_value={
                "payment_intent_id": "pi_test_123",
                "client_secret": "pi_test_123_secret",
                "status": "requires_payment_method",
                "amount": 9999
            })
            
            response = client.post("/payments/create-intent", json=sample_payment_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "payment_intent_id" in data
            assert "client_secret" in data

    def test_process_payment_success(self, client: TestClient, sample_payment_data):
        """Test successful payment processing."""
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.process_payment = AsyncMock(return_value={
                "payment_id": "pay_123",
                "status": "succeeded",
                "amount": 9999,
                "currency": "usd",
                "receipt_url": "https://example.com/receipt"
            })
            
            response = client.post("/payments/process", json=sample_payment_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "succeeded"
            assert data["payment_id"] == "pay_123"

    def test_process_payment_failed(self, client: TestClient, sample_payment_data):
        """Test failed payment processing."""
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.process_payment = AsyncMock(return_value={
                "payment_id": None,
                "status": "failed",
                "error": "Card declined",
                "error_code": "card_declined"
            })
            
            response = client.post("/payments/process", json=sample_payment_data)
            
            assert response.status_code == 402  # Payment Required
            data = response.json()
            assert data["status"] == "failed"
            assert "error" in data

    def test_get_payment_status(self, client: TestClient):
        """Test getting payment status."""
        payment_id = "pay_123"
        
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.get_payment_status = AsyncMock(return_value={
                "payment_id": payment_id,
                "status": "succeeded",
                "amount": 9999,
                "currency": "usd",
                "created_at": "2025-08-09T10:00:00Z"
            })
            
            response = client.get(f"/payments/{payment_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["payment_id"] == payment_id
            assert data["status"] == "succeeded"

    def test_create_refund_success(self, client: TestClient, sample_refund_data):
        """Test successful refund creation."""
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.create_refund = AsyncMock(return_value={
                "refund_id": "re_123",
                "status": "succeeded",
                "amount": 5000,
                "payment_id": "pay_123"
            })
            
            response = client.post("/payments/refund", json=sample_refund_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["refund_id"] == "re_123"
            assert data["status"] == "succeeded"

    def test_get_payment_methods(self, client: TestClient):
        """Test getting available payment methods."""
        customer_id = "customer_123"
        
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.get_payment_methods = AsyncMock(return_value=[
                {
                    "id": "pm_123",
                    "type": "card",
                    "card": {
                        "brand": "visa",
                        "last4": "4242",
                        "exp_month": 12,
                        "exp_year": 2025
                    }
                }
            ])
            
            response = client.get(f"/payments/methods/{customer_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["type"] == "card"

    def test_webhook_payment_succeeded(self, client: TestClient, webhook_payment_data):
        """Test webhook handling for successful payment."""
        with patch("api.routers.webhook_controller.WebhookService") as mock_service:
            mock_service.return_value.handle_payment_webhook = AsyncMock(return_value={
                "processed": True,
                "payment_id": "pi_test_payment",
                "status": "succeeded"
            })
            
            response = client.post("/webhooks/payment", json=webhook_payment_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["processed"] is True

    def test_invalid_payment_data(self, client: TestClient):
        """Test payment processing with invalid data."""
        invalid_data = {
            "order_id": "",  # Empty order_id
            "amount": -10,   # Negative amount
            "currency": "INVALID"  # Invalid currency
        }
        
        response = client.post("/payments/process", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_payment_service_error_handling(self, client: TestClient, sample_payment_data):
        """Test error handling when payment service fails."""
        with patch("api.routers.payment_controller.PaymentService") as mock_service:
            mock_service.return_value.process_payment = AsyncMock(
                side_effect=Exception("Payment gateway unavailable")
            )
            
            response = client.post("/payments/process", json=sample_payment_data)
            assert response.status_code == 500
