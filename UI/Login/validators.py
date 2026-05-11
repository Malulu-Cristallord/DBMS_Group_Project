import re


EMAIL_ERROR = "Email must be a valid Gmail address."
PASSWORD_RULE_ERROR = (
    "Password must be 8-20 characters and include uppercase, lowercase, "
    "number, and special character."
)
PASSWORD_ALLOWED_CHARS_ERROR = (
    "Password may only contain English letters, numbers, and these special "
    "characters: ! @ # $ % ^ & * _ -."
)

_GMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@gmail\.com$",
    re.IGNORECASE,
)
_PASSWORD_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9!@#$%^&*_-]+$")


def validate_google_email(email: str) -> tuple[bool, str]:
    normalized_email = (email or "").strip()

    if not _GMAIL_PATTERN.fullmatch(normalized_email):
        return False, EMAIL_ERROR

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not 8 <= len(password or "") <= 20:
        return False, PASSWORD_RULE_ERROR

    if not _PASSWORD_ALLOWED_PATTERN.fullmatch(password):
        return False, PASSWORD_ALLOWED_CHARS_ERROR

    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_number = any(char.isdigit() for char in password)
    has_special = any(char in "!@#$%^&*_-" for char in password)

    if not all([has_uppercase, has_lowercase, has_number, has_special]):
        return False, PASSWORD_RULE_ERROR

    return True, ""
