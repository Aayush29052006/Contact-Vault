"""Contacts list frame (add/view/search/edit/delete UI)."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.exceptions import ContactVaultError


class ContactsFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = app.service
        self._editing_id: str | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_add_form()
        self._build_search_bar()
        self._build_list_area()

        self.refresh()
    def _build_add_form(self) -> None:
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=0)

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.grid(row=0, column=0, sticky="ew", padx=(10, 10), pady=10)
        fields.grid_columnconfigure((0, 1), weight=1)

        self.name_entry = ctk.CTkEntry(fields, placeholder_text="Name")
        self.name_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.email_entry = ctk.CTkEntry(fields, placeholder_text="Email")
        self.email_entry.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=0, column=1, sticky="e", pady=10)

        self.add_btn = ctk.CTkButton(
            buttons, text="Add contact", width=130, border_spacing=10, command=self._on_add
        )
        self.add_btn.grid(row=0, column=0, padx=(0, 8))

        self.undo_btn = ctk.CTkButton(
            buttons, text="Undo", width=90, border_spacing=10,
            fg_color="transparent", border_width=1,
            command=self._on_undo,
        )
        self.undo_btn.grid(row=0, column=1)

        # DEBUG MARKER -- a real widget with a forced fixed width, not a
        # padding value that can get silently absorbed. This proves the
        # margin exists. We'll recolor it to match the background once
        # you confirm you can see it.
        margin_spacer = ctk.CTkFrame(form, width=24, height=10, fg_color="transparent")
        margin_spacer.grid(row=0, column=2, sticky="ns", pady=10)
        margin_spacer.grid_propagate(False)

        for entry in (self.name_entry, self.email_entry):
            entry.bind("<Return>", lambda e: self._on_add())
            entry.bind("<Escape>", lambda e: self._cancel_edit())

    def _build_search_bar(self) -> None:
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search by name or email...")
        self.search_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        self.search_entry.bind("<Escape>", lambda e: self._clear_search())

    def _build_list_area(self) -> None:
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        canvas = self.list_frame._parent_canvas
        canvas.bind("<Enter>", lambda e: canvas.focus_set())
        canvas.bind("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        canvas.bind("<Next>", lambda e: canvas.yview_scroll(1, "pages"))
        canvas.bind("<Home>", lambda e: canvas.yview_moveto(0))
        canvas.bind("<End>", lambda e: canvas.yview_moveto(1))
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        query = self.search_entry.get().strip()
        contacts = self.service.search(query) if query else self.service.get_all()

        if not contacts:
            ctk.CTkLabel(self.list_frame, text="No contacts yet.", text_color="gray").grid(
                row=0, column=0, pady=20
            )
            return

        for i, contact in enumerate(contacts):
            row = ctk.CTkFrame(self.list_frame)
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row, text=f"{contact.name}   —   {contact.email}", anchor="w",
                text_color=("gray10", "gray90"),
            ).grid(row=0, column=0, padx=10, pady=8, sticky="ew")

            ctk.CTkButton(
                row, text="Edit", width=80, border_spacing=8,
                fg_color="transparent", border_width=1,
                text_color=("gray10", "gray90"),
                command=lambda c=contact: self._start_edit(c),
            ).grid(row=0, column=1, padx=(0, 6), pady=8)

            ctk.CTkButton(
                row, text="Delete", width=90, border_spacing=8,
                fg_color="#993C1D", hover_color="#712B13",
                command=lambda c=contact: self._on_delete(c),
            ).grid(row=0, column=2, padx=(0, 10), pady=8)

    def _start_edit(self, contact) -> None:
        self._editing_id = contact.id
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, contact.name)
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, contact.email)
        self.add_btn.configure(text="Save changes")
        self.name_entry.focus_set()

    def _cancel_edit(self) -> None:
        if self._editing_id is None:
            return
        self._editing_id = None
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.add_btn.configure(text="Add contact")
        self.app.set_status("Edit cancelled.")

    def _clear_search(self) -> None:
        self.search_entry.delete(0, "end")
        self.refresh()

    def _on_add(self) -> None:
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not email:
            self.app.set_status("Name and email are both required.", is_error=True)
            return

        try:
            if self._editing_id:
                self.service.edit_contact(self._editing_id, name=name, email=email)
                self.app.set_status(f"Updated {name}.")
                self._editing_id = None
                self.add_btn.configure(text="Add contact")
            else:
                self.service.add_contact(name, email)
                self.app.set_status(f"Added {name}.")
        except ContactVaultError as exc:
            self.app.set_status(str(exc), is_error=True)
            return

        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.refresh()

    def _on_delete(self, contact) -> None:
        self.service.delete_contact(contact.id)
        self.app.set_status(f"Deleted {contact.name}. Undo available.")
        self.refresh()

    def _on_undo(self) -> None:
        if self.service.undo():
            self.app.set_status("Last action undone.")
        else:
            self.app.set_status("Nothing to undo.", is_error=True)
        self.refresh()