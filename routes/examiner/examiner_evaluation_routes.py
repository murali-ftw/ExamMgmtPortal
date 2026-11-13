# Examiner pages to list my students to evaluate and to submit marks with the exam's rubric.
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required
from helpers.form_helpers import to_float
from models import Booking, Evaluation, EvaluationScore, Slot
from rules.result_rules import evaluation_allowed

bp = Blueprint("examiner_evaluations", __name__, url_prefix="/examiner/evaluations")


def get_my_booking(booking_id):
    # Load a booking in one of MY slots; a booking in another examiner's slot gives 404
    booking = db.get_or_404(Booking, booking_id)
    if booking.slot.examiner_id != get_current_user().id:
        abort(404)
    return booking


@bp.route("/")
@role_required("examiner")
def my_evaluations():
    # Booked/Completed bookings in my slots: pending ones first, then evaluated ones
    user = get_current_user()
    pending = []
    evaluated = []
    for slot in Slot.query.filter_by(examiner_id=user.id).order_by(Slot.date, Slot.start_time).all():
        for booking in slot.bookings:
            if booking.status != "Booked" and booking.status != "Completed":
                continue
            if booking.evaluation is None:
                pending.append(booking)
            else:
                evaluated.append(booking)

    return render_template("examiner/evaluations.html", bookings=pending + evaluated)


@bp.route("/<int:booking_id>", methods=["GET", "POST"])
@role_required("examiner")
def evaluate(booking_id):
    # Show the submitted evaluation, or the rubric form; on POST check and save the marks
    booking = get_my_booking(booking_id)
    back_to_list = redirect(url_for("examiner_evaluations.my_evaluations"))

    # Already evaluated: show it read-only (a second POST is refused below by evaluation_allowed)
    if request.method == "GET" and booking.evaluation is not None:
        return render_template("examiner/evaluate.html", booking=booking, evaluation=booking.evaluation)

    ok, reason = evaluation_allowed(booking)
    if not ok:
        flash(reason, "warning")
        return back_to_list

    rubrics = booking.slot.exam.rubrics
    if len(rubrics) == 0:
        flash("This exam has no rubric yet. Ask the admin to add one.", "warning")
        return back_to_list

    form = {}
    if request.method == "POST":
        form = request.form
        error = None
        marks_list = []
        total = 0
        for rubric in rubrics:
            marks = to_float(request.form.get("marks_" + str(rubric.id)))
            # "not (0 <= marks <= max)" also rejects odd values like "nan"
            if marks is None or not (0 <= marks <= rubric.max_marks):
                error = "Marks for " + rubric.criterion_name + " must be a number from 0 to " + str(rubric.max_marks) + "."
                break
            marks_list.append((rubric, marks))
            total = total + marks

        remarks = request.form.get("remarks", "").strip()
        if error is None and not remarks:
            error = "Remarks are required."

        if error:
            flash(error, "danger")
        else:
            # One Evaluation + one EvaluationScore per criterion, saved together in ONE commit
            evaluation = Evaluation(booking=booking, total_marks=total, remarks=remarks)
            for rubric, marks in marks_list:
                evaluation.scores.append(EvaluationScore(rubric=rubric, marks=marks))
            db.session.add(evaluation)
            booking.status = "Completed"
            db.session.commit()
            flash("Evaluation saved for " + booking.student.name + ". Total: " + str(total) + ".", "success")
            return back_to_list

    return render_template("examiner/evaluate.html", booking=booking, evaluation=None, rubrics=rubrics, form=form)
