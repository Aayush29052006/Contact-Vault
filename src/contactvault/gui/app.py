"""ContactVault GUI application entry point."""

from __future__ import annotations

import customtkinter as ctk

from contactvault.repository.json_repository import JSONContactRepository
from contactvault.services.contact_service import ContactService
from contactvault.utils.config import load_config
from contactvault.utils.logger import get_logger
from contactvault.gui import theme, icons
from contactvault.gui.frames.contacts_frame import ContactsFrame
from contactvault.gui.frames.import_export_frame import ImportExportFrame
from contactvault.gui.frames.settings_frame import SettingsFrame
from contactvault.gui.frames.about_frame import AboutFrame

logger = get_logger(__name__)


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        config = load_config()

        ctk.set_appearance_mode(config.get("theme", "dark"))
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(config.get("text_scale", 1.0))

        self.fonts = theme.fonts()

        base_width, base_height = 1040, 660
        scale = config.get("text_scale", 1.0)
        self.scale = scale
        self.title("ContactVault")
        self.geometry(f"{int(base_width * scale)}x{int(base_height * scale)}")
        self.minsize(int(820 * scale), int(520 * scale))
        self.configure(fg_color=theme.COLOR["bg"])

        self.service = ContactService(JSONContactRepository(config["data_file"]))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._nav_buttons: dict[str, ctk.CTkButton] = {}

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
        # No grid_propagate(False) here on purpose: the sidebar holds
        # text (brand name, nav labels) whose rendered width changes
        # with the text-size setting, so the container must be free
        # to grow and shrink to fit it -- same lesson as the earlier
        # Undo-button overflow bug.
        sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color=theme.COLOR["surface"])
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(6, weight=1)


        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=18, pady=(22, 26), sticky="w")

        badge_size = int(36 * self.scale)
        logo_badge = ctk.CTkFrame(brand, width=badge_size, height=badge_size,
                                   corner_radius=int(badge_size * 0.28),
                                   fg_color=theme.COLOR["accent"])
        
        logo_badge.grid(row=0, column=0, padx=(0, 10))
        logo_badge.grid_propagate(False)
        ctk.CTkLabel(logo_badge, text="CV", text_color="#FFFFFF",
                     font=self.fonts["logo"]).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(brand, text="ContactVault", font=self.fonts["heading"],
                     text_color=theme.COLOR["text"]).grid(row=0, column=1, sticky="w")

        nav_items = [
            ("Contacts", "contacts", "users"),
            ("Import / Export", "import_export", "upload"),
            ("Settings", "settings", "settings"),
            ("About", "about", "info"),
        ]
        for i, (label, key, icon_name) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w", corner_radius=theme.RADIUS["sm"],
                height=40, fg_color="transparent", hover_color=theme.COLOR["surface_alt"],
                text_color=theme.COLOR["text_secondary"], font=self.fonts["nav"],
                image=icons.ctk_icon(icon_name, 17, theme.COLOR["text_secondary"][0],
                                      theme.COLOR["text_secondary"][1]),
                compound="left",
                command=lambda k=key: self.show_frame(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=3, sticky="ew")
            self._nav_buttons[key] = btn

    def _build_content_area(self) -> None:
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=theme.COLOR["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _build_status_bar(self) -> None:
        bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=theme.COLOR["surface"])
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self._status_dot = ctk.CTkLabel(bar, text="●", text_color=theme.COLOR["success"],
                                         font=self.fonts["caption"])
        self._status_dot.pack(side="left", padx=(16, 6), pady=4)

        self.status_label = ctk.CTkLabel(bar, text="Ready", anchor="w",
                                          text_color=theme.COLOR["text_secondary"],
                                          font=self.fonts["caption"])
        self.status_label.pack(side="left", pady=4)

    def _register_frame(self, key: str, frame_cls) -> None:
        frame = frame_cls(self.content, app=self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[key] = frame

    def show_frame(self, key: str) -> None:
        self.frames[key].tkraise()
        if hasattr(self.frames[key], "on_show"):
            self.frames[key].on_show()
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(fg_color=theme.COLOR["accent_soft"], text_color=theme.COLOR["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=theme.COLOR["text_secondary"])

    def set_status(self, message: str, is_error: bool = False) -> None:
        color = theme.COLOR["danger"] if is_error else theme.COLOR["success"]
        self._status_dot.configure(text_color=color)
        self.status_label.configure(text=message)
        (logger.error if is_error else logger.info)(message)


def run() -> None:
    App().mainloop()


if __name__ == "__main__":
    run()