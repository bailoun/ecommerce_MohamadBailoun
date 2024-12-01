from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from common.db import init_db_connection, close_db
from customers import init_customers_service
from inventory import init_inventory_service
from sales import init_sales_service
from reviews import init_reviews_service


def create_app():
    app = Flask(__name__)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    init_db_connection()
    app.teardown_appcontext(close_db)

    init_customers_service(app)
    init_inventory_service(app)
    init_sales_service(app)
    init_reviews_service(app)

    @app.errorhandler(429)
    def ratelimit_error(error):
        return (
            jsonify(
                {
                    "error": "Too Many Requests",
                    "message": "You have exceeded the rate limit. Please try again later.",
                    "retry_after": error.description,
                }
            ),
            429,
        )

    return app
