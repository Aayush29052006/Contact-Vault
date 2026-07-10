"""Email validation wrapper around the email-validator library."""

from __future__ import annotations

from email_validator import validate_email, EmailNotValidError

from contactvault.exceptions import InvalidEmailError


def validate_and_normalize(email: str) -> str:
    """Check if an email is valid, and return a cleaned-up version.

    Raises InvalidEmailError if the email is badly formatted.
    """
    email = email.strip()
    try:
        result = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidEmailError(email, str(exc)) from exc
    return result.normalized
