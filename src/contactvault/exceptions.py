"""Custom exception hierarchy for ContactVault.

Specific exception types let calling code catch precisely what it
expects, and let the GUI/CLI show tailored error messages instead
of parsing strings.
"""

from __future__ import annotations


class ContactVaultError(Exception):
    """Base class for all ContactVault-specific errors."""


class InvalidEmailError(ContactVaultError):
    """Raised when an email address fails validation."""

    def __init__(self, email: str, reason: str) -> None:
        self.email = email
        self.reason = reason
        super().__init__(f"Invalid email '{email}': {reason}")


class DuplicateContactError(ContactVaultError):
    """Raised when adding a contact whose email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"A contact with email '{email}' already exists")


class ContactNotFoundError(ContactVaultError):
    """Raised when looking up a contact that doesn't exist."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"No contact found for '{identifier}'")


class StorageError(ContactVaultError):
    """Raised when reading from or writing to the storage backend fails."""
