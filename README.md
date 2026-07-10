# ContactVault

A cross-platform, production-grade contact and email list manager, with both a modern desktop GUI (CustomTkinter) and a full CLI, sharing a single validated, deduplicated data layer.

## Features

- Add, view, search, edit, and delete contacts
- Case- and Unicode-aware duplicate detection (`alice@x.com` and `ALICE@X.com` are treated as the same contact)
- Email validation via the `email-validator` library (RFC-compliant, not regex-based)
- Undo for the last add / edit / delete action (Command pattern)
- Bulk CSV import with a live progress bar and a per-row report of what was added vs. skipped
- CSV export
- Adjustable UI text size (80%–150%), saved across restarts
- Full light/dark theme support
- Keyboard support: Enter to submit, Escape to cancel an edit or clear search, arrow/Page Up/Page Down/Home/End to scroll the contact list
- CLI with the same feature set as the GUI, for scripting and automation (`add`, `list`, `search`, `edit`, `delete`)
- Atomic, crash-safe file writes — a failed save can never corrupt existing data
- Structured logging to `logs/`
- 43 automated tests covering business logic, validation, storage, and CLI behavior

## Installation

**Requirements:** Python 3.11+

```bash
git clone https://github.com/Aayush29052006/contactvault.git
cd contactvault
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

**Run the GUI:**
```bash
python3 main.py
```

**Run the CLI:**
```bash
python3 main.py add "Alice" alice@example.com
python3 main.py list
```

**Run the test suite:**
```bash
pytest -v
```

## Architecture

GUI and CLI both call a single `ContactService`, which delegates storage to a `ContactRepository`. Neither front-end contains business logic or touches the data file directly — this keeps validation, deduplication, and undo behavior in exactly one place.

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown and design rationale.


## Project Structure
```
contactvault/
├── src/contactvault/   # application package (models, services, repository,
│                         validation, gui, cli, utils)
├── assets/             # icons and static assets
├── docs/                # architecture notes and guides
├── screenshots/         # app screenshots
├── tests/               # pytest suite (43 tests)
├── logs/                 # runtime logs (gitignored)
├── output/               # exported files and data (gitignored)
├── config/               # default_config.json
├── .github/workflows/    # CI (pytest across OS matrix)
├── main.py               # entry point (GUI or CLI dispatch)
└── requirements.txt
```

## Technologies Used
- Python 3.11+
- CustomTkinter (GUI)
- argparse (CLI, stdlib)
- email-validator (validation)
- pytest (testing)

## How It Works
_TODO — filled in during Step 11 (Documentation)._

## Future Improvements
_TODO — filled in during Step 11 (Documentation)._

## License
MIT — see [LICENSE](LICENSE).

## Acknowledgements
Built as part of a portfolio following the Google IT Automation with
Python Professional Certificate.
