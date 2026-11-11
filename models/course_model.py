# Course table: a course can have many exams.
from database import db


class Course(db.Model):
    """A course such as 'MAD I'."""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")
