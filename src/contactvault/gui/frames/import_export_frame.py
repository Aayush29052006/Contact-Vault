"""Bulk import/export frame."""

from __future__ import annotations

import csv
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from contactvault.exceptions import ContactVaultError
from contactvault.gui import theme, icons


class ImportExportFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = app.service
        self.fonts = app.fonts

        ctk.CTkLabel(self, text="Import / Export", font=self.fonts["heading"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(self, text="CSV files need 'name' and 'email' columns.",
                     font=self.fonts["caption"], text_color=theme.COLOR["text_secondary"]
                     ).pack(anchor="w", padx=20, pady=(0, 16))

        card = ctk.CTkFrame(self, corner_radius=theme.RADIUS["lg"], fg_color=theme.COLOR["surface"],
                             border_width=1, border_color=theme.COLOR["border"])
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=20, pady=(20, 14))

        ctk.CTkButton(
            btn_row, text="Import CSV", height=38, width=140, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["accent"], hover_color=theme.COLOR["accent_hover"],
            image=icons.solid_icon("upload", 15, "#FFFFFF"), compound="left",
            font=self.fonts["body_bold"], command=self._import_csv,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="Export CSV", height=38, width=140, corner_radius=theme.RADIUS["md"],
            fg_color="transparent", border_width=1, border_color=theme.COLOR["border"],
            text_color=theme.COLOR["text"],
            image=icons.ctk_icon("download", 15, theme.COLOR["text"][0], theme.COLOR["text"][1]),
            compound="left", font=self.fonts["body"], command=self._export_csv,
        ).grid(row=0, column=1)

        self.progress = ctk.CTkProgressBar(card, width=440, height=8, corner_radius=theme.RADIUS["pill"],
                                            progress_color=theme.COLOR["accent"],
                                            fg_color=theme.COLOR["surface_alt"])
        self.progress.set(0)
        self.progress.pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(card, text="Activity log", font=self.fonts["body_bold"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20)

        self.report_box = ctk.CTkTextbox(
            card, width=500, height=220, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["surface_alt"], border_width=1, border_color=theme.COLOR["border"],
            font=self.fonts["caption"],
        )
        self.report_box.pack(anchor="w", fill="both", expand=True, padx=20, pady=(8, 20))

    def _log(self, message: str) -> None:
        self.report_box.insert("end", message + "\n")
        self.report_box.see("end")

    def _import_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        self.report_box.delete("1.0", "end")
        rows = list(csv.DictReader(Path(path).read_text(encoding="utf-8").splitlines()))
        total = len(rows) or 1
        added = skipped = 0

        for i, row in enumerate(rows, start=1):
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip()
            try:
                self.service.add_contact(name, email)
                added += 1
                self._log(f"✓ Added: {name} <{email}>")
            except ContactVaultError as exc:
                skipped += 1
                self._log(f"✗ Skipped {email or name}: {exc}")
            self.progress.set(i / total)
            self.update_idletasks()

        self.app.set_status(f"Import complete: {added} added, {skipped} skipped.")

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        contacts = self.service.get_all()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email"])
            for c in contacts:
                writer.writerow([c.name, c.email])

        self.app.set_status(f"Exported {len(contacts)} contacts to {path}.")