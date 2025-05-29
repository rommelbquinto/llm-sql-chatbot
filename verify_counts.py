from app.db import execute_query

tables = [
    'fleets','vehicles','drivers','driver_trip_map','trips','alerts',
    'battery_cycles','charging_sessions','geofence_events',
    'maintenance_logs','fleet_daily_summary','processed_metrics','raw_telemetry'
]

for tbl in tables:
    rows = execute_query(f"SELECT COUNT(*) FROM {tbl}")
    print(f"{tbl}: {rows[0][0]}")
