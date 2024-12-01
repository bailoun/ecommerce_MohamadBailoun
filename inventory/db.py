from common.db import get_db
from psycopg2 import sql


def init_inventory_db():
    """
    Initializes the 'inventory' table in the database by creating it if it doesn't exist.
    The table contains information about inventory items, including name, category,
    price, description, and stock count.

    This function establishes a connection to the database, executes the SQL query to
    create the table, and commits the changes.

    Args:
        None

    Returns:
        None
    """
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
