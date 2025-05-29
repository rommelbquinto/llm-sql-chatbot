import os
import psycopg2

def import_csvs():
    "/** Establish connection to the database **/"
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    "/** Bulk load CSVs using client-side COPY to avoid server file privileges issues **/"
    for fname in os.listdir('data'):
        if fname.endswith('.csv'):
            table = fname.replace('.csv', '')
            filepath = os.path.join('data', fname)
            with open(filepath, 'r') as f:
                # COPY from STDIN uses the client connection, bypassing server file restrictions
                cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER;", f)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_csvs()
