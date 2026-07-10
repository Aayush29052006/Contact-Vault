"""Configuration loader for ContactVault."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config/default_config.json")

_DEFAULTS = {
    "data_file": "output/contacts.json",
    "theme": "dark",
    "log_level": "INFO",
    "text_scale": 1.0,
}


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    """Load config from a JSON file, falling back to safe defaults."""
    path = Path(path)
    if not path.exists():
        return dict(_DEFAULTS)
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)
    return {**_DEFAULTS, **data}