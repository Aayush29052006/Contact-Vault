"""Configuration loader for ContactVault."""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_CONFIG_PATH = Path("config/default_config.json")


def load_config(path: str | Path = _DEFAULT_CONFIG_PATH) -> dict:
    """Load config from a JSON file, falling back to safe defaults."""
    defaults = {"data_file": "output/contacts.json", "theme": "dark", "log_level": "INFO"}
    path = Path(path)
    if not path.exists():
        return defaults
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return defaults
    return {**defaults, **data}