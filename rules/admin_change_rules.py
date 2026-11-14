# Decides IF the admin may reschedule a booking or change a slot's examiner. No web code, no saving.
from models import ExamAssignment


def can_move_booking(booking):
    # Returns (True, "") or (False, reason): can this booking be moved to ANY other slot?
    if booking.status != "Booked":
        return False, "Only a Booked booking can be rescheduled."
    if booking.slot.exam.status == "Completed":
        return False, "This exam is completed, so its bookings can no longer be rescheduled."
    return True, ""


def can_reschedule(booking, new_slot):
    # Returns (True, "") or (False, reason). Checks run in order; the first problem is returned.
    # The admin may do this outside the booking window, so booking_open is NOT checked here.

    # a) the booking itself must be movable
    ok, reason = can_move_booking(booking)
    if not ok:
        return False, reason

    # b) same exam only, and a different slot
    if new_slot.exam_id != booking.slot.exam_id:
        return False, "Choose a slot of the same exam."
    if new_slot.id == booking.slot_id:
        return False, "The booking is already in this slot."

    # c) the new slot must be open
    if new_slot.status == "Cancelled":
        return False, "This slot has been cancelled."
    if new_slot.status == "Completed":
        return False, "This slot is already completed."
    if new_slot.status == "Full":
        return False, "This slot is full."
    if new_slot.status != "Available":
        return False, "This slot is not available."

    # d) no overbooking: count the seats that are really free
    if new_slot.available_seats <= 0:
        return False, "No seats are left in this slot."

    return True, ""


def can_change_examiner(slot, new_examiner):
    # Returns (True, "") or (False, reason). Checks run in order; the first problem is returned.

    # a) only a slot that is still running
    if slot.status == "Cancelled" or slot.status == "Completed":
        return False, "The examiner of a " + slot.status + " slot cannot be changed."

    # b) the new person must be an active examiner
    if new_examiner.role != "examiner":
        return False, "This user is not an examiner."
    if new_examiner.status != "active":
        return False, "This examiner is not active."

    # c) the new examiner must be assigned to this slot's exam
    assignment = ExamAssignment.query.filter_by(exam_id=slot.exam_id, examiner_id=new_examiner.id).first()
    if assignment is None:
        return False, new_examiner.name + " is not assigned to this exam."

    # d) it must really be a change
    if new_examiner.id == slot.examiner_id:
        return False, new_examiner.name + " is already the examiner of this slot."

    return True, ""
