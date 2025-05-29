import os
import psycopg2

"""
1) Run schema migrations from schema.sql
2) Bulk-load CSV files from data/ in dependency order to satisfy foreign keys
"""

def import_csvs():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    # 1) Apply schema definitions
    schema_path = 'schema.sql'
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
            print(f"Applied schema from {schema_path}")

    # 2) Define load order to satisfy FKs
    load_order = [
        'fleets',
        'vehicles',
        'drivers',
        'driver_trip_map',
        'trips',
        'alerts',
        'battery_cycles',
        'charging_sessions',
        'geofence_events',
        'maintenance_logs',
        'fleet_daily_summary',
        'processed_metrics',
        'raw_telemetry'
    ]

    # 3) Load CSV files via COPY STDIN in specified order
    data_dir = 'data'
    for table in load_order:
        csv_file = f"{table}.csv"
        filepath = os.path.join(data_dir, csv_file)
        if os.path.exists(filepath):
            print(f"Loading {filepath} into {table}...")
            with open(filepath, 'r') as f:
                cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER;", f)
        else:
            print(f"Warning: {filepath} not found, skipping {table}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_csvs()
