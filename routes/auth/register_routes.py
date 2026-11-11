# Registration pages for students and examiners (admins are never registered).
from flask import Blueprint, flash, redirect, render_template, request, url_for

from helpers.user_helpers import create_user, email_exists

bp = Blueprint("register", __name__, url_prefix="/register")


def check_basic_fields(name, email, password):
    # Return an error message, or None if the fields are fine
    if not name or not email or not password:
        return "Name, email and password are required."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if email_exists(email):
        return "This email is already registered."
    return None


@bp.route("/student", methods=["GET", "POST"])
def register_student():
    # Students are active straight away
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        roll_no = request.form.get("roll_no", "").strip()
        contact = request.form.get("contact", "").strip()

        error = check_basic_fields(name, email, password)
        if error:
            flash(error, "danger")
        else:
            create_user(name, email, password, "student", "active", contact=contact, roll_no=roll_no)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login.login"))

    return render_template("auth/register_student.html")


@bp.route("/examiner", methods=["GET", "POST"])
def register_examiner():
    # Examiners start as pending until the admin approves them
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        department = request.form.get("department", "").strip()
        contact = request.form.get("contact", "").strip()

        error = check_basic_fields(name, email, password)
        if error:
            flash(error, "danger")
        else:
            create_user(name, email, password, "examiner", "pending", department=department, contact=contact)
            flash("Registration successful. You can log in after the admin approves your account.", "success")
            return redirect(url_for("login.login"))

    return render_template("auth/register_examiner.html")
