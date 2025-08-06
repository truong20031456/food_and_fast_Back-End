# 🛍️ Product Service

## Overview

The Product Service is a core microservice within the Food & Fast E-Commerce platform, dedicated to managing all aspects of the product catalog. It handles products, categories, inventory, customer reviews, and advanced search functionalities, ensuring a seamless and efficient shopping experience.

## ✨ Features

-   **Product Catalog Management**: Comprehensive CRUD operations for products and categories.
-   **Real-time Inventory**: Accurate stock tracking, updates, and low-stock alerts.
-   **Customer Reviews & Ratings**: Integrated system for product feedback.
-   **Advanced Search**: Powerful full-text search with filtering, sorting, and suggestions.
-   **Image Handling**: Secure storage and optimization for product images.
-   **Performance Optimized**: Built for speed with caching, pagination, and efficient queries.
-   **Monitoring & Observability**: Health checks, structured logging, and performance metrics.

## 🚀 Tech Stack

-   **Framework**: FastAPI (Python)
-   **Database**: PostgreSQL (Asynchronous with `asyncpg`)
-   **ORM**: SQLAlchemy (Async)
-   **Search**: PostgreSQL Full-Text Search
-   **Validation**: Pydantic
-   **Testing**: Pytest
-   **Containerization**: Docker

## 📂 Project Structure

```
product_service/
├── controllers/          # API route handlers
├── core/                 # Core configuration, database, and utilities
├── models/               # SQLAlchemy ORM models
├── schemas/              # Pydantic data validation schemas
├── modules/              # Business logic modules (e.g., catalog, inventory, reviews)
├── tests/                # Unit and integration tests
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker build instructions
└── .env.example          # Example environment variables
```

## 🔌 API Endpoints

The service exposes a comprehensive set of RESTful APIs:

-   `/products`: Manage product listings, details, and images.
-   `/categories`: Handle product categories and their relationships.
-   `/inventory`: Track and update product stock levels.
-   `/reviews`: Submit, retrieve, and manage product reviews.
-   `/search`: Perform advanced product searches and get suggestions.

Detailed endpoint specifications are available via the auto-generated OpenAPI documentation.

## ⚙️ Environment Variables

Configure the service using a `.env` file based on `.env.example`:

```env
# Database Connection
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/product_db"
DATABASE_ECHO=False # Set to True for SQL query logging

# Application Settings
HOST="0.0.0.0"
PORT=8002
DEBUG=True

# Cross-Origin Resource Sharing (CORS)
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Upload Configuration
MAX_FILE_SIZE=10485760 # 10MB
UPLOAD_DIR="./uploads"
ALLOWED_EXTENSIONS="jpg,jpeg,png,webp"

# Search & Pagination
SEARCH_RESULTS_LIMIT=50
MIN_SEARCH_LENGTH=2
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL="INFO"
```

## 🚀 Installation & Local Setup

### Prerequisites

-   Python 3.9+
-   PostgreSQL
-   Docker (optional, for containerized deployment)

### Steps

1.  **Clone the repository and navigate to the service directory:**
    ```bash
    git clone <repository_url>
    cd food-fast-ecommerce/Back-End/food-fast-ecommerce/product_service
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    ```bash
    cp .env.example .env
    # Open .env and update with your database credentials and other settings.
    ```

5.  **Initialize the database schema:**
    ```bash
    python -c "import asyncio; from core.database import init_db; asyncio.run(init_db())"
    ```

6.  **Start the FastAPI application:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8002
    ```
    The service will be accessible at `http://localhost:8002`.

### Docker Deployment

1.  **Build the Docker image:**
    ```bash
    docker build -t product-service:latest .
    ```

2.  **Run the container (ensure PostgreSQL is accessible):**
    ```bash
    docker run -d --name product-service -p 8002:8002 --env-file .env product-service:latest
    ```

## ✅ Testing

Run tests using `pytest`:

-   **All tests**: `pytest`
-   **With coverage**: `pytest --cov=./modules`
-   **Specific file**: `pytest tests/test_products.py`

## 📚 API Documentation

Once the service is running, access the interactive API documentation:

-   **Swagger UI**: `http://localhost:8002/docs`
-   **ReDoc**: `http://localhost:8002/redoc`
-   **Health Check**: `http://localhost:8002/health`

## 🤝 Contributing

Contributions are welcome! Please refer to the main repository's `CONTRIBUTING.md` for guidelines.

## 📄 License

This project is part of the Food & Fast E-Commerce platform and is licensed under the [MIT License](LICENSE).