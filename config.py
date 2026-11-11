# Settings for the app: secret key, database location and the default admin login.
import os

# Folder that contains this file (the EMP folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder for the SQLite database file; create it if it is missing
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Used by Flask to sign the session cookie
SECRET_KEY = "emp-secret-key-change-me"

# SQLite database file at EMP/instance/emp.db
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "emp.db")

# Turn off an extra change-tracking feature we do not use
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Default admin account, created when the database is set up
ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@emp.com"
ADMIN_PASSWORD = "admin123"
