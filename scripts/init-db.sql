-- Initialize MariaDB for MES Production
-- This script runs automatically when the database container starts

-- Create database if not exists (handled by environment variables)
-- CREATE DATABASE IF NOT EXISTS mes_production_db;

-- Optimize MariaDB for production (runtime settings only)
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL query_cache_type = 1;

-- Set timezone to UTC for consistency
SET GLOBAL time_zone = '+00:00';

-- Create indexes for better performance (Django migrations will handle table creation)
-- These will be created after Django migrations run

-- Log initialization
INSERT INTO mysql.general_log (event_time, user_host, thread_id, server_id, command_type, argument) 
VALUES (NOW(), 'system', 0, 1, 'Init', 'MES Database initialized for production') 
ON DUPLICATE KEY UPDATE argument = 'MES Database re-initialized';