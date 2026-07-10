"""Tests for the Contact data model."""

from __future__ import annotations

import time

from contactvault.models.contact import Contact


def test_contact_gets_generated_id_and_timestamps():
    c = Contact(name="Alice", email="alice@example.com")
    assert c.id
    assert c.created_at
    assert c.updated_at


def test_two_contacts_get_different_ids():
    a = Contact(name="Alice", email="alice@example.com")
    b = Contact(name="Bob", email="bob@example.com")
    assert a.id != b.id


def test_to_dict_and_from_dict_round_trip():
    original = Contact(name="Alice", email="alice@example.com")
    rebuilt = Contact.from_dict(original.to_dict())
    assert rebuilt == original


def test_touch_updates_updated_at_only():
    c = Contact(name="Alice", email="alice@example.com")
    original_created = c.created_at
    original_updated = c.updated_at
    time.sleep(0.01)
    c.touch()
    assert c.created_at == original_created
    assert c.updated_at != original_updated