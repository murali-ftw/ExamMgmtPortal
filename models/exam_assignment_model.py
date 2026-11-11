# ExamAssignment table: links examiners to exams (one exam can have many examiners and the other way round).
from database import db


class ExamAssignment(db.Model):
    """One row = this examiner is assigned to this exam."""
    __tablename__ = "exam_assignments"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    examiner = db.relationship("User")
