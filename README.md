# Product Service

## Overview

The Product Service is a microservice responsible for managing product catalog, categories, inventory, reviews, and search functionality in the Food & Fast E-Commerce platform. It provides comprehensive product management capabilities including CRUD operations, inventory tracking, and advanced search features.

## Features

- 🛍️ **Product Catalog**: Complete product management with categories
- 📦 **Inventory Management**: Real-time stock tracking and updates
- ⭐ **Review System**: Product reviews and ratings
- 🔍 **Advanced Search**: Full-text search with filters and sorting
- 📸 **Image Management**: Product image handling and optimization
- 📊 **Category Management**: Hierarchical category structure
- 🔄 **Real-time Updates**: Live inventory and product updates
- 📈 **Analytics**: Product performance metrics

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Search**: Full-text search with PostgreSQL
- **Image Processing**: Pillow
- **Validation**: Pydantic
- **Testing**: pytest
- **Documentation**: Auto-generated OpenAPI/Swagger

## Project Structure

```
product_service/
├── controllers/          # API route handlers
│   ├── product_controller.py
│   ├── category_controller.py
│   ├── inventory_controller.py
│   ├── review_controller.py
│   ├── search_controller.py
│   └── __init__.py
├── core/                # Core configuration and database
│   ├── config.py        # Application settings
│   └── database.py      # Database connection
├── models/              # SQLAlchemy models
│   ├── base.py
│   ├── product.py
│   ├── category.py
│   ├── inventory.py
│   ├── review.py
│   └── product_image.py
├── schemas/             # Pydantic schemas
│   ├── product.py
│   ├── category.py
│   ├── inventory.py
│   ├── review.py
│   └── common.py
├── modules/             # Business logic modules
│   ├── catalog/
│   │   └── catalog_service.py
│   ├── inventory/
│   │   └── inventory_service.py
│   └── reviews/
│       └── review_service.py
├── utils/               # Utility functions
│   └── logger.py
├── tests/               # Test files
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
├── pytest.ini         # pytest configuration
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Products
- `GET /products` - List all products with pagination and filters
- `GET /products/{product_id}` - Get product by ID
- `POST /products` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product
- `GET /products/{product_id}/images` - Get product images
- `POST /products/{product_id}/images` - Upload product images

### Categories
- `GET /categories` - List all categories
- `GET /categories/{category_id}` - Get category by ID
- `POST /categories` - Create new category
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category
- `GET /categories/{category_id}/products` - Get products by category

### Inventory
- `GET /inventory` - List inventory items
- `GET /inventory/{product_id}` - Get inventory for product
- `PUT /inventory/{product_id}` - Update inventory
- `POST /inventory/bulk-update` - Bulk inventory update
- `GET /inventory/low-stock` - Get low stock alerts

### Reviews
- `GET /reviews` - List reviews with filters
- `GET /reviews/{review_id}` - Get review by ID
- `POST /reviews` - Create new review
- `PUT /reviews/{review_id}` - Update review
- `DELETE /reviews/{review_id}` - Delete review
- `GET /products/{product_id}/reviews` - Get reviews for product

### Search
- `GET /search` - Search products with filters
- `GET /search/suggestions` - Get search suggestions
- `GET /search/trending` - Get trending products
- `POST /search/advanced` - Advanced search with complex filters

## Environment Variables

Create a `.env` file in the product_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_db

# Application
HOST=0.0.0.0
PORT=8002
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

# Search
SEARCH_RESULTS_LIMIT=50
MIN_SEARCH_LENGTH=2

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

### Local Development

1. **Clone the repository**
   ```bash
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
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   # Create tables (if using SQLAlchemy create_all)
   python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t product-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8002:8002 --env-file .env product-service
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
pytest tests/test_products.py
```

### Run health check tests
```bash
pytest tests/test_health.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/health
- **Root**: http://localhost:8002/

## Database Schema

### Products Table
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `category_id`: Foreign key to categories
- `sku`: Stock keeping unit
- `is_active`: Product availability
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Categories Table
- `id`: Primary key
- `name`: Category name
- `description`: Category description
- `parent_id`: Parent category (for hierarchy)
- `is_active`: Category availability
- `created_at`: Creation timestamp

### Inventory Table
- `id`: Primary key
- `product_id`: Foreign key to products
- `quantity`: Available quantity
- `reserved_quantity`: Reserved quantity
- `min_stock_level`: Minimum stock threshold
- `updated_at`: Last update timestamp

### Reviews Table
- `id`: Primary key
- `product_id`: Foreign key to products
- `user_id`: Foreign key to users
- `rating`: Review rating (1-5)
- `comment`: Review comment
- `is_verified`: Purchase verification
- `created_at`: Creation timestamp

### Product Images Table
- `id`: Primary key
- `product_id`: Foreign key to products
- `image_url`: Image URL/path
- `alt_text`: Image alt text
- `is_primary`: Primary image flag
- `order_index`: Display order
- `created_at`: Creation timestamp

## Search Features

### Full-text Search
- Product name and description search
- Category-based filtering
- Price range filtering
- Rating filtering
- Availability filtering

### Advanced Search
- Multiple category selection
- Brand filtering
- Date range filtering
- Sort by relevance, price, rating, date

## Image Management

- **Supported Formats**: JPG, JPEG, PNG, WebP
- **Size Limits**: Configurable maximum file size
- **Optimization**: Automatic image optimization
- **Multiple Images**: Support for multiple product images
- **Primary Image**: Designated primary product image

## Performance Features

- **Pagination**: Efficient pagination for large datasets
- **Caching**: Redis-based caching for frequently accessed data
- **Indexing**: Database indexes for fast search and queries
- **Lazy Loading**: Efficient loading of related data

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Structured Logging**: Consistent log format
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Query performance monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 