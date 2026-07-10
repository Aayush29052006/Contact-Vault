"""Design tokens: color palette, typography, spacing. Single source of
truth for the app's visual style -- change values here and the whole
UI updates consistently. All colors are (light_mode, dark_mode) tuples;
CTk resolves the right one automatically based on appearance mode.
"""

from __future__ import annotations

import customtkinter as ctk

COLOR = {
    "bg": ("#F5F6FA", "#111318"),
    "surface": ("#FFFFFF", "#1B1E25"),
    "surface_alt": ("#EEF0F5", "#22252E"),
    "border": ("#E1E4EB", "#2B2F3A"),
    "border_strong": ("#C7CBD6", "#3A3F4D"),
    "text": ("#1B1E27", "#F1F2F6"),
    "text_secondary": ("#6B7080", "#9298A8"),
    "text_muted": ("#9CA0AD", "#6B7080"),

    "accent": ("#4F46E5", "#6366F1"),
    "accent_hover": ("#4338CA", "#818CF8"),
    "accent_soft": ("#EEF0FF", "#262A44"),

    "success": ("#16A34A", "#22C55E"),
    "danger": ("#DC2626", "#EF4444"),
    "danger_hover": ("#B91C1C", "#F87171"),
    "danger_soft": ("#FDECEC", "#3A2020"),
    "warning": ("#D97706", "#F59E0B"),
}

AVATAR_COLORS = [
    ("#4F46E5", "#6366F1"),
    ("#0EA5A4", "#14B8A6"),
    ("#D97706", "#F59E0B"),
    ("#DB2777", "#EC4899"),
    ("#16A34A", "#22C55E"),
    ("#7C3AED", "#8B5CF6"),
]

RADIUS = {"sm": 6, "md": 10, "lg": 14, "pill": 999}


def fonts() -> dict[str, ctk.CTkFont]:
    """Build font objects. Must be called after a CTk root exists."""
    return {
        "logo": ctk.CTkFont(size=17, weight="bold"),
        "heading": ctk.CTkFont(size=19, weight="bold"),
        "subheading": ctk.CTkFont(size=14, weight="bold"),
        "body": ctk.CTkFont(size=13),
        "body_bold": ctk.CTkFont(size=13, weight="bold"),
        "caption": ctk.CTkFont(size=11),
        "nav": ctk.CTkFont(size=13, weight="bold"),
    }