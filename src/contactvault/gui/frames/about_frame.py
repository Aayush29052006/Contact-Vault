"""About frame."""

from __future__ import annotations

import customtkinter as ctk


class AboutFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="ContactVault", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 4))
        ctk.CTkLabel(self, text="Version 0.1.0", text_color="gray").pack()

        text = (
            "A cross-platform contact and email list manager, built with a "
            "shared service layer powering both a desktop GUI and a CLI.\n\n"
            "Author: Aayush Jivan Chaudhari\n"
            "License: MIT"
        )
        ctk.CTkLabel(self, text=text, justify="center", wraplength=420).pack(pady=20)