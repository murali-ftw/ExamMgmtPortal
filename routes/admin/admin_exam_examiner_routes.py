# Admin buttons on the exam page to assign examiners to an exam or remove them.
from flask import Blueprint, abort, flash, redirect, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import to_int
from models import Exam, ExamAssignment, Slot, User

bp = Blueprint("admin_exam_examiners", __name__, url_prefix="/admin/exams")


@bp.route("/<int:exam_id>/examiners/assign", methods=["POST"])
@role_required("admin")
def assign_examiner(exam_id):
    # Link one active examiner to this exam
    exam = db.get_or_404(Exam, exam_id)
    examiner_id = to_int(request.form.get("examiner_id"))
    examiner = None
    if examiner_id is not None:
        examiner = db.session.get(User, examiner_id)

    if examiner is None or examiner.role != "examiner" or examiner.status != "active":
        flash("Please choose an active examiner.", "danger")
    elif ExamAssignment.query.filter_by(exam_id=exam.id, examiner_id=examiner.id).first() is not None:
        flash(examiner.name + " is already assigned to this exam.", "warning")
    else:
        db.session.add(ExamAssignment(exam_id=exam.id, examiner_id=examiner.id))
        db.session.commit()
        flash(examiner.name + " assigned to this exam.", "success")
    return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))


@bp.route("/<int:exam_id>/examiners/<int:assignment_id>/remove", methods=["POST"])
@role_required("admin")
def remove_examiner(exam_id, assignment_id):
    # Unlink an examiner, but not if they already created slots for this exam
    exam = db.get_or_404(Exam, exam_id)
    assignment = db.get_or_404(ExamAssignment, assignment_id)
    if assignment.exam_id != exam.id:
        abort(404)

    slot_count = Slot.query.filter_by(exam_id=exam.id, examiner_id=assignment.examiner_id).count()
    if slot_count > 0:
        flash(assignment.examiner.name + " already has slots in this exam. Change the slot examiner first.", "warning")
    else:
        name = assignment.examiner.name
        db.session.delete(assignment)
        db.session.commit()
        flash(name + " removed from this exam.", "success")
    return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))
