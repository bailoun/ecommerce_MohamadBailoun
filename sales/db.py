from common.db import get_db


def init_sales_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL REFERENCES customers(id),
            item_id INT NOT NULL REFERENCES inventory(id),
            quantity INT NOT NULL CHECK (quantity > 0),
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    )
    conn.commit()
    cur.close()
