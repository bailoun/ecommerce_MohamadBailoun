from app_init import create_app

app = create_app()

if __name__ == "__main__":
    """
    Starts the Flask application in debug mode.
    """
    app.run(debug=True)
