import os, psycopg2

def import_csvs():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    for fname in os.listdir('main'):
        if fname.endswith('.csv'):
            table = fname.replace('.csv', '')
            cur.execute(
                f"COPY {table} FROM 'data/{fname}' CSV HEADER;"
            )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_csvs()
