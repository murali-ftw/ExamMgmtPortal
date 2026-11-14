# Reads the admin search box. The "search by name or ID" rule lives here, in one place.
from helpers.form_helpers import to_int


def read_search(text):
    # "  12 " -> ("12", 12)   "abc" -> ("abc", None)   "" -> ("", None)
    clean_text = (text or "").strip()
    id_number = None
    if clean_text.isdigit():
        # to_int gives None above 2147483647, so a huge number is searched as plain text only
        id_number = to_int(clean_text)
    return clean_text, id_number
