# The admin buttons that move an exam: Draft -> Slot Creation -> Booking Open -> Closed -> Completed.
from database import db

# action name: (allowed current statuses, new status, button label, message shown)
STATUS_ACTIONS = {
    "open_slot_creation": (["Draft"], "Slot Creation", "Open slot creation", "Slot creation is now open."),
    "close_slot_creation": (["Slot Creation"], "Draft", "Close slot creation", "Slot creation is now closed."),
    "open_booking": (["Draft", "Slot Creation", "Closed"], "Booking Open", "Open booking", "Student booking is now open."),
    "close_booking": (["Booking Open"], "Closed", "Close booking", "Student booking is now closed."),
    "complete": (["Closed"], "Completed", "Mark completed (publish results)", "Exam completed. Results are published."),
}


def get_actions_for(exam):
    # List of (action_name, button_label) the admin may click right now
    actions = []
    for action_name, (allowed, new_status, label, message) in STATUS_ACTIONS.items():
        if exam.status in allowed:
            actions.append((action_name, label))
    return actions


def change_exam_status(exam, action):
    # Apply one action; returns (True/False, message)
    if action not in STATUS_ACTIONS:
        return False, "Unknown action."

    allowed, new_status, label, message = STATUS_ACTIONS[action]
    if exam.status not in allowed:
        return False, "This action is not possible when the exam is " + exam.status + "."

    exam.status = new_status
    db.session.commit()
    return True, message
