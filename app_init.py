from flask import Flask
from common.db import init_db_connection, close_db
from customers import init_customers_service
from inventory import init_inventory_service
from sales import init_sales_service


def create_app():
    app = Flask(__name__)

    init_db_connection()
    app.teardown_appcontext(close_db)

    init_customers_service(app)
    init_inventory_service(app)
    init_sales_service(app)

    return app
