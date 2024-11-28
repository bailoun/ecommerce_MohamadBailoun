from .routes import reviews_bp
from .db import init_reviews_db


def init_reviews_service(app):
    with app.app_context():
        init_reviews_db()
    app.register_blueprint(reviews_bp)
