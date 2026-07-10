# ContactVault

A cross-platform, production-grade email/contact list manager with
both a modern desktop GUI (CustomTkinter) and a full CLI, sharing a
single validated, deduplicated data layer.

> Status: scaffolding stage. Full documentation lands in Step 11 of
> the project workflow.

## Features
_TODO — filled in during Step 11 (Documentation)._

## Installation
_TODO — filled in during Step 11 (Documentation)._

## Architecture
GUI and CLI both call a single `ContactService`, which delegates
storage to a `ContactRepository`. See `docs/architecture.md`
(added in Step 11) for the full diagram and rationale.

## Project Structure
```
contactvault/
├── src/contactvault/   # application package (models, services, repository,
│                         validation, gui, cli, utils)
├── assets/             # icons and static assets
├── docs/                # architecture notes and guides
├── screenshots/         # app screenshots
├── tests/               # pytest suite
├── logs/                 # runtime logs (gitignored)
├── output/               # exported files (gitignored)
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
