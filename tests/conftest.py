import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from app_init import create_app
from common.db import get_db, close_db
import psycopg2


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS customers")
        cur.execute("DROP TABLE IF EXISTS inventory")
        from customers.db import init_customers_db
        from inventory.db import init_inventory_db

        init_customers_db()
        init_inventory_db()
        conn.commit()
        cur.close()
    yield app
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS customers")
        cur.execute("DROP TABLE IF EXISTS inventory")
        conn.commit()
        cur.close()


@pytest.fixture
def client(app):
    return app.test_client()
