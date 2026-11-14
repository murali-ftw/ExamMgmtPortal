# Student booking actions: book a slot, see my bookings, cancel a booking (rules decide).
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required
from models import Booking, Slot
from rules.booking_rules import can_book, can_cancel, refresh_slot_status
from rules.window_rules import booking_open

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
        # When booking is closed the slots page is hidden, so go to the exam list (avoids a second message)
        if not booking_open(slot.exam):
            return redirect(url_for("student_exams.browse_exams"))
        return redirect(back_to_slots)

    # slot=slot also adds the booking to slot.bookings, so the seat count sees it
    booking = Booking(student=student, slot=slot, status="Booked")
    db.session.add(booking)
    refresh_slot_status(slot)
    db.session.commit()

    flash("Slot booked.", "success")
    return redirect(back_to_slots)


@bp.route("/")
@role_required("student")
def my_bookings():
    # All my bookings (history), newest first, each with can_cancel's (ok, reason)
    student = get_current_user()
    bookings = (Booking.query.filter_by(student_id=student.id)
                .order_by(Booking.booking_date.desc(), Booking.id.desc()).all())

    rows = []
    for booking in bookings:
        ok, reason = can_cancel(booking)
        rows.append({"booking": booking, "can_cancel": ok})

    return render_template("student/bookings.html", rows=rows)


@bp.route("/<int:booking_id>/cancel", methods=["POST"])
@role_required("student")
def cancel_booking(booking_id):
    # Cancel my own booking if the rules allow it; the row is kept as history
    student = get_current_user()
    booking = db.get_or_404(Booking, booking_id)
    if booking.student_id != student.id:
        abort(404)

    ok, reason = can_cancel(booking)
    if not ok:
        flash(reason, "danger")
        return redirect(url_for("student_bookings.my_bookings"))

    booking.status = "Cancelled"
    refresh_slot_status(booking.slot)
    db.session.commit()

    flash("Booking cancelled.", "success")
    return redirect(url_for("student_bookings.my_bookings"))
