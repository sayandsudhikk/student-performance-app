import re


def is_valid_username(username: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))


def is_valid_password(password: str) -> bool:
    # simple length check; expand as needed
    return len(password) >= 6
