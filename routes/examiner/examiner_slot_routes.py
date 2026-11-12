# Examiner pages to list, create, edit and delete my own slots.
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required
from helpers.form_helpers import parse_date, parse_time, to_int
from models import Exam, ExamAssignment, Slot
from rules.window_rules import slot_can_be_edited, slot_creation_open

bp = Blueprint("examiner_slots", __name__, url_prefix="/examiner/slots")


def read_slot_form(form):
    # Read and check the slot form; returns (data, error_message)
    data = {
        "slot_date": parse_date(form.get("slot_date")),
        "start_time": parse_time(form.get("start_time")),
        "end_time": parse_time(form.get("end_time")),
        "capacity": to_int(form.get("capacity")),
    }
    if data["slot_date"] is None:
        return data, "Please enter a valid date."
    if data["slot_date"] < date.today():
        return data, "The slot date cannot be in the past."
    if data["start_time"] is None or data["end_time"] is None:
        return data, "Please enter a start time and an end time."
    if data["end_time"] <= data["start_time"]:
        return data, "The end time must be after the start time."
    if data["capacity"] is None or data["capacity"] < 1:
        return data, "Capacity must be a whole number of at least 1."
    return data, None


def is_assigned(examiner, exam):
    # True if this examiner is assigned to this exam
    return ExamAssignment.query.filter_by(exam_id=exam.id, examiner_id=examiner.id).first() is not None


def get_my_slot(slot_id):
    # Load a slot of the logged-in examiner; someone else's slot gives 404
    slot = db.get_or_404(Slot, slot_id)
    if slot.examiner_id != get_current_user().id:
        abort(404)
    return slot


@bp.route("/")
@role_required("examiner")
def my_slots():
    # All my slots, newest date first, optionally for one exam (?exam_id=)
    user = get_current_user()
    exam_id = to_int(request.args.get("exam_id"))
    query = Slot.query.filter_by(examiner_id=user.id)
    if exam_id is not None:
        query = query.filter_by(exam_id=exam_id)
    slots = query.order_by(Slot.date.desc(), Slot.start_time).all()

    # Exams for the filter dropdown: the ones I am assigned to
    my_exams = []
    for assignment in ExamAssignment.query.filter_by(examiner_id=user.id).all():
        my_exams.append(assignment.exam)
    return render_template("examiner/slots.html", slots=slots, my_exams=my_exams, exam_id=exam_id)


@bp.route("/create/<int:exam_id>", methods=["GET", "POST"])
@role_required("examiner")
def create_slot(exam_id):
    # Create a slot for an exam I am assigned to, only while slot creation is open
    user = get_current_user()
    exam = db.get_or_404(Exam, exam_id)
    if not is_assigned(user, exam):
        flash("You are not assigned to this exam.", "danger")
        return redirect(url_for("examiner_exams.my_exams"))
    if not slot_creation_open(exam):
        flash("Slot creation is not open for this exam.", "danger")
        return redirect(url_for("examiner_exams.my_exams"))

    form = {}
    if request.method == "POST":
        data, error = read_slot_form(request.form)
        if error:
            flash(error, "danger")
            form = request.form
        else:
            slot = Slot(exam_id=exam.id, examiner_id=user.id, date=data["slot_date"],
                        start_time=data["start_time"], end_time=data["end_time"],
                        capacity=data["capacity"], status="Available")
            db.session.add(slot)
            db.session.commit()
            flash("Slot created.", "success")
            return redirect(url_for("examiner_slots.my_slots"))

    return render_template("examiner/slot_form.html", exam=exam, slot=None, form=form)


@bp.route("/<int:slot_id>/edit", methods=["GET", "POST"])
@role_required("examiner")
def edit_slot(slot_id):
    # Change my slot, only before booking starts
    slot = get_my_slot(slot_id)
    if not slot_can_be_edited(slot):
        flash("This slot can no longer be changed because booking has started.", "warning")
        return redirect(url_for("examiner_slots.my_slots"))

    form = {"slot_date": slot.date.isoformat(), "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"), "capacity": slot.capacity}

    if request.method == "POST":
        data, error = read_slot_form(request.form)
        if error is None and data["capacity"] < slot.booked_count:
            error = "Capacity cannot be less than the " + str(slot.booked_count) + " seats already booked."
        if error:
            flash(error, "danger")
            form = request.form
        else:
            slot.date = data["slot_date"]
            slot.start_time = data["start_time"]
            slot.end_time = data["end_time"]
            slot.capacity = data["capacity"]
            db.session.commit()
            flash("Slot updated.", "success")
            return redirect(url_for("examiner_slots.my_slots"))

    return render_template("examiner/slot_form.html", exam=slot.exam, slot=slot, form=form)


@bp.route("/<int:slot_id>/delete", methods=["POST"])
@role_required("examiner")
def delete_slot(slot_id):
    # Remove my slot, only before booking starts and only if nobody booked it
    slot = get_my_slot(slot_id)
    if not slot_can_be_edited(slot):
        flash("This slot can no longer be removed because booking has started.", "warning")
    elif len(slot.bookings) > 0:
        flash("This slot has bookings, so it cannot be deleted.", "warning")
    else:
        db.session.delete(slot)
        db.session.commit()
        flash("Slot deleted.", "success")
    return redirect(url_for("examiner_slots.my_slots"))
