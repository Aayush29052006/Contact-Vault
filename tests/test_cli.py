"""Tests for the CLI, exercised via cli.main() with captured stdout."""

from __future__ import annotations

import pytest

from contactvault.cli import cli as cli_module


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    data_file = tmp_path / "contacts.json"
    monkeypatch.setattr(cli_module, "load_config", lambda: {"data_file": str(data_file)})
    return data_file


def test_add_and_list(cli_env, capsys):
    assert cli_module.main(["add", "Alice", "alice@example.com"]) == 0
    assert "Added: Alice" in capsys.readouterr().out

    assert cli_module.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "Alice" in out and "alice@example.com" in out


def test_add_duplicate_returns_error_exit_code(cli_env, capsys):
    cli_module.main(["add", "Alice", "alice@example.com"])
    capsys.readouterr()
    exit_code = cli_module.main(["add", "Alice Again", "alice@example.com"])
    assert exit_code == 1
    assert "already exists" in capsys.readouterr().err


def test_add_invalid_email_returns_error_exit_code(cli_env, capsys):
    assert cli_module.main(["add", "Bad", "not-an-email"]) == 1


def test_list_with_no_contacts(cli_env, capsys):
    cli_module.main(["list"])
    assert "No contacts found." in capsys.readouterr().out


def test_search(cli_env, capsys):
    cli_module.main(["add", "Alice", "alice@example.com"])
    cli_module.main(["add", "Bob", "bob@example.com"])
    capsys.readouterr()
    cli_module.main(["search", "alice"])
    out = capsys.readouterr().out
    assert "Alice" in out and "Bob" not in out


def test_delete(cli_env, capsys):
    cli_module.main(["add", "Alice", "alice@example.com"])
    added_line = capsys.readouterr().out.strip()
    contact_id = added_line.split("id=")[1].rstrip(")")

    assert cli_module.main(["delete", contact_id]) == 0
    capsys.readouterr()
    cli_module.main(["list"])
    assert "No contacts found." in capsys.readouterr().out