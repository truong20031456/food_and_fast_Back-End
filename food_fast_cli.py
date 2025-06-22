#!/usr/bin/env python3
"""
Food & Fast E-Commerce Microservices Project Generator
CLI tool to generate project structure using Typer
"""

import typer
import os
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.panel import Panel
import time

app = typer.Typer(
    name="food-fast-gen",
    help="Food & Fast E-Commerce Microservices Project Generator",
    add_completion=False
)
console = Console()

# Service configurations
SERVICES = {
    "api_gateway": {
        "description": "API Gateway - Entry point và routing",
        "folders": ["src", "middleware", "routes", "config", "tests"],
        "files": {
            "main.py": "# API Gateway Main Application\n",
            "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0\nhttpx==0.25.2\n",
            "config/settings.py": "# Gateway settings\n",
            "middleware/auth.py": "# Authentication middleware\n",
            "routes/router.py": "# Main router\n"
        }
    },
    "auth_service": {
        "description": "Authentication Service - User auth & JWT",
        "folders": ["models", "controllers", "services", "utils", "tests"],
        "files": {
            "main.py": "# Auth Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\nsqlalchemy==2.0.23\npyjwt==2.8.0\npasslib==1.7.4\n",
            "models/user.py": "# User models\n",
            "services/auth_service.py": "# Auth business logic\n",
            "controllers/auth_controller.py": "# Auth endpoints\n"
        }
    },
    "user_service": {
        "description": "User Service - Profile & account management",
        "folders": ["models", "controllers", "services", "tests"],
        "files": {
            "main.py": "# User Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\nsqlalchemy==2.0.23\n",
            "models/user_profile.py": "# User profile models\n",
            "services/user_service.py": "# User business logic\n"
        }
    },
    "product_service": {
        "description": "Product Service - Catalog, inventory, reviews",
        "folders": ["modules/catalog", "modules/inventory", "modules/reviews", "modules/search", "models",
                    "controllers", "tests"],
        "files": {
            "main.py": "# Product Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\nsqlalchemy==2.0.23\nelasticsearch==8.11.0\n",
            "models/product.py": "# Product models\n",
            "models/category.py": "# Category models\n",
            "modules/catalog/catalog_service.py": "# Catalog management\n",
            "modules/inventory/inventory_service.py": "# Inventory management\n",
            "modules/reviews/review_service.py": "# Review system\n"
        }
    },
    "order_service": {
        "description": "Order Service - Cart, orders, delivery",
        "folders": ["modules/cart", "modules/orders", "modules/delivery", "models", "controllers", "tests"],
        "files": {
            "main.py": "# Order Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\nsqlalchemy==2.0.23\ncelery==5.3.4\n",
            "models/order.py": "# Order models\n",
            "models/cart.py": "# Cart models\n",
            "modules/cart/cart_service.py": "# Cart management\n",
            "modules/orders/order_service.py": "# Order processing\n"
        }
    },
    "payment_service": {
        "description": "Payment Service - Gateways & promotions",
        "folders": ["gateways", "promotions", "models", "controllers", "tests"],
        "files": {
            "main.py": "# Payment Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\nstripe==7.8.0\nrequests==2.31.0\n",
            "gateways/vnpay.py": "# VNPay gateway\n",
            "gateways/momo.py": "# Momo gateway\n",
            "gateways/stripe.py": "# Stripe gateway\n",
            "promotions/promotion_service.py": "# Promotion management\n"
        }
    },
    "notification_service": {
        "description": "Notification Service - Email, SMS, chat support",
        "folders": ["channels", "support", "models", "controllers", "tests"],
        "files": {
            "main.py": "# Notification Service Main\n",
            "requirements.txt": "fastapi==0.104.1\ncelery==5.3.4\nsendgrid==6.10.0\ntwilio==8.11.0\n",
            "channels/email.py": "# Email notifications\n",
            "channels/sms.py": "# SMS notifications\n",
            "support/chat_service.py": "# Live chat support\n"
        }
    },
    "analytics_service": {
        "description": "Analytics Service - Reports & dashboard data",
        "folders": ["models", "controllers", "services", "reports", "tests"],
        "files": {
            "main.py": "# Analytics Service Main\n",
            "requirements.txt": "fastapi==0.104.1\npsycopg2-binary==2.9.9\npandas==2.1.4\nplotly==5.17.0\n",
            "services/analytics_service.py": "# Analytics logic\n",
            "reports/sales_report.py": "# Sales reporting\n"
        }
    }
}

