# Admin page to view all bookings of every status (the complete history), with a search (read-only).
from flask import Blueprint, render_template, request
from sqlalchemy import or_

from helpers.auth_helpers import role_required
from helpers.search_helpers import read_search
from models import Booking, Exam, Slot, User

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
