"""About frame."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.gui import theme


class AboutFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        fonts = app.fonts

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(expand=True)

        badge_size = int(64 * getattr(app, "scale", 1.0))
        badge = ctk.CTkFrame(wrapper, width=badge_size, height=badge_size,
                              corner_radius=int(badge_size * 0.25),
                              fg_color=theme.COLOR["accent"])
        badge.pack(pady=(40, 16))
        badge.grid_propagate(False)

        ctk.CTkLabel(badge, text="CV", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=24, weight="bold")).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(wrapper, text="ContactVault", font=fonts["heading"],
                     text_color=theme.COLOR["text"]).pack()
        ctk.CTkLabel(wrapper, text="Version 0.1.0", font=fonts["caption"],
                     text_color=theme.COLOR["text_muted"]).pack(pady=(2, 20))

        card = ctk.CTkFrame(wrapper, corner_radius=theme.RADIUS["lg"],
                             fg_color=theme.COLOR["surface"], border_width=1,
                             border_color=theme.COLOR["border"])
        card.pack(padx=20)

        text = (
            "A cross-platform contact and email list manager, built with a "
            "shared service layer powering both a desktop GUI and a CLI."
        )
        ctk.CTkLabel(card, text=text, font=fonts["body"], text_color=theme.COLOR["text_secondary"],
                     justify="center", wraplength=420).grid(
            row=0, column=0, columnspan=2, padx=32, pady=(28, 20), sticky="ew")

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)

        for i, (label, value) in enumerate([("Author", "Aayush Jivan Chaudhari"), ("License", "MIT")], start=1):
            ctk.CTkLabel(card, text=label, font=fonts["caption"],
                         text_color=theme.COLOR["text_muted"]).grid(
                row=i, column=0, padx=(32, 12), pady=6, sticky="w")
            ctk.CTkLabel(card, text=value, font=fonts["body_bold"],
                         text_color=theme.COLOR["text"]).grid(
                row=i, column=1, padx=(0, 32), pady=6, sticky="e")

        ctk.CTkFrame(card, height=1, fg_color=theme.COLOR["border"]).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=32, pady=(16, 24))