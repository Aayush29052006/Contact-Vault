"""Tests for the JSON-backed contact repository."""

from __future__ import annotations

import pytest

from contactvault.exceptions import StorageError
from contactvault.models.contact import Contact
from contactvault.repository.json_repository import JSONContactRepository


def test_load_on_missing_file_returns_empty_list(tmp_path):
    repo = JSONContactRepository(tmp_path / "does_not_exist.json")
    assert repo.load() == []


def test_load_on_empty_file_returns_empty_list(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")
    assert JSONContactRepository(path).load() == []


def test_save_then_load_round_trip(tmp_path):
    repo = JSONContactRepository(tmp_path / "contacts.json")
    contacts = [
        Contact(name="Alice", email="alice@example.com"),
        Contact(name="Bob", email="bob@example.com"),
    ]
    repo.save(contacts)
    loaded = repo.load()
    assert [c.email for c in loaded] == [c.email for c in contacts]


def test_save_creates_missing_parent_directories(tmp_path):
    nested_path = tmp_path / "nested" / "dir" / "contacts.json"
    repo = JSONContactRepository(nested_path)
    repo.save([Contact(name="Alice", email="alice@example.com")])
    assert nested_path.exists()


def test_corrupted_json_raises_storage_error(tmp_path):
    path = tmp_path / "corrupted.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    with pytest.raises(StorageError):
        JSONContactRepository(path).load()


def test_save_failure_raises_storage_error(tmp_path, monkeypatch):
    path = tmp_path / "contacts.json"
    repo = JSONContactRepository(path)

    def boom(*args, **kwargs):
        raise OSError("simulated disk failure")

    monkeypatch.setattr("contactvault.repository.json_repository.tempfile.mkstemp", boom)

    with pytest.raises(StorageError):
        repo.save([Contact(name="Alice", email="alice@example.com")])
    assert not path.exists()


def test_original_file_untouched_if_write_fails_midway(tmp_path, monkeypatch):
    path = tmp_path / "contacts.json"
    repo = JSONContactRepository(path)
    repo.save([Contact(name="Alice", email="alice@example.com")])
    original_content = path.read_text(encoding="utf-8")

    def boom(*args, **kwargs):
        raise OSError("simulated failure after temp file created")

    monkeypatch.setattr("contactvault.repository.json_repository.os.replace", boom)

    with pytest.raises(StorageError):
        repo.save([Contact(name="Bob", email="bob@example.com")])

    assert path.read_text(encoding="utf-8") == original_content


def test_non_list_json_raises_storage_error(tmp_path):
    path = tmp_path / "invalid_structure.json"
    path.write_text('{"name": "Alice"}', encoding="utf-8")

    with pytest.raises(StorageError, match="must be a JSON list"):
        JSONContactRepository(path).load()


def test_invalid_contact_data_raises_storage_error(tmp_path):
    path = tmp_path / "invalid_contact.json"
    path.write_text('[{"name": "Alice"}]', encoding="utf-8")

    with pytest.raises(StorageError, match="Invalid contact data"):
        JSONContactRepository(path).load()