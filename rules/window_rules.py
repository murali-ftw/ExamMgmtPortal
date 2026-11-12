# Decides WHEN things are allowed: slot creation, booking, and editing a slot.
from datetime import date


def slot_creation_open(exam):
    # Examiners can create slots only if the admin opened it AND today is inside the dates
    if exam.status != "Slot Creation":
        return False
    if exam.slot_creation_start is None or exam.slot_creation_end is None:
        return False
    today = date.today()
    return exam.slot_creation_start <= today <= exam.slot_creation_end


def booking_open(exam):
    # Students can book only if the admin opened booking AND today is inside the dates
    if exam.status != "Booking Open":
        return False
    if exam.booking_start is None or exam.booking_end is None:
        return False
    today = date.today()
    return exam.booking_start <= today <= exam.booking_end


def slot_can_be_edited(slot):
    # Slots can be changed or removed only before booking starts
    return slot.exam.status in ["Draft", "Slot Creation"]
