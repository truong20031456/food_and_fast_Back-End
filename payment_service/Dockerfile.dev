FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies
RUN pip install --no-cache-dir watchdog[watchmedo] alembic

# Copy application code
COPY . .

# Create shared directory
RUN mkdir -p /app/shared

# Expose port
EXPOSE 8005

# Command for development with hot reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--reload", "--reload-dir", "/app"] 