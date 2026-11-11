# Small user functions shared by register and admin pages.
from werkzeug.security import generate_password_hash

from database import db
from models import User


def email_exists(email):
    # True if some user already has this email
    return User.query.filter_by(email=email).first() is not None


def create_user(name, email, password, role, status, department=None, contact=None, roll_no=None):
    # Save a new user with a hashed password and return it
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        status=status,
        department=department,
        contact=contact,
        roll_no=roll_no,
    )
    db.session.add(user)
    db.session.commit()
    return user
