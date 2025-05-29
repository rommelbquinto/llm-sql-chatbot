import os
import psycopg2

"""
1) Run schema migrations from schema.sql
2) Bulk-load CSV files from data/ in dependency order, mapping columns by CSV header
"""

def import_csvs():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    # Apply schema definitions
    schema_path = 'schema.sql'
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
            print(f"Applied schema from {schema_path}")

    # Define load order
    load_order = [
        'fleets', 'vehicles', 'drivers', 'driver_trip_map', 'trips',
        'alerts', 'battery_cycles', 'charging_sessions', 'geofence_events',
        'maintenance_logs', 'fleet_daily_summary', 'processed_metrics', 'raw_telemetry'
    ]

    data_dir = 'data'
    for table in load_order:
        filepath = os.path.join(data_dir, f"{table}.csv")
        if not os.path.exists(filepath):
            print(f"Skipping {table}, file not found.")
            continue
        print(f"Loading {filepath} into {table}...")
        with open(filepath, 'r') as f:
            # Read header line to get column names
            header = f.readline().strip()
            columns = header  # e.g. 'col1,col2,col3'
            f.seek(0)
            # Use column list in COPY to align CSV to table
            sql = f"COPY {table}({columns}) FROM STDIN WITH CSV HEADER;"
            cur.copy_expert(sql, f)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_csvs()
