# Product Service

A FastAPI-based microservice for managing products, categories, inventory, and reviews in the Food & Fast E-Commerce platform.

## Features

- **Product Management**: CRUD operations for products with categories, images, and metadata
- **Category Management**: Hierarchical category system with parent-child relationships
- **Inventory Management**: Stock tracking, reservations, and low stock alerts
- **Review System**: Product reviews with ratings and verification
- **Search Functionality**: Advanced product search with filters
- **RESTful API**: Complete REST API with OpenAPI documentation

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Cache**: Redis
- **Testing**: pytest with async support
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd product_service
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
   # Edit .env with your database and Redis credentials
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8003
   ```

### Docker

```bash
# Build the image
docker build -t product-service .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run standalone
docker run -p 8003:8003 product-service
```

## API Documentation

Once the service is running, you can access:

- **Interactive API Docs**: http://localhost:8003/docs
- **ReDoc Documentation**: http://localhost:8003/redoc
- **OpenAPI Schema**: http://localhost:8003/openapi.json

### Key Endpoints

#### Products
- `GET /products/` - List products with filters
- `POST /products/` - Create a new product
- `GET /products/{id}` - Get product by ID
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

#### Categories
- `GET /categories/` - List categories
- `POST /categories/` - Create a new category
- `GET /categories/{id}` - Get category by ID
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

#### Inventory
- `GET /inventory/product/{product_id}` - Get inventory for product
- `POST /inventory/product/{product_id}/adjust` - Adjust inventory
- `POST /inventory/product/{product_id}/reserve` - Reserve inventory
- `POST /inventory/product/{product_id}/release` - Release reserved inventory

#### Reviews
- `GET /reviews/product/{product_id}` - Get product reviews
- `POST /reviews/` - Create a new review
- `PUT /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_products.py

# Run with verbose output
pytest -v
```

### Test Structure
- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_health.py` - Health check tests
- `tests/test_products.py` - Product API tests
- `tests/test_categories.py` - Category API tests
- `tests/test_inventory.py` - Inventory API tests
- `tests/test_reviews.py` - Review API tests

## Development

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Bandit**: Security linting

```bash
# Format code
black .

# Run linting
flake8 .

# Run type checking
mypy .

# Run security checks
bandit -r .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://truong:truong123@localhost:5432/product_service_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/1` |
| `DEBUG` | Enable debug mode | `False` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8003` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## CI/CD

The service includes a comprehensive CI/CD pipeline with GitHub Actions:

- **Lint**: Code formatting and linting checks
- **Test**: Unit and integration tests
- **Security**: Security vulnerability scanning
- **Docker**: Container build and validation
- **Integration**: End-to-end service testing

## Monitoring

### Health Checks
- `GET /health` - Service health status
- Docker health check configured
- Prometheus metrics (planned)

### Logging
- Structured logging with structlog
- Configurable log levels
- Request/response logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 