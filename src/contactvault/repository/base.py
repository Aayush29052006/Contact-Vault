"""Abstract contact repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from contactvault.models.contact import Contact


class ContactRepository(ABC):
    """Contract that any storage backend must fulfill."""

    @abstractmethod
    def load(self) -> list[Contact]:
        """Return all stored contacts."""

    @abstractmethod
    def save(self, contacts: list[Contact]) -> None:
        """Persist the given list of contacts, replacing what's stored."""