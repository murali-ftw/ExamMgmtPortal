# Decides when results are shown to students and when an examiner may evaluate a booking.


def results_visible(exam):
    # Students see marks only after the admin marks the exam Completed
    return exam.status == "Completed"


def evaluation_allowed(booking):
    # Returns (True, "") or (False, reason) for evaluating one booking
    if booking.status != "Booked" and booking.status != "Completed":
        return False, "Only a booked student can be evaluated."

    if booking.evaluation is not None:
        return False, "This booking has already been evaluated."

    # Evaluate after booking opens and before results are published (Completed)
    exam = booking.slot.exam
    if exam.status != "Booking Open" and exam.status != "Closed":
        return False, "Evaluation is not allowed when the exam is " + exam.status + "."

    return True, ""
