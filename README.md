# Order Service

## Overview

The Order Service is a microservice responsible for managing orders, shopping carts, and order processing in the Food & Fast E-Commerce platform. It handles the complete order lifecycle from cart creation to order fulfillment, including order tracking, status updates, and integration with other services.

## Features

- 🛒 **Shopping Cart**: Add, remove, and manage cart items
- 📦 **Order Management**: Complete order lifecycle management
- 🔄 **Order Processing**: Order status tracking and updates
- 📋 **Order History**: Comprehensive order history and tracking
- 🎯 **Order Validation**: Business rule validation and inventory checks
- 📊 **Order Analytics**: Order statistics and reporting
- 🔗 **Service Integration**: Integration with product, payment, and user services
- 📱 **Real-time Updates**: Live order status updates

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Message Queue**: Redis/RabbitMQ for async processing
- **Validation**: Pydantic
- **Testing**: pytest
- **Documentation**: Auto-generated OpenAPI/Swagger

## Project Structure

```
order_service/
├── models/              # SQLAlchemy models
│   ├── order.py        # Order model
│   └── cart.py         # Cart model
├── modules/             # Business logic modules
│   ├── cart/
│   │   └── cart_service.py
│   └── orders/
│       └── order_service.py
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Shopping Cart
- `GET /cart` - Get user's shopping cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item quantity
- `DELETE /cart/items/{item_id}` - Remove item from cart
- `DELETE /cart` - Clear entire cart
- `POST /cart/apply-coupon` - Apply discount coupon
- `DELETE /cart/remove-coupon` - Remove applied coupon

### Orders
- `GET /orders` - List user's orders with pagination
- `GET /orders/{order_id}` - Get order details
- `POST /orders` - Create new order from cart
- `PUT /orders/{order_id}/status` - Update order status
- `POST /orders/{order_id}/cancel` - Cancel order
- `GET /orders/{order_id}/tracking` - Get order tracking info
- `POST /orders/{order_id}/refund` - Request order refund

### Order Management
- `GET /orders/pending` - Get pending orders (admin)
- `GET /orders/processing` - Get processing orders (admin)
- `PUT /orders/{order_id}/assign` - Assign order to delivery (admin)
- `POST /orders/{order_id}/ship` - Mark order as shipped
- `POST /orders/{order_id}/deliver` - Mark order as delivered

### Analytics
- `GET /analytics/orders` - Order statistics
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/top-products` - Top selling products
- `GET /analytics/order-status` - Order status distribution

## Environment Variables

Create a `.env` file in the order_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/order_db

# Application
HOST=0.0.0.0
PORT=8003
DEBUG=true

# Service URLs
PRODUCT_SERVICE_URL=http://localhost:8002
PAYMENT_SERVICE_URL=http://localhost:8004
USER_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8006

# Redis
REDIS_URL=redis://localhost:6379

# Order Configuration
MAX_CART_ITEMS=50
MAX_ORDER_AMOUNT=10000
ORDER_EXPIRY_HOURS=24
CART_EXPIRY_DAYS=30

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL=INFO
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

### Local Development

1. **Clone the repository**
   ```bash
   cd order_service
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

5. **Run database migrations**
   ```bash
   # Create tables (if using SQLAlchemy create_all)
   python -c "from models import Base; from database import engine; Base.metadata.create_all(engine)"
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8003
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t order-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8003:8003 --env-file .env order-service
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
pytest tests/test_orders.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **Health Check**: http://localhost:8003/health

## Database Schema

### Orders Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `order_number`: Unique order number
- `status`: Order status (pending, confirmed, processing, shipped, delivered, cancelled)
- `total_amount`: Total order amount
- `shipping_address`: Delivery address
- `billing_address`: Billing address
- `payment_method`: Payment method used
- `payment_status`: Payment status
- `created_at`: Order creation timestamp
- `updated_at`: Last update timestamp

### Order Items Table
- `id`: Primary key
- `order_id`: Foreign key to orders
- `product_id`: Foreign key to products
- `quantity`: Item quantity
- `unit_price`: Unit price at time of order
- `total_price`: Total price for this item
- `product_name`: Product name snapshot
- `product_sku`: Product SKU snapshot

### Cart Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_id`: Session identifier
- `created_at`: Cart creation timestamp
- `updated_at`: Last update timestamp
- `expires_at`: Cart expiration timestamp

### Cart Items Table
- `id`: Primary key
- `cart_id`: Foreign key to cart
- `product_id`: Foreign key to products
- `quantity`: Item quantity
- `added_at`: Item addition timestamp

## Order Lifecycle

### 1. Cart Creation
- User adds items to cart
- Cart validation and inventory checks
- Price calculations and discounts

### 2. Order Placement
- Cart to order conversion
- Payment processing
- Inventory reservation
- Order confirmation

### 3. Order Processing
- Order validation
- Inventory allocation
- Payment confirmation
- Order status updates

### 4. Order Fulfillment
- Order assignment to delivery
- Shipping and tracking
- Delivery confirmation
- Order completion

### 5. Post-Order
- Order history maintenance
- Review solicitation
- Analytics and reporting

## Order Statuses

- **PENDING**: Order created, awaiting payment
- **CONFIRMED**: Payment received, order confirmed
- **PROCESSING**: Order being prepared
- **SHIPPED**: Order shipped, in transit
- **DELIVERED**: Order delivered successfully
- **CANCELLED**: Order cancelled
- **REFUNDED**: Order refunded

## Integration Points

### Product Service
- Product information retrieval
- Inventory availability checks
- Price validation

### Payment Service
- Payment processing
- Payment status updates
- Refund processing

### User Service
- User information validation
- Address verification
- User preferences

### Notification Service
- Order confirmation emails
- Status update notifications
- Delivery tracking updates

## Business Rules

### Cart Rules
- Maximum 50 items per cart
- Cart expires after 30 days of inactivity
- Real-time inventory validation
- Price updates on cart refresh

### Order Rules
- Minimum order amount validation
- Maximum order amount limits
- Payment method validation
- Address verification requirements

### Inventory Rules
- Real-time inventory checks
- Inventory reservation during checkout
- Inventory release on order cancellation
- Low stock notifications

## Performance Features

- **Caching**: Redis-based caching for frequently accessed data
- **Pagination**: Efficient pagination for order history
- **Indexing**: Database indexes for fast queries
- **Async Processing**: Background task processing
- **Connection Pooling**: Database connection optimization

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Order Tracking**: Comprehensive order status tracking
- **Error Logging**: Detailed error logging for debugging
- **Performance Metrics**: Order processing time monitoring
- **Business Metrics**: Order volume and revenue tracking

## Security Features

- **Input Validation**: Pydantic-based request validation
- **User Authorization**: Order ownership verification
- **Data Sanitization**: SQL injection prevention
- **Rate Limiting**: API rate limiting for abuse prevention
- **Audit Logging**: Order modification audit trail

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 