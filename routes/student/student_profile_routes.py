# Student page to view and edit my own profile (name, department, contact; email is fixed).
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import get_current_user, role_required

bp = Blueprint("student_profile", __name__, url_prefix="/student/profile")


@bp.route("/", methods=["GET", "POST"])
@role_required("student")
def edit_profile():
    # Always the logged-in student's own record, so there is no id in the URL
    student = get_current_user()
    form = {"name": student.name, "department": student.department or "", "contact": student.contact or ""}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        contact = request.form.get("contact", "").strip()

        if not name:
            flash("Name is required.", "danger")
            form = request.form
        else:
            student.name = name
            student.department = department
            student.contact = contact
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("student_profile.edit_profile"))

    return render_template("student/profile.html", student=student, form=form)
