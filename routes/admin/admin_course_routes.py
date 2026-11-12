# Admin pages to list, add, edit and delete courses.
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from helpers.auth_helpers import role_required
from helpers.form_helpers import to_int
from models import Course

bp = Blueprint("admin_courses", __name__, url_prefix="/admin/courses")

COURSE_STATUSES = ["Active", "Inactive"]


def read_course_form(form, course_id=None):
    # Return (data, error_message); course_id is the course being edited (its own code is allowed)
    data = {
        "code": form.get("code", "").strip().upper(),
        "name": form.get("name", "").strip(),
        "description": form.get("description", "").strip(),
        "status": form.get("status", "Active"),
        "credits": to_int(form.get("credits")),
    }
    if not data["code"] or not data["name"]:
        return data, "Course code and name are required."
    if data["status"] not in COURSE_STATUSES:
        return data, "Please choose a valid status."
    if data["credits"] is None or data["credits"] < 1 or data["credits"] > 10:
        return data, "Credits must be a whole number from 1 to 10."
    same_code = Course.query.filter_by(code=data["code"]).first()
    if same_code is not None and same_code.id != course_id:
        return data, "Another course already uses the code " + data["code"] + "."
    return data, None


@bp.route("/")
@role_required("admin")
def list_courses():
    # Show all courses ordered by code
    courses = Course.query.order_by(Course.code).all()
    return render_template("admin/courses.html", courses=courses)


@bp.route("/add", methods=["GET", "POST"])
@role_required("admin")
def add_course():
    # Show an empty form, and save a new course when it is sent
    form = {}
    if request.method == "POST":
        data, error = read_course_form(request.form)
        if error:
            flash(error, "danger")
            form = request.form
        else:
            course = Course(code=data["code"], name=data["name"], description=data["description"],
                            status=data["status"], credits=data["credits"])
            db.session.add(course)
            db.session.commit()
            flash("Course " + course.code + " added.", "success")
            return redirect(url_for("admin_courses.list_courses"))

    return render_template("admin/course_form.html", form=form, course=None, statuses=COURSE_STATUSES)


@bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_course(course_id):
    # Show the form filled with the course, and save the changes
    course = db.get_or_404(Course, course_id)
    form = {"code": course.code, "name": course.name,
            "description": course.description or "", "status": course.status, "credits": course.credits}

    if request.method == "POST":
        data, error = read_course_form(request.form, course_id=course.id)
        if error:
            flash(error, "danger")
            form = request.form
        else:
            course.code = data["code"]
            course.name = data["name"]
            course.description = data["description"]
            course.status = data["status"]
            course.credits = data["credits"]
            db.session.commit()
            flash("Course " + course.code + " updated.", "success")
            return redirect(url_for("admin_courses.list_courses"))

    return render_template("admin/course_form.html", form=form, course=course, statuses=COURSE_STATUSES)


@bp.route("/<int:course_id>/delete", methods=["POST"])
@role_required("admin")
def delete_course(course_id):
    # Delete a course, but only if it has no exams
    course = db.get_or_404(Course, course_id)
    if len(course.exams) > 0:
        flash("Course " + course.code + " has exams, so it cannot be deleted. Set it to Inactive instead.", "warning")
        return redirect(url_for("admin_courses.list_courses"))

    code = course.code
    db.session.delete(course)
    db.session.commit()
    flash("Course " + code + " deleted.", "success")
    return redirect(url_for("admin_courses.list_courses"))
