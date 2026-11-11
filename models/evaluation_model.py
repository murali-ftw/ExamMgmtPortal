# Evaluation tables: the result of a booking, and the marks for each rubric criterion.
from datetime import datetime

from database import db


class Evaluation(db.Model):
    """The total marks and remarks for one booking."""
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True: a booking can be evaluated only once
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False)
    total_marks = db.Column(db.Float, default=0)
    remarks = db.Column(db.Text)
    evaluated_on = db.Column(db.DateTime, default=datetime.now)

    # Scores are deleted together with the evaluation
    scores = db.relationship("EvaluationScore", backref="evaluation", cascade="all, delete-orphan")


class EvaluationScore(db.Model):
    """Marks given for one rubric criterion inside an evaluation."""
    __tablename__ = "evaluation_scores"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey("evaluations.id"), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubrics.id"), nullable=False)
    marks = db.Column(db.Float, nullable=False)

    rubric = db.relationship("Rubric")
