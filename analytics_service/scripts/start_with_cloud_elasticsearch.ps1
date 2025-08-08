# Start Analytics Service with Google Cloud Elasticsearch
# This script starts the analytics service connected to cloud Elasticsearch

Write-Host "Starting Analytics Service with Google Cloud Elasticsearch..." -ForegroundColor Green

# Check if .env.cloud exists
if (-not (Test-Path ".env.cloud")) {
    Write-Host "❌ .env.cloud file not found! Please create it first." -ForegroundColor Red
    Write-Host "You can copy from .env.example and update with your cloud settings." -ForegroundColor Yellow
    exit 1
}

# Use cloud configuration
Write-Host "Using cloud Elasticsearch configuration..." -ForegroundColor Yellow
Copy-Item ".env.cloud" ".env" -Force

# Start only local services (without Elasticsearch)
Write-Host "Starting local services (Redis and PostgreSQL)..." -ForegroundColor Yellow
docker-compose up redis postgres -d

# Wait for local services
Write-Host "Waiting for local services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test cloud Elasticsearch connection
Write-Host "Testing cloud Elasticsearch connection..." -ForegroundColor Yellow
$testConnection = Read-Host "Do you want to test the cloud connection first? (Y/n)"
if ($testConnection -ne "n" -and $testConnection -ne "N") {
    python scripts/test_elasticsearch_cloud.py
    
    $continue = Read-Host "Connection test completed. Continue with startup? (Y/n)"
    if ($continue -eq "n" -or $continue -eq "N") {
        Write-Host "Startup cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Initialize cloud indices and generate sample data
$initializeData = Read-Host "Do you want to initialize indices and generate sample data? (y/N)"
if ($initializeData -eq "y" -or $initializeData -eq "Y") {
    Write-Host "Initializing cloud Elasticsearch with sample data..." -ForegroundColor Yellow
    python scripts/generate_sample_data.py
}

# Start the Analytics Service
Write-Host "Starting Analytics Service with cloud Elasticsearch..." -ForegroundColor Green
Write-Host "Service will be available at: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:8001/health" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8001/docs" -ForegroundColor Cyan

python main.py
