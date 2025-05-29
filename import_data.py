import os
import psycopg2

"""
1) Run schema migrations from schema.sql
2) Bulk-load CSV files from data/
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
    else:
        print(f"Warning: {schema_path} not found; ensure tables exist.")

    # 2) Load CSV files via COPY STDIN
    data_dir = 'data'
    for fname in os.listdir(data_dir):
        if fname.endswith('.csv'):
            table = fname.replace('.csv', '')
            filepath = os.path.join(data_dir, fname)
            print(f"Loading {filepath} into {table}...")
            with open(filepath, 'r') as f:
                cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER;", f)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_csvs()
