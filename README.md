# � Food Fast E-commerce Backend

A comprehensive, production-ready microservices-based e-commerce platform for food delivery built with FastAPI, featuring advanced analytics, security, and scalability.

## 🏗️ Architecture Overview

This project follows a sophisticated microservices architecture with enterprise-grade features:

### Core Services
- **🚪 API Gateway**: Intelligent routing, rate limiting, and request aggregation
- **🔐 Auth Service**: JWT authentication, OAuth2, 2FA, and role-based access control
- **� User Service**: User management, profiles, preferences, and loyalty programs
- **🛒 Product Service**: Product catalog, inventory, recommendations, and search
- **📋 Order Service**: Order processing, cart management, and order tracking
- **💳 Payment Service**: Multi-gateway payment processing (Stripe, PayPal)
- **📧 Notification Service**: Multi-channel notifications (Email, SMS, Push)
- **📊 Analytics Service**: Real-time analytics, ML recommendations, and business intelligence

### Supporting Infrastructure
- **🔄 Background Workers**: Celery task processing
- **� Monitoring**: Prometheus metrics + Grafana dashboards
- **🔍 Logging**: ELK stack (Elasticsearch, Logstash, Kibana)
- **🛡️ Security**: Rate limiting, CSRF protection, encryption at rest
- **🚀 Performance**: Redis caching, connection pooling, async processing

## �️ Technology Stack

### Backend Framework
- **FastAPI 0.104+**: Modern, fast web framework with automatic API documentation
- **Python 3.11+**: Latest Python features and performance improvements
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy 2.0**: Modern async ORM with type safety

### Data Storage
- **PostgreSQL 15**: Primary database with advanced features
- **Redis 7**: Caching, session storage, and message broker
- **Elasticsearch 8**: Full-text search and log aggregation

### Security & Authentication
- **JWT**: Stateless authentication tokens
- **OAuth2**: Google, Facebook social login
- **2FA**: Time-based one-time passwords (TOTP)
- **Encryption**: AES-256 for sensitive data

### Infrastructure & Deployment
- **Docker**: Containerization with multi-stage builds
- **Docker Compose**: Local development and staging deployment
- **Nginx**: Reverse proxy and load balancing
- **GitHub Actions**: CI/CD pipeline with automated testing

### Monitoring & Observability
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **OpenTelemetry**: Distributed tracing
- **Sentry**: Error tracking and performance monitoring

## 📊 Service Status

| Service | Port | Status | Features |
|---------|------|--------|----------|
| 🌐 **API Gateway** | `8000` | ✅ **Production Ready** | Rate limiting, JWT validation, request routing |
| 🔐 **Auth Service** | `8001` | ✅ **Production Ready** | JWT, OAuth2, 2FA, role-based access |
| 👤 **User Service** | `8002` | ✅ **Production Ready** | Profiles, preferences, loyalty program |
| 📦 **Product Service** | `8003` | ✅ **Production Ready** | Catalog, search, recommendations, inventory |
| 🛒 **Order Service** | `8004` | ✅ **Production Ready** | Cart, orders, tracking, status management |
| 💳 **Payment Service** | `8005` | ✅ **Production Ready** | Stripe, PayPal, webhooks, refunds |
| 📱 **Notification Service** | `8006` | ✅ **Production Ready** | Email, SMS, push notifications, templates |
| 📈 **Analytics Service** | `8007` | ✅ **Production Ready** | Real-time analytics, ML recommendations, BI |

## 📁 Project Structure

## 🚀 Bắt đầu nhanh (Quick Start)

### Yêu cầu
- Docker & Docker Compose
- Git

### Cài đặt với một lệnh duy nhất
```bash
# 1. Clone a project
git clone https://github.com/truong20031456/food_and_fast_Back-End.git
cd food-fast-ecommerce/Back-End/food-fast-ecommerce

# 2. Sao chép tệp môi trường
cp .env.example .env
# Mở tệp .env và cấu hình các biến cần thiết (JWT_SECRET_KEY, DATABASE_URL,...)

# 3. Khởi chạy toàn bộ hệ thống
docker-compose up -d
```

Sau khi khởi chạy, hệ thống sẽ có sẵn tại các cổng đã được cấu hình.

---

## 🛠️ Phát triển & Testing

### Chạy một Service riêng lẻ
Nếu bạn chỉ muốn phát triển một service cụ thể (ví dụ: `auth_service`):

```bash
# 1. Chỉ khởi chạy các dịch vụ hạ tầng
docker-compose up -d postgres redis elasticsearch

# 2. Cài đặt môi trường ảo và dependencies cho service
cd auth_service
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Chạy service với hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Chạy Tests
Để đảm bảo chất lượng code, hãy chạy test trong thư mục của từng service:
```bash
cd auth_service
pytest
```

---

## 📝 Tài liệu API (Swagger)

Mỗi service đều tự động tạo tài liệu API tương tác. Sau khi khởi chạy, bạn có thể truy cập:

- **API Gateway:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Auth Service:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **User Service:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **Product Service:** [http://localhost:8003/docs](http://localhost:8003/docs)
- ... và các service khác tại cổng tương ứng.

---

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi sự đóng góp! Vui lòng tạo **Fork** và gửi **Pull Request**.

## � CI/CD Pipeline

### ✅ **Production Features**
- **🏗️ Production Docker Compose**: Resource limits, health checks, monitoring stack
- **🗄️ Database Migration Automation**: Automated migrations with backup and rollback
- **🔥 Load Testing Integration**: Automated Locust testing with CI/CD integration
- **🧪 E2E Testing Pipeline**: End-to-end testing with security scanning
- **📊 Monitoring & Alerting**: Prometheus metrics with Grafana dashboards

### **Deployment Commands**
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Database migrations
./scripts/migrate.sh

# Load testing
python scripts/load_test.py --scenario=load
```

---

## 🏗️ Service Architecture Standards

### **Standardized Structure**
All services follow this consistent structure:
```
{service_name}/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── .env.example        # Environment template
├── README.md           # Service documentation
├── api/routers/        # API route handlers
├── core/              # Core configuration
├── models/            # Data models
├── schemas/           # API schemas
├── services/          # Business logic
└── tests/             # Test suite
```

### **Shared App Factory Pattern**
All services use the standardized pattern:
```python
from shared_code.core.app import create_app

app = create_app(
    service_name="Service Name",
    settings=settings,
    routers=[router1, router2],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)
```

---

## 🔧 Development Guidelines

### **Adding a New Service**
1. Copy the standardized service template
2. Update service-specific configuration
3. Implement business logic in `services/`
4. Add API routes in `api/routers/`
5. Write tests in `tests/`

### **Shared Code Usage**
- **Core**: Application factory, configuration, database
- **Cache**: Redis caching with unified interface
- **Utils**: Logging, security, validation utilities
- **Models**: Shared database models

---

## �📄 Giấy phép

Dự án này được cấp phép theo [MIT License](LICENSE).