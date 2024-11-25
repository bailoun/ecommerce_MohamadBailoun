from .routes import customers_bp
from .db import init_customers_db


def init_customers_service(app):
    with app.app_context():
        init_customers_db()
    app.register_blueprint(customers_bp)
