-- Define tables for each CSV file based on provided headers

-- fleets.csv
CREATE TABLE IF NOT EXISTS fleets (
    fleet_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    time_zone TEXT
);

-- vehicles.csv
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    vin TEXT,
    fleet_id TEXT REFERENCES fleets(fleet_id),
    model TEXT,
    make TEXT,
    variant TEXT,
    registration_no TEXT,
    purchase_date DATE
);

-- drivers.csv
CREATE TABLE IF NOT EXISTS drivers (
    driver_id TEXT PRIMARY KEY,
    fleet_id TEXT REFERENCES fleets(fleet_id),
    name TEXT,
    license_no TEXT,
    hire_date DATE
);

-- driver_trip_map.csv
CREATE TABLE IF NOT EXISTS driver_trip_map (
    trip_id TEXT,
    driver_id TEXT,
    primary_bool BOOLEAN,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- trips.csv
CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    driver_id TEXT REFERENCES drivers(driver_id),
    start_ts TIMESTAMPTZ,
    end_ts TIMESTAMPTZ,
    distance_km DOUBLE PRECISION,
    energy_kwh DOUBLE PRECISION,
    idle_minutes INTEGER,
    avg_temp_c DOUBLE PRECISION
);

-- alerts.csv
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    alert_type TEXT,
    severity TEXT,
    alert_ts TIMESTAMPTZ,
    value DOUBLE PRECISION,
    threshold INTEGER,
    resolved_bool BOOLEAN,
    resolved_ts TIMESTAMPTZ
);

-- battery_cycles.csv
CREATE TABLE IF NOT EXISTS battery_cycles (
    cycle_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    ts TIMESTAMPTZ,
    dod_pct INTEGER,
    soh_pct INTEGER
);

-- charging_sessions.csv
CREATE TABLE IF NOT EXISTS charging_sessions (
    session_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    start_ts TIMESTAMPTZ,
    end_ts TIMESTAMPTZ,
    start_soc INTEGER,
    end_soc INTEGER,
    energy_kwh INTEGER,
    location TEXT
);

-- geofence_events.csv
CREATE TABLE IF NOT EXISTS geofence_events (
    event_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    geofence_name TEXT,
    enter_ts TIMESTAMPTZ,
    exit_ts TIMESTAMPTZ
);

-- maintenance_logs.csv
CREATE TABLE IF NOT EXISTS maintenance_logs (
    maint_id TEXT PRIMARY KEY,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    maint_type TEXT,
    start_ts TIMESTAMPTZ,
    end_ts TIMESTAMPTZ,
    cost_sgd INTEGER,
    notes TEXT
);

-- fleet_daily_summary.csv
CREATE TABLE IF NOT EXISTS fleet_daily_summary (
    fleet_id TEXT REFERENCES fleets(fleet_id),
    date DATE,
    total_distance_km DOUBLE PRECISION,
    total_energy_kwh DOUBLE PRECISION,
    active_vehicles INTEGER,
    avg_soc_pct INTEGER
);

-- processed_metrics.csv
CREATE TABLE IF NOT EXISTS processed_metrics (
    ts TIMESTAMPTZ,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    avg_speed_kph_15m DOUBLE PRECISION,
    distance_km_15m DOUBLE PRECISION,
    energy_kwh_15m DOUBLE PRECISION,
    battery_health_pct INTEGER,
    soc_band TEXT
);

-- raw_telemetry.csv
CREATE TABLE IF NOT EXISTS raw_telemetry (
    ts TIMESTAMPTZ,
    vehicle_id TEXT REFERENCES vehicles(vehicle_id),
    soc_pct INTEGER,
    pack_voltage_v DOUBLE PRECISION,
    pack_current_a DOUBLE PRECISION,
    batt_temp_c DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    speed_kph DOUBLE PRECISION,
    odo_km DOUBLE PRECISION
);
