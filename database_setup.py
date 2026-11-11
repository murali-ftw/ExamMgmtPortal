# Creates all tables and the default admin account when the app starts.
from werkzeug.security import generate_password_hash

import models  # loads every model so create_all knows all the tables
from database import db
from models import User


def create_default_admin(app):
    # Make the admin from config.py, but only if there is no admin yet
    admin = User.query.filter_by(role="admin").first()
    if admin is not None:
        return

    admin = User(
        name=app.config["ADMIN_NAME"],
        email=app.config["ADMIN_EMAIL"],
        password_hash=generate_password_hash(app.config["ADMIN_PASSWORD"]),
        role="admin",
        status="active",
    )
    db.session.add(admin)
    db.session.commit()


def setup_database(app):
    # Create missing tables, then make sure the admin exists
    with app.app_context():
        db.create_all()
        create_default_admin(app)
