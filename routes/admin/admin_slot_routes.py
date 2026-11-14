# Admin page to view all slots of all examiners and exams (read-only).
from flask import Blueprint, render_template

from helpers.auth_helpers import role_required
from models import Slot

bp = Blueprint("admin_slots", __name__, url_prefix="/admin/slots")


@bp.route("/")
@role_required("admin")
def list_slots():
    # Every slot, newest date first (latest start time first on the same day)
    slots = Slot.query.order_by(Slot.date.desc(), Slot.start_time.desc()).all()
    return render_template("admin/slots.html", slots=slots)
