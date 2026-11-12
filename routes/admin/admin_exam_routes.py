# Admin pages to list, add, edit, delete and view examinations.
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import parse_date, to_int
from models import EXAM_TYPES, Course, Exam, Slot
from rules.exam_status_rules import get_actions_for

bp = Blueprint("admin_exams", __name__, url_prefix="/admin/exams")


def read_exam_form(form):
    # Read and check the exam form; returns (data, error_message). Used by add and edit.
    data = {
        "course_id": to_int(form.get("course_id")),
        "name": form.get("name", "").strip(),
        "exam_type": form.get("exam_type", ""),
        "duration": to_int(form.get("duration")),
        "max_marks": to_int(form.get("max_marks")),
        "slot_creation_start": parse_date(form.get("slot_creation_start")),
        "slot_creation_end": parse_date(form.get("slot_creation_end")),
        "booking_start": parse_date(form.get("booking_start")),
        "booking_end": parse_date(form.get("booking_end")),
    }

    # Every field must be filled in with a valid value (None means missing or invalid)
    for key, value in data.items():
        if value is None or value == "":
            return data, "Please fill in every field with a valid value."

    if db.session.get(Course, data["course_id"]) is None:
        return data, "Please choose a valid course."
    if data["exam_type"] not in EXAM_TYPES:
        return data, "Please choose a valid exam type."
    if data["duration"] <= 0:
        return data, "Duration must be more than 0 minutes."
    if data["max_marks"] <= 0:
        return data, "Maximum marks must be more than 0."
    if data["slot_creation_end"] < data["slot_creation_start"]:
        return data, "Slot creation end date cannot be before its start date."
    if data["booking_end"] < data["booking_start"]:
        return data, "Booking end date cannot be before its start date."
    return data, None


def copy_data_to_exam(exam, data):
    # Put the checked form values onto the exam object
    exam.course_id = data["course_id"]
    exam.name = data["name"]
    exam.exam_type = data["exam_type"]
    exam.duration = data["duration"]
    exam.max_marks = data["max_marks"]
    exam.slot_creation_start = data["slot_creation_start"]
    exam.slot_creation_end = data["slot_creation_end"]
    exam.booking_start = data["booking_start"]
    exam.booking_end = data["booking_end"]


@bp.route("/")
@role_required("admin")
def list_exams():
    # Show all exams, newest first
    exams = Exam.query.order_by(Exam.id.desc()).all()
    return render_template("admin/exams.html", exams=exams)


@bp.route("/add", methods=["GET", "POST"])
@role_required("admin")
def add_exam():
    # Create a new exam (starts as Draft)
    courses = Course.query.filter_by(status="Active").order_by(Course.code).all()
    if len(courses) == 0:
        flash("Add an active course before creating an examination.", "warning")
        return redirect(url_for("admin_courses.list_courses"))

    form = {}
    if request.method == "POST":
        data, error = read_exam_form(request.form)
        if error:
            flash(error, "danger")
            form = request.form
        else:
            exam = Exam(status="Draft")
            copy_data_to_exam(exam, data)
            db.session.add(exam)
            db.session.commit()
            flash("Examination " + exam.name + " created as Draft.", "success")
            return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    return render_template("admin/exam_form.html", form=form, exam=None, courses=courses, exam_types=EXAM_TYPES)


@bp.route("/<int:exam_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_exam(exam_id):
    # Change an exam's details (the status is changed only with the status buttons)
    exam = db.get_or_404(Exam, exam_id)
    courses = Course.query.order_by(Course.code).all()
    form = {
        "course_id": str(exam.course_id),
        "name": exam.name,
        "exam_type": exam.exam_type,
        "duration": exam.duration,
        "max_marks": exam.max_marks,
        "slot_creation_start": exam.slot_creation_start.isoformat() if exam.slot_creation_start else "",
        "slot_creation_end": exam.slot_creation_end.isoformat() if exam.slot_creation_end else "",
        "booking_start": exam.booking_start.isoformat() if exam.booking_start else "",
        "booking_end": exam.booking_end.isoformat() if exam.booking_end else "",
    }

    if request.method == "POST":
        data, error = read_exam_form(request.form)
        if error:
            flash(error, "danger")
            form = request.form
        else:
            copy_data_to_exam(exam, data)
            db.session.commit()
            flash("Examination " + exam.name + " updated.", "success")
            return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    return render_template("admin/exam_form.html", form=form, exam=exam, courses=courses, exam_types=EXAM_TYPES)


@bp.route("/<int:exam_id>/delete", methods=["POST"])
@role_required("admin")
def delete_exam(exam_id):
    # Delete an exam, but only if no slots were created for it
    exam = db.get_or_404(Exam, exam_id)
    if len(exam.slots) > 0:
        flash("This examination already has slots, so it cannot be deleted.", "warning")
        return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    name = exam.name
    db.session.delete(exam)
    db.session.commit()
    flash("Examination " + name + " deleted.", "success")
    return redirect(url_for("admin_exams.list_exams"))


@bp.route("/<int:exam_id>")
@role_required("admin")
def exam_detail(exam_id):
    # Show one exam with its timeline, status buttons and slots
    exam = db.get_or_404(Exam, exam_id)
    slots = Slot.query.filter_by(exam_id=exam.id).order_by(Slot.date, Slot.start_time).all()
    return render_template("admin/exam_detail.html", exam=exam, slots=slots, actions=get_actions_for(exam))
