-- Database initialization script for User Service
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional databases if needed
-- CREATE DATABASE user_service_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE user_db TO user;
GRANT ALL PRIVILEGES ON SCHEMA public TO user;

-- Create indexes for better performance (will be created by SQLAlchemy models)
-- These are just examples, actual indexes should be created by the application

-- Set timezone
SET timezone = 'UTC';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'User Service database initialized successfully at %', NOW();
END $$; 