#!/bin/bash

# Start Analytics Service with Elasticsearch
# This script starts the required services and the analytics application

echo "Starting Analytics Service with Elasticsearch..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Start Elasticsearch and related services using Docker Compose
echo "Starting Elasticsearch, Kibana, Redis, and PostgreSQL..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check if Elasticsearch is ready
echo "Checking Elasticsearch health..."
for i in {1..30}; do
    if curl -f -s "http://localhost:9200/_cluster/health" > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... ($i/30)"
    sleep 2
done

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Generate sample data (optional)
read -p "Do you want to generate sample data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Generating sample data..."
    python scripts/generate_sample_data.py
fi

# Start the Analytics Service
echo "Starting Analytics Service..."
python main.py
