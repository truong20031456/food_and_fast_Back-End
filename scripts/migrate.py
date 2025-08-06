#!/usr/bin/env python3
"""
Database Migration System for Food Fast E-commerce
Handles database schema migrations across all services
"""

import asyncio
import asyncpg
import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Migration metadata"""

    id: str
    version: str
    name: str
    service: str
    sql_up: str
    sql_down: str
    checksum: str
    applied_at: Optional[datetime] = None


class MigrationManager:
    """Manages database migrations across all services"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migrations_table = "schema_migrations"
        self.conn = None

    async def connect(self):
        """Connect to database"""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            await self.ensure_migrations_table()
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            await self.conn.close()
            logger.info("Disconnected from database")

    async def ensure_migrations_table(self):
        """Ensure migrations tracking table exists"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id VARCHAR(255) PRIMARY KEY,
            version VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            service VARCHAR(100) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER,
            success BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX IF NOT EXISTS idx_migrations_service ON {self.migrations_table}(service);
        CREATE INDEX IF NOT EXISTS idx_migrations_version ON {self.migrations_table}(version);
        """

        await self.conn.execute(create_table_sql)
        logger.info("Migrations table ensured")

    def scan_migrations_directory(self, base_path: str = ".") -> List[Migration]:
        """Scan for migration files across all services"""
        migrations = []
        base_path = Path(base_path)

        # Service directories to scan
        services = [
            "auth_service",
            "user_service",
            "product_service",
            "order_service",
            "payment_service",
            "notification_service",
            "analytics_service",
        ]

        for service in services:
            service_path = base_path / service / "migrations" / "versions"
            if service_path.exists():
                migrations.extend(self._scan_service_migrations(service, service_path))

        # Sort by version
        migrations.sort(key=lambda x: x.version)
        return migrations

    def _scan_service_migrations(
        self, service: str, migrations_path: Path
    ) -> List[Migration]:
        """Scan migrations for a specific service"""
        migrations = []

        for migration_file in migrations_path.glob("*.sql"):
            try:
                migration = self._parse_migration_file(service, migration_file)
                migrations.append(migration)
            except Exception as e:
                logger.error(f"Failed to parse migration {migration_file}: {e}")

        return migrations

    def _parse_migration_file(self, service: str, file_path: Path) -> Migration:
        """Parse migration file and extract metadata"""
        content = file_path.read_text(encoding="utf-8")

        # Extract version from filename (format: V001__description.sql)
        filename = file_path.stem
        parts = filename.split("__", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid migration filename format: {filename}")

        version = parts[0]
        name = parts[1].replace("_", " ").title()

        # Split UP and DOWN sections
        sections = content.split("-- DOWN\n", 1)
        if len(sections) != 2:
            sql_up = content
            sql_down = ""
        else:
            sql_up = sections[0].replace("-- UP\n", "").strip()
            sql_down = sections[1].strip()

        # Generate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()

        migration_id = f"{service}_{version}"

        return Migration(
            id=migration_id,
            version=version,
            name=name,
            service=service,
            sql_up=sql_up,
            sql_down=sql_down,
            checksum=checksum,
        )

    async def get_applied_migrations(self) -> List[Migration]:
        """Get list of applied migrations"""
        query = f"SELECT * FROM {self.migrations_table} ORDER BY version"
        rows = await self.conn.fetch(query)

        migrations = []
        for row in rows:
            migration = Migration(
                id=row["id"],
                version=row["version"],
                name=row["name"],
                service=row["service"],
                sql_up="",  # Not stored
                sql_down="",  # Not stored
                checksum=row["checksum"],
                applied_at=row["applied_at"],
            )
            migrations.append(migration)

        return migrations

    async def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        all_migrations = self.scan_migrations_directory()
        applied_migrations = await self.get_applied_migrations()
        applied_ids = {m.id for m in applied_migrations}

        pending = [m for m in all_migrations if m.id not in applied_ids]
        return pending

    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        start_time = datetime.now()

        try:
            logger.info(f"Applying migration: {migration.id} - {migration.name}")

            # Start transaction
            async with self.conn.transaction():
                # Execute migration
                await self.conn.execute(migration.sql_up)

                # Record migration
                execution_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                await self.conn.execute(
                    f"""
                    INSERT INTO {self.migrations_table} 
                    (id, version, name, service, checksum, execution_time_ms, success)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    migration.id,
                    migration.version,
                    migration.name,
                    migration.service,
                    migration.checksum,
                    execution_time,
                    True,
                )

            logger.info(f"✅ Applied migration {migration.id} in {execution_time}ms")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration.id}: {e}")

            # Record failed migration
            try:
                execution_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                await self.conn.execute(
                    f"""
                    INSERT INTO {self.migrations_table} 
                    (id, version, name, service, checksum, execution_time_ms, success)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    migration.id,
                    migration.version,
                    migration.name,
                    migration.service,
                    migration.checksum,
                    execution_time,
                    False,
                )
            except:
                pass  # Don't fail if we can't record the failure

            return False

    async def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration"""
        if not migration.sql_down.strip():
            logger.error(f"No rollback SQL available for migration {migration.id}")
            return False

        start_time = datetime.now()

        try:
            logger.info(f"Rolling back migration: {migration.id}")

            async with self.conn.transaction():
                # Execute rollback
                await self.conn.execute(migration.sql_down)

                # Remove from migrations table
                await self.conn.execute(
                    f"DELETE FROM {self.migrations_table} WHERE id = $1", migration.id
                )

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(
                f"✅ Rolled back migration {migration.id} in {execution_time}ms"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to rollback migration {migration.id}: {e}")
            return False

    async def migrate_up(self, target_version: Optional[str] = None) -> bool:
        """Apply pending migrations up to target version"""
        pending_migrations = await self.get_pending_migrations()

        if not pending_migrations:
            logger.info("No pending migrations")
            return True

        if target_version:
            pending_migrations = [
                m for m in pending_migrations if m.version <= target_version
            ]

        logger.info(f"Found {len(pending_migrations)} pending migrations")

        success_count = 0
        for migration in pending_migrations:
            if await self.apply_migration(migration):
                success_count += 1
            else:
                logger.error(f"Migration failed, stopping at {migration.id}")
                break

        logger.info(f"Applied {success_count}/{len(pending_migrations)} migrations")
        return success_count == len(pending_migrations)

    async def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations down to target version"""
        applied_migrations = await self.get_applied_migrations()

        # Find migrations to rollback (those newer than target)
        to_rollback = [m for m in applied_migrations if m.version > target_version]

        # Sort in reverse order for rollback
        to_rollback.sort(key=lambda x: x.version, reverse=True)

        if not to_rollback:
            logger.info(f"Already at or below version {target_version}")
            return True

        logger.info(
            f"Rolling back {len(to_rollback)} migrations to version {target_version}"
        )

        # Need to get the SQL from files
        all_migrations = self.scan_migrations_directory()
        migration_map = {m.id: m for m in all_migrations}

        success_count = 0
        for migration in to_rollback:
            if migration.id in migration_map:
                file_migration = migration_map[migration.id]
                if await self.rollback_migration(file_migration):
                    success_count += 1
                else:
                    logger.error(f"Rollback failed, stopping at {migration.id}")
                    break
            else:
                logger.error(f"Migration file not found for {migration.id}")
                break

        logger.info(f"Rolled back {success_count}/{len(to_rollback)} migrations")
        return success_count == len(to_rollback)

    async def show_status(self):
        """Show migration status"""
        all_migrations = self.scan_migrations_directory()
        applied_migrations = await self.get_applied_migrations()
        applied_ids = {m.id for m in applied_migrations}

        print(f"\n📊 Migration Status")
        print(f"{'=' * 60}")

        # Group by service
        services = {}
        for migration in all_migrations:
            if migration.service not in services:
                services[migration.service] = {"total": 0, "applied": 0, "pending": 0}

            services[migration.service]["total"] += 1
            if migration.id in applied_ids:
                services[migration.service]["applied"] += 1
            else:
                services[migration.service]["pending"] += 1

        for service, stats in services.items():
            status = "✅" if stats["pending"] == 0 else "⚠️"
            print(
                f"{status} {service:20} | Applied: {stats['applied']:2} | Pending: {stats['pending']:2} | Total: {stats['total']:2}"
            )

        # Show recent migrations
        recent_applied = sorted(
            applied_migrations, key=lambda x: x.applied_at, reverse=True
        )[:5]
        if recent_applied:
            print(f"\n📋 Recent Migrations")
            print(f"{'=' * 60}")
            for migration in recent_applied:
                print(
                    f"✅ {migration.id:25} | {migration.applied_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )

        # Show pending migrations
        pending = [m for m in all_migrations if m.id not in applied_ids]
        if pending:
            print(f"\n⏳ Pending Migrations")
            print(f"{'=' * 60}")
            for migration in pending[:5]:
                print(f"⏳ {migration.id:25} | {migration.name}")

            if len(pending) > 5:
                print(f"   ... and {len(pending) - 5} more")

    async def validate_migrations(self) -> bool:
        """Validate migration integrity"""
        logger.info("Validating migration integrity...")

        all_migrations = self.scan_migrations_directory()
        applied_migrations = await self.get_applied_migrations()
        applied_map = {m.id: m for m in applied_migrations}

        errors = []

        # Check for checksum mismatches
        for migration in all_migrations:
            if migration.id in applied_map:
                applied = applied_map[migration.id]
                if migration.checksum != applied.checksum:
                    errors.append(f"Checksum mismatch for {migration.id}")

        # Check for missing migration files
        all_ids = {m.id for m in all_migrations}
        for applied in applied_migrations:
            if applied.id not in all_ids:
                errors.append(f"Missing migration file for {applied.id}")

        if errors:
            logger.error("Migration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False

        logger.info("✅ Migration validation passed")
        return True

    async def create_migration_template(self, service: str, name: str) -> str:
        """Create a new migration template"""
        # Get next version number for service
        existing = self.scan_migrations_directory()
        service_migrations = [m for m in existing if m.service == service]

        if service_migrations:
            last_version = max(
                int(m.version.replace("V", "")) for m in service_migrations
            )
            next_version = f"V{last_version + 1:03d}"
        else:
            next_version = "V001"

        # Create filename
        safe_name = name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{next_version}__{safe_name}.sql"

        # Create migration directory if it doesn't exist
        migration_dir = Path(f"{service}/migrations/versions")
        migration_dir.mkdir(parents=True, exist_ok=True)

        # Template content
        template = f"""-- Migration: {next_version} - {name}
-- Service: {service}
-- Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

-- UP
-- Add your migration SQL here
-- Example:
-- CREATE TABLE example_table (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- DOWN
-- Add your rollback SQL here
-- Example:
-- DROP TABLE IF EXISTS example_table;
"""

        file_path = migration_dir / filename
        file_path.write_text(template)

        logger.info(f"Created migration template: {file_path}")
        return str(file_path)


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument(
        "--db-url", default=os.getenv("DATABASE_URL"), help="Database URL"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    subparsers.add_parser("status", help="Show migration status")

    # Migrate up command
    migrate_up_parser = subparsers.add_parser("up", help="Apply pending migrations")
    migrate_up_parser.add_argument("--target", help="Target version")

    # Migrate down command
    migrate_down_parser = subparsers.add_parser("down", help="Rollback migrations")
    migrate_down_parser.add_argument("target", help="Target version")

    # Validate command
    subparsers.add_parser("validate", help="Validate migration integrity")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("service", help="Service name")
    create_parser.add_argument("name", help="Migration name")

    args = parser.parse_args()

    if not args.db_url:
        logger.error(
            "Database URL is required. Set DATABASE_URL environment variable or use --db-url"
        )
        return 1

    if not args.command:
        parser.print_help()
        return 1

    manager = MigrationManager(args.db_url)

    try:
        if args.command == "create":
            # Create command doesn't need database connection
            await manager.create_migration_template(args.service, args.name)
            return 0

        await manager.connect()

        if args.command == "status":
            await manager.show_status()

        elif args.command == "up":
            success = await manager.migrate_up(args.target)
            return 0 if success else 1

        elif args.command == "down":
            success = await manager.migrate_down(args.target)
            return 0 if success else 1

        elif args.command == "validate":
            success = await manager.validate_migrations()
            return 0 if success else 1

        return 0

    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1

    finally:
        await manager.disconnect()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
