import psycopg2
from flask import g

DB_NAME = "ecommerce_db"
DB_USER = "bailoun"
DB_PASSWORD = "Hellohello123"
DB_HOST = "postgres"
DB_PORT = "5432"


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_connection():
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.close()
