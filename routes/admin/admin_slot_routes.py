# Admin pages to view all slots of all examiners and exams, and to change a slot's examiner.
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import to_int
from models import Slot, User
from rules.admin_change_rules import can_change_examiner

bp = Blueprint("admin_slots", __name__, url_prefix="/admin/slots")


@bp.route("/")
@role_required("admin")
def list_slots():
    # Every slot, newest date first (latest start time first on the same day)
    slots = Slot.query.order_by(Slot.date.desc(), Slot.start_time.desc()).all()
    return render_template("admin/slots.html", slots=slots)


@bp.route("/<int:slot_id>/examiner", methods=["GET", "POST"])
@role_required("admin")
def change_examiner(slot_id):
    # GET: pick another examiner of this exam. POST: check the rule again and save. Bookings are not touched.
    slot = db.get_or_404(Slot, slot_id)

    if request.method == "POST":
        examiner_id = to_int(request.form.get("examiner_id"))
        if examiner_id is None:
            flash("Please choose an examiner.", "danger")
            return redirect(url_for("admin_slots.change_examiner", slot_id=slot.id))
        new_examiner = db.get_or_404(User, examiner_id)

        ok, reason = can_change_examiner(slot, new_examiner)
        if not ok:
            flash(reason, "danger")
            return redirect(url_for("admin_slots.change_examiner", slot_id=slot.id))

        old_name = slot.examiner.name
        slot.examiner = new_examiner
        db.session.commit()
        flash("Slot " + str(slot.id) + " moved from " + old_name + " to " + new_examiner.name + ".", "success")
        return redirect(url_for("admin_slots.list_slots"))

    # Examiners assigned to this exam who pass the rule (active, not the current one)
    examiners = []
    for assignment in slot.exam.assignments:
        ok, reason = can_change_examiner(slot, assignment.examiner)
        if ok:
            examiners.append(assignment.examiner)

    return render_template("admin/change_examiner.html", slot=slot, examiners=examiners)
