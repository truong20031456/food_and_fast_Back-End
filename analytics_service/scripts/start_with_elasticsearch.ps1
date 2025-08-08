# Start Analytics Service with Elasticsearch on Windows
# This script starts the required services and the analytics application

Write-Host "Starting Analytics Service with Elasticsearch..." -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Start Elasticsearch and related services using Docker Compose
Write-Host "Starting Elasticsearch, Kibana, Redis, and PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if Elasticsearch is ready
Write-Host "Checking Elasticsearch health..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 1

do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Elasticsearch is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "Waiting for Elasticsearch... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        $attempt++
    }
} while ($attempt -le $maxAttempts)

if ($attempt -gt $maxAttempts) {
    Write-Host "Warning: Elasticsearch may not be ready" -ForegroundColor Red
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Generate sample data (optional)
$generateData = Read-Host "Do you want to generate sample data? (y/N)"
if ($generateData -eq "y" -or $generateData -eq "Y") {
    Write-Host "Generating sample data..." -ForegroundColor Yellow
    python scripts/generate_sample_data.py
}

# Start the Analytics Service
Write-Host "Starting Analytics Service..." -ForegroundColor Green
python main.py
