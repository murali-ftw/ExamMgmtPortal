# User table: one table for admins, examiners and students (the role column tells them apart).
from datetime import datetime

from database import db


class User(db.Model):
    """A person who can log in: admin, examiner or student."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)               # admin / examiner / student
    status = db.Column(db.String(20), default="active")           # active / pending / inactive
    department = db.Column(db.String(100))                        # used by examiners
    contact = db.Column(db.String(20))
    roll_no = db.Column(db.String(30))                            # used by students
    created_on = db.Column(db.DateTime, default=datetime.now)
