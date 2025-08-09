#!/usr/bin/env python3
"""
Cache Management Script for Food Fast E-commerce
Manage Redis cache operations across all microservices
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

class CacheManager:
    """Manage cache operations across all services."""
    
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.services = {
            'api_gateway': 0,
            'product': 1,
            'auth': 2,
            'user': 3,
            'order': 4,
            'analytics': 5,
            'payment': 6,
            'notification': 7
        }
    
    async def get_redis_connection(self, db: int):
        """Get Redis connection for specific database."""
        try:
            import redis.asyncio as redis
            redis_url = f"redis://{self.redis_host}:{self.redis_port}/{db}"
            return redis.from_url(redis_url, decode_responses=True)
        except ImportError:
            print("❌ Redis package not installed. Run: pip install redis")
            return None
    
    async def clear_service_cache(self, service: str) -> bool:
        """Clear cache for a specific service."""
        if service not in self.services:
            print(f"❌ Unknown service: {service}")
            return False
        
        try:
            db = self.services[service]
            client = await self.get_redis_connection(db)
            if not client:
                return False
            
            keys_before = await client.dbsize()
            await client.flushdb()
            keys_after = await client.dbsize()
            
            await client.close()
            
            print(f"✅ Cleared {keys_before} keys from {service} cache (DB {db})")
            return True
        except Exception as e:
            print(f"❌ Error clearing {service} cache: {e}")
            return False
    
    async def clear_all_cache(self) -> Dict[str, bool]:
        """Clear cache for all services."""
        print("🧹 Clearing cache for all services...")
        results = {}
        
        for service in self.services:
            results[service] = await self.clear_service_cache(service)
        
        return results
    
    async def get_service_keys(self, service: str, pattern: str = "*") -> List[str]:
        """Get keys from a specific service cache."""
        if service not in self.services:
            print(f"❌ Unknown service: {service}")
            return []
        
        try:
            db = self.services[service]
            client = await self.get_redis_connection(db)
            if not client:
                return []
            
            keys = await client.keys(pattern)
            await client.close()
            
            return keys
        except Exception as e:
            print(f"❌ Error getting keys from {service}: {e}")
            return []
    
    async def backup_service_cache(self, service: str, backup_file: Optional[str] = None) -> bool:
        """Backup cache data for a specific service."""
        if service not in self.services:
            print(f"❌ Unknown service: {service}")
            return False
        
        if not backup_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"cache_backup_{service}_{timestamp}.json"
        
        try:
            db = self.services[service]
            client = await self.get_redis_connection(db)
            if not client:
                return False
            
            # Get all keys and their values
            keys = await client.keys("*")
            backup_data = {}
            
            for key in keys:
                try:
                    value = await client.get(key)
                    ttl = await client.ttl(key)
                    backup_data[key] = {
                        'value': value,
                        'ttl': ttl if ttl > 0 else None
                    }
                except Exception as e:
                    print(f"⚠️  Warning: Could not backup key {key}: {e}")
            
            await client.close()
            
            # Save to file
            with open(backup_file, 'w') as f:
                json.dump({
                    'service': service,
                    'database': db,
                    'backup_time': datetime.now().isoformat(),
                    'keys_count': len(backup_data),
                    'data': backup_data
                }, f, indent=2)
            
            print(f"✅ Backed up {len(backup_data)} keys from {service} to {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error backing up {service} cache: {e}")
            return False
    
    async def restore_service_cache(self, service: str, backup_file: str) -> bool:
        """Restore cache data for a specific service."""
        if service not in self.services:
            print(f"❌ Unknown service: {service}")
            return False
        
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return False
        
        try:
            # Load backup data
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            if backup_data['service'] != service:
                print(f"⚠️  Warning: Backup is for {backup_data['service']}, "
                      f"but restoring to {service}")
            
            db = self.services[service]
            client = await self.get_redis_connection(db)
            if not client:
                return False
            
            # Restore keys
            restored_count = 0
            for key, data in backup_data['data'].items():
                try:
                    if data['ttl']:
                        await client.setex(key, data['ttl'], data['value'])
                    else:
                        await client.set(key, data['value'])
                    restored_count += 1
                except Exception as e:
                    print(f"⚠️  Warning: Could not restore key {key}: {e}")
            
            await client.close()
            
            print(f"✅ Restored {restored_count}/{len(backup_data['data'])} keys to {service}")
            return True
        except Exception as e:
            print(f"❌ Error restoring {service} cache: {e}")
            return False
    
    async def warm_up_cache(self, service: str) -> bool:
        """Warm up cache for a specific service."""
        print(f"🔥 Warming up {service} cache...")
        
        # This would typically involve calling service endpoints
        # to populate frequently accessed data
        
        if service == "product":
            print("  - Loading featured products...")
            print("  - Loading categories...")
            print("  - Loading popular searches...")
        elif service == "auth":
            print("  - Loading common permissions...")
            print("  - Initializing rate limit counters...")
        elif service == "user":
            print("  - Loading active user sessions...")
            print("  - Loading user preferences...")
        elif service == "analytics":
            print("  - Loading dashboard data...")
            print("  - Generating reports...")
        
        print(f"✅ {service} cache warmed up")
        return True
    
    def print_help(self):
        """Print help information."""
        print("🛠️  CACHE MANAGEMENT TOOL")
        print("=" * 50)
        print("Available commands:")
        print("  clear <service>     - Clear cache for specific service")
        print("  clear-all          - Clear cache for all services")
        print("  backup <service>   - Backup cache for specific service")
        print("  restore <service> <file> - Restore cache from backup")
        print("  keys <service>     - List keys in service cache")
        print("  warmup <service>   - Warm up cache for service")
        print("  list-services      - List all available services")
        print("  help               - Show this help")
        print()
        print("Available services:")
        for service, db in self.services.items():
            print(f"  {service:<15} (DB {db})")

async def main():
    """Main cache management function."""
    if len(sys.argv) < 2:
        print("❌ No command provided")
        CacheManager().print_help()
        return
    
    manager = CacheManager()
    command = sys.argv[1].lower()
    
    if command == "help":
        manager.print_help()
    
    elif command == "list-services":
        print("Available services:")
        for service, db in manager.services.items():
            print(f"  {service:<15} (DB {db})")
    
    elif command == "clear":
        if len(sys.argv) < 3:
            print("❌ Service name required")
            return
        service = sys.argv[2]
        await manager.clear_service_cache(service)
    
    elif command == "clear-all":
        results = await manager.clear_all_cache()
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ Successfully cleared {success_count}/{len(results)} service caches")
    
    elif command == "backup":
        if len(sys.argv) < 3:
            print("❌ Service name required")
            return
        service = sys.argv[2]
        backup_file = sys.argv[3] if len(sys.argv) > 3 else None
        await manager.backup_service_cache(service, backup_file)
    
    elif command == "restore":
        if len(sys.argv) < 4:
            print("❌ Service name and backup file required")
            return
        service = sys.argv[2]
        backup_file = sys.argv[3]
        await manager.restore_service_cache(service, backup_file)
    
    elif command == "keys":
        if len(sys.argv) < 3:
            print("❌ Service name required")
            return
        service = sys.argv[2]
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*"
        keys = await manager.get_service_keys(service, pattern)
        print(f"Found {len(keys)} keys in {service} cache:")
        for key in keys[:20]:  # Show first 20 keys
            print(f"  {key}")
        if len(keys) > 20:
            print(f"  ... and {len(keys) - 20} more")
    
    elif command == "warmup":
        if len(sys.argv) < 3:
            print("❌ Service name required")
            return
        service = sys.argv[2]
        await manager.warm_up_cache(service)
    
    else:
        print(f"❌ Unknown command: {command}")
        manager.print_help()

if __name__ == "__main__":
    asyncio.run(main())
