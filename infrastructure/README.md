# 🍕 Food Fast Platform - Setup & Configuration Guide

A comprehensive microservices-based food delivery platform with enterprise-grade features including high availability, monitoring, logging, and security.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Service Architecture](#service-architecture)
- [Database Setup](#database-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Security Configuration](#security-configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **Docker**: >= 20.10.0
- **Docker Compose**: >= 2.0.0
- **RAM**: Minimum 8GB (Recommended 16GB+)
- **CPU**: Minimum 4 cores
- **Storage**: Minimum 50GB free space

### Development Tools
- **Git**: Latest version
- **Make**: For automation scripts
- **OpenSSL**: For SSL certificate generation

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd food-fast-platform
```

### 2. Create Environment File
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

### 3. Generate SSL Certificates
```bash
make generate-ssl
# OR manually:
./scripts/generate-ssl.sh
```

### 4. Initialize Configuration Files
```bash
make init-config
# OR manually create config files (see Configuration Files section)
```

### 5. Start Infrastructure Services
```bash
docker-compose up -d postgres_primary redis_master elasticsearch rabbitmq
```

### 6. Wait for Services to be Ready
```bash
# Check health status
docker-compose ps
# Wait until all services show "healthy"
```

### 7. Start Application Services
```bash
docker-compose up -d
```

### 8. Verify Deployment
```bash
# Check all services
curl http://localhost/health

# Access monitoring
# Grafana: http://localhost:3000 (admin/your_password)
# Prometheus: http://localhost:9090
# Kibana: http://localhost:5601
# RabbitMQ: http://localhost:15672
```

## 📁 Configuration Files

Create the following directory structure and configuration files:

### Directory Structure
```
food-fast-platform/
├── .env
├── docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       ├── api-gateway.conf
│       ├── grafana.conf
│       └── kibana.conf
├── ssl/
│   ├── cert.pem
│   └── key.pem
├── postgres/
│   ├── postgresql.conf
│   ├── pg_hba.conf
│   └── init/
│       ├── 01-init-databases.sql
│       └── 02-init-users.sql
├── redis/
│   ├── redis.conf
│   └── sentinel.conf
├── elasticsearch/
│   └── elasticsearch.yml
├── rabbitmq/
│   └── rabbitmq.conf
├── monitoring/
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   └── alertmanager.yml
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   └── dashboards/
│   └── dashboards/
├── elk/
│   └── logstash/
│       ├── config/
│       │   └── logstash.yml
│       └── pipeline/
│           └── logstash.conf
├── scripts/
│   ├── backup-postgres.sh
│   ├── generate-ssl.sh
│   └── health-check.sh
└── security/
    └── trivy-scan.sh
```

### 1. Nginx Configuration

**nginx/nginx.conf**
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

    # Upstream servers
    upstream api_gateway {
        least_conn;
        server api_gateway_1:8000 max_fails=3 fail_timeout=30s;
        server api_gateway_2:8000 max_fails=3 fail_timeout=30s;
    }

    # Include site configurations
    include /etc/nginx/conf.d/*.conf;
}
```

**nginx/conf.d/api-gateway.conf**
```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name localhost api.foodfast.local;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API Gateway
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://api_gateway/health;
    }

    # Auth endpoints with stricter rate limiting
    location /auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. PostgreSQL Configuration

**postgres/postgresql.conf**
```conf
# Connection settings
listen_addresses = '*'
port = 5432
max_connections = 200

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# WAL settings for replication
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
wal_keep_size = 256MB

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'mod'
log_min_duration_statement = 1000

# Performance
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
```

**postgres/pg_hba.conf**
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             172.22.0.0/24           md5
host    replication     replicator      172.22.0.0/24           md5
```

**postgres/init/01-init-databases.sql**
```sql
-- Create databases for each service
CREATE DATABASE auth_service_db;
CREATE DATABASE user_service_db;
CREATE DATABASE product_service_db;
CREATE DATABASE order_service_db;
CREATE DATABASE payment_service_db;
CREATE DATABASE notification_service_db;
CREATE DATABASE analytics_service_db;

-- Create replication user
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';
```

### 3. Redis Configuration

**redis/redis.conf**
```conf
# Network
bind 0.0.0.0
port 6379
protected-mode no

# General
daemonize no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""

# Snapshotting
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Security
requirepass your_redis_password

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Append only file
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
```

**redis/sentinel.conf**
```conf
port 26379
sentinel monitor mymaster redis_master 6379 1
sentinel auth-pass mymaster your_redis_password
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1
```

### 4. Elasticsearch Configuration

**elasticsearch/elasticsearch.yml**
```yaml
cluster.name: food-fast-cluster
node.name: elasticsearch
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs
network.host: 0.0.0.0
discovery.type: single-node
bootstrap.memory_lock: true

# Security
xpack.security.enabled: true
xpack.security.authc.api_key.enabled: true

# Performance
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 20%
```

### 5. RabbitMQ Configuration

**rabbitmq/rabbitmq.conf**
```conf
# Network
listeners.tcp.default = 5672
management.tcp.port = 15672

# Security
default_user = food_fast_mq
default_pass = mq_secure_password
default_vhost = food_fast

# Performance
vm_memory_high_watermark.relative = 0.6
disk_free_limit.relative = 2.0

# Clustering
cluster_formation.peer_discovery_backend = classic_config
```

### 6. Monitoring Configuration

**monitoring/prometheus.yml**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api_gateway_1:8000', 'api_gateway_2:8000']
    metrics_path: '/metrics'

  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth_service:8001']
    metrics_path: '/metrics'

  - job_name: 'user-service'
    static_configs:
      - targets: ['user_service:8002']
    metrics_path: '/metrics'

  - job_name: 'product-service'
    static_configs:
      - targets: ['product_service:8003']
    metrics_path: '/metrics'

  - job_name: 'order-service'
    static_configs:
      - targets: ['order_service:8004']
    metrics_path: '/metrics'

  - job_name: 'payment-service'
    static_configs:
      - targets: ['payment_service:8005']
    metrics_path: '/metrics'

  - job_name: 'notification-service'
    static_configs:
      - targets: ['notification_service:8006']
    metrics_path: '/metrics'

  - job_name: 'analytics-service'
    static_configs:
      - targets: ['analytics_service:8007']
    metrics_path: '/metrics'

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres_exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis_exporter:9121']

  - job_name: 'elasticsearch-exporter'
    static_configs:
      - targets: ['elasticsearch_exporter:9114']

  - job_name: 'rabbitmq-exporter'
    static_configs:
      - targets: ['rabbitmq_exporter:9419']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node_exporter:9100']
```

**monitoring/alert_rules.yml**
```yaml
groups:
  - name: food_fast_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"

      - alert: DatabaseConnectionHigh
        expr: pg_stat_activity_count > 150
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "PostgreSQL connections are above 150"

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Redis memory usage"
          description: "Redis memory usage is above 90%"
```

**monitoring/alertmanager.yml**
```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@foodfast.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@foodfast.com'
        subject: 'Food Fast Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Food Fast Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

## 🔐 Environment Variables

Create a `.env` file with the following variables:

```bash
# ===== DATABASE CONFIGURATION =====
DATABASE_NAME=food_fast_db
DATABASE_USER=food_fast_user
DATABASE_PASSWORD=your_secure_database_password
POSTGRES_REPLICATION_USER=replicator
POSTGRES_REPLICATION_PASSWORD=your_replication_password

# ===== CACHE CONFIGURATION =====
REDIS_PASSWORD=your_secure_redis_password

# ===== SEARCH CONFIGURATION =====
ELASTIC_PASSWORD=your_secure_elastic_password

# ===== MESSAGE QUEUE CONFIGURATION =====
RABBITMQ_USER=food_fast_mq
RABBITMQ_PASSWORD=your_secure_rabbitmq_password
RABBITMQ_VHOST=food_fast

# ===== SECURITY CONFIGURATION =====
JWT_SECRET=your_very_long_and_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your_32_byte_encryption_key_here

# ===== PAYMENT CONFIGURATION =====
# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox  # or live for production

# ===== NOTIFICATION CONFIGURATION =====
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
SMTP_USE_TLS=true

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications (Firebase)
FCM_SERVER_KEY=your_fcm_server_key
FCM_PROJECT_ID=your_firebase_project_id

# ===== MONITORING CONFIGURATION =====
GRAFANA_ADMIN_PASSWORD=your_secure_grafana_password
GRAFANA_SECRET_KEY=your_32_byte_grafana_secret_key

# ===== BACKUP CONFIGURATION =====
BACKUP_RETENTION_DAYS=30
AWS_ACCESS_KEY_ID=your_aws_access_key  # for S3 backup
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your-backup-bucket
AWS_REGION=us-east-1

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
SENTRY_DSN=your_sentry_dsn_for_error_tracking

# ===== EXTERNAL SERVICES =====
# Google Maps API (for delivery tracking)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Social Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# ===== RATE LIMITING =====
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# ===== CORS CONFIGURATION =====
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization

# ===== SESSION CONFIGURATION =====
SESSION_SECRET=your_32_byte_session_secret_key
SESSION_TIMEOUT=3600  # 1 hour in seconds

# ===== FILE UPLOAD CONFIGURATION =====
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf
UPLOAD_PATH=/uploads

# ===== ENVIRONMENT =====
ENVIRONMENT=development  # development, staging, production
DEBUG=true  # set to false in production
```

## 🏗️ Service Architecture

The platform consists of the following services:

### Core Services
- **API Gateway** (Port 8000): Entry point, routing, authentication
- **Auth Service** (Port 8001): User authentication and authorization
- **User Service** (Port 8002): User profile management
- **Product Service** (Port 8003): Menu and product catalog
- **Order Service** (Port 8004): Order processing and management
- **Payment Service** (Port 8005): Payment processing
- **Notification Service** (Port 8006): Email, SMS, push notifications
- **Analytics Service** (Port 8007): Data analytics and reporting

### Infrastructure Services
- **PostgreSQL**: Primary database with replication
- **Redis**: Caching and session storage
- **Elasticsearch**: Search engine and log storage
- **RabbitMQ**: Message queue for async communication
- **Nginx**: Reverse proxy and load balancer

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Alertmanager**: Alert management
- **ELK Stack**: Log management (Elasticsearch, Logstash, Kibana)

## 🗄️ Database Setup

### Database Structure
Each service has its own database for data isolation:
- `auth_service_db`: User credentials, tokens
- `user_service_db`: User profiles, preferences
- `product_service_db`: Products, categories, inventory
- `order_service_db`: Orders, order items, status
- `payment_service_db`: Payment records, transactions
- `notification_service_db`: Notification logs, templates
- `analytics_service_db`: Analytics data, reports

### Migration Commands
```bash
# Run initial migrations
docker-compose exec auth_service python manage.py migrate
docker-compose exec user_service python manage.py migrate
docker-compose exec product_service python manage.py migrate
docker-compose exec order_service python manage.py migrate
docker-compose exec payment_service python manage.py migrate
docker-compose exec notification_service python manage.py migrate
docker-compose exec analytics_service python manage.py migrate

# Create superuser for admin access
docker-compose exec auth_service python manage.py createsuperuser
```

### Backup and Restore
```bash
# Manual backup
docker-compose exec postgres_backup /usr/local/bin/backup-postgres.sh

# Restore from backup
docker-compose exec postgres_primary pg_restore -U $DATABASE_USER -d $DATABASE_NAME /backups/backup_file.sql
```

## 📊 Monitoring & Logging

### Access Monitoring Dashboards
- **Grafana**: http://localhost:3000 (admin/your_grafana_password)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Kibana**: http://localhost:5601
- **RabbitMQ Management**: http://localhost:15672

### Key Metrics to Monitor
- **Application Metrics**: Request rate, response time, error rate
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Database Metrics**: Connection count, query performance
- **Cache Metrics**: Hit rate, memory usage
- **Business Metrics**: Orders per minute, revenue, user activity

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about service operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for recoverable errors
- **CRITICAL**: Critical errors that may cause service failure

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Generate self-signed certificates for development
./scripts/generate-ssl.sh

# For production, use Let's Encrypt or proper CA certificates
```

### Security Best Practices
1. **Change all default passwords** in .env file
2. **Use strong encryption keys** (32+ characters)
3. **Enable HTTPS** for all external communications
4. **Configure firewall rules** to restrict access
5. **Regular security scans** with Trivy
6. **Keep dependencies updated**
7. **Use secrets management** for production

### Network Security
- Services are isolated in separate networks
- Only necessary ports are exposed
- Internal communications use service names
- Rate limiting configured on API endpoints

## 🚢 Deployment

### Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api_gateway_1

# Scale services
docker-compose up -d --scale api_gateway_1=2
```

### Staging/Production Environment
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Deploy with zero downtime
./scripts/zero-downtime-deploy.sh

# Health check all services
./scripts/health-check.sh
```

### CI/CD Integration
The platform includes GitHub Actions workflows for:
- Code quality checks
- Security scanning
- Automated testing
- Docker image building
- Deployment automation

## 🔧 Utility Scripts

Create these helper scripts in the `scripts/` directory:

### scripts/generate-ssl.sh
```bash
#!/bin/bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
echo "SSL certificates generated in ssl/ directory"
```

### scripts/health-check.sh
```bash
#!/bin/bash
services=("api_gateway_1" "auth_service" "user_service" "product_service" "order_service" "payment_service" "notification_service" "analytics_service")

for service in "${services[@]}"; do
    echo "Checking $service..."
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is unhealthy"
    fi
done
```

### scripts/backup-postgres.sh
```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASES=("auth_service_db" "user_service_db" "product_service_db" "order_service_db" "payment_service_db" "notification_service_db" "analytics_service_db")

mkdir -p $BACKUP_DIR

for db in "${DATABASES[@]}"; do
    echo "Backing up $db..."
    pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $db > "$BACKUP_DIR/${db}_${DATE}.sql"
done

# Clean old backups
find $BACKUP_DIR -name "*.sql" -mtime +$BACKUP_RETENTION_DAYS -delete
echo "Backup completed"
```

## 🐛 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service logs
docker-compose logs service_name

# Check system resources
docker system df
docker system prune

# Restart specific service
docker-compose restart service_name
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres_primary

# Test connection
docker-compose exec postgres_primary psql -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT 1;"

# Check network connectivity
docker-compose exec auth_service ping postgres_primary
```

#### High Memory Usage
```bash
# Check container resource usage
docker stats

# Restart memory-intensive services
docker-compose restart elasticsearch analytics_service
```

#### SSL Certificate Issues
```bash
# Regenerate certificates
./scripts/generate-ssl.sh

# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout
```

### Performance Optimization

#### Database Performance
- Monitor slow queries in PostgreSQL logs
- Add appropriate indexes
- Configure connection pooling
- Use read replicas for read-heavy operations

#### Cache Optimization
- Monitor Redis memory usage
- Implement cache warming strategies
- Use appropriate TTL values
- Consider Redis Cluster for high availability

#### Application Performance
- Monitor response times in Grafana
- Implement async processing with RabbitMQ
- Use CDN for static assets
- Optimize database queries

### Monitoring Alerts
Configure alerts for:
- Service downtime
- High CPU/memory usage
- Database connection limits
- High error rates
- Disk space usage

## 📝 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Best Practices](https://redis.io/topics/memory-optimization)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Prometheus Monitoring](https://prometheus.io/docs/guides/go-application/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For questions and support, please contact the development team or create an issue in the repository.