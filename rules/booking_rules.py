# Decides IF a student may book or cancel, and keeps a slot's Full / Available status correct.
from rules.window_rules import booking_open


def can_book(student, slot):
    # Returns (True, "") or (False, reason). Checks run in order; the first problem is returned.

    # a) only active students can book
    if student.status != "active":
        return False, "Your account is not active."

    # b) the slot itself must be open for booking
    if slot.status == "Cancelled":
        return False, "This slot has been cancelled."
    if slot.status == "Completed":
        return False, "This slot is already completed."
    if slot.status == "Full":
        return False, "This slot is full."
    if slot.status != "Available":
        return False, "This slot is not available."

    # c) the admin must have opened booking and today must be inside the booking dates
    if not booking_open(slot.exam):
        return False, "Booking is not open for this exam."

    # d) no overbooking: count the seats that are really free
    if slot.available_seats <= 0:
        return False, "No seats are left in this slot."

    # e) no duplicate: one live booking per student per exam (any slot of that exam)
    for exam_slot in slot.exam.slots:
        for booking in exam_slot.bookings:
            if booking.student_id == student.id:
                if booking.status == "Booked" or booking.status == "Completed":
                    return False, "You already have a booking for this exam."

    return True, ""


def can_cancel(booking):
    # Returns (True, "") or (False, reason). Only a Booked seat, and only while booking is open.
    if booking.status != "Booked":
        return False, "Only a booking with status Booked can be cancelled."

    if not booking_open(booking.slot.exam):
        return False, "Bookings can no longer be cancelled."

    return True, ""


def refresh_slot_status(slot):
    # Sets the slot to Full when no seats are left, back to Available when one is free.
    # Cancelled and Completed slots are never changed. Does not commit: the caller commits.
    if slot.status == "Cancelled" or slot.status == "Completed":
        return

    if slot.available_seats <= 0:
        slot.status = "Full"
    else:
        slot.status = "Available"
