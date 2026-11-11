# Collects every blueprint and registers them on the app.
# When you add a new route file, import its bp here and add it to ALL_BLUEPRINTS.
from routes.auth.login_routes import bp as login_bp
from routes.auth.register_routes import bp as register_bp
from routes.admin.admin_dashboard_routes import bp as admin_dashboard_bp
from routes.examiner.examiner_dashboard_routes import bp as examiner_dashboard_bp
from routes.student.student_dashboard_routes import bp as student_dashboard_bp

ALL_BLUEPRINTS = [
    login_bp,
    register_bp,
    admin_dashboard_bp,
    examiner_dashboard_bp,
    student_dashboard_bp,
]


def register_all_blueprints(app):
    # Attach every blueprint (group of pages) to the app
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
