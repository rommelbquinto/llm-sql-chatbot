-- Example table definitions; adjust columns & types per your CSV headers
CREATE TABLE IF NOT EXISTS vehicle_status (
    vehicle_id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    soc_percent NUMERIC
);

CREATE TABLE IF NOT EXISTS battery_metrics (
    vehicle_id TEXT,
    timestamp TIMESTAMPTZ,
    temperature_celsius NUMERIC,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle_status(vehicle_id)
);

-- Add CREATE TABLE statements for each CSV (e.g., drivers, trips, etc.)
