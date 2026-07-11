# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-07-11

### Added
- Contact model, custom exception hierarchy
- Email validation via email-validator library
- JSON repository with atomic, crash-safe writes
- ContactService with add/edit/delete/search and Command-pattern undo
- CLI (add, list, search, edit, delete)
- GUI: Contacts, Import/Export, Settings, About pages (CustomTkinter)
- Custom design system: color tokens, hand-drawn icon set, avatar initials, card layout
- Confirmation dialog before deleting a contact
- Bulk import from CSV or pasted emails (no file required), with automatic
  name derivation from email when left blank
- Adjustable UI text-size scaling (80%-150%), saved across restarts
- Full light/dark theme support
- Keyboard support: Enter/Escape/arrow keys/Page Up/Page Down/Home/End
- 52 automated tests (pytest) covering model, validation, repository,
  service, and CLI
- CI workflow running tests across Ubuntu, Windows, and macOS
- Full documentation: README with screenshots, architecture doc

### Fixed
- Atomic write error handling for temp-file creation failures
- Several UI scaling/layout bugs at non-default text sizes
- Startup performance: icon caching and lazy page construction
  (~2.4s -> ~0.86s to first render)
- Contact list no longer rebuilds unnecessarily on every tab revisit