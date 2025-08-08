# Analytics Service

## Overview

The Analytics Service is a microservice responsible for collecting, processing, and analyzing data from across the Food & Fast E-Commerce platform. It provides comprehensive business intelligence, reporting, and data analytics capabilities powered by **Elasticsearch** for high-performance search and analytics.

## Features

- 📊 **Business Intelligence**: Comprehensive business metrics and KPIs
- 📈 **Sales Analytics**: Revenue tracking and sales performance analysis
- 👥 **User Analytics**: User behavior and engagement metrics
- 🛍️ **Product Analytics**: Product performance and inventory insights
- 📋 **Order Analytics**: Order processing and fulfillment metrics
- 💳 **Payment Analytics**: Payment processing and financial insights
- 🔄 **Real-time Dashboards**: Live data visualization and monitoring
- 📊 **Custom Reports**: Configurable reporting and data export
- 🔍 **Elasticsearch Integration**: High-performance search and analytics
- ⚡ **Real-time Data Processing**: Stream processing for live analytics
- 📊 **Kibana Dashboards**: Advanced data visualization

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Search & Analytics**: Elasticsearch 8.11+
- **Visualization**: Kibana, Plotly, Matplotlib
- **Data Processing**: Pandas, NumPy
- **Caching**: Redis
- **Queue**: Redis/RabbitMQ for data processing
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
analytics_service/
├── core/                    # Core modules
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection
│   └── elasticsearch_client.py # Elasticsearch client
├── services/               # Analytics services
│   ├── analytics_service.py           # Main analytics service
│   ├── elasticsearch_analytics_service.py # Elasticsearch analytics
│   ├── sales_report.py     # Sales reports
│   └── dashboard_service.py # Dashboard service
├── controllers/            # API controllers
│   └── analytics_controller.py # Analytics endpoints
├── schemas/               # Pydantic schemas
│   └── analytics.py       # Analytics schemas
├── scripts/               # Utility scripts
│   ├── generate_sample_data.py      # Sample data generator
│   ├── start_with_elasticsearch.sh  # Bash startup script
│   └── start_with_elasticsearch.ps1 # PowerShell startup script
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker services configuration
└── Dockerfile            # Docker configuration
```

## API Endpoints

### Core Analytics
- `GET /api/v1/analytics/dashboard` - Main dashboard data
- `GET /api/v1/analytics/products/top-selling` - Top selling products
- `GET /api/v1/analytics/users/activity` - User activity summary
- `GET /api/v1/analytics/revenue/trends` - Revenue trends analysis

### Elasticsearch Integration
- `POST /api/v1/analytics/events/track` - Track analytics events
- `POST /api/v1/analytics/orders/index` - Index order data
- `POST /api/v1/analytics/user-activity/index` - Index user activity
- `GET /api/v1/analytics/search` - Search analytics data
- `GET /api/v1/analytics/health/elasticsearch` - Elasticsearch health

### Sales Analytics
- `GET /analytics/sales/revenue` - Revenue analytics
- `GET /analytics/sales/orders` - Order analytics
- `GET /analytics/sales/products` - Product sales performance
- `GET /analytics/sales/categories` - Category performance
- `GET /analytics/sales/geographic` - Geographic sales data

### User Analytics
- `GET /analytics/users/behavior` - User behavior analysis
- `GET /analytics/users/engagement` - User engagement metrics
- `GET /analytics/users/retention` - User retention analysis
- `GET /analytics/users/conversion` - Conversion funnel analysis
- `GET /analytics/users/segments` - User segmentation

### Product Analytics
- `GET /analytics/products/performance` - Product performance metrics
- `GET /analytics/products/inventory` - Inventory analytics
- `GET /analytics/products/reviews` - Product review analytics
- `GET /analytics/products/search` - Search analytics

### Financial Analytics
- `GET /analytics/financial/revenue` - Revenue breakdown
- `GET /analytics/financial/profit` - Profitability analysis
- `GET /analytics/financial/expenses` - Expense tracking
- `GET /analytics/financial/payments` - Payment method analytics

### Custom Reports
- `POST /reports/generate` - Generate custom report
- `GET /reports/{report_id}` - Get report status
- `GET /reports/{report_id}/download` - Download report
- `GET /reports/history` - Report history

### Data Export
- `GET /export/sales` - Export sales data
- `GET /export/users` - Export user data
- `GET /export/products` - Export product data
- `GET /export/orders` - Export order data

## Quick Start with Elasticsearch

### Option 1: Using Google Cloud Elasticsearch (Recommended for Production)

1. **Configure cloud settings:**
   ```bash
   # Copy cloud configuration
   cp .env.cloud .env
   
   # Update .env with your cloud credentials:
   # ELASTICSEARCH_HOST=your-cloud-host
   # ELASTICSEARCH_API_KEY=your-api-key
   ```

2. **Start with cloud Elasticsearch:**
   ```bash
   # On Windows (PowerShell)
   .\scripts\start_with_cloud_elasticsearch.ps1

   # Manual setup:
   # Start only local services (Redis, PostgreSQL)
   docker-compose up redis postgres -d
   
   # Test cloud connection
   python scripts/test_elasticsearch_cloud.py
   
   # Install dependencies and start
   pip install -r requirements.txt
   python main.py
   ```

### Option 2: Using Local Docker Elasticsearch (Development)

1. **Start with local Elasticsearch:**
   ```bash
   # On Linux/Mac
   ./scripts/start_with_elasticsearch.sh

   # On Windows (PowerShell)
   .\scripts\start_with_elasticsearch.ps1
   ```

2. **Manual setup:**
   ```bash
   # Copy local configuration
   cp .env.example .env

   # Start all local services including Elasticsearch
   docker-compose --profile local-es up -d

   # Install Python dependencies
   pip install -r requirements.txt

   # Generate sample data (optional)
   python scripts/generate_sample_data.py

   # Start the service
   python main.py
   ```

## Environment Variables

Create a `.env` file in the analytics_service directory:

```env
# Application Settings
APP_NAME=Analytics Service
DEBUG=false
LOG_LEVEL=INFO
PORT=8001

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=password
DB_NAME=analytics_db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_SCHEME=http
ELASTICSEARCH_VERIFY_CERTS=false

