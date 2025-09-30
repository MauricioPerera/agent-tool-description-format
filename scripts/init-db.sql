-- ATDF Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS atdf;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set default schema
SET search_path TO atdf, public;

-- Create tables for ATDF tools
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    examples JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create table for tool executions
CREATE TABLE IF NOT EXISTS tool_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES tools(id) ON DELETE CASCADE,
    request_id VARCHAR(255),
    input_data JSONB NOT NULL,
    output_data JSONB,
    error_data JSONB,
    execution_time_ms INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create table for API keys and authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    rate_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create table for monitoring metrics
CREATE TABLE IF NOT EXISTS monitoring.metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC NOT NULL,
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name);
CREATE INDEX IF NOT EXISTS idx_tools_active ON tools(is_active);
CREATE INDEX IF NOT EXISTS idx_tool_executions_tool_id ON tool_executions(tool_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_status ON tool_executions(status);
CREATE INDEX IF NOT EXISTS idx_tool_executions_created_at ON tool_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON monitoring.metrics(metric_name, timestamp);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tools_updated_at 
    BEFORE UPDATE ON tools 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO tools (name, description, version, input_schema, output_schema, metadata, examples) VALUES
(
    'hotel_reservation',
    'Make hotel reservations with availability checking',
    '1.0.0',
    '{
        "type": "object",
        "properties": {
            "hotel_name": {"type": "string", "description": "Name of the hotel"},
            "check_in": {"type": "string", "format": "date", "description": "Check-in date"},
            "check_out": {"type": "string", "format": "date", "description": "Check-out date"},
            "guests": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Number of guests"}
        },
        "required": ["hotel_name", "check_in", "check_out", "guests"]
    }',
    '{
        "type": "object",
        "properties": {
            "reservation_id": {"type": "string"},
            "status": {"type": "string", "enum": ["confirmed", "pending", "failed"]},
            "total_cost": {"type": "number"},
            "confirmation_details": {"type": "object"}
        }
    }',
    '{
        "category": "travel",
        "tags": ["hotel", "booking", "travel"],
        "rate_limit": 100,
        "timeout_seconds": 30
    }',
    '[
        {
            "name": "Basic reservation",
            "description": "Make a simple hotel reservation",
            "input": {
                "hotel_name": "Grand Plaza Hotel",
                "check_in": "2024-03-15",
                "check_out": "2024-03-17",
                "guests": 2
            },
            "expected_output": {
                "reservation_id": "RES-123456",
                "status": "confirmed",
                "total_cost": 299.99
            }
        }
    ]'
),
(
    'weather_forecast',
    'Get weather forecast for a specific location',
    '1.0.0',
    '{
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name or coordinates"},
            "days": {"type": "integer", "minimum": 1, "maximum": 7, "default": 3, "description": "Number of forecast days"}
        },
        "required": ["location"]
    }',
    '{
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "forecast": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "format": "date"},
                        "temperature": {"type": "object"},
                        "conditions": {"type": "string"},
                        "humidity": {"type": "number"}
                    }
                }
            }
        }
    }',
    '{
        "category": "weather",
        "tags": ["weather", "forecast", "location"],
        "rate_limit": 1000,
        "timeout_seconds": 10
    }',
    '[
        {
            "name": "City weather",
            "description": "Get weather for a major city",
            "input": {
                "location": "New York",
                "days": 3
            },
            "expected_output": {
                "location": "New York, NY",
                "forecast": [
                    {
                        "date": "2024-03-15",
                        "temperature": {"high": 22, "low": 15},
                        "conditions": "Partly cloudy",
                        "humidity": 65
                    }
                ]
            }
        }
    ]'
) ON CONFLICT (name) DO NOTHING;

-- Create a sample API key (for development only)
INSERT INTO api_keys (key_hash, name, description, permissions) VALUES
(
    'dev_key_hash_12345',
    'Development Key',
    'API key for development and testing',
    '["tools:read", "tools:execute", "metrics:read"]'
) ON CONFLICT (key_hash) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA atdf TO atdf_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO atdf_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA atdf TO atdf_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA monitoring TO atdf_user;