import os
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize a PostgreSQL connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=int(os.getenv("DB_POOL_MAX", 10)),
    dsn=os.getenv("DATABASE_URL")
)

@contextmanager
def get_db_connection():
    """
    Context manager that yields a connection from the pool and returns it afterward.
    """
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def execute_query(sql: str, params: dict = None):
    """
    Execute a parameterized SQL query and return all fetched rows.

    :param sql: The SQL query to execute, with placeholders.
    :param params: A dict of parameters to bind to the query.
    :return: A list of rows (tuples).
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or {})
            return cur.fetchall()
