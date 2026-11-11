# Student dashboard (placeholder for now; real content comes later).
from flask import Blueprint, render_template

from helpers.auth_helpers import role_required

bp = Blueprint("student_dashboard", __name__, url_prefix="/student")


@bp.route("/dashboard")
@role_required("student")
def dashboard():
    # Show the student welcome page
    return render_template("student/dashboard.html")
