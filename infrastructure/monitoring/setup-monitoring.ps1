# Food & Fast Monitoring Setup Script (PowerShell)

Write-Host "🚀 Setting up Food & Fast Monitoring Stack..." -ForegroundColor Green

# Create necessary directories
New-Item -ItemType Directory -Force -Path "monitoring/grafana-dashboards" | Out-Null
New-Item -ItemType Directory -Force -Path "monitoring/alertmanager" | Out-Null

Write-Host "✅ Monitoring configuration files created" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "🐳 Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

Write-Host "🐳 Starting monitoring services..." -ForegroundColor Yellow

# Start monitoring services
Set-Location infrastructure
docker-compose up -d prometheus grafana alertmanager postgres_exporter redis_exporter node-exporter

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Test Prometheus
Write-Host "🔍 Testing Prometheus..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/status/config" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Prometheus is running at http://localhost:9090" -ForegroundColor Green
    } else {
        Write-Host "❌ Prometheus is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Prometheus is not responding" -ForegroundColor Red
}

# Test Grafana
Write-Host "📈 Testing Grafana..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Grafana is running at http://localhost:3000" -ForegroundColor Green
        Write-Host "   Default credentials: admin/admin" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Grafana is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Grafana is not responding" -ForegroundColor Red
}

# Test Alertmanager
Write-Host "🚨 Testing Alertmanager..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9093/api/v1/status/config" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Alertmanager is running at http://localhost:9093" -ForegroundColor Green
    } else {
        Write-Host "❌ Alertmanager is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Alertmanager is not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Monitoring setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Access URLs:" -ForegroundColor Cyan
Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "   Alertmanager: http://localhost:9093" -ForegroundColor White
Write-Host ""
Write-Host "📊 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Login to Grafana with admin/admin" -ForegroundColor White
Write-Host "   2. Add Prometheus as a data source (http://prometheus:9090)" -ForegroundColor White
Write-Host "   3. Import the dashboard from monitoring/grafana-dashboards/" -ForegroundColor White
Write-Host "   4. Configure alerting rules in Alertmanager" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To start all services:" -ForegroundColor Cyan
Write-Host "   cd infrastructure && docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f prometheus grafana alertmanager" -ForegroundColor White 