SHARED_STRUCTURE = {
    "shared": {
        "folders": ["database", "messaging", "utils", "models", "middleware"],
        "files": {
            "database/connection.py": "# Database connection\n",
            "messaging/redis_client.py": "# Redis client\n",
            "utils/logger.py": "# Logging utilities\n",
            "models/base.py": "# Base models\n"
        }
    },
    "infrastructure": {
        "folders": ["monitoring"],
        "files": {
            "docker-compose.yml": """version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: food_fast
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
""",
            "monitoring/prometheus.yml": "# Prometheus config\n",
            ".env.example": """# Environment variables
DATABASE_URL=postgresql://admin:password@localhost:5432/food_fast
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
"""
        }
    }
}


@app.command()
def create(
        project_name: str = typer.Argument("food-fast-ecommerce", help="Project name"),
        services: Optional[List[str]] = typer.Option(None, "--services", "-s", help="Specific services to create"),
        output_dir: Optional[str] = typer.Option(".", "--output", "-o", help="Output directory"),
        include_tests: bool = typer.Option(True, "--tests/--no-tests", help="Include test files"),
        include_docker: bool = typer.Option(True, "--docker/--no-docker", help="Include Docker files")
):
    """Create Food & Fast E-Commerce microservices project"""

    console.print(Panel.fit(
        "Food & Fast E-Commerce Project Generator",
        style="bold blue"
    ))

    base_path = Path(output_dir) / project_name

    if base_path.exists():
        if not typer.confirm(f"Directory {base_path} already exists. Continue?"):
            raise typer.Abort()

    # Create base directory
    base_path.mkdir(parents=True, exist_ok=True)

    # Determine which services to create
    services_to_create = services if services else list(SERVICES.keys())

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
    ) as progress:

        # Create services
        for service_name in services_to_create:
            if service_name not in SERVICES:
                console.print(f"❌ Unknown service: {service_name}", style="red")
                continue

            task = progress.add_task(f"Creating {service_name}...", total=None)

            service_config = SERVICES[service_name]
            service_path = base_path / service_name

            # Create service directory and folders
            service_path.mkdir(exist_ok=True)

            for folder in service_config["folders"]:
                (service_path / folder).mkdir(parents=True, exist_ok=True)

            # Create files
            for file_path, content in service_config["files"].items():
                full_path = service_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Write with UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Add Dockerfile if requested
            if include_docker:
                dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""
                with open(service_path / "Dockerfile", "w", encoding="utf-8") as f:
                    f.write(dockerfile_content)

            progress.update(task, completed=True)
            time.sleep(0.1)  # Visual effect

        # Create shared structure
        shared_task = progress.add_task("Creating shared components...", total=None)

        for component_name, config in SHARED_STRUCTURE.items():
            component_path = base_path / component_name
            component_path.mkdir(exist_ok=True)

            for folder in config["folders"]:
                (component_path / folder).mkdir(parents=True, exist_ok=True)

            for file_path, content in config["files"].items():
                full_path = component_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Write with UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

        progress.update(shared_task, completed=True)

        # Create README
        readme_task = progress.add_task("Creating documentation...", total=None)
        create_readme(base_path, services_to_create)
        progress.update(readme_task, completed=True)

    console.print(f"\n✅ Project created successfully at: {base_path}", style="green bold")
    show_project_tree(base_path)


