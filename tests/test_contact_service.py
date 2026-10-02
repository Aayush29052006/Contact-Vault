"""Tests for ContactService business logic."""

from __future__ import annotations

import pytest

from contactvault.exceptions import (
    ContactNotFoundError,
    DuplicateContactError,
    InvalidEmailError,
    StorageError,
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


def test_add_bulk_adds_multiple_contacts_with_a_single_save(service, monkeypatch):
    save_calls = []
    monkeypatch.setattr(service._repository, "save", lambda contacts: save_calls.append(len(contacts)))

    entries = [(f"User {i}", f"user{i}@example.com") for i in range(50)]
    result = service.add_bulk(entries)

    assert len(result.added) == 50
    assert len(save_calls) == 1


def test_add_bulk_derives_names_when_blank(service):
    result = service.add_bulk([("", "alice.sharma@example.com")])
    contact, derived = result.added[0]
    assert contact.name == "Alice Sharma"
    assert derived is True


def test_add_bulk_skips_duplicates_within_the_same_batch(service):
    entries = [("Alice", "alice@example.com"), ("Alice Again", "ALICE@EXAMPLE.COM")]
    result = service.add_bulk(entries)
    assert len(result.added) == 1
    assert len(result.skipped) == 1


def test_add_bulk_skips_duplicates_against_existing_contacts(service):
    service.add_contact("Alice", "alice@example.com")
    result = service.add_bulk([("Alice Again", "alice@example.com")])
    assert len(result.added) == 0
    assert len(result.skipped) == 1


def test_add_bulk_skips_invalid_emails(service):
    entries = [("Alice", "alice@example.com"), ("Bad", "not-an-email")]
    result = service.add_bulk(entries)
    assert len(result.added) == 1
    assert len(result.skipped) == 1


def test_add_bulk_with_empty_list_does_not_save(service, monkeypatch):
    save_calls = []
    monkeypatch.setattr(service._repository, "save", lambda contacts: save_calls.append(contacts))
    result = service.add_bulk([])
    assert result.added == []
    assert save_calls == []

def test_add_contact_with_blank_name_derives_from_email(service):
    contact = service.add_contact("", "alice.sharma@example.com")
    assert contact.name == "Alice Sharma"
    assert service.last_name_was_derived is True


def test_add_contact_with_provided_name_is_not_derived(service):
    contact = service.add_contact("Alice", "alice@example.com")
    assert contact.name == "Alice"
    assert service.last_name_was_derived is False


def test_derived_name_handles_dots_and_underscores(service):
    contact = service.add_contact("", "john_doe.smith@example.com")
    assert contact.name == "John Doe Smith"

def test_edit_contact_restores_original_on_save_failure(service, monkeypatch):
    original = service.add_contact("Alice", "alice@example.com")

    def fail_save():
        raise StorageError("simulated save failure")

    monkeypatch.setattr(service, "_save", fail_save)

    with pytest.raises(StorageError):
        service.edit_contact(original.id, name="Changed")

    restored = service.get_all()[0]

    assert restored.name == "Alice"
    assert restored.email == "alice@example.com"

def test_undo_bulk_add_removes_all_imported_contacts(service):
    service.add_contact("Existing", "existing@example.com")

    entries = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com"),
    ]

    result = service.add_bulk(entries)

    assert len(result.added) == 3
    assert len(service.get_all()) == 4

    assert service.undo() is True

    assert [contact.email for contact in service.get_all()] == [
        "existing@example.com"
    ]