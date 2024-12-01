from .routes import sales_bp
from .db import init_sales_db


def init_sales_service(app):
    """
    Initializes the sales service for the application by setting up the database
    and registering the sales blueprint with the app.
    """
    with app.app_context():
        init_sales_db()
    app.register_blueprint(sales_bp)
