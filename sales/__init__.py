from .routes import sales_bp
from .db import init_sales_db


def init_sales_service(app):
    with app.app_context():
        init_sales_db()
    app.register_blueprint(sales_bp)
