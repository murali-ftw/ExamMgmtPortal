# Admin pages to list, add, approve, deactivate and activate examiners.
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.user_helpers import create_user, email_exists
from models import User

bp = Blueprint("admin_examiners", __name__, url_prefix="/admin/examiners")

EXAMINER_STATUSES = ["pending", "active", "inactive"]


@bp.route("/")
@role_required("admin")
def list_examiners():
    # Show all examiners, optionally only one status (?status=pending)
    status = request.args.get("status", "")
    query = User.query.filter_by(role="examiner")
    if status in EXAMINER_STATUSES:
        query = query.filter_by(status=status)
    examiners = query.order_by(User.name).all()
    return render_template("admin/examiners.html", examiners=examiners, status=status, statuses=EXAMINER_STATUSES)


@bp.route("/add", methods=["GET", "POST"])
@role_required("admin")
def add_examiner():
    # The admin creates an examiner who is active straight away
    form = {}
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        contact = request.form.get("contact", "").strip()
        password = request.form.get("password", "")

        error = None
        if not name or not email:
            error = "Name and email are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif email_exists(email):
            error = "This email is already registered."

        if error:
            flash(error, "danger")
            form = request.form
        else:
            create_user(name, email, password, "examiner", "active", department=department, contact=contact)
            flash("Examiner " + name + " added and active.", "success")
            return redirect(url_for("admin_examiners.list_examiners"))

    return render_template("admin/examiner_form.html", form=form)


def set_examiner_status(examiner_id, new_status, message):
    # Shared by approve / deactivate / activate: change the status of one examiner
    user = db.get_or_404(User, examiner_id)
    if user.role != "examiner":
        flash("This user is not an examiner.", "danger")
    else:
        user.status = new_status
        db.session.commit()
        flash(message + " " + user.name + ".", "success")
    return redirect(url_for("admin_examiners.list_examiners"))


@bp.route("/<int:examiner_id>/approve", methods=["POST"])
@role_required("admin")
def approve_examiner(examiner_id):
    # pending -> active
    return set_examiner_status(examiner_id, "active", "Approved")


@bp.route("/<int:examiner_id>/deactivate", methods=["POST"])
@role_required("admin")
def deactivate_examiner(examiner_id):
    # active -> inactive (they can no longer log in)
    return set_examiner_status(examiner_id, "inactive", "Deactivated")


@bp.route("/<int:examiner_id>/activate", methods=["POST"])
@role_required("admin")
def activate_examiner(examiner_id):
    # inactive -> active again
    return set_examiner_status(examiner_id, "active", "Activated")
