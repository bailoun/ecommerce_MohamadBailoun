from common.db import get_db


def init_reviews_db():
    """
    Initializes the reviews database by creating a 'reviews' table if it doesn't
    already exist.

    The 'reviews' table includes the following fields:
    - id: A unique identifier for each review (primary key).
    - customer_id: The ID of the customer who wrote the review (foreign key).
    - item_id: The ID of the item being reviewed (foreign key).
    - rating: The rating given to the item, ranging from 1 to 5.
    - comment: A textual comment from the customer about the item.
    - is_approved: A boolean indicating if the review has been approved.
    - review_date: The timestamp when the review was created.

    The table also includes constraints for valid ratings and ensures foreign key relationships
    with the `customers` and `inventory` tables.

    Returns:
        None
    """
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
