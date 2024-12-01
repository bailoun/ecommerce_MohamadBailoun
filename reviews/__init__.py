from .routes import reviews_bp
from .db import init_reviews_db


def init_reviews_service(app):
    """
    Initializes the reviews service by setting up the database and registering
    the reviews blueprint with the given Flask application.

    This function is meant to be called within the Flask app context. It ensures
    that the necessary database tables are created and prepares the routes
    for handling review-related API requests.

    Args:
        app (Flask): The Flask application instance to register the blueprint with.

    Returns:
        None
    """
    with app.app_context():
        init_reviews_db()
    app.register_blueprint(reviews_bp)
