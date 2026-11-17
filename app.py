# Start the app here: python app.py
from flask import Flask, request
from werkzeug.exceptions import NotFound

from database import db
from database_setup import setup_database
from helpers.auth_helpers import get_current_user
from routes import register_all_blueprints
from rules.window_rules import booking_open, slot_can_be_edited, slot_creation_open


def create_app():
    # Build the Flask app, connect the database, add the pages, create tables + admin
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    register_all_blueprints(app)

    @app.context_processor
    def add_template_values():
        # Every template can use current_user and the three window rules
        return {
            "current_user": get_current_user(),
            "booking_open": booking_open,
            "slot_creation_open": slot_creation_open,
            "slot_can_be_edited": slot_can_be_edited,
        }

    @app.after_request
    def no_cache(response):
        # Browser must not keep pages (Back after logout shows nothing old); static CSS/JS may still be cached
        if not request.path.startswith("/static"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(OverflowError)
    def number_too_big(error):
        # A huge id in the URL (too big for SQLite) cannot exist, so show the normal "Not Found" page
        return NotFound()

    setup_database(app)
    return app


app = create_app()

if __name__ == "__main__":
    # Port 5001 because macOS uses port 5000 for AirPlay
    app.run(debug=True, port=5001)
