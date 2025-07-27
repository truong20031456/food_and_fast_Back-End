# Food & Fast Monitoring Stack

This directory contains the monitoring configuration for the Food & Fast microservices platform.

## 🏗️ Architecture

The monitoring stack consists of:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards
- **Alertmanager**: Alert routing and notification
- **Exporters**: Database and system metrics collection

## 📁 File Structure

```
monitoring/
├── prometheus.yml          # Prometheus configuration
├── alert_rules.yml         # Alerting rules
├── alertmanager.yml        # Alertmanager configuration
├── grafana-dashboards/     # Grafana dashboard definitions
│   └── food-fast-dashboard.json
├── setup-monitoring.sh     # Setup script
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Setup Monitoring Stack

```bash
# Make setup script executable
chmod +x monitoring/setup-monitoring.sh

# Run setup script
./monitoring/setup-monitoring.sh
```

### 2. Manual Setup

```bash
# Start monitoring services
cd infrastructure
docker-compose up -d prometheus grafana alertmanager postgres_exporter redis_exporter node-exporter

# Check service status
docker-compose ps
```

## 📊 Access URLs

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Prometheus** | http://localhost:9090 | None |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Alertmanager** | http://localhost:9093 | None |

## 🔧 Configuration

### Prometheus Configuration

The `prometheus.yml` file configures:

- **Global settings**: Scrape intervals and evaluation intervals
- **Service targets**: All microservices endpoints
- **Database exporters**: PostgreSQL and Redis metrics
- **System metrics**: Node exporter for host metrics

### Alerting Rules

The `alert_rules.yml` file defines alerts for:

- **Service Health**: Service down detection
- **Performance**: High response times and error rates
- **Infrastructure**: Database, cache, and system issues
- **Resource Usage**: CPU, memory, and disk space

### Alertmanager Configuration

The `alertmanager.yml` file configures:

- **Notification channels**: Email and webhook receivers
- **Alert routing**: Grouping and timing rules
- **Inhibition rules**: Prevent alert spam

## 📈 Metrics Collection

### Service Metrics

Each service exposes metrics at `/metrics` endpoint:

- **Request counts**: Total requests by method and endpoint
- **Response times**: Request duration histograms
- **Error rates**: 5xx error percentages
- **Health status**: Service availability

### Infrastructure Metrics

- **PostgreSQL**: Connection counts, query performance
- **Redis**: Memory usage, command statistics
- **System**: CPU, memory, disk, network usage

## 🎯 Key Metrics

### Application Metrics

```promql
# Request rate
rate(http_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Service health
service_health_status
```

### Infrastructure Metrics

```promql
# CPU usage
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# Database connections
pg_stat_database_numbackends

# Redis memory
redis_memory_used_bytes / redis_memory_max_bytes * 100
```

## 🚨 Alerting

### Critical Alerts

- **ServiceDown**: Service unavailable for >1 minute
- **HighErrorRate**: Error rate >5% for >2 minutes
- **DatabaseConnectionIssues**: PostgreSQL not accessible
- **RedisConnectionIssues**: Redis not accessible

### Warning Alerts

- **HighResponseTime**: 95th percentile >2 seconds
- **HighMemoryUsage**: Memory usage >85%
- **HighCPUUsage**: CPU usage >80%
- **DiskSpaceLow**: Disk space <10%

## 📊 Dashboards

### Food & Fast Dashboard

The main dashboard includes:

1. **Service Health Status**: Real-time service availability
2. **Request Rate**: Requests per second by service
3. **Response Time**: 95th percentile response times
4. **Error Rate**: Error percentages by service
5. **Active Requests**: Currently processing requests
6. **Database Connections**: PostgreSQL connection count
7. **Redis Memory Usage**: Cache memory utilization
8. **System CPU Usage**: Host CPU utilization

### Importing Dashboards

1. Login to Grafana (admin/admin)
2. Go to Dashboards → Import
3. Upload `grafana-dashboards/food-fast-dashboard.json`
4. Select Prometheus as data source
5. Save dashboard

## 🔍 Troubleshooting

### Common Issues

#### Prometheus Not Scraping

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check service endpoints
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

#### Grafana No Data

1. Verify Prometheus data source is configured
2. Check Prometheus is accessible from Grafana
3. Verify metrics are being collected

#### Alerts Not Firing

1. Check alert rules syntax
2. Verify Alertmanager is running
3. Check notification configuration

### Logs

```bash
# View service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager

# Check specific service
docker-compose logs api_gateway
```

### Health Checks

```bash
# Test service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8003/health

# Test metrics endpoints
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

## 🔧 Customization

### Adding New Services

1. Add service to `prometheus.yml` scrape configs
2. Add health check to service
3. Add metrics endpoint to service
4. Update dashboard if needed

### Custom Alerts

1. Add alert rule to `alert_rules.yml`
2. Configure notification in `alertmanager.yml`
3. Test alert with Prometheus query

### Custom Dashboards

1. Create dashboard JSON file
2. Add to `grafana-dashboards/` directory
3. Import via Grafana UI

## 📚 Best Practices

### Monitoring

- Use consistent metric naming
- Include service and endpoint labels
- Set appropriate scrape intervals
- Monitor both application and infrastructure

### Alerting

- Set meaningful thresholds
- Use appropriate severity levels
- Include helpful descriptions
- Test alert conditions

### Dashboards

- Keep dashboards focused
- Use appropriate visualization types
- Include time range controls
- Add helpful annotations

## 🔐 Security

### Access Control

- Change default Grafana password
- Use reverse proxy for external access
- Configure firewall rules
- Use HTTPS in production

### Data Retention

- Configure Prometheus retention (default: 200h)
- Set up data backup strategy
- Monitor storage usage
- Archive old metrics if needed

## 📞 Support

For monitoring issues:

1. Check service logs
2. Verify configuration files
3. Test individual components
4. Review alert rules syntax

## 🔄 Updates

To update monitoring stack:

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Verify configuration
docker-compose logs prometheus
``` 