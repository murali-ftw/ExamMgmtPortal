# The status buttons on the exam detail page (open/close slot creation, open/close booking, complete).
from flask import Blueprint, flash, redirect, url_for

from database import db
from helpers.auth_helpers import role_required
from models import Exam
from rules.exam_status_rules import change_exam_status

bp = Blueprint("admin_exam_status", __name__, url_prefix="/admin/exams")


@bp.route("/<int:exam_id>/status/<action>", methods=["POST"])
@role_required("admin")
def change_status(exam_id, action):
    # Run one status action and go back to the exam page
    exam = db.get_or_404(Exam, exam_id)
    ok, message = change_exam_status(exam, action)
    if ok:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("admin_exams.exam_detail", exam_id=exam.id))
