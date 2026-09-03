import psycopg
from contextlib import contextmanager
from config import DB_CONFIG

@contextmanager
def get_conn():
    conn = psycopg.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()