"""Command-pattern undo stack for contact operations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """A reversible action. undo() reverses an action that already happened."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse this action."""


class UndoStack:
    """Keeps a history of executed actions so the last one can be undone."""

    def __init__(self) -> None:
        self._stack: list[Command] = []

    def push(self, command: Command) -> None:
        self._stack.append(command)

    def undo_last(self) -> bool:
        """Undo the most recent action. Returns False if there's nothing to undo."""
        if not self._stack:
            return False
        command = self._stack.pop()
        command.undo()
        return True

    def clear(self) -> None:
        self._stack.clear()

    def __len__(self) -> int:
        return len(self._stack)