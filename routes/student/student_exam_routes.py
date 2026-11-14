# Student pages to browse exams that are open for booking and see their slots.
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required
from models import Exam, Slot
from rules.booking_rules import can_book
from rules.window_rules import booking_open

bp = Blueprint("student_exams", __name__, url_prefix="/student/exams")


def has_booked(student, exam):
    # True if the student has a "Booked" booking in any slot of this exam
    for slot in exam.slots:
        for booking in slot.bookings:
            if booking.student_id == student.id and booking.status == "Booked":
                return True
    return False


@bp.route("/")
@role_required("student")
def browse_exams():
    # Exams whose booking is open today, with optional ?q= search on exam or course name
    student = get_current_user()
    q = request.args.get("q", "").strip()

    rows = []
    for exam in Exam.query.order_by(Exam.booking_end).all():
        if not booking_open(exam):
            continue
        if q != "":
            text = q.lower()
            if text not in exam.name.lower() and text not in exam.course.name.lower():
                continue
        rows.append({"exam": exam, "already_booked": has_booked(student, exam)})

    return render_template("student/exams.html", rows=rows, q=q)


@bp.route("/<int:exam_id>/slots")
@role_required("student")
def exam_slots(exam_id):
    # One exam with its slots; each slot gets (ok, reason) from can_book
    student = get_current_user()
    exam = db.get_or_404(Exam, exam_id)

    # Slots are shown only while booking is open (same rule as the exam list)
    if not booking_open(exam):
        flash("Booking is not open for this exam.", "warning")
        return redirect(url_for("student_exams.browse_exams"))

    slots = (Slot.query.filter(Slot.exam_id == exam.id, Slot.status != "Cancelled")
             .order_by(Slot.date, Slot.start_time).all())

    rows = []
    for slot in slots:
        ok, reason = can_book(student, slot)
        rows.append({"slot": slot, "ok": ok, "reason": reason})

    return render_template("student/exam_slots.html", exam=exam, rows=rows)
