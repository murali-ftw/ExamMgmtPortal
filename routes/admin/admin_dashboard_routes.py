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
    return render_template("admin/dashboard.html", counts=counts)
