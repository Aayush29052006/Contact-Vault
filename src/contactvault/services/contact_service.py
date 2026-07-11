"""Core business logic for managing contacts.

Both the GUI and CLI call only into ContactService -- neither
touches the repository or validator directly. This keeps every
business rule (validation, duplicate-checking, undo) in one place.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from contactvault.exceptions import DuplicateContactError, ContactNotFoundError, InvalidEmailError
from contactvault.models.contact import Contact
from contactvault.repository.base import ContactRepository
from contactvault.services.undo import Command, UndoStack
from contactvault.validation.email_validator import validate_and_normalize


def _derive_name_from_email(email: str) -> str:
    """Fallback display name when no name is given -- e.g. a bulk
    import of an email-only list. Turns 'alice.sharma@x.com' into
    'Alice Sharma' rather than silently accepting a blank name."""
    local_part = email.split("@")[0]
    cleaned = re.sub(r"[._\-]+", " ", local_part).strip()
    return cleaned.title() if cleaned else "Unknown Contact"


@dataclass
class BulkAddResult:
    """Report of a bulk add: what got added (and whether its name was
    auto-derived), and what got skipped (and why)."""

    added: list[tuple[Contact, bool]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


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
        self.last_name_was_derived: bool = False
        # Bumped on every real save (see _save below). Lets other
        # parts of the UI (like ContactsFrame) cheaply check "did
        # anything change since I last rendered?" instead of either
        # always re-rendering (slow) or never re-rendering (stale).
        self.version: int = 0

    def _save(self) -> None:
        self._repository.save(self._contacts)
        self.version += 1

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

        cleaned_name = name.strip()
        self.last_name_was_derived = not cleaned_name
        if not cleaned_name:
            cleaned_name = _derive_name_from_email(normalized_email)

        contact = Contact(name=cleaned_name, email=normalized_email)
        self._contacts.append(contact)
        self._save()
        self.undo_stack.push(_AddCommand(self, contact))
        return contact

    def add_bulk(self, entries: list[tuple[str, str]]) -> BulkAddResult:
        """Add many (name, email) pairs at once.

        Unlike calling add_contact() in a loop, this validates and
        dedupes every entry in memory and writes to disk only ONCE at
        the end -- essential once you're importing hundreds or
        thousands of contacts instead of just a handful.
        """
        result = BulkAddResult()
        seen_this_batch: set[str] = set()

        for name, email in entries:
            try:
                normalized_email = validate_and_normalize(email)
            except InvalidEmailError as exc:
                identifier = email.strip() or name.strip() or "(blank)"
                result.skipped.append((identifier, str(exc)))
                continue

            key = normalized_email.casefold()
            if key in seen_this_batch or self._is_duplicate(normalized_email):
                result.skipped.append(
                    (normalized_email, f"A contact with email '{normalized_email}' already exists")
                )
                continue

            cleaned_name = name.strip()
            derived = not cleaned_name
            if not cleaned_name:
                cleaned_name = _derive_name_from_email(normalized_email)

            contact = Contact(name=cleaned_name, email=normalized_email)
            self._contacts.append(contact)
            seen_this_batch.add(key)
            result.added.append((contact, derived))

        if result.added:
            self._save()
            for contact, _ in result.added:
                self.undo_stack.push(_AddCommand(self, contact))

        return result

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

        if name is not None:
            cleaned_name = name.strip()
            current.name = cleaned_name if cleaned_name else _derive_name_from_email(new_email)
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