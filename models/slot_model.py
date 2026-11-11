# Slot table: a time slot an examiner creates for an exam; students book seats in it.
from database import db


class Slot(db.Model):
    """A date and time window with a fixed number of seats (capacity)."""
    __tablename__ = "slots"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    # Available / Full / Cancelled / Completed
    status = db.Column(db.String(20), default="Available")

    examiner = db.relationship("User", foreign_keys=[examiner_id])
    bookings = db.relationship("Booking", backref="slot")

    @property
    def booked_count(self):
        # Count bookings that take a seat (Cancelled ones free the seat)
        count = 0
        for booking in self.bookings:
            if booking.status == "Booked" or booking.status == "Completed":
                count = count + 1
        return count

    @property
    def available_seats(self):
        # Seats still free in this slot
        return self.capacity - self.booked_count
