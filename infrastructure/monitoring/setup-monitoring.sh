#!/bin/bash

# Food & Fast Monitoring Setup Script

echo "🚀 Setting up Food & Fast Monitoring Stack..."

# Create necessary directories
mkdir -p monitoring/grafana-dashboards
mkdir -p monitoring/alertmanager

# Set proper permissions
chmod 755 monitoring/
chmod 644 monitoring/*.yml
chmod 644 monitoring/grafana-dashboards/*.json

echo "✅ Monitoring configuration files created"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting monitoring services..."

# Start monitoring services
cd infrastructure
docker-compose up -d prometheus grafana alertmanager postgres_exporter redis_exporter node-exporter

echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test Prometheus
echo "🔍 Testing Prometheus..."
if curl -s http://localhost:9090/api/v1/status/config > /dev/null; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "❌ Prometheus is not responding"
fi

# Test Grafana
echo "📈 Testing Grafana..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is running at http://localhost:3000"
    echo "   Default credentials: admin/admin"
else
    echo "❌ Grafana is not responding"
fi

# Test Alertmanager
echo "🚨 Testing Alertmanager..."
if curl -s http://localhost:9093/api/v1/status/config > /dev/null; then
    echo "✅ Alertmanager is running at http://localhost:9093"
else
    echo "❌ Alertmanager is not responding"
fi

echo ""
echo "🎉 Monitoring setup complete!"
echo ""
echo "📋 Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Alertmanager: http://localhost:9093"
echo ""
echo "📊 Next steps:"
echo "   1. Login to Grafana with admin/admin"
echo "   2. Add Prometheus as a data source (http://prometheus:9090)"
echo "   3. Import the dashboard from monitoring/grafana-dashboards/"
echo "   4. Configure alerting rules in Alertmanager"
echo ""
echo "🔧 To start all services:"
echo "   cd infrastructure && docker-compose up -d"
echo ""
echo "🔍 To view logs:"
echo "   docker-compose logs -f prometheus grafana alertmanager" 