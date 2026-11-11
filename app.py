# Start the app here: python app.py
from flask import Flask

from database import db
from database_setup import setup_database
from helpers.auth_helpers import get_current_user
from routes import register_all_blueprints


def create_app():
    # Build the Flask app, connect the database, add the pages, create tables + admin
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    register_all_blueprints(app)

    @app.context_processor
    def add_current_user():
        # Every template can use {{ current_user }}
        return {"current_user": get_current_user()}

    setup_database(app)
    return app


app = create_app()

if __name__ == "__main__":
    # Port 5001 because macOS uses port 5000 for AirPlay
    app.run(debug=True, port=5001)
