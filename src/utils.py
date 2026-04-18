import psycopg
from psycopg import Connection
from pgvector.psycopg import register_vector

from config import DB_CONFIG


def get_connection() -> Connection:
    conn = psycopg.connect(**DB_CONFIG)
    register_vector(conn)
    return conn