# Elasticsearch Index Names
ELASTICSEARCH_ANALYTICS_INDEX=analytics
ELASTICSEARCH_ORDER_INDEX=orders
ELASTICSEARCH_USER_ACTIVITY_INDEX=user_activity
ELASTICSEARCH_PRODUCT_INDEX=products

# External Services
ORDER_SERVICE_URL=http://localhost:8003
PRODUCT_SERVICE_URL=http://localhost:8002
USER_SERVICE_URL=http://localhost:8006

# Analytics Settings
ANALYTICS_DATA_RETENTION_DAYS=365
ANALYTICS_REAL_TIME_TRACKING=true
ANALYTICS_BATCH_PROCESSING=true
```

## Elasticsearch Integration

### Data Flow
1. **Order Events**: Automatically indexed when orders are processed
2. **User Activity**: Tracked and indexed in real-time
3. **Product Analytics**: Updated based on sales and interactions
4. **Custom Events**: Track any business event via API

### Sample Data Generation
Generate sample data for testing:
```bash
python scripts/generate_sample_data.py
```

This creates:
- 1,000 sample orders
- 5,000 user activity records
- Product analytics data
- Analytics events

### Kibana Dashboards
Access Kibana at `http://localhost:5601` to create visualizations:
- Revenue trends
- User behavior patterns
- Product performance
- Order analytics

### Search Capabilities
Use the search API to query analytics data:
```bash
curl -X GET "localhost:8001/api/v1/analytics/search?query=order_placed&size=10"
```
MAX_DATA_POINTS=1000

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
   cd analytics_service
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
   uvicorn main:app --reload --host 0.0.0.0 --port 8007
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t analytics-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8007:8007 --env-file .env analytics-service
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
pytest tests/test_analytics.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8007/docs
- **ReDoc**: http://localhost:8007/redoc
- **Health Check**: http://localhost:8007/health

## Database Schema

### Analytics Events Table
- `id`: Primary key
- `event_type`: Event type (page_view, purchase, etc.)
- `user_id`: Foreign key to users
- `session_id`: User session identifier
- `event_data`: Event-specific data (JSON)
- `timestamp`: Event timestamp
- `source`: Event source (web, mobile, api)

### Metrics Table
- `id`: Primary key
- `metric_name`: Metric identifier
- `metric_value`: Metric value
- `dimension`: Metric dimension (date, product, user)
- `dimension_value`: Dimension value
- `timestamp`: Metric timestamp
- `aggregation_type`: Aggregation type (sum, avg, count)

### Reports Table
- `id`: Primary key
- `report_name`: Report name
- `report_type`: Report type
- `parameters`: Report parameters (JSON)
- `status`: Report status (pending, processing, completed, failed)
- `file_path`: Generated report file path
- `created_at`: Report creation timestamp
- `completed_at`: Report completion timestamp

