"""Shared pytest fixtures for ContactVault tests."""

from __future__ import annotations

import pytest

from contactvault.repository.json_repository import JSONContactRepository
from contactvault.services.contact_service import ContactService


@pytest.fixture
def repo(tmp_path):
    """A JSON repository pointed at a fresh temp file per test."""
    return JSONContactRepository(tmp_path / "contacts.json")


@pytest.fixture
def service(repo):
    """A ContactService backed by the temp repository above."""
    return ContactService(repo)