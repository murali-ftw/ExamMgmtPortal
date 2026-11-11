# Examiner dashboard (placeholder for now; real content comes later).
from flask import Blueprint, render_template

from helpers.auth_helpers import role_required

bp = Blueprint("examiner_dashboard", __name__, url_prefix="/examiner")


@bp.route("/dashboard")
@role_required("examiner")
def dashboard():
    # Show the examiner welcome page
    return render_template("examiner/dashboard.html")
