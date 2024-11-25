from .routes import inventory_bp
from .db import init_inventory_db


def init_inventory_service(app):
    with app.app_context():
        init_inventory_db()
    app.register_blueprint(inventory_bp)
