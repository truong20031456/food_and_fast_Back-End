"""
Tests for API Gateway Routing and Middleware
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json


class TestAPIGatewayRouting:
    """Test cases for API Gateway routing functionality."""

    def test_route_forwarding_to_user_service(self, client: TestClient):
        """Test route forwarding to user service."""
        with patch("services.request_forwarder.RequestForwarder") as mock_forwarder:
            mock_forwarder.return_value.forward_request = AsyncMock(return_value={
                "status_code": 200,
                "data": {"user_id": "123", "username": "testuser"}
            })
            
            response = client.get("/api/users/123")
            
            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data

    def test_route_forwarding_to_product_service(self, client: TestClient):
        """Test route forwarding to product service."""
        with patch("services.request_forwarder.RequestForwarder") as mock_forwarder:
            mock_forwarder.return_value.forward_request = AsyncMock(return_value={
                "status_code": 200,
                "data": {"products": [{"id": "1", "name": "Pizza"}]}
            })
            
            response = client.get("/api/products")
            
            assert response.status_code == 200
            data = response.json()
            assert "products" in data

    def test_authentication_middleware_valid_token(self, client: TestClient):
        """Test authentication middleware with valid token."""
        valid_token = "Bearer valid_jwt_token"
        
        with patch("core.auth_middleware.verify_token") as mock_verify:
            mock_verify.return_value = {"user_id": "123", "role": "user"}
            
            response = client.get(
                "/api/users/123",
                headers={"Authorization": valid_token}
            )
            
            # Should proceed to route forwarding
            assert response.status_code in [200, 404]  # 404 if service not mocked

    def test_authentication_middleware_invalid_token(self, client: TestClient):
        """Test authentication middleware with invalid token."""
        invalid_token = "Bearer invalid_token"
        
        with patch("core.auth_middleware.verify_token") as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")
            
            response = client.get(
                "/api/users/123",
                headers={"Authorization": invalid_token}
            )
            
            assert response.status_code == 401

    def test_service_discovery_mechanism(self, client: TestClient):
        """Test service discovery for routing."""
        with patch("services.service_registry.ServiceRegistry") as mock_registry:
            mock_registry.return_value.get_service_url.return_value = "http://user-service:8000"
            
            # Test service discovery
            response = client.get("/api/users/health")
            
            # Should attempt to discover and route to user service
            mock_registry.return_value.get_service_url.assert_called()

    def test_rate_limiting_middleware(self, client: TestClient):
        """Test rate limiting middleware."""
        with patch("core.rate_limiter.RateLimiter") as mock_limiter:
            # First requests should pass
            mock_limiter.return_value.is_allowed.return_value = True
            
            response = client.get("/api/products")
            assert response.status_code != 429  # Not rate limited
            
            # Exceed rate limit
            mock_limiter.return_value.is_allowed.return_value = False
            
            response = client.get("/api/products")
            assert response.status_code == 429  # Rate limited

    def test_cors_middleware_handling(self, client: TestClient):
        """Test CORS middleware handling."""
        # Test preflight request
        response = client.options(
            "/api/users",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        assert "Access-Control-Allow-Origin" in response.headers

    def test_error_handling_service_unavailable(self, client: TestClient):
        """Test error handling when downstream service is unavailable."""
        with patch("services.request_forwarder.RequestForwarder") as mock_forwarder:
            mock_forwarder.return_value.forward_request = AsyncMock(
                side_effect=Exception("Service unavailable")
            )
            
            response = client.get("/api/users/123")
            
            assert response.status_code == 503  # Service Unavailable
            data = response.json()
            assert "error" in data

    def test_request_timeout_handling(self, client: TestClient):
        """Test request timeout handling."""
        with patch("services.request_forwarder.RequestForwarder") as mock_forwarder:
            mock_forwarder.return_value.forward_request = AsyncMock(
                side_effect=TimeoutError("Request timeout")
            )
            
            response = client.get("/api/products")
            
            assert response.status_code == 504  # Gateway Timeout

    def test_load_balancing_between_instances(self, client: TestClient):
        """Test load balancing between service instances."""
        with patch("services.service_registry.ServiceRegistry") as mock_registry:
            # Mock multiple service instances
            mock_registry.return_value.get_available_instances.return_value = [
                "http://user-service-1:8000",
                "http://user-service-2:8000"
            ]
            
            with patch("services.load_balancer.LoadBalancer") as mock_lb:
                mock_lb.return_value.select_instance.return_value = "http://user-service-1:8000"
                
                response = client.get("/api/users/health")
                
                # Should use load balancer to select instance
                mock_lb.return_value.select_instance.assert_called()

    def test_api_versioning_routing(self, client: TestClient):
        """Test API versioning routing."""
        with patch("services.request_forwarder.RequestForwarder") as mock_forwarder:
            mock_forwarder.return_value.forward_request = AsyncMock(return_value={
                "status_code": 200,
                "data": {"version": "v1"}
            })
            
            # Test v1 API
            response = client.get("/api/v1/users/123")
            assert response.status_code == 200
            
            # Test v2 API  
            response = client.get("/api/v2/users/123")
            assert response.status_code == 200

    def test_request_logging_middleware(self, client: TestClient):
        """Test request logging middleware."""
        with patch("core.logging_middleware.logger") as mock_logger:
            response = client.get("/api/users/123")
            
            # Should log the request
            mock_logger.info.assert_called()

    def test_circuit_breaker_pattern(self, client: TestClient):
        """Test circuit breaker pattern for failing services."""
        with patch("core.circuit_breaker.CircuitBreaker") as mock_cb:
            # Circuit breaker is open (service failing)
            mock_cb.return_value.is_open.return_value = True
            
            response = client.get("/api/products")
            
            assert response.status_code == 503
            data = response.json()
            assert "circuit breaker" in data.get("error", "").lower()
