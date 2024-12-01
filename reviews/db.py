from common.db import get_db


def init_reviews_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL REFERENCES customers(id),
            item_id INT NOT NULL REFERENCES inventory(id),
            rating INT CHECK (rating >= 1 AND rating <= 5) NOT NULL,
            comment TEXT,
            is_approved BOOLEAN DEFAULT FALSE,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    )
    conn.commit()
    cur.close()
