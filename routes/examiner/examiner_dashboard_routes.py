# Examiner dashboard: four counts (assigned exams, my slots, students booked, pending evaluations).
from flask import Blueprint, render_template

from helpers.auth_helpers import get_current_user, role_required
from models import ExamAssignment, Slot

bp = Blueprint("examiner_dashboard", __name__, url_prefix="/examiner")


@bp.route("/dashboard")
@role_required("examiner")
def dashboard():
    # Count the numbers for my cards; only MY slots and their bookings are counted
    user = get_current_user()
    my_slots = Slot.query.filter_by(examiner_id=user.id).all()

    students_booked = 0
    pending = 0
    for slot in my_slots:
        for booking in slot.bookings:
            if booking.status == "Booked" or booking.status == "Completed":
                students_booked = students_booked + 1
            if booking.status == "Booked" and booking.evaluation is None:
                pending = pending + 1

    counts = {
        "assigned": ExamAssignment.query.filter_by(examiner_id=user.id).count(),
        "slots": len(my_slots),
        "students_booked": students_booked,
        "pending": pending,
    }
    return render_template("examiner/dashboard.html", counts=counts)
