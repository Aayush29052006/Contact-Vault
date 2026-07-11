"""Settings frame."""

from __future__ import annotations

import json
from logging import config

import customtkinter as ctk

from contactvault.utils.config import load_config, DEFAULT_CONFIG_PATH
from contactvault.gui import theme, icons


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.fonts = app.fonts

        config = load_config()

        ctk.CTkLabel(self, text="Settings", font=self.fonts["heading"],
                     text_color=theme.COLOR["text"]).pack(anchor="w", padx=20, pady=(20, 16))

        self._build_data_card(config)
        self._build_appearance_card(config)

        ctk.CTkButton(
            self, text="Save settings", height=40, width=160, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["accent"], hover_color=theme.COLOR["accent_hover"],
            image=icons.solid_icon("check", 15, "#FFFFFF"), compound="left",
            font=self.fonts["body_bold"], command=self._save,
        ).pack(anchor="w", padx=20, pady=(4, 20))

    def _card(self, title: str, icon_name: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, corner_radius=theme.RADIUS["lg"], fg_color=theme.COLOR["surface"],
                             border_width=1, border_color=theme.COLOR["border"])
        card.pack(fill="x", padx=20, pady=(0, 14))
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(header, image=icons.ctk_icon(icon_name, 16, theme.COLOR["accent"][0],
                     theme.COLOR["accent"][1]), text="").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(header, text=title, font=self.fonts["subheading"],
                     text_color=theme.COLOR["text"]).pack(side="left")
        return card

    def _build_data_card(self, config: dict) -> None:
        card = self._card("Data", "download")
        ctk.CTkLabel(card, text="Data file path", font=self.fonts["caption"],
                     text_color=theme.COLOR["text_secondary"]).pack(anchor="w", padx=18)
        self.data_file_entry = ctk.CTkEntry(
            card, width=420, height=36, corner_radius=theme.RADIUS["md"],
            fg_color=theme.COLOR["surface_alt"], border_color=theme.COLOR["border"],
        )
        self.data_file_entry.insert(0, config["data_file"])
        self.data_file_entry.pack(anchor="w", padx=18, pady=(4, 18))

    def _build_appearance_card(self, config: dict) -> None:
        card = self._card("Appearance", "settings")

        self.theme_option = ctk.CTkOptionMenu(
            card, values=["Dark", "Light"], width=160, height=34,
            corner_radius=theme.RADIUS["md"], fg_color=theme.COLOR["accent"],
            button_color=theme.COLOR["accent"], button_hover_color=theme.COLOR["accent_hover"],
        )
        self.theme_option.set(config["theme"].capitalize())
        self.theme_option.pack(anchor="w", padx=18, pady=(4, 14))

        ctk.CTkLabel(card, text="Log level", font=self.fonts["caption"],
                     text_color=theme.COLOR["text_secondary"]).pack(anchor="w", padx=18)
        self.log_level_option = ctk.CTkOptionMenu(
            card, values=["DEBUG", "INFO", "WARNING", "ERROR"], width=160, height=34,
            corner_radius=theme.RADIUS["md"], fg_color=theme.COLOR["accent"],
            button_color=theme.COLOR["accent"], button_hover_color=theme.COLOR["accent_hover"],
        )
        self.log_level_option.set(config["log_level"])
        self.log_level_option.pack(anchor="w", padx=18, pady=(4, 14))

        ctk.CTkLabel(card, text="Text size", font=self.fonts["caption"],
                     text_color=theme.COLOR["text_secondary"]).pack(anchor="w", padx=18)

        scale_row = ctk.CTkFrame(card, fg_color="transparent")
        scale_row.pack(anchor="w", fill="x", padx=18, pady=(4, 4))

        self._scale = config.get("text_scale", 1.0)
        self.scale_label = ctk.CTkLabel(scale_row, text=f"{int(self._scale * 100)}%",
                                         width=50, font=self.fonts["body"],
                                         text_color=theme.COLOR["text"])
        self.scale_label.pack(side="right", padx=(10, 0))

        self.scale_slider = ctk.CTkSlider(
            scale_row, from_=0.8, to=1.5, number_of_steps=14,
            progress_color=theme.COLOR["accent"], button_color=theme.COLOR["accent"],
            button_hover_color=theme.COLOR["accent_hover"],
            command=self._on_slider_move,
        )
        self.scale_slider.set(self._scale)
        self.scale_slider.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            card, text="Preview size", height=32, width=130, corner_radius=theme.RADIUS["sm"],
            fg_color=theme.COLOR["surface_alt"], hover_color=theme.COLOR["border_strong"],
            text_color=theme.COLOR["text"], font=self.fonts["caption"],
            command=self._apply_preview,
        ).pack(anchor="w", padx=18, pady=(4, 6))

        ctk.CTkLabel(
            card, text="Drag to pick a size, Preview to apply instantly, Save to keep it.",
            text_color=theme.COLOR["text_muted"], font=self.fonts["caption"], justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def _on_slider_move(self, value: float) -> None:
        self._scale = round(value, 2)
        self.scale_label.configure(text=f"{int(self._scale * 100)}%")

    def _apply_preview(self) -> None:
        ctk.set_widget_scaling(self._scale)

    def _save(self) -> None:
        ctk.set_widget_scaling(self._scale)
        new_config = {
            "data_file": self.data_file_entry.get().strip(),
            "theme": self.theme_option.get().lower(),
            "log_level": self.log_level_option.get(),
            "text_scale": self._scale,
        }

        DEFAULT_CONFIG_PATH.write_text(json.dumps(new_config, indent=2), encoding="utf-8")
        ctk.set_appearance_mode(new_config["theme"])
        self.app.set_status("Settings saved.")