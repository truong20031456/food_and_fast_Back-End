# User Service Deployment Script for Windows
# Usage: .\scripts\deploy.ps1 [environment] [version]

param(
    [string]$Environment = "staging",
    [string]$Version = "latest"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Default values
$Registry = "ghcr.io"
$ImageName = "your-username/user-service"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if Docker is installed
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed"
        exit 1
    }
    
    # Check if Docker Compose is installed
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed"
        exit 1
    }
    
    # Check if kubectl is installed (for Kubernetes deployment)
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Warning "kubectl is not installed - Kubernetes deployment will be skipped"
    }
    
    Write-Success "Prerequisites check completed"
}

# Function to build Docker image
function Build-Image {
    Write-Status "Building Docker image..."
    
    docker build -t "${Registry}/${ImageName}:${Version}" .
    docker tag "${Registry}/${ImageName}:${Version}" "${Registry}/${ImageName}:latest"
    
    Write-Success "Docker image built successfully"
}

# Function to push Docker image
function Push-Image {
    Write-Status "Pushing Docker image to registry..."
    
    docker push "${Registry}/${ImageName}:${Version}"
    docker push "${Registry}/${ImageName}:latest"
    
    Write-Success "Docker image pushed successfully"
}

# Function to deploy to Docker Compose
function Deploy-DockerCompose {
    Write-Status "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    if ($Environment -eq "production") {
        docker-compose --profile production up -d
    } else {
        docker-compose up -d
    }
    
    Write-Success "Docker Compose deployment completed"
}

# Function to deploy to Kubernetes
function Deploy-Kubernetes {
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Warning "Skipping Kubernetes deployment - kubectl not available"
        return
    }
    
    Write-Status "Deploying to Kubernetes..."
    
    # Update image tag in deployment (PowerShell way)
    $deploymentContent = Get-Content "k8s/deployment.yaml" -Raw
    $deploymentContent = $deploymentContent -replace "image: .*", "image: ${Registry}/${ImageName}:${Version}"
    $deploymentContent | Set-Content "k8s/deployment.yaml"
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/user-service
    
    Write-Success "Kubernetes deployment completed"
}

# Function to run health checks
function Test-HealthCheck {
    Write-Status "Running health checks..."
    
    # Wait for service to be ready
    Start-Sleep -Seconds 10
    
    # Check health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Success "Health check passed"
        } else {
            Write-Error "Health check failed with status code: $($response.StatusCode)"
            exit 1
        }
    } catch {
        Write-Error "Health check failed: $($_.Exception.Message)"
        exit 1
    }
}

# Function to show deployment info
function Show-DeploymentInfo {
    Write-Status "Deployment Information:"
    Write-Host "  Environment: $Environment"
    Write-Host "  Version: $Version"
    Write-Host "  Image: ${Registry}/${ImageName}:${Version}"
    Write-Host "  Health Check: http://localhost:8002/health"
    Write-Host "  API Docs: http://localhost:8002/docs"
}

# Main deployment function
function Start-Deployment {
    Write-Status "Starting deployment for environment: $Environment, version: $Version"
    
    Test-Prerequisites
    Build-Image
    Push-Image
    
    switch ($Environment) {
        { $_ -in @("local", "development") } {
            Deploy-DockerCompose
        }
        { $_ -in @("staging", "production") } {
            Deploy-DockerCompose
            Deploy-Kubernetes
        }
        default {
            Write-Error "Unknown environment: $Environment"
            Write-Status "Available environments: local, development, staging, production"
            exit 1
        }
    }
    
    Test-HealthCheck
    Show-DeploymentInfo
    
    Write-Success "Deployment completed successfully!"
}

# Run main deployment function
Start-Deployment 