# Admin dashboard (placeholder for now; the totals come in the next chunk).
from flask import Blueprint, render_template

from helpers.auth_helpers import role_required

bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")


@bp.route("/dashboard")
@role_required("admin")
def dashboard():
    # Show the admin welcome page
    return render_template("admin/dashboard.html")
