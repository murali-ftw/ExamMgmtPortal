# Student pages to see my published results (only for exams the admin marked Completed).
from flask import Blueprint, abort, render_template

from database import db
from helpers.auth_helpers import get_current_user, role_required
from models import Booking
from rules.result_rules import results_visible

bp = Blueprint("student_results", __name__, url_prefix="/student/results")


def get_published_bookings(student):
    # My bookings that have an evaluation AND whose exam results are visible (also used by the dashboard)
    published = []
    for booking in Booking.query.filter_by(student_id=student.id).all():
        if booking.evaluation is not None and results_visible(booking.slot.exam):
            published.append(booking)
    return published


@bp.route("/")
@role_required("student")
def my_results():
    # List of my published results
    bookings = get_published_bookings(get_current_user())
    return render_template("student/results.html", bookings=bookings)


@bp.route("/<int:booking_id>")
@role_required("student")
def result_detail(booking_id):
    # One result with marks per criterion; every "not allowed" case is a 404 so nothing leaks
    booking = db.get_or_404(Booking, booking_id)
    if booking.student_id != get_current_user().id:
        abort(404)
    if booking.evaluation is None:
        abort(404)
    if not results_visible(booking.slot.exam):
        abort(404)

    return render_template("student/result_detail.html", booking=booking, evaluation=booking.evaluation)
