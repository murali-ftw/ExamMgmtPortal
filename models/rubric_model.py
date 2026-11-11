# Rubric table: the evaluation criteria of an exam (for example "Code quality, 10 marks").
from database import db


class Rubric(db.Model):
    """One criterion an examiner gives marks for."""
    __tablename__ = "rubrics"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    criterion_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
