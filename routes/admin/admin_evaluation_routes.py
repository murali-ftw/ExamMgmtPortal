# Admin pages to view every evaluation (all examiners) and one evaluation in detail. Read-only: nothing is changed here.
from flask import Blueprint, render_template, request
from sqlalchemy import or_

from database import db
from helpers.auth_helpers import role_required
from helpers.search_helpers import read_search
from models import Booking, Evaluation, Exam, Slot, User

bp = Blueprint("admin_evaluations", __name__, url_prefix="/admin/evaluations")


@bp.route("/")
@role_required("admin")
def list_evaluations():
    # All evaluations, newest first; ?q= matches evaluation / booking / student ID (if a number) or student name/email / exam name
    q, id_number = read_search(request.args.get("q", ""))

    # Join booking -> student and booking -> slot -> exam so we can search on their columns
    query = Evaluation.query.join(Evaluation.booking).join(Booking.student).join(Booking.slot).join(Slot.exam)

    if q:
        pattern = "%" + q + "%"
        text_match = or_(User.name.ilike(pattern), User.email.ilike(pattern), Exam.name.ilike(pattern))
        if id_number is not None:
            query = query.filter(or_(Evaluation.id == id_number, Evaluation.booking_id == id_number,
                                     Booking.student_id == id_number, text_match))
        else:
            query = query.filter(text_match)

    evaluations = query.order_by(Evaluation.evaluated_on.desc(), Evaluation.id.desc()).all()
    return render_template("admin/evaluations.html", evaluations=evaluations, q=q)


@bp.route("/<int:evaluation_id>")
@role_required("admin")
def evaluation_detail(evaluation_id):
    # One evaluation with the marks for each rubric criterion; a missing id gives 404
    evaluation = db.get_or_404(Evaluation, evaluation_id)
    return render_template("admin/evaluation_detail.html", evaluation=evaluation, booking=evaluation.booking)
