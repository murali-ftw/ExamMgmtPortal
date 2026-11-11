# Exam table: belongs to a course and has rubrics, examiner assignments and slots.
from database import db

# The exam types shown in the exam form dropdown
EXAM_TYPES = ["Viva", "Practical", "Project Demo", "Assessment"]


class Exam(db.Model):
    """An exam of a course, with its 4 timeline dates and a status."""
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(30))
    duration = db.Column(db.Integer)                 # in minutes
    max_marks = db.Column(db.Integer)

    # Timeline: when examiners can create slots, and when students can book
    slot_creation_start = db.Column(db.Date)
    slot_creation_end = db.Column(db.Date)
    booking_start = db.Column(db.Date)
    booking_end = db.Column(db.Date)

    # Draft / Slot Creation / Booking Open / Closed / Completed
    status = db.Column(db.String(20), default="Draft")

    # course.exams gives all exams of a course
    course = db.relationship("Course", backref="exams")
    # Rubrics and assignments are deleted together with the exam
    rubrics = db.relationship("Rubric", backref="exam", cascade="all, delete-orphan")
    assignments = db.relationship("ExamAssignment", backref="exam", cascade="all, delete-orphan")
    slots = db.relationship("Slot", backref="exam")
