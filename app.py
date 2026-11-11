# Start the app here: python app.py
from flask import Flask

from database import db
from database_setup import setup_database


def create_app():
    # Build the Flask app, connect the database and create tables + admin
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    setup_database(app)
    return app


app = create_app()

if __name__ == "__main__":
    # Port 5001 because macOS uses port 5000 for AirPlay
    app.run(debug=True, port=5001)
