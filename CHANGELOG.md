# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Added
- Contact model, custom exception hierarchy
- Email validation via email-validator library
- JSON repository with atomic, crash-safe writes
- ContactService with add/edit/delete/search and Command-pattern undo
- CLI (add, list, search, edit, delete)
- GUI: Contacts, Import/Export, Settings, About pages (CustomTkinter, dark/light themes)
- Adjustable UI text-size scaling
- 43 automated tests (pytest) covering model, validation, repository, service, and CLI
- CI workflow running tests across Ubuntu, Windows, and macOS
- Full documentation: README, architecture doc