### Dashboards Table
- `id`: Primary key
- `dashboard_name`: Dashboard name
- `dashboard_config`: Dashboard configuration (JSON)
- `user_id`: Dashboard owner
- `is_public`: Public dashboard flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Analytics Categories

### Business Intelligence
- **Revenue Metrics**: Total revenue, growth rate, average order value
- **Order Metrics**: Order volume, conversion rate, order status distribution
- **Customer Metrics**: Customer acquisition, retention, lifetime value
- **Product Metrics**: Product performance, inventory turnover, category analysis

### User Analytics
- **Behavior Analysis**: Page views, session duration, bounce rate
- **Engagement Metrics**: Time on site, pages per session, return visits
- **Conversion Funnel**: Cart abandonment, checkout completion, payment success
- **User Segmentation**: Demographics, purchase behavior, loyalty tiers

### Product Analytics
- **Performance Metrics**: Sales volume, revenue contribution, profit margin
- **Inventory Analytics**: Stock levels, turnover rate, reorder points
- **Review Analytics**: Rating distribution, review sentiment, review volume
- **Search Analytics**: Search queries, search results, product discovery

### Financial Analytics
- **Revenue Analysis**: Revenue by period, payment methods, geographic distribution
- **Profitability**: Gross margin, net profit, cost analysis
- **Payment Analytics**: Payment success rate, refund rate, chargeback analysis
- **Expense Tracking**: Operational costs, marketing spend, overhead analysis

## Report Types

### Standard Reports
- **Daily Sales Report**: Daily revenue and order summary
- **Weekly Performance Report**: Weekly business performance overview
- **Monthly Business Review**: Comprehensive monthly analysis
- **Quarterly Executive Summary**: High-level quarterly insights

### Custom Reports
- **Product Performance Report**: Detailed product analysis
- **Customer Behavior Report**: User behavior insights
- **Marketing Campaign Report**: Campaign performance analysis
- **Inventory Report**: Stock level and turnover analysis

### Real-time Dashboards
- **Live Sales Dashboard**: Real-time sales monitoring
- **Order Status Dashboard**: Live order tracking
- **User Activity Dashboard**: Real-time user engagement
- **System Health Dashboard**: Service performance monitoring

## Data Processing

### Data Collection
- **Event Tracking**: User interaction events
- **Transaction Data**: Order and payment data
- **User Data**: Profile and behavior data
- **Product Data**: Inventory and performance data

### Data Processing
- **Batch Processing**: Scheduled data aggregation
- **Real-time Processing**: Live data updates
- **Data Cleaning**: Data validation and normalization
- **Data Enrichment**: Additional context and metadata

### Data Storage
- **Raw Data**: Unprocessed event data
- **Aggregated Data**: Processed metrics and KPIs
- **Cached Data**: Frequently accessed data
- **Archived Data**: Historical data storage

## Visualization Features

### Chart Types
- **Line Charts**: Time series data
- **Bar Charts**: Categorical comparisons
- **Pie Charts**: Proportional data
- **Scatter Plots**: Correlation analysis
- **Heatmaps**: Multi-dimensional data

### Dashboard Features
- **Interactive Charts**: Zoom, filter, drill-down
- **Real-time Updates**: Live data refresh
- **Customizable Layout**: Drag-and-drop widgets
- **Export Capabilities**: Chart and data export
- **Mobile Responsive**: Mobile-friendly dashboards

## Performance Features

- **Caching**: Redis-based caching for frequently accessed data
- **Data Aggregation**: Pre-computed metrics for fast queries
- **Indexing**: Database indexes for fast data retrieval
- **Async Processing**: Background data processing
- **Connection Pooling**: Database connection optimization

## Security Features

- **Data Access Control**: Role-based data access
- **Data Encryption**: Sensitive data encryption
- **Audit Logging**: Data access audit trail
- **API Rate Limiting**: Request rate limiting
- **Input Validation**: Data validation and sanitization

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Performance Metrics**: Query performance monitoring
- **Error Tracking**: Data processing error logging
- **Business Metrics**: Key business indicators tracking
- **System Metrics**: Resource usage monitoring

## Data Export

### Export Formats
- **CSV**: Comma-separated values
- **Excel**: Microsoft Excel format
- **JSON**: JavaScript Object Notation
- **PDF**: Portable Document Format

### Export Features
- **Filtered Exports**: Data filtering and selection
- **Scheduled Exports**: Automated report generation
- **Email Delivery**: Report delivery via email
- **File Storage**: Secure file storage and access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 