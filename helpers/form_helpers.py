# Turn form text into numbers, dates and times. Each returns None if the text is invalid.
from datetime import datetime


def to_int(text):
    # "5" -> 5; a huge number is treated as invalid (SQLite cannot store it, and no real value is that big)
    try:
        number = int(text)
    except (ValueError, TypeError):
        return None
    if number > 2147483647 or number < -2147483647:
        return None
    return number


def to_float(text):
    # "7.5" -> 7.5
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def parse_date(text):
    # "2026-11-15" -> date(2026, 11, 15)
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_time(text):
    # "10:30" or "10:30:00" -> time(10, 30)
    for time_format in ["%H:%M", "%H:%M:%S"]:
        try:
            return datetime.strptime(text, time_format).time()
        except (ValueError, TypeError):
            pass
    return None
