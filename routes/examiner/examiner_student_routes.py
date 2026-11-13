# Examiner page: the students booked into one of MY slots.
from flask import Blueprint, abort, render_template

from database import db
from helpers.auth_helpers import get_current_user, role_required
from models import Slot

bp = Blueprint("examiner_students", __name__, url_prefix="/examiner/slots")


@bp.route("/<int:slot_id>/students")
@role_required("examiner")
def slot_students(slot_id):
    # Booked and Completed bookings of my slot; another examiner's slot gives 404
    slot = db.get_or_404(Slot, slot_id)
    if slot.examiner_id != get_current_user().id:
        abort(404)

    bookings = []
    for booking in slot.bookings:
        if booking.status == "Booked" or booking.status == "Completed":
            bookings.append(booking)

    return render_template("examiner/slot_students.html", slot=slot, bookings=bookings)
