"""Bulk import/export frame."""

from __future__ import annotations

import csv
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from contactvault.exceptions import ContactVaultError


class ImportExportFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = app.service

        ctk.CTkLabel(
            self, text="Import / Export", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(10, 20))

        ctk.CTkLabel(
            self, text="CSV must have 'name' and 'email' columns.", text_color="gray"
        ).pack(anchor="w", pady=(0, 10))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(0, 15))
        ctk.CTkButton(btn_row, text="Import CSV...", command=self._import_csv).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(btn_row, text="Export CSV...", command=self._export_csv).grid(row=0, column=1)

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(anchor="w", pady=(0, 10))

        self.report_box = ctk.CTkTextbox(self, width=500, height=220)
        self.report_box.pack(anchor="w", fill="both", expand=True)

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
                self._log(f"Added: {name} <{email}>")
            except ContactVaultError as exc:
                skipped += 1
                self._log(f"Skipped {email or name}: {exc}")
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