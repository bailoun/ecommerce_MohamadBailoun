from common.db import get_db
from psycopg2 import sql


def init_inventory_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            category VARCHAR(50) CHECK (category IN ('food', 'clothes', 'accessories', 'electronics')) NOT NULL,
            price_per_item NUMERIC NOT NULL,
            description TEXT,
            count_in_stock INT NOT NULL CHECK (count_in_stock >= 0)
        );"""
    )
    conn.commit()
    cur.close()
