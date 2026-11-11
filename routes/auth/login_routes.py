# Login, logout and the home page that sends each role to its own dashboard.
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from helpers.auth_helpers import get_current_user
from models import User

bp = Blueprint("login", __name__)

# Which dashboard page each role goes to
DASHBOARDS = {
    "admin": "admin_dashboard.dashboard",
    "examiner": "examiner_dashboard.dashboard",
    "student": "student_dashboard.dashboard",
}


@bp.route("/")
def home():
    # Not logged in -> login page, otherwise -> the user's dashboard
    user = get_current_user()
    if user is None:
        return redirect(url_for("login.login"))
    return redirect(url_for(DASHBOARDS[user.role]))


@bp.route("/login", methods=["GET", "POST"])
def login():
    # Show the login form, and check the email + password when it is sent
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Wrong email or password.", "danger")
        elif user.status == "pending":
            flash("Your account is waiting for admin approval.", "warning")
        elif user.status == "inactive":
            flash("Your account has been deactivated. Contact the admin.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("login.home"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    # Forget the logged-in user
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login.login"))
