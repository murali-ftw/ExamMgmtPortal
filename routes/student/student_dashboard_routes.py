# Student dashboard: five counts (open exams, open slots, upcoming, booked, published results).
from datetime import date

from flask import Blueprint, render_template

from helpers.auth_helpers import get_current_user, role_required
from models import Booking, Exam, Slot
from routes.student.student_result_routes import get_published_bookings
from rules.window_rules import booking_open

bp = Blueprint("student_dashboard", __name__, url_prefix="/student")


@bp.route("/dashboard")
@role_required("student")
def dashboard():
    # Count the numbers for my cards and send them to the page
    student = get_current_user()

    # Exams whose booking is open right now, and their Available slots
    open_exams = 0
    available_slots = 0
    for exam in Exam.query.all():
        if booking_open(exam):
            open_exams = open_exams + 1
            available_slots = available_slots + Slot.query.filter_by(exam_id=exam.id, status="Available").count()

    # My Booked bookings; the upcoming ones have a slot date of today or later
    booked = Booking.query.filter_by(student_id=student.id, status="Booked").all()
    upcoming = 0
    for booking in booked:
        if booking.slot.date >= date.today():
            upcoming = upcoming + 1

    counts = {
        "open_exams": open_exams,
        "available_slots": available_slots,
        "upcoming": upcoming,
        "booked": len(booked),
        "results": len(get_published_bookings(student)),
    }
    return render_template("student/dashboard.html", counts=counts)
