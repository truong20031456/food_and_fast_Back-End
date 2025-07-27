# API Gateway

## Overview

The API Gateway is a microservice that serves as the single entry point for all client requests in the Food & Fast E-Commerce platform. It handles request routing, authentication, rate limiting, request/response transformation, and provides a unified API interface for all backend services.

## Features

- 🚪 **Request Routing**: Intelligent routing to appropriate microservices
- 🔐 **Authentication**: Centralized authentication and authorization
- 🛡️ **Security**: Rate limiting, CORS, and security headers
- 📊 **Monitoring**: Request/response logging and metrics
- 🔄 **Load Balancing**: Request distribution across service instances
- 📝 **Request Transformation**: Request/response modification and validation
- 🚨 **Error Handling**: Centralized error handling and response formatting
- 📱 **API Versioning**: Support for multiple API versions

## Tech Stack

- **Framework**: FastAPI
- **Proxy**: HTTPX for service communication
- **Authentication**: JWT token validation
- **Rate Limiting**: Redis-based rate limiting
- **Monitoring**: Prometheus metrics
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
api_gateway/
├── config/              # Configuration files
│   └── settings.py     # Application settings
├── middleware/          # Custom middleware
│   └── auth.py         # Authentication middleware
├── routes/              # API route handlers
│   └── router.py       # Main router configuration
├── services/            # Service integrations
├── utils/               # Utility functions
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Authentication Routes
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Token refresh
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset

### Product Routes
- `GET /products` - List products
- `GET /products/{product_id}` - Get product details
- `POST /products` - Create product (admin)
- `PUT /products/{product_id}` - Update product (admin)
- `DELETE /products/{product_id}` - Delete product (admin)
- `GET /products/search` - Search products
- `GET /categories` - List categories
- `GET /categories/{category_id}/products` - Get products by category

### Order Routes
- `GET /orders` - List user orders
- `GET /orders/{order_id}` - Get order details
- `POST /orders` - Create order
- `PUT /orders/{order_id}/cancel` - Cancel order
- `GET /cart` - Get shopping cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item
- `DELETE /cart/items/{item_id}` - Remove cart item

### Payment Routes
- `POST /payments/create` - Create payment
- `POST /payments/confirm` - Confirm payment
- `GET /payments/{payment_id}` - Get payment details
- `POST /payments/{payment_id}/refund` - Process refund
- `GET /payment-methods` - List payment methods

### User Routes
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `GET /users/addresses` - Get user addresses
- `POST /users/addresses` - Add address
- `PUT /users/addresses/{address_id}` - Update address
- `DELETE /users/addresses/{address_id}` - Delete address

### Notification Routes
- `GET /notifications` - Get user notifications
- `POST /notifications/mark-read` - Mark notification as read
- `PUT /notifications/preferences` - Update notification preferences

### Analytics Routes
- `GET /analytics/overview` - Business overview
- `GET /analytics/sales` - Sales analytics
- `GET /analytics/users` - User analytics
- `GET /analytics/products` - Product analytics

## Environment Variables

Create a `.env` file in the api_gateway directory:

```env
# Application
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
PRODUCT_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
USER_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8006
ANALYTICS_SERVICE_URL=http://localhost:8007

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Timeout Configuration
REQUEST_TIMEOUT_SECONDS=30
SERVICE_TIMEOUT_SECONDS=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Redis

### Local Development

1. **Clone the repository**
   ```bash
   cd api_gateway
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t api-gateway .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 --env-file .env api-gateway
   ```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=.
```

