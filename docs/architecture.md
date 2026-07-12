# Architecture

## Layers

                    ┌───────────────┐          ┌───────────────┐
                    │      GUI      │          │      CLI      │
                    │ CustomTkinter │          │   argparse    │
                    └───────┬───────┘          └───────┬───────┘
                            │                          │
                            └───────────┬──────────────┘
                                        │
                                        ▼
                           ┌───────────────────────────┐
                           │      ContactService       │
                           │ • Validation              │
                           │ • Duplicate Detection     │
                           │ • Undo Operations         │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────┐
                     │     JSONContactRepository          │
                     │ • Atomic Read/Write                │
                     │ • Data Persistence                 │
                     └──────────────────┬─────────────────┘
                                        │
                                        ▼
                             ┌───────────────────┐
                             │   contacts.json   │
                             └───────────────────┘


## Why this shape

**Both front-ends call one service.** Neither the GUI nor the CLI contains
validation or deduplication logic — they collect input, call
`ContactService`, and display the result or the error. This means every
business rule is enforced identically no matter which interface is used,
and a bug fix in one place fixes both.

**Storage is abstracted behind a repository interface.**
`ContactRepository` is an abstract base class defining `load()`/`save()`.
`JSONContactRepository` is the only implementation today, but
`ContactService` depends only on the interface — swapping to SQLite,
adding cloud sync, or writing a test double all become isolated changes
that never touch business logic.

**Writes are atomic.** `JSONContactRepository.save()` writes the new data
to a temporary file in the same directory, then calls `os.replace()` to
swap it into place. `os.replace` is atomic at the OS level — the real
file is always either the complete old version or the complete new
version, never a partially-written one, even if the process is killed
mid-write.

**Undo uses the Command pattern.** Every mutating action
(`add_contact`, `edit_contact`, `delete_contact`) constructs a `Command`
object that knows how to reverse that specific action, and pushes it
onto an `UndoStack`. Calling `undo()` pops the most recent command and
reverses it. This avoids manually snapshotting "the whole previous
state" and scales cleanly if more undoable actions are added later.

## Data flow example: adding a contact

1. User submits a name and email (GUI form or `cli add` command).
2. `ContactService.add_contact()` normalizes and validates the email via
   `email_validator`.
3. The service checks for a case-insensitive duplicate against contacts
   already in memory.
4. A new `Contact` is created and appended to the in-memory list.
5. `JSONContactRepository.save()` is called, performing an atomic write.
6. An `_AddCommand` is pushed onto the undo stack.
7. The new `Contact` is returned to the caller (GUI refreshes its list;
   CLI prints a confirmation line).
