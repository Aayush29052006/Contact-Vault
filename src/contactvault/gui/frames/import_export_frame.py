"""Bulk import/export frame."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from contactvault.gui import theme, icons


class ImportExportFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = app.service
        self.fonts = app.fonts

        ctk.CTkLabel(self, text="Import / Export", font=self.fonts["heading"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(
            self,
            text="CSV needs 'name' and 'email' columns -- name is optional and auto-generated from the email if left blank.",
            font=self.fonts["caption"], text_color=theme.COLOR["text_secondary"],
            wraplength=600, justify="left",
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
            fg_color=theme.COLOR["surface_alt"], hover_color=theme.COLOR["border_strong"],
            text_color=theme.COLOR["text"],
            image=icons.ctk_icon("download", 15, theme.COLOR["text"][0], theme.COLOR["text"][1]),
            compound="left", font=self.fonts["body"], command=self._export_csv,
        ).grid(row=0, column=1)

        ctk.CTkFrame(card, height=1, fg_color=theme.COLOR["border"]).pack(fill="x", padx=20, pady=(6, 16))

        ctk.CTkLabel(card, text="Or paste emails directly", font=self.fonts["body_bold"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20)
        ctk.CTkLabel(
            card,
            text="One per line, or separated by commas/spaces -- no file needed. Names are auto-generated from each email.",
            font=self.fonts["caption"], text_color=theme.COLOR["text_secondary"],
            wraplength=600, justify="left",
        ).pack(anchor="w", padx=20, pady=(2, 10))

        self.paste_box = ctk.CTkTextbox(
            card, width=500, height=90, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["surface_alt"], border_width=1, border_color=theme.COLOR["border"],
            font=self.fonts["caption"],
        )
        self.paste_box.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkButton(
            card, text="Import pasted emails", height=36, width=190, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["accent"], hover_color=theme.COLOR["accent_hover"],
            image=icons.solid_icon("plus", 14, "#FFFFFF"), compound="left",
            font=self.fonts["body_bold"], command=self._import_pasted,
        ).pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkFrame(card, height=1, fg_color=theme.COLOR["border"]).pack(fill="x", padx=20, pady=(0, 16))

        self.progress = ctk.CTkProgressBar(card, width=440, height=8, corner_radius=theme.RADIUS["pill"],
                                            progress_color=theme.COLOR["accent"],
                                            fg_color=theme.COLOR["surface_alt"])
        self.progress.set(0)
        self.progress.pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(card, text="Activity log", font=self.fonts["body_bold"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20)

        self.report_box = ctk.CTkTextbox(
            card, width=500, height=180, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["surface_alt"], border_width=1, border_color=theme.COLOR["border"],
            font=self.fonts["caption"],
        )
        self.report_box.pack(anchor="w", fill="both", expand=True, padx=20, pady=(8, 20))

    def _report_result(self, result, source_label: str) -> None:
        lines = []
        for contact, derived in result.added:
            note = " (name auto-generated from email)" if derived else ""
            lines.append(f"✓ Added: {contact.name} <{contact.email}>{note}")
        for identifier, reason in result.skipped:
            lines.append(f"✗ Skipped {identifier}: {reason}")

        self.report_box.delete("1.0", "end")
        # One bulk insert instead of one insert per line -- for large
        # imports, hundreds of individual widget inserts is its own
        # slowdown, separate from (but related to) the disk-I/O fix.
        self.report_box.insert("end", "\n".join(lines) if lines else "No entries found.")
        self.progress.set(1.0)
        self.app.set_status(f"{source_label}: {len(result.added)} added, {len(result.skipped)} skipped.")

    def _import_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        self.progress.set(0)
        rows = list(csv.DictReader(Path(path).read_text(encoding="utf-8").splitlines()))
        entries = [((row.get("name") or "").strip(), (row.get("email") or "").strip()) for row in rows]

        result = self.service.add_bulk(entries)
        self._report_result(result, "CSV import complete")

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

    def _import_pasted(self) -> None:
        raw_text = self.paste_box.get("1.0", "end")
        tokens = [t for t in re.split(r"[\s,;]+", raw_text) if t]

        if not tokens:
            self.app.set_status("Paste some emails first.", is_error=True)
            return

        self.progress.set(0)
        entries = [("", token) for token in tokens]
        result = self.service.add_bulk(entries)
        self._report_result(result, "Paste import complete")
        self.paste_box.delete("1.0", "end")