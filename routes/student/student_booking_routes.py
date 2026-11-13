# Student action to book a seat in a slot (POST only; the rules decide if it is allowed).
from flask import Blueprint, flash, redirect, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required
from models import Booking, Slot
from rules.booking_rules import can_book, refresh_slot_status

bp = Blueprint("student_bookings", __name__, url_prefix="/student/bookings")


@bp.route("/book/<int:slot_id>", methods=["POST"])
@role_required("student")
def book_slot(slot_id):
    # Check the rules again right now, then save the booking and update the slot status
    student = get_current_user()
    slot = db.get_or_404(Slot, slot_id)
    back_to_slots = url_for("student_exams.exam_slots", exam_id=slot.exam_id)

    ok, reason = can_book(student, slot)
    if not ok:
        flash(reason, "danger")
        return redirect(back_to_slots)

    # slot=slot also adds the booking to slot.bookings, so the seat count sees it
    booking = Booking(student=student, slot=slot, status="Booked")
    db.session.add(booking)
    refresh_slot_status(slot)
    db.session.commit()

    flash("Slot booked.", "success")
    return redirect(back_to_slots)
