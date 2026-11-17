# Admin pages to add, edit and delete the rubric (marking criteria) of one exam.
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import to_float, to_int
from models import EvaluationScore, Exam, Rubric

bp = Blueprint("admin_rubrics", __name__, url_prefix="/admin/exams/<int:exam_id>/rubrics")


def read_rubric_form(form):
    # Read and check the rubric form; returns (data, error_message)
    data = {
        "criterion_name": form.get("criterion_name", "").strip(),
        "max_marks": to_int(form.get("max_marks")),
        "weightage": to_float(form.get("weightage")),
        "description": form.get("description", "").strip(),
    }
    if not data["criterion_name"]:
        return data, "Criterion name is required."
    if data["max_marks"] is None or data["max_marks"] <= 0:
        return data, "Maximum marks must be a whole number above 0."
    if data["weightage"] is None or data["weightage"] < 0:
        return data, "Weightage must be a number that is 0 or more."
    return data, None


def rubric_total(exam):
    # Sum of max_marks of all criteria of this exam (weightage is not used)
    total = 0
    for rubric in exam.rubrics:
        total = total + rubric.max_marks
    return total


def get_rubric_of_exam(exam, rubric_id):
    # Load the rubric, and give 404 if it belongs to a different exam
    rubric = db.get_or_404(Rubric, rubric_id)
    if rubric.exam_id != exam.id:
        abort(404)
    return rubric


@bp.route("/add", methods=["GET", "POST"])
@role_required("admin")
def add_rubric(exam_id):
    # Add one criterion to this exam
    exam = db.get_or_404(Exam, exam_id)
    form = {"weightage": "0"}
    if request.method == "POST":
        data, error = read_rubric_form(request.form)
        # The new criterion must not push the rubric total above the exam's maximum marks
        if error is None:
            new_total = rubric_total(exam) + data["max_marks"]
            if new_total > exam.max_marks:
                error = ("Rubric marks would add up to " + str(new_total) + ", but the exam maximum is "
                         + str(exam.max_marks) + ".")
        if error:
            flash(error, "danger")
            form = request.form
        else:
            rubric = Rubric(exam_id=exam.id, criterion_name=data["criterion_name"], max_marks=data["max_marks"],
                            weightage=data["weightage"], description=data["description"])
            db.session.add(rubric)
            db.session.commit()
            flash("Criterion " + rubric.criterion_name + " added.", "success")
            return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    return render_template("admin/rubric_form.html", exam=exam, rubric=None, form=form)


@bp.route("/<int:rubric_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_rubric(exam_id, rubric_id):
    # Change one criterion of this exam
    exam = db.get_or_404(Exam, exam_id)
    rubric = get_rubric_of_exam(exam, rubric_id)
    form = {"criterion_name": rubric.criterion_name, "max_marks": rubric.max_marks,
            "weightage": rubric.weightage, "description": rubric.description or ""}

    if request.method == "POST":
        data, error = read_rubric_form(request.form)
        # Count the NEW value of this criterion instead of its old value
        if error is None:
            new_total = rubric_total(exam) - rubric.max_marks + data["max_marks"]
            if new_total > exam.max_marks:
                error = ("Rubric marks would add up to " + str(new_total) + ", but the exam maximum is "
                         + str(exam.max_marks) + ".")
        if error:
            flash(error, "danger")
            form = request.form
        else:
            rubric.criterion_name = data["criterion_name"]
            rubric.max_marks = data["max_marks"]
            rubric.weightage = data["weightage"]
            rubric.description = data["description"]
            db.session.commit()
            flash("Criterion " + rubric.criterion_name + " updated.", "success")
            return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    return render_template("admin/rubric_form.html", exam=exam, rubric=rubric, form=form)


@bp.route("/<int:rubric_id>/delete", methods=["POST"])
@role_required("admin")
def delete_rubric(exam_id, rubric_id):
    # Delete a criterion, but not if marks were already given for it
    exam = db.get_or_404(Exam, exam_id)
    rubric = get_rubric_of_exam(exam, rubric_id)
    if EvaluationScore.query.filter_by(rubric_id=rubric.id).count() > 0:
        flash("Marks were already given for this criterion, so it cannot be deleted.", "warning")
        return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))

    name = rubric.criterion_name
    db.session.delete(rubric)
    db.session.commit()
    flash("Criterion " + name + " deleted.", "success")
    return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))
