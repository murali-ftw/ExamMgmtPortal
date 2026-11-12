# Examiner page: the exams I am assigned to, and whether I can create slots for each one now.
from flask import Blueprint, render_template

from helpers.auth_helpers import get_current_user, role_required
from models import ExamAssignment
from rules.window_rules import slot_creation_open

bp = Blueprint("examiner_exams", __name__, url_prefix="/examiner/exams")


@bp.route("/")
@role_required("examiner")
def my_exams():
    # Only exams linked to me in exam_assignments
    user = get_current_user()
    assignments = ExamAssignment.query.filter_by(examiner_id=user.id).all()

    rows = []
    for assignment in assignments:
        exam = assignment.exam
        rows.append({"exam": exam, "creation_open": slot_creation_open(exam)})
    return render_template("examiner/exams.html", rows=rows)
