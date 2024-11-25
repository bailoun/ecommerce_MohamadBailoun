from common.db import get_db
from psycopg2 import sql


def init_customers_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(50) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            age INT,
            address TEXT,
            gender VARCHAR(1),
            marital_status BOOLEAN,
            wallet_balance NUMERIC DEFAULT 0
        );"""
    )
    conn.commit()
    cur.close()
