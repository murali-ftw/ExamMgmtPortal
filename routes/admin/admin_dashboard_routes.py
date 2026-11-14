# Admin dashboard: shows the six totals (courses, exams, examiners, students, slots, bookings).
from flask import Blueprint, render_template

from helpers.auth_helpers import role_required
from models import Booking, Course, Exam, Slot, User

bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")


@bp.route("/dashboard")
@role_required("admin")
def dashboard():
    # Count the rows in each table and send the numbers to the page
    counts = {
        "courses": Course.query.count(),
        "exams": Exam.query.count(),
        "examiners": User.query.filter_by(role="examiner").count(),
        "students": User.query.filter_by(role="student").count(),
        "slots": Slot.query.count(),
        "bookings": Booking.query.count(),  # includes cancelled bookings (history)
    }

    # Bookings per exam: add up the Booked + Completed seats of every slot (slot.booked_count skips Cancelled)
    exam_rows = []
    for exam in Exam.query.order_by(Exam.name).all():
        booking_count = 0
        for slot in exam.slots:
            booking_count = booking_count + slot.booked_count
        exam_rows.append({"exam": exam, "course_name": exam.course.name, "booking_count": booking_count})

    return render_template("admin/dashboard.html", counts=counts, exam_rows=exam_rows)
