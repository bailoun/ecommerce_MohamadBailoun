from .routes import inventory_bp
from .db import init_inventory_db


def init_inventory_service(app):
    """
    Initializes the inventory service by setting up the database and registering
    the inventory blueprint with the provided Flask app.

    Args:
        app: The Flask application instance to register the blueprint with.
    """
    with app.app_context():
        init_inventory_db()
    app.register_blueprint(inventory_bp)
