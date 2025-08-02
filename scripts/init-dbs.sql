-- Create databases for each service
CREATE DATABASE auth_service_db;
CREATE DATABASE user_service_db;
CREATE DATABASE product_service_db;
CREATE DATABASE order_service_db;
CREATE DATABASE payment_service_db;
CREATE DATABASE notification_service_db;
CREATE DATABASE analytics_service_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE auth_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE product_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE order_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE payment_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE analytics_service_db TO postgres;