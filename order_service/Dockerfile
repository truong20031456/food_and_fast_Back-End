FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && rm -rf /root/.cache/pip

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

HEALTHCHECK CMD curl --fail http://localhost:8004/health || exit 1

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
