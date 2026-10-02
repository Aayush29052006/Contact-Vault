"""Modern confirmation dialog, replacing the previous instant-action
delete flow. Used for destructive actions."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.gui import theme


class ConfirmDialog(ctk.CTkToplevel):
    """Display a confirmation dialog for potentially destructive actions."""

    def __init__(
        self,
        parent,
        fonts,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        danger: bool = False,
        on_confirm=None,
    ) -> None:
        super().__init__(parent)

        self._on_confirm = on_confirm
        self._configure_window(parent, title)

        self._build_content(
            fonts,
            title,
            message,
            confirm_text,
            danger,
        )

        self._center_on_parent(parent)

    def _configure_window(self, parent, title: str) -> None:
        """Configure the dialog window and modal behavior."""
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=theme.COLOR["surface"])
        self.transient(parent)
        self.after(10, self.grab_set)

    def _build_content(
        self,
        fonts,
        title: str,
        message: str,
        confirm_text: str,
        danger: bool,
    ) -> None:
        """Build the dialog labels and action buttons."""
        icon_color = (
            theme.COLOR["danger"] if danger else theme.COLOR["accent"]
        )

        ctk.CTkLabel(
            self,
            text=title,
            font=fonts["subheading"],
            text_color=icon_color,
        ).pack(pady=(26, 8), padx=24, anchor="w")

        ctk.CTkLabel(
            self,
            text=message,
            font=fonts["body"],
            text_color=theme.COLOR["text_secondary"],
            wraplength=360,
            justify="left",
        ).pack(padx=24, anchor="w")

        self._build_buttons(confirm_text, danger)

        self.bind("<Escape>", lambda event: self.destroy())

    def _build_buttons(self, confirm_text: str, danger: bool) -> None:
        """Build the Cancel and Confirm buttons."""
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=24, pady=22)

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            border_color=theme.COLOR["border_strong"],
            text_color=theme.COLOR["text"],
            corner_radius=theme.RADIUS["md"],
            command=self.destroy,
            width=100,
        ).pack(side="right", padx=(8, 0))

        confirm_color = (
            theme.COLOR["danger"] if danger else theme.COLOR["accent"]
        )
        confirm_hover = (
            theme.COLOR["danger_hover"]
            if danger
            else theme.COLOR["accent_hover"]
        )

        ctk.CTkButton(
            btn_row,
            text=confirm_text,
            fg_color=confirm_color,
            hover_color=confirm_hover,
            corner_radius=theme.RADIUS["md"],
            command=self._confirm,
            width=110,
        ).pack(side="right")

    def _center_on_parent(self, parent) -> None:
        """Size and center the dialog over its parent window."""
        self.update_idletasks()

        width = max(self.winfo_reqwidth() + 20, 380)
        height = self.winfo_reqheight() + 20
        self.geometry(f"{width}x{height}")

        parent.update_idletasks()

        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()

        x = px + (pw - width) // 2
        y = py + (ph - height) // 3

        self.geometry(f"+{x}+{y}")

    def _confirm(self) -> None:
        """Execute the confirmation callback and close the dialog."""
        self.destroy()

        if self._on_confirm:
            self._on_confirm()