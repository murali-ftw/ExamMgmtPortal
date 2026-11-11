# Booking table: a student booking a seat in a slot.
from datetime import datetime

from database import db


class Booking(db.Model):
    """One student in one slot. Never deleted, so the history is kept."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slots.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)

    # Booked / Cancelled / Completed
    status = db.Column(db.String(20), default="Booked")

    student = db.relationship("User", foreign_keys=[student_id])
    # One booking has at most one evaluation (uselist=False gives one object, not a list)
    evaluation = db.relationship("Evaluation", uselist=False, backref="booking")
