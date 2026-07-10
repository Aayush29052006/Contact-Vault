# Contributing to ContactVault

Thanks for considering a contribution.

## Getting started
1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   `pip install -r requirements.txt`
3. Create a feature branch: `git checkout -b feature/your-feature-name`

## Guidelines
- Follow PEP8 and use type hints.
- Keep business logic in the `services/` layer — the GUI and CLI
  should only call into it, never duplicate it.
- Add or update tests in `tests/` for any behavior change.
- Run `pytest` before opening a pull request.
- Write clear, meaningful commit messages (no "fix stuff" commits).

## Reporting issues
Please include your OS, Python version, and steps to reproduce.
