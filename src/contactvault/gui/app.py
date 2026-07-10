"""ContactVault GUI application entry point."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.repository.json_repository import JSONContactRepository
from contactvault.services.contact_service import ContactService
from contactvault.utils.config import load_config
from contactvault.utils.logger import get_logger
from contactvault.gui.frames.contacts_frame import ContactsFrame
from contactvault.gui.frames.import_export_frame import ImportExportFrame
from contactvault.gui.frames.settings_frame import SettingsFrame
from contactvault.gui.frames.about_frame import AboutFrame

logger = get_logger(__name__)


class App(ctk.CTk):
    """Main window: sidebar navigation + swappable content pages."""

    def __init__(self) -> None:
        super().__init__()

        config = load_config()

        ctk.set_appearance_mode(config.get("theme", "dark"))
        ctk.set_default_color_theme("blue")
        # Apply saved text-size preference before building any widgets.
        ctk.set_widget_scaling(config.get("text_scale", 1.0))

        self.title("ContactVault")
        self.geometry("960x620")
        self.minsize(780, 480)

        self.service = ContactService(JSONContactRepository(config["data_file"]))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()
        self._build_status_bar()

        self.frames: dict[str, ctk.CTkFrame] = {}
        self._register_frame("contacts", ContactsFrame)
        self._register_frame("import_export", ImportExportFrame)
        self._register_frame("settings", SettingsFrame)
        self._register_frame("about", AboutFrame)

        self.show_frame("contacts")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(5, weight=1)

        # Explicit (light, dark) tuple -- without this the label/button
        # text falls back to a color meant for dark backgrounds only,
        # which is invisible in light mode.
        ctk.CTkLabel(
            sidebar, text="ContactVault", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray95"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        nav_items = [
            ("Contacts", "contacts"),
            ("Import / Export", "import_export"),
            ("Settings", "settings"),
            ("About", "about"),
        ]
        for i, (label, key) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", corner_radius=8,
                fg_color="transparent", hover_color=("gray80", "gray25"),
                text_color=("gray10", "gray90"),
                command=lambda k=key: self.show_frame(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=4, sticky="ew")

    def _build_content_area(self) -> None:
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _build_status_bar(self) -> None:
        self.status_bar = ctk.CTkLabel(
            self, text="Ready", anchor="w", height=24,
            fg_color=("gray85", "gray17"), text_color=("gray10", "gray90"),
            corner_radius=0,
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._default_status_color = self.status_bar.cget("text_color")

    def _register_frame(self, key: str, frame_cls) -> None:
        frame = frame_cls(self.content, app=self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[key] = frame

    def show_frame(self, key: str) -> None:
        self.frames[key].tkraise()
        if hasattr(self.frames[key], "on_show"):
            self.frames[key].on_show()

    def set_status(self, message: str, is_error: bool = False) -> None:
        color = "#E24B4A" if is_error else self._default_status_color
        self.status_bar.configure(text=message, text_color=color)
        (logger.error if is_error else logger.info)(message)


def run() -> None:
    App().mainloop()


if __name__ == "__main__":
    run()