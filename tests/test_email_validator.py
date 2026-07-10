"""Tests for email validation."""

from __future__ import annotations

import pytest

from contactvault.exceptions import InvalidEmailError
from contactvault.validation.email_validator import validate_and_normalize


def test_valid_email_is_accepted():
    assert validate_and_normalize("alice@example.com") == "alice@example.com"


def test_email_is_stripped_of_surrounding_whitespace():
    assert validate_and_normalize("   alice@example.com   ") == "alice@example.com"


def test_domain_is_lowercased():
    result = validate_and_normalize("Alice@EXAMPLE.COM")
    assert result.endswith("@example.com")


@pytest.mark.parametrize("bad_email", [
    "not-an-email",
    "missing-at-sign.com",
    "@missing-local-part.com",
    "spaces in@email.com",
    "",
    "   ",
])
def test_invalid_emails_are_rejected(bad_email):
    with pytest.raises(InvalidEmailError):
        validate_and_normalize(bad_email)