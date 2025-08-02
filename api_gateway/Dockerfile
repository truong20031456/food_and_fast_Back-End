FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared dependencies first
COPY shared/ ./shared/

# Copy requirements first for better layer caching
COPY api_gateway/requirements.txt ./api_gateway/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r api_gateway/requirements.txt

# Copy application code
COPY api_gateway/ ./api_gateway/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Set working directory to api_gateway for running the app
WORKDIR /app/api_gateway

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
