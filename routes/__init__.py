# Collects every blueprint and registers them on the app.
# When you add a new route file, import its bp here and add it to ALL_BLUEPRINTS.
from routes.auth.login_routes import bp as login_bp
from routes.auth.register_routes import bp as register_bp
from routes.admin.admin_dashboard_routes import bp as admin_dashboard_bp
from routes.admin.admin_course_routes import bp as admin_courses_bp
from routes.admin.admin_exam_routes import bp as admin_exams_bp
from routes.admin.admin_exam_status_routes import bp as admin_exam_status_bp
from routes.admin.admin_rubric_routes import bp as admin_rubrics_bp
from routes.admin.admin_examiner_routes import bp as admin_examiners_bp
from routes.admin.admin_exam_examiner_routes import bp as admin_exam_examiners_bp
from routes.admin.admin_student_routes import bp as admin_students_bp
from routes.admin.admin_slot_routes import bp as admin_slots_bp
from routes.admin.admin_booking_routes import bp as admin_bookings_bp
from routes.admin.admin_evaluation_routes import bp as admin_evaluations_bp
from routes.examiner.examiner_dashboard_routes import bp as examiner_dashboard_bp
from routes.examiner.examiner_exam_routes import bp as examiner_exams_bp
from routes.examiner.examiner_slot_routes import bp as examiner_slots_bp
from routes.examiner.examiner_student_routes import bp as examiner_students_bp
from routes.examiner.examiner_evaluation_routes import bp as examiner_evaluations_bp
from routes.student.student_dashboard_routes import bp as student_dashboard_bp
from routes.student.student_exam_routes import bp as student_exams_bp
from routes.student.student_booking_routes import bp as student_bookings_bp
from routes.student.student_profile_routes import bp as student_profile_bp
from routes.student.student_result_routes import bp as student_results_bp

ALL_BLUEPRINTS = [
    login_bp,
    register_bp,
    admin_dashboard_bp,
    admin_courses_bp,
    admin_exams_bp,
    admin_exam_status_bp,
    admin_rubrics_bp,
    admin_examiners_bp,
    admin_exam_examiners_bp,
    admin_students_bp,
    admin_slots_bp,
    admin_bookings_bp,
    admin_evaluations_bp,
    examiner_dashboard_bp,
    examiner_exams_bp,
    examiner_slots_bp,
    examiner_students_bp,
    examiner_evaluations_bp,
    student_dashboard_bp,
    student_exams_bp,
    student_bookings_bp,
    student_profile_bp,
    student_results_bp,
]


def register_all_blueprints(app):
    # Attach every blueprint (group of pages) to the app
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
