"""Contacts list frame (add/view/search/edit/delete UI)."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.exceptions import ContactVaultError
from contactvault.gui import theme, icons
from contactvault.gui.dialogs import ConfirmDialog


class ContactsFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = app.service
        self.fonts = app.fonts
        self._editing_id: str | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_add_form()
        self._build_search_bar()
        self._build_list_area()

        self.refresh()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Contacts", font=self.fonts["heading"],
                     text_color=theme.COLOR["text"]).grid(row=0, column=0, sticky="w")

        self.count_badge = ctk.CTkLabel(
            header, text="0", font=self.fonts["caption"], text_color=theme.COLOR["accent"],
            fg_color=theme.COLOR["accent_soft"], corner_radius=theme.RADIUS["pill"],
            width=32, height=22,
        )
        self.count_badge.grid(row=0, column=1, sticky="e")

    def _build_add_form(self) -> None:
        form = ctk.CTkFrame(self, corner_radius=theme.RADIUS["lg"], fg_color=theme.COLOR["surface"],
                             border_width=1, border_color=theme.COLOR["border"])
        form.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=0)

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.grid(row=0, column=0, sticky="ew", padx=(16, 10), pady=16)
        fields.grid_columnconfigure((0, 1), weight=1)

        self.name_entry = ctk.CTkEntry(
            fields, placeholder_text="Name", height=38, corner_radius=theme.RADIUS["md"],
            border_color=theme.COLOR["border"], fg_color=theme.COLOR["surface_alt"],
        )
        self.name_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.email_entry = ctk.CTkEntry(
            fields, placeholder_text="Email address", height=38, corner_radius=theme.RADIUS["md"],
            border_color=theme.COLOR["border"], fg_color=theme.COLOR["surface_alt"],
        )
        self.email_entry.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=16)

        self.add_btn = ctk.CTkButton(
            buttons, text="Add contact", height=38, width=140, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["accent"], hover_color=theme.COLOR["accent_hover"],
            image=icons.solid_icon("plus", 15, "#FFFFFF"), compound="left",
            font=self.fonts["body_bold"], command=self._on_add,
        )
        self.add_btn.grid(row=0, column=0, padx=(0, 8))

        # Filled background (not transparent+border) -- a filled shape
        # is always visibly a box regardless of how the border renders,
        # closing the recurring "invisible outline" bug for good.
        self.undo_btn = ctk.CTkButton(
            buttons, text="Undo", height=38, width=90, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["surface_alt"], hover_color=theme.COLOR["border_strong"],
            text_color=theme.COLOR["text"], font=self.fonts["body"], command=self._on_undo,
        )
        self.undo_btn.grid(row=0, column=1)

        for entry in (self.name_entry, self.email_entry):
            entry.bind("<Return>", lambda e: self._on_add())
            entry.bind("<Escape>", lambda e: self._cancel_edit())

    def _build_search_bar(self) -> None:
        wrapper = ctk.CTkFrame(self, corner_radius=theme.RADIUS["pill"],
                                fg_color=theme.COLOR["surface"], border_width=1,
                                border_color=theme.COLOR["border"])
        wrapper.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 14))
        wrapper.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(wrapper, image=icons.ctk_icon("search", 15, theme.COLOR["text_muted"][0],
                     theme.COLOR["text_muted"][1]), text="").grid(row=0, column=0, padx=(14, 6))

        self.search_entry = ctk.CTkEntry(
            wrapper, placeholder_text="Search by name or email...", border_width=0,
            fg_color="transparent",
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        self.search_entry.bind("<Escape>", lambda e: self._clear_search())

    def _build_list_area(self) -> None:
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.list_frame.grid_columnconfigure(0, weight=1)

        canvas = self.list_frame._parent_canvas
        canvas.bind("<Enter>", lambda e: canvas.focus_set())
        canvas.bind("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        canvas.bind("<Next>", lambda e: canvas.yview_scroll(1, "pages"))
        canvas.bind("<Home>", lambda e: canvas.yview_moveto(0))
        canvas.bind("<End>", lambda e: canvas.yview_moveto(1))
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))


    def refresh(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        query = self.search_entry.get().strip()
        contacts = self.service.search(query) if query else self.service.get_all()
        self.count_badge.configure(text=str(len(self.service.get_all())))

        if not contacts:
            ctk.CTkLabel(
                self.list_frame,
                text="No contacts match your search." if query else "No contacts yet — add your first one above.",
                text_color=theme.COLOR["text_muted"], font=self.fonts["body"],
            ).grid(row=0, column=0, pady=40)
            return
        
        for i, contact in enumerate(contacts):
            self._build_row(i, contact)

    def _build_row(self, index: int, contact) -> None:
        row = ctk.CTkFrame(self.list_frame, corner_radius=theme.RADIUS["md"],
                            fg_color=theme.COLOR["surface"], border_width=1,
                            border_color=theme.COLOR["border"])
        row.grid(row=index, column=0, sticky="ew", pady=4)
        row.grid_columnconfigure(1, weight=1)

        avatar_color = theme.AVATAR_COLORS[hash(contact.id) % len(theme.AVATAR_COLORS)]
        avatar = ctk.CTkFrame(row, width=38, height=38, corner_radius=19, fg_color=avatar_color)
        avatar.grid(row=0, column=0, padx=(14, 12), pady=12)
        avatar.grid_propagate(False)
        initial = (contact.name.strip()[:1] or "?").upper()
        ctk.CTkLabel(avatar, text=initial, text_color="#FFFFFF",
                     font=self.fonts["body_bold"]).place(relx=0.5, rely=0.5, anchor="center")

        text_col = ctk.CTkFrame(row, fg_color="transparent")
        text_col.grid(row=0, column=1, sticky="ew", pady=10)
        ctk.CTkLabel(text_col, text=contact.name, font=self.fonts["body_bold"],
                     text_color=theme.COLOR["text"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_col, text=contact.email, font=self.fonts["caption"],
                     text_color=theme.COLOR["text_secondary"], anchor="w").pack(anchor="w")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=2, padx=(0, 12), pady=10)

        # Filled style here too, for the same reason as Undo above.
        ctk.CTkButton(
            actions, text="Edit", width=76, height=32, corner_radius=theme.RADIUS["sm"],
            fg_color=theme.COLOR["surface_alt"], hover_color=theme.COLOR["border_strong"],
            text_color=theme.COLOR["text"],
            image=icons.ctk_icon("edit", 13, theme.COLOR["text"][0], theme.COLOR["text"][1]),
            compound="left", font=self.fonts["caption"],
            command=lambda c=contact: self._start_edit(c),
        ).grid(row=0, column=0, padx=(0, 6))

        ctk.CTkButton(
            actions, text="Delete", width=86, height=32, corner_radius=theme.RADIUS["sm"],
            fg_color=theme.COLOR["danger_soft"], hover_color=theme.COLOR["danger"],
            text_color=theme.COLOR["danger"],
            image=icons.ctk_icon("trash", 13, theme.COLOR["danger"][0], theme.COLOR["danger"][1]),
            compound="left", font=self.fonts["caption"],
            command=lambda c=contact: self._confirm_delete(c),
        ).grid(row=0, column=1)

        row.bind("<Enter>", lambda e, r=row: r.configure(border_color=theme.COLOR["accent"]))
        row.bind("<Leave>", lambda e, r=row: r.configure(border_color=theme.COLOR["border"]))

    def _start_edit(self, contact) -> None:
        self._editing_id = contact.id
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, contact.name)
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, contact.email)
        self.add_btn.configure(text="Save changes", image=icons.solid_icon("check", 15, "#FFFFFF"))
        self.name_entry.focus_set()

    def _cancel_edit(self) -> None:
        if self._editing_id is None:
            return
        self._editing_id = None
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.add_btn.configure(text="Add contact", image=icons.solid_icon("plus", 15, "#FFFFFF"))
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
                self.add_btn.configure(text="Add contact", image=icons.solid_icon("plus", 15, "#FFFFFF"))
            else:
                self.service.add_contact(name, email)
                self.app.set_status(f"Added {name}.")
        except ContactVaultError as exc:
            self.app.set_status(str(exc), is_error=True)
            return

        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.refresh()

    def _confirm_delete(self, contact) -> None:
        ConfirmDialog(
            self.winfo_toplevel(), fonts=self.fonts,
            title="Delete contact?",
            message=f"Remove {contact.name} ({contact.email}) from your contacts? You can undo this right after.",
            confirm_text="Delete", danger=True,
            on_confirm=lambda: self._on_delete(contact),
        )

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