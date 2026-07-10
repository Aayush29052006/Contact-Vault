"""Command-line interface for ContactVault.

Every subcommand just parses arguments and calls ContactService --
no business logic lives here.
"""

from __future__ import annotations

import argparse
import sys

from contactvault.exceptions import (
    ContactVaultError,
)
from contactvault.repository.json_repository import JSONContactRepository
from contactvault.services.contact_service import ContactService
from contactvault.utils.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contactvault", description="Manage your contact list from the terminal."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a new contact")
    add_p.add_argument("name")
    add_p.add_argument("email")

    list_p = sub.add_parser("list", help="List all contacts")

    search_p = sub.add_parser("search", help="Search contacts by name or email")
    search_p.add_argument("query")

    edit_p = sub.add_parser("edit", help="Edit a contact by id")
    edit_p.add_argument("id")
    edit_p.add_argument("--name")
    edit_p.add_argument("--email")

    delete_p = sub.add_parser("delete", help="Delete a contact by id")
    delete_p.add_argument("id")

    return parser


def _print_contacts(contacts) -> None:
    if not contacts:
        print("No contacts found.")
        return
    for c in contacts:
        print(f"{c.id}  {c.name:<25} {c.email}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config()
    service = ContactService(JSONContactRepository(config["data_file"]))

    try:
        if args.command == "add":
            contact = service.add_contact(args.name, args.email)
            print(f"Added: {contact.name} <{contact.email}> (id={contact.id})")

        elif args.command == "list":
            _print_contacts(service.get_all())

        elif args.command == "search":
            _print_contacts(service.search(args.query))

        elif args.command == "edit":
            contact = service.edit_contact(args.id, name=args.name, email=args.email)
            print(f"Updated: {contact.name} <{contact.email}>")

        elif args.command == "delete":
            service.delete_contact(args.id)
            print("Deleted.")

    except ContactVaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
