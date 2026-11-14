# Admin pages to view all bookings of every status (the complete history), search them, and reschedule one.
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import to_int
from helpers.search_helpers import read_search
from models import Booking, Exam, Slot, User
from rules.admin_change_rules import can_move_booking, can_reschedule
from rules.booking_rules import refresh_slot_status

bp = Blueprint("admin_bookings", __name__, url_prefix="/admin/bookings")


@bp.route("/")
@role_required("admin")
def list_bookings():
    # All bookings, newest first; ?q= matches booking ID / student ID (if a number) or student name/email / exam name
    q, id_number = read_search(request.args.get("q", ""))

    # Join the student, slot and exam tables so we can search on their columns
    query = Booking.query.join(Booking.student).join(Booking.slot).join(Slot.exam)

    if q:
        pattern = "%" + q + "%"
        text_match = or_(User.name.ilike(pattern), User.email.ilike(pattern), Exam.name.ilike(pattern))
        if id_number is not None:
            query = query.filter(or_(Booking.id == id_number, Booking.student_id == id_number, text_match))
        else:
            query = query.filter(text_match)

    bookings = query.order_by(Booking.booking_date.desc(), Booking.id.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings, q=q)


@bp.route("/<int:booking_id>/reschedule", methods=["GET", "POST"])
@role_required("admin")
def reschedule_booking(booking_id):
    # GET: pick a new slot of the same exam. POST: check the rule again, move the booking, fix both slots.
    booking = db.get_or_404(Booking, booking_id)
    back_to_page = redirect(url_for("admin_bookings.reschedule_booking", booking_id=booking.id))

    if request.method == "POST":
        new_slot_id = to_int(request.form.get("new_slot_id"))
        if new_slot_id is None:
            flash("Please choose a slot.", "danger")
            return back_to_page
        new_slot = db.get_or_404(Slot, new_slot_id)

        ok, reason = can_reschedule(booking, new_slot)
        if not ok:
            flash(reason, "danger")
            return back_to_page

        # booking.slot = new_slot also updates old_slot.bookings and new_slot.bookings, so the seat counts are right
        old_slot = booking.slot
        booking.slot = new_slot
        refresh_slot_status(old_slot)
        refresh_slot_status(new_slot)
        db.session.commit()
        flash("Booking " + str(booking.id) + " of " + booking.student.name + " moved to the slot on "
              + str(new_slot.date) + " at " + new_slot.start_time.strftime("%H:%M") + ".", "success")
        return redirect(url_for("admin_bookings.list_bookings"))

    # GET: if this booking cannot move at all (Cancelled, Completed, exam completed), go back to the list
    ok, reason = can_move_booking(booking)
    if not ok:
        flash(reason, "warning")
        return redirect(url_for("admin_bookings.list_bookings"))

    # The slots of the same exam that this booking may move to (the rule decides)
    eligible_slots = []
    for slot in Slot.query.filter_by(exam_id=booking.slot.exam_id).order_by(Slot.date, Slot.start_time).all():
        ok, reason = can_reschedule(booking, slot)
        if ok:
            eligible_slots.append(slot)

    return render_template("admin/reschedule_booking.html", booking=booking, slots=eligible_slots)
