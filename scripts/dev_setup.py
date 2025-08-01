#!/usr/bin/env python3
"""
Development setup script for Food & Fast E-Commerce Platform
"""
import os
import sys
import asyncio
import subprocess
import secrets
import string
from pathlib import Path
import shutil
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "shared"))

def run_command(command: str, cwd: Path = None) -> bool:
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or project_root,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command {command}: {e}")
        return False

def install_dependencies():
    """Install dependencies for all services"""
    print("📦 Installing dependencies...")
    
    services = [
        "api_gateway",
        "auth_service", 
        "user_service",
        "product_service",
        "order_service",
        "payment_service",
        "notification_service",
        "analytics_service"
    ]
    
    for service in services:
        service_path = project_root / service
        if (service_path / "requirements.txt").exists():
            print(f"Installing {service} dependencies...")
            if not run_command(f"pip install -r requirements.txt", service_path):
                print(f"⚠️  Failed to install {service} dependencies")
            else:
                print(f"✅ {service} dependencies installed")

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_files():
    """Create .env files for each service"""
    print("🔧 Creating environment files...")
    
    # Generate a secure secret key
    secret_key = generate_secret_key(64)
    print(f"🔑 Generated secret key: {secret_key[:20]}...")
    
    # Base environment variables
    base_env = {
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "LOG_LEVEL": "INFO",
        "SECRET_KEY": secret_key,
        "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/food_fast_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "ALLOWED_ORIGINS": "*"
    }
    
    # Service-specific configurations
    service_configs = {
        "api_gateway": {
            "SERVICE_PORT": "8000",
            "AUTH_SERVICE_URL": "http://localhost:8001",
            "USER_SERVICE_URL": "http://localhost:8002",
            "PRODUCT_SERVICE_URL": "http://localhost:8003",
            "ORDER_SERVICE_URL": "http://localhost:8004",
            "PAYMENT_SERVICE_URL": "http://localhost:8005",
            "NOTIFICATION_SERVICE_URL": "http://localhost:8006",
            "ANALYTICS_SERVICE_URL": "http://localhost:8007",
        },
        "auth_service": {
            "SERVICE_PORT": "8001",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/auth_service_db",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        },
        "user_service": {
            "SERVICE_PORT": "8002",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/user_service_db",
        },
        "product_service": {
            "SERVICE_PORT": "8003",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/product_service_db",
            "ELASTICSEARCH_URL": "http://localhost:9200",
        },
        "order_service": {
            "SERVICE_PORT": "8004",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/order_service_db",
        },
        "payment_service": {
            "SERVICE_PORT": "8005",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/payment_service_db",
        },
        "notification_service": {
            "SERVICE_PORT": "8006",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/notification_service_db",
        },
        "analytics_service": {
            "SERVICE_PORT": "8007",
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/analytics_service_db",
            "ELASTICSEARCH_URL": "http://localhost:9200",
        }
    }
    
    for service, config in service_configs.items():
        env_path = project_root / service / ".env"
        
        # Merge base config with service-specific config
        full_config = {**base_env, **config}
        
        # Write .env file
        with open(env_path, "w") as f:
            f.write("# Environment configuration for " + service + "\n")
            f.write("# Generated by dev_setup.py\n\n")
            for key, value in full_config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Created {service}/.env")

def setup_databases():
    """Setup development databases"""
    print("🗄️  Setting up databases...")
    
    databases = [
        "food_fast_db",
        "auth_service_db",
        "user_service_db", 
        "product_service_db",
        "order_service_db",
        "payment_service_db",
        "notification_service_db",
        "analytics_service_db"
    ]
    
    for db in databases:
        # Create database if it doesn't exist
        create_db_command = f'psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = \'{db}\'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE {db};"'
        if run_command(create_db_command):
            print(f"✅ Database {db} ready")
        else:
            print(f"⚠️  Could not setup database {db}")

def create_shared_symlinks():
    """Create symbolic links to shared modules in each service"""
    print("🔗 Creating shared module links...")
    
    services = [
        "api_gateway",
        "auth_service",
        "user_service", 
        "product_service",
        "order_service",
        "payment_service",
        "notification_service",
        "analytics_service"
    ]
    
    shared_path = project_root / "shared"
    
    for service in services:
        service_path = project_root / service
        shared_link = service_path / "shared"
        
        # Remove existing link/directory if it exists
        if shared_link.exists() or shared_link.is_symlink():
            if shared_link.is_symlink():
                shared_link.unlink()
            else:
                shutil.rmtree(shared_link)
        
        # Create symlink (Windows requires admin privileges, so copy instead)
        try:
            if os.name == 'nt':  # Windows
                shutil.copytree(shared_path, shared_link, dirs_exist_ok=True)
                print(f"✅ Copied shared modules to {service}")
            else:  # Unix-like
                os.symlink(shared_path, shared_link)
                print(f"✅ Linked shared modules to {service}")
        except Exception as e:
            print(f"⚠️  Could not link shared modules to {service}: {e}")

def verify_setup():
    """Verify the development setup"""
    print("🔍 Verifying setup...")
    
    checks = []
    
    # Check if shared modules are accessible
    try:
        from shared.core.config import BaseServiceSettings
        checks.append(("Shared modules", True))
    except ImportError as e:
        checks.append(("Shared modules", False, str(e)))
    
    # Check if services can import shared modules
    services_to_check = ["api_gateway", "auth_service"]
    
    for service in services_to_check:
        try:
            service_path = project_root / service
            if (service_path / "main.py").exists():
                checks.append((f"{service} main.py", True))
            else:
                checks.append((f"{service} main.py", False, "File not found"))
        except Exception as e:
            checks.append((f"{service} main.py", False, str(e)))
    
    # Print verification results
    print("\n📋 Setup Verification:")
    print("-" * 50)
    for check in checks:
        if check[1]:
            print(f"✅ {check[0]}")
        else:
            error_msg = check[2] if len(check) > 2 else "Failed"
            print(f"❌ {check[0]}: {error_msg}")

def print_next_steps():
    """Print next steps for development"""
    print("\n🚀 Next Steps:")
    print("-" * 50)
    print("1. Start infrastructure services:")
    print("   cd infrastructure")
    print("   docker-compose up -d postgres redis elasticsearch")
    print()
    print("2. Start individual services:")
    print("   cd auth_service && python main.py")
    print("   cd api_gateway && python main.py")
    print()
    print("3. Access the API documentation:")
    print("   API Gateway: http://localhost:8000/docs")
    print("   Auth Service: http://localhost:8001/docs")
    print()
    print("4. Check service health:")
    print("   curl http://localhost:8000/health")
    print("   curl http://localhost:8001/health")

def main():
    """Main setup function"""
    print("🍔 Food & Fast E-Commerce - Development Setup")
    print("=" * 50)
    
    try:
        # Run setup steps
        create_shared_symlinks()
        create_env_files()
        install_dependencies()
        
        # Optional database setup (requires PostgreSQL)
        setup_db = input("\n🗄️  Setup databases? (requires PostgreSQL running) [y/N]: ")
        if setup_db.lower() in ['y', 'yes']:
            setup_databases()
        
        # Verify setup
        verify_setup()
        
        # Print next steps
        print_next_steps()
        
        print("\n✅ Development setup completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())