"""Core business logic for managing contacts.

Both the GUI and CLI call only into ContactService -- neither
touches the repository or validator directly. This keeps every
business rule (validation, duplicate-checking, undo) in one place.
"""

from __future__ import annotations

from contactvault.exceptions import DuplicateContactError, ContactNotFoundError
from contactvault.models.contact import Contact
from contactvault.repository.base import ContactRepository
from contactvault.services.undo import Command, UndoStack
from contactvault.validation.email_validator import validate_and_normalize


class _AddCommand(Command):
    def __init__(self, service: "ContactService", contact: Contact) -> None:
        self._service = service
        self._contact = contact

    def undo(self) -> None:
        self._service._remove_and_save(self._contact.id)


class _DeleteCommand(Command):
    def __init__(self, service: "ContactService", contact: Contact, index: int) -> None:
        self._service = service
        self._contact = contact
        self._index = index

    def undo(self) -> None:
        self._service._contacts.insert(self._index, self._contact)
        self._service._save()


class _EditCommand(Command):
    def __init__(self, service: "ContactService", contact_id: str, previous: Contact) -> None:
        self._service = service
        self._contact_id = contact_id
        self._previous = previous

    def undo(self) -> None:
        contacts = self._service._contacts
        for i, c in enumerate(contacts):
            if c.id == self._contact_id:
                contacts[i] = self._previous
                break
        self._service._save()


class ContactService:
    """Business logic for contacts. GUI and CLI both call only this class."""

    def __init__(self, repository: ContactRepository) -> None:
        self._repository = repository
        self._contacts: list[Contact] = repository.load()
        self.undo_stack = UndoStack()

    # -- internal helpers --
    def _save(self) -> None:
        self._repository.save(self._contacts)

    def _remove_and_save(self, contact_id: str) -> None:
        self._contacts = [c for c in self._contacts if c.id != contact_id]
        self._save()

    def _find_index(self, contact_id: str) -> int:
        for i, c in enumerate(self._contacts):
            if c.id == contact_id:
                return i
        raise ContactNotFoundError(contact_id)

    def _is_duplicate(self, email: str, exclude_id: str | None = None) -> bool:
        target = email.casefold()
        return any(
            c.email.casefold() == target and c.id != exclude_id
            for c in self._contacts
        )

    # -- public API --
    def get_all(self) -> list[Contact]:
        return list(self._contacts)

    def search(self, query: str) -> list[Contact]:
        q = query.casefold()
        return [
            c for c in self._contacts
            if q in c.name.casefold() or q in c.email.casefold()
        ]

    def add_contact(self, name: str, email: str) -> Contact:
        normalized_email = validate_and_normalize(email)
        if self._is_duplicate(normalized_email):
            raise DuplicateContactError(normalized_email)

        contact = Contact(name=name.strip(), email=normalized_email)
        self._contacts.append(contact)
        self._save()
        self.undo_stack.push(_AddCommand(self, contact))
        return contact

    def edit_contact(
        self, contact_id: str, name: str | None = None, email: str | None = None
    ) -> Contact:
        index = self._find_index(contact_id)
        current = self._contacts[index]
        previous_snapshot = Contact(
            name=current.name, email=current.email, id=current.id,
            created_at=current.created_at, updated_at=current.updated_at,
        )

        new_email = current.email
        if email is not None:
            new_email = validate_and_normalize(email)
            if self._is_duplicate(new_email, exclude_id=contact_id):
                raise DuplicateContactError(new_email)

        current.name = name.strip() if name is not None else current.name
        current.email = new_email
        current.touch()
        self._save()
        self.undo_stack.push(_EditCommand(self, contact_id, previous_snapshot))
        return current

    def delete_contact(self, contact_id: str) -> None:
        index = self._find_index(contact_id)
        contact = self._contacts.pop(index)
        self._save()
        self.undo_stack.push(_DeleteCommand(self, contact, index))

    def undo(self) -> bool:
        """Undo the last add/edit/delete. Returns False if nothing to undo."""
        return self.undo_stack.undo_last()