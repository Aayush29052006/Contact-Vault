"""Contact data model."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import uuid


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Contact:
    """Represents a single contact entry.

    `id` is generated automatically and should never be set by a
    caller directly -- it's how the app tells two contacts apart
    even if a name or email is edited later.
    """

    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def touch(self) -> None:
        """Update the `updated_at` timestamp. Call this after any edit."""
        self.updated_at = _now_iso()

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """Rebuild a Contact from a dict loaded from JSON."""
        return cls(
            name=data["name"],
            email=data["email"],
            id=data["id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
