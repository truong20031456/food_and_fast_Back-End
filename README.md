# Food & Fast E-Commerce Microservices

🚀 **Modern e-commerce platform for food delivery and fast supermarket shopping**

A comprehensive microservices-based e-commerce platform built with FastAPI, featuring authentication, product management, order processing, payments, notifications, and analytics.

## 🏗️ Architecture

This project follows a **microservices architecture** with the following services:

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **API Gateway** | 8000 | Entry point, routing, load balancing | 🚧 In Progress |
| **Auth Service** | 8001 | Authentication, JWT, user management | ✅ Complete |
| **User Service** | 8002 | Profile & account management | 🚧 In Progress |
| **Product Service** | 8003 | Catalog, inventory, reviews | 🚧 In Progress |
| **Order Service** | 8004 | Cart, orders, delivery | 🚧 In Progress |
| **Payment Service** | 8005 | Payment gateways & promotions | 🚧 In Progress |
| **Notification Service** | 8006 | Email, SMS, chat support | 🚧 In Progress |
| **Analytics Service** | 8007 | Reports & dashboard data | 🚧 In Progress |

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for sessions and caching
- **Search**: Elasticsearch for product search
- **Message Queue**: Celery (planned)
- **Containerization**: Docker with docker-compose

### Monitoring & Observability
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: Structured logging with structlog
- **Health Checks**: Built-in health endpoints

### Development Tools
- **Code Quality**: Black, Flake8, MyPy
- **Testing**: Pytest with async support
- **API Documentation**: Auto-generated with FastAPI

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd food-fast-ecommerce
```

### 2. Environment Setup
```bash
# Copy environment configuration
cp env.example .env

# Edit .env file with your configuration
nano .env
```

### 3. Start Infrastructure Services
```bash
cd infrastructure
docker-compose up -d postgres redis elasticsearch
```

### 4. Start All Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start services individually
docker-compose up -d api_gateway auth_service product_service
```

### 5. Verify Installation
```bash
# Check service health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs

# Check individual services
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8003/health  # Product Service
```

## 📁 Project Structure

```
food-fast-ecommerce/
├── api_gateway/          # API Gateway with routing & load balancing
├── auth_service/         # Authentication & authorization
├── user_service/         # User management & profiles
├── product_service/      # Product catalog & inventory
├── order_service/        # Order processing & cart
├── payment_service/      # Payment processing
├── notification_service/ # Notifications & messaging
├── analytics_service/    # Analytics & reporting
├── shared/              # Shared utilities & models
├── infrastructure/      # Docker & deployment configs
├── env.example          # Environment configuration template
└── README.md           # This file
```

## 🔧 Development

### Local Development Setup

#### 1. Install Dependencies
```bash
# For each service
cd auth_service
pip install -r requirements.txt

cd ../product_service
pip install -r requirements.txt
```

#### 2. Database Migrations
```bash
# Run migrations for each service
cd auth_service
alembic upgrade head

cd ../product_service
alembic upgrade head
```

#### 3. Start Services Locally
```bash
# Start infrastructure
cd infrastructure
docker-compose up -d postgres redis elasticsearch

# Start services (in separate terminals)
cd ../auth_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

cd ../product_service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload

cd ../api_gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Once services are running, access the interactive API documentation:

- **API Gateway**: http://localhost:8000/docs
- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8003/docs

### Testing

```bash
# Run tests for a service
cd auth_service
pytest

# Run with coverage
pytest --cov=.

# Run all tests
pytest --cov=. --cov-report=html
```

## 🐳 Docker Deployment

### Production Deployment

#### 1. Build Images
```bash
docker-compose build
```

#### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api_gateway
```

#### 3. Scale Services
```bash
# Scale specific services
docker-compose up -d --scale product_service=3
docker-compose up -d --scale auth_service=2
```

### Monitoring

Access monitoring dashboards:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🔐 Authentication

The platform uses JWT-based authentication:

### Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### Use Authentication
```bash
# Include token in requests
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Product Management

### Create a Product
```bash
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Organic Bananas",
    "description": "Fresh organic bananas",
    "price": 2.99,
    "category_id": 1,
    "sku": "BAN-ORG-001"
  }'
```

### List Products
```bash
curl -X GET "http://localhost:8000/products/?page=1&size=10"
```

### Search Products
```bash
curl -X GET "http://localhost:8000/products/?search=banana&min_price=1&max_price=5"
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/food_fast

# Redis
REDIS_URL=redis://localhost:6379

# JWT
AUTH_SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Services
AUTH_SERVICE_PORT=8001
PRODUCT_SERVICE_PORT=8003
```

### Service Configuration

Each service has its own configuration in `core/config.py`:

- Database connection settings
- Redis configuration
- Service-specific settings
- Security parameters

## 🧪 Testing

### Running Tests

```bash
# Unit tests
pytest

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/

# With coverage
pytest --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test fixtures
└── conftest.py    # Pytest configuration
```

## 📈 Monitoring & Observability

### Health Checks

All services provide health check endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8003/health
```

### Metrics

Prometheus metrics are available at `/metrics` endpoints:

```bash
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

### Logging

Structured logging with correlation IDs:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing order", extra={"order_id": "123", "user_id": "456"})
```

## 🔒 Security

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **Rate Limiting**: Built-in rate limiting per IP
- **CORS**: Configurable CORS policies
- **Input Validation**: Pydantic validation for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM protection

### Security Headers

```python
# Automatic security headers
SECURITY_HEADERS = True
```

## 🚀 Deployment

### Production Checklist

- [ ] Update environment variables
- [ ] Set secure JWT secret
- [ ] Configure database credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring
- [ ] Set up backup strategy
- [ ] Configure logging aggregation

### Kubernetes Deployment

```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: food-fast-api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: food-fast/api-gateway:latest
        ports:
        - containerPort: 8000
```

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests
5. **Run** tests and linting
6. **Submit** a pull request

### Code Standards

- Follow PEP 8 style guide
- Use type hints
- Write docstrings
- Add tests for new features
- Update documentation

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📝 API Documentation

### OpenAPI/Swagger

Interactive API documentation is available at:

- **API Gateway**: http://localhost:8000/docs
- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8003/docs

### API Examples

See the `examples/` directory for API usage examples.

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Service Not Starting
```bash
# Check service logs
docker-compose logs auth_service

# Check service health
curl http://localhost:8001/health

# Restart service
docker-compose restart auth_service
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
ports:
  - "8001:8001"  # Change to different port
```

## 📞 Support

### Getting Help

- **Documentation**: Check this README and API docs
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions

### Community

- **Discord**: Join our community server
- **Email**: support@foodandfast.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI community for the excellent framework
- SQLAlchemy team for the ORM
- Docker team for containerization
- All contributors to this project

---

**Made with ❤️ by the Food & Fast Team**