@app.command()
def list_services():
    """List all available services"""

    console.print("\nAvailable Services:", style="bold blue")

    for service_name, config in SERVICES.items():
        console.print(f"  • {service_name}: {config['description']}", style="cyan")

    console.print(f"\nTotal: {len(SERVICES)} services available")


@app.command()
def add_service(
        service_name: str = typer.Argument(..., help="Service name to add"),
        project_path: str = typer.Argument(".", help="Project path")
):
    """Add a new service to existing project"""

    if service_name not in SERVICES:
        console.print(f"❌ Unknown service: {service_name}", style="red")
        console.print("Use 'list-services' to see available services")
        raise typer.Abort()

    base_path = Path(project_path)
    if not base_path.exists():
        console.print(f"❌ Project path does not exist: {base_path}", style="red")
        raise typer.Abort()

    service_config = SERVICES[service_name]
    service_path = base_path / service_name

    if service_path.exists():
        if not typer.confirm(f"Service {service_name} already exists. Overwrite?"):
            raise typer.Abort()

    # Create service
    service_path.mkdir(exist_ok=True)

    for folder in service_config["folders"]:
        (service_path / folder).mkdir(parents=True, exist_ok=True)

    for file_path, content in service_config["files"].items():
        full_path = service_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        # Write with UTF-8 encoding
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    console.print(f"✅ Service {service_name} added successfully!", style="green")


def create_readme(base_path: Path, services: List[str]):
    """Create README.md file"""
    readme_content = f"""# Food & Fast E-Commerce Microservices

Modern e-commerce platform for food delivery and fast supermarket shopping.

## Architecture

This project follows a microservices architecture with the following services:

"""

    for service in services:
        if service in SERVICES:
            readme_content += f"- **{service}**: {SERVICES[service]['description']}\n"

    readme_content += """
## Quick Start

1. **Start infrastructure services:**
   ```bash
   cd infrastructure
   docker-compose up -d
   ```

2. **Install dependencies for each service:**
   ```bash
   cd <service_name>
   pip install -r requirements.txt
   ```

3. **Run services:**
   ```bash
   python main.py
   ```

## Project Structure

```
food-fast-ecommerce/
├── api_gateway/          # API Gateway
├── auth_service/         # Authentication
├── user_service/         # User Management
├── product_service/      # Products & Inventory
├── order_service/        # Orders & Cart
├── payment_service/      # Payments & Promotions
├── notification_service/ # Notifications & Support
├── analytics_service/    # Analytics & Reports
├── shared/              # Shared utilities
└── infrastructure/      # Docker & configs
```

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL
- **Cache**: Redis
- **Search**: Elasticsearch (for product search)
- **Message Queue**: Celery
- **Monitoring**: Prometheus

## Environment Setup

Copy `.env.example` to `.env` and configure your environment variables.

## Development

Each service is independently deployable and follows FastAPI best practices.

## API Documentation

Once services are running, visit:
- API Gateway: http://localhost:8000/docs
- Individual services: http://localhost:800X/docs

---
Generated by Food & Fast CLI Generator
"""

    # Write with UTF-8 encoding to handle Unicode characters
    with open(base_path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)


def show_project_tree(base_path: Path):
    """Display project structure as tree"""
    tree = Tree(f"[bold blue]{base_path.name}[/bold blue]")

    for item in sorted(base_path.iterdir()):
        if item.is_dir():
            branch = tree.add(f"[cyan]{item.name}/[/cyan]")
            # Show first level of subdirectories
            try:
                for subitem in sorted(list(item.iterdir())[:5]):  # Limit to 5 items
                    if subitem.is_dir():
                        branch.add(f"[dim cyan]{subitem.name}/[/dim cyan]")
                    else:
                        branch.add(f"[dim white]{subitem.name}[/dim white]")
                if len(list(item.iterdir())) > 5:
                    branch.add("[dim]...[/dim]")
            except PermissionError:
                pass
        else:
            tree.add(f"[white]{item.name}[/white]")

    console.print("\nProject Structure:")
    console.print(tree)


if __name__ == "__main__":
    app()