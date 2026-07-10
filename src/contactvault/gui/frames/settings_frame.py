"""Settings frame."""

from __future__ import annotations

import json

import customtkinter as ctk

from contactvault.utils.config import load_config, DEFAULT_CONFIG_PATH


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color="transparent")
        self.app = app

        config = load_config()

        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(10, 20))

        ctk.CTkLabel(self, text="Data file path").pack(anchor="w")
        self.data_file_entry = ctk.CTkEntry(self, width=400)
        self.data_file_entry.insert(0, config["data_file"])
        self.data_file_entry.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(self, text="Theme").pack(anchor="w")
        self.theme_option = ctk.CTkOptionMenu(self, values=["dark", "light"])
        self.theme_option.set(config["theme"])
        self.theme_option.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(self, text="Log level").pack(anchor="w")
        self.log_level_option = ctk.CTkOptionMenu(self, values=["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_option.set(config["log_level"])
        self.log_level_option.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self, text="Text size").pack(anchor="w")
        scale_row = ctk.CTkFrame(self, fg_color="transparent")
        scale_row.pack(anchor="w", fill="x", pady=(0, 4))

        self._scale = config.get("text_scale", 1.0)
        self.scale_label = ctk.CTkLabel(scale_row, text=f"{int(self._scale * 100)}%", width=50)
        self.scale_label.pack(side="right", padx=(10, 0))

        # IMPORTANT: this command only runs while dragging, and must
        # stay cheap (label text only). Never call set_widget_scaling()
        # here -- it rebuilds every widget in the app and will flicker
        # badly if triggered on every drag tick.
        self.scale_slider = ctk.CTkSlider(
            scale_row, from_=0.8, to=1.5, number_of_steps=14, command=self._on_slider_move
        )
        self.scale_slider.set(self._scale)
        self.scale_slider.pack(side="left", fill="x", expand=True)

        preview_row = ctk.CTkFrame(self, fg_color="transparent")
        preview_row.pack(anchor="w", pady=(4, 4))
        ctk.CTkButton(
            preview_row, text="Preview size", width=120,
            fg_color="transparent", border_width=1,
            command=self._apply_preview,
        ).pack(side="left")

        ctk.CTkLabel(
            self,
            text="Drag to pick a size, click Preview to see it applied instantly.\n"
                 "Click Save settings to keep it for next launch.",
            text_color="gray", font=ctk.CTkFont(size=11), justify="left",
        ).pack(anchor="w", pady=(4, 20))

        ctk.CTkButton(self, text="Save settings", command=self._save).pack(anchor="w")

    def _on_slider_move(self, value: float) -> None:
        """Cheap: only updates the percentage label. No widget rebuild."""
        self._scale = round(value, 2)
        self.scale_label.configure(text=f"{int(self._scale * 100)}%")

    def _apply_preview(self) -> None:
        """Expensive: applies the scale once, on demand -- a single clean
        redraw instead of continuous flicker during dragging."""
        ctk.set_widget_scaling(self._scale)

    def _save(self) -> None:
        ctk.set_widget_scaling(self._scale)
        new_config = {
            "data_file": self.data_file_entry.get().strip(),
            "theme": self.theme_option.get(),
            "log_level": self.log_level_option.get(),
            "text_scale": self._scale,
        }
        DEFAULT_CONFIG_PATH.write_text(json.dumps(new_config, indent=2), encoding="utf-8")
        ctk.set_appearance_mode(new_config["theme"])
        self.app.set_status("Settings saved.")