### Run specific test file
```bash
pytest tests/test_routing.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Request Flow

### 1. Request Reception
- Client sends request to API Gateway
- Request validation and parsing
- Authentication token extraction

### 2. Authentication & Authorization
- JWT token validation
- User permission verification
- Rate limiting check

### 3. Request Routing
- Service identification based on route
- Load balancing (if multiple instances)
- Request forwarding to appropriate service

### 4. Response Processing
- Service response reception
- Response transformation (if needed)
- Error handling and formatting

### 5. Response Delivery
- Response validation
- CORS headers addition
- Response delivery to client

## Service Routing

### Route Configuration
```python
# Example route configuration
ROUTES = {
    "/auth": "http://auth-service:8001",
    "/products": "http://product-service:8002",
    "/orders": "http://order-service:8003",
    "/payments": "http://payment-service:8004",
    "/users": "http://user-service:8005",
    "/notifications": "http://notification-service:8006",
    "/analytics": "http://analytics-service:8007"
}
```

### Route Patterns
- **Exact Match**: `/auth/login`
- **Path Parameters**: `/products/{product_id}`
- **Query Parameters**: `/products?category=electronics`
- **Wildcard Routes**: `/api/v1/*`

## Authentication & Authorization

### JWT Token Validation
- Token signature verification
- Token expiration check
- User permission validation
- Token refresh handling

### Role-Based Access Control
- **Public Routes**: No authentication required
- **User Routes**: Authenticated user access
- **Admin Routes**: Admin-only access
- **Service Routes**: Internal service communication

### Rate Limiting
- **Per User**: Individual user rate limits
- **Per IP**: IP-based rate limiting
- **Per Endpoint**: Endpoint-specific limits
- **Global Limits**: Overall API limits

## Security Features

### Request Security
- **Input Validation**: Request data validation
- **SQL Injection Prevention**: Parameter sanitization
- **XSS Prevention**: Content security headers
- **CSRF Protection**: Cross-site request forgery protection

### Response Security
- **CORS Headers**: Cross-origin resource sharing
- **Security Headers**: Security-related HTTP headers
- **Content Type Validation**: Response content validation
- **Error Information Sanitization**: Safe error messages

### Monitoring & Logging
- **Request Logging**: Comprehensive request logs
- **Error Tracking**: Error monitoring and alerting
- **Performance Metrics**: Response time tracking
- **Security Events**: Security incident logging

## Error Handling

### Error Types
- **Authentication Errors**: Invalid tokens, expired sessions
- **Authorization Errors**: Insufficient permissions
- **Validation Errors**: Invalid request data
- **Service Errors**: Backend service failures
- **Network Errors**: Connection timeouts, service unavailable

### Error Response Format
```json
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid authentication token",
    "details": "Token has expired",
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Recovery
- **Retry Logic**: Automatic retry for transient errors
- **Circuit Breaker**: Service failure protection
- **Fallback Responses**: Graceful degradation
- **Error Aggregation**: Error pattern analysis

## Performance Features

### Caching
- **Response Caching**: Cache frequently requested data
- **Token Caching**: Cache validated tokens
- **Route Caching**: Cache route configurations
- **Rate Limit Caching**: Cache rate limit counters

### Load Balancing
- **Round Robin**: Simple load distribution
- **Least Connections**: Connection-based balancing
- **Health Check**: Service health monitoring
- **Failover**: Automatic service failover

### Connection Pooling
- **HTTP Connection Pooling**: Reuse HTTP connections
- **Database Connection Pooling**: Database connection management
- **Redis Connection Pooling**: Redis connection optimization

## Monitoring & Metrics

### Health Checks
- **Service Health**: Individual service health monitoring
- **Dependency Health**: Database, Redis health checks
- **Response Time**: Service response time tracking
- **Error Rates**: Error rate monitoring

### Metrics Collection
- **Request Count**: Total request count
- **Response Time**: Average response time
- **Error Rate**: Error percentage
- **Throughput**: Requests per second

### Logging
- **Request Logs**: Detailed request information
- **Error Logs**: Error details and stack traces
- **Access Logs**: User access patterns
- **Performance Logs**: Performance metrics

## API Versioning

### Version Strategies
- **URL Versioning**: `/api/v1/products`
- **Header Versioning**: `Accept: application/vnd.api+json;version=1`
- **Query Parameter**: `/products?version=1`
- **Content Negotiation**: Multiple content types

### Version Management
- **Backward Compatibility**: Maintain old versions
- **Deprecation Notices**: Version deprecation warnings
- **Migration Support**: Version migration assistance
- **Documentation**: Version-specific documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 