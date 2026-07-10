"""Tests for ContactService business logic."""

from __future__ import annotations

import pytest

from contactvault.exceptions import (
    ContactNotFoundError,
    DuplicateContactError,
    InvalidEmailError,
)


def test_add_contact_success(service):
    contact = service.add_contact("Alice", "alice@example.com")
    assert contact.name == "Alice"
    assert [c.email for c in service.get_all()] == ["alice@example.com"]


def test_add_contact_persists_to_repository(repo, service):
    service.add_contact("Alice", "alice@example.com")
    assert len(repo.load()) == 1


def test_duplicate_email_is_rejected(service):
    service.add_contact("Alice", "alice@example.com")
    with pytest.raises(DuplicateContactError):
        service.add_contact("Alice Again", "alice@example.com")


def test_duplicate_check_is_case_insensitive(service):
    service.add_contact("Alice", "alice@example.com")
    with pytest.raises(DuplicateContactError):
        service.add_contact("Alice Again", "ALICE@EXAMPLE.COM")


def test_invalid_email_is_rejected(service):
    with pytest.raises(InvalidEmailError):
        service.add_contact("Bad", "not-an-email")


def test_search_matches_name_or_email_case_insensitively(service):
    service.add_contact("Alice", "alice@example.com")
    service.add_contact("Bob", "bob@example.com")
    assert [c.name for c in service.search("ALICE")] == ["Alice"]
    assert [c.name for c in service.search("bob@")] == ["Bob"]
    assert service.search("nomatch") == []


def test_edit_contact_updates_fields(service):
    contact = service.add_contact("Alice", "alice@example.com")
    updated = service.edit_contact(contact.id, name="Alice Smith")
    assert updated.name == "Alice Smith"
    assert updated.email == "alice@example.com"


def test_edit_contact_to_duplicate_email_is_rejected(service):
    service.add_contact("Alice", "alice@example.com")
    bob = service.add_contact("Bob", "bob@example.com")
    with pytest.raises(DuplicateContactError):
        service.edit_contact(bob.id, email="alice@example.com")


def test_edit_nonexistent_contact_raises(service):
    with pytest.raises(ContactNotFoundError):
        service.edit_contact("does-not-exist", name="X")


def test_delete_contact_removes_it(service):
    contact = service.add_contact("Alice", "alice@example.com")
    service.delete_contact(contact.id)
    assert service.get_all() == []


def test_delete_nonexistent_contact_raises(service):
    with pytest.raises(ContactNotFoundError):
        service.delete_contact("does-not-exist")


def test_undo_add_removes_the_contact(service):
    service.add_contact("Alice", "alice@example.com")
    assert service.undo() is True
    assert service.get_all() == []


def test_undo_delete_restores_the_contact(service):
    contact = service.add_contact("Alice", "alice@example.com")
    service.delete_contact(contact.id)
    assert service.undo() is True
    assert [c.email for c in service.get_all()] == ["alice@example.com"]


def test_undo_edit_restores_previous_values(service):
    contact = service.add_contact("Alice", "alice@example.com")
    service.edit_contact(contact.id, name="Alice Smith")
    assert service.undo() is True
    assert service.get_all()[0].name == "Alice"


def test_undo_with_nothing_to_undo_returns_false(service):
    assert service.undo() is False


def test_undo_stack_only_undoes_most_recent_action(service):
    service.add_contact("Alice", "alice@example.com")
    service.add_contact("Bob", "bob@example.com")
    service.undo()
    assert [c.name for c in service.get_all()] == ["Alice"]


def test_bulk_add_of_many_contacts(service):
    for i in range(200):
        service.add_contact(f"User {i}", f"user{i}@example.com")
    assert len(service.get_all()) == 200