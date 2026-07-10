"""JSON-backed contact repository with atomic, crash-safe writes."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from contactvault.exceptions import StorageError
from contactvault.models.contact import Contact
from contactvault.repository.base import ContactRepository


class JSONContactRepository(ContactRepository):
    """Stores contacts as a JSON array in a single file."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> list[Contact]:
        if not self.file_path.exists():
            return []
        try:
            raw = self.file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not read {self.file_path}: {exc}") from exc

        if not raw.strip():
            return []

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Corrupted data file {self.file_path}: {exc}") from exc

        return [Contact.from_dict(item) for item in data]

    def save(self, contacts: list[Contact]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([c.to_dict() for c in contacts], indent=2)

        # Atomic write: write to a temp file in the same directory,
        # then swap it into place with os.replace. This guarantees
        # the real file is never left half-written if the process
        # dies mid-save.
        fd, tmp_path = tempfile.mkstemp(
            dir=self.file_path.parent, prefix=".tmp_", suffix=".json"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(payload)
            os.replace(tmp_path, self.file_path)
        except OSError as exc:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise StorageError(f"Could not write {self.file_path}: {exc}") from exc