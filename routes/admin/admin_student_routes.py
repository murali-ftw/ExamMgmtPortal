# Admin page to view all students, with a search by name, email or ID (read-only).
from flask import Blueprint, render_template, request
from sqlalchemy import or_

from helpers.auth_helpers import role_required
from helpers.search_helpers import read_search
from models import Booking, User

bp = Blueprint("admin_students", __name__, url_prefix="/admin/students")


@bp.route("/")
@role_required("admin")
def list_students():
    # All students by name; ?q= matches the exact ID (if a number) or part of the name/email
    q, id_number = read_search(request.args.get("q", ""))
    query = User.query.filter_by(role="student")

    if q:
        pattern = "%" + q + "%"
        if id_number is not None:
            query = query.filter(or_(User.id == id_number, User.name.ilike(pattern), User.email.ilike(pattern)))
        else:
            query = query.filter(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

    students = query.order_by(User.name).all()

    # One row per student with how many bookings they have (all statuses)
    rows = []
    for student in students:
        booking_count = Booking.query.filter_by(student_id=student.id).count()
        rows.append({"student": student, "booking_count": booking_count})

    return render_template("admin/students.html", rows=rows, q=q)
