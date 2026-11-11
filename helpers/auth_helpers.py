# Login helpers: who is logged in, and the @role_required check for protected pages.
from functools import wraps

from flask import flash, redirect, session, url_for

from database import db
from models import User


def get_current_user():
    # Return the logged-in User from the session, or None
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


def role_required(role):
    # Use as @role_required("admin") under @bp.route(...)
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = get_current_user()

            # Not logged in, or account pending/inactive
            if user is None or user.status != "active":
                session.clear()
                flash("Please log in first.")
                return redirect(url_for("login.login"))

            # Logged in but wrong role for this page
            if user.role != role:
                flash("You are not allowed to open that page.")
                return redirect(url_for("login.home"))

            return view(*args, **kwargs)
        return wrapper
    return decorator
