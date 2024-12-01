from .routes import customers_bp
from .db import init_customers_db


def init_customers_service(app):
    """
    Initializes the customers service by setting up the database and registering the
    customers blueprint within the provided Flask app context.

    This function performs the following tasks:
    1. Initializes the database connection by calling `init_customers_db`.
    2. Registers the `customers_bp` blueprint, which handles all customer-related routes.

    Args:
        app (Flask): The Flask application instance to register the blueprint and initialize the service.
    """
    with app.app_context():
        init_customers_db()
    app.register_blueprint(customers_bp)
