"""Minimal, dependency-free icon set drawn with Pillow at 4x and
downscaled for clean anti-aliased edges. No external icon files or
network downloads -- Pillow is already a customtkinter dependency,
so nothing new needs installing. Icons adapt to light/dark mode.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw
import customtkinter as ctk

_SCALE = 4


def _canvas(size: int):
    s = size * _SCALE
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), s


def _stroke(s: int) -> int:
    return max(3, s // 11)


def _finish(img: Image.Image, size: int) -> Image.Image:
    return img.resize((size, size), Image.LANCZOS)


def _plus(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    p = s * 0.22
    d.line([(s / 2, p), (s / 2, s - p)], fill=color, width=w)
    d.line([(p, s / 2), (s - p, s / 2)], fill=color, width=w)
    return _finish(img, size)


def _x(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    p = s * 0.26
    d.line([(p, p), (s - p, s - p)], fill=color, width=w)
    d.line([(s - p, p), (p, s - p)], fill=color, width=w)
    return _finish(img, size)


def _check(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.line([(s * 0.2, s * 0.52), (s * 0.42, s * 0.74), (s * 0.82, s * 0.28)],
           fill=color, width=w, joint="curve")
    return _finish(img, size)


def _edit(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.line([(s * 0.22, s * 0.78), (s * 0.68, s * 0.32)], fill=color, width=w)
    tip = [(s * 0.68, s * 0.32), (s * 0.84, s * 0.16), (s * 0.90, s * 0.22), (s * 0.74, s * 0.38)]
    d.polygon(tip, fill=color)
    return _finish(img, size)


def _trash(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.line([(s * 0.22, s * 0.30), (s * 0.78, s * 0.30)], fill=color, width=w)
    d.rectangle([s * 0.40, s * 0.16, s * 0.60, s * 0.26], outline=color, width=w)
    d.rounded_rectangle([s * 0.28, s * 0.30, s * 0.72, s * 0.86], radius=s * 0.06, outline=color, width=w)
    d.line([(s * 0.42, s * 0.42), (s * 0.42, s * 0.74)], fill=color, width=max(2, w - 1))
    d.line([(s * 0.58, s * 0.42), (s * 0.58, s * 0.74)], fill=color, width=max(2, w - 1))
    return _finish(img, size)


def _search(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.ellipse([s * 0.15, s * 0.15, s * 0.62, s * 0.62], outline=color, width=w)
    d.line([(s * 0.56, s * 0.56), (s * 0.86, s * 0.86)], fill=color, width=w)
    return _finish(img, size)


def _undo(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    box = [s * 0.15, s * 0.15, s * 0.85, s * 0.85]
    d.arc(box, start=40, end=320, fill=color, width=w)
    cx, cy, r = s * 0.5, s * 0.5, s * 0.35
    ang = math.radians(40)
    px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
    tri = [(px, py), (px - s * 0.14, py - s * 0.02), (px - s * 0.03, py + s * 0.14)]
    d.polygon(tri, fill=color)
    return _finish(img, size)


def _upload(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.line([(s * 0.5, s * 0.7), (s * 0.5, s * 0.2)], fill=color, width=w)
    d.polygon([(s * 0.5, s * 0.14), (s * 0.32, s * 0.36), (s * 0.68, s * 0.36)], fill=color)
    d.line([(s * 0.2, s * 0.82), (s * 0.8, s * 0.82)], fill=color, width=w)
    return _finish(img, size)


def _download(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.line([(s * 0.5, s * 0.18), (s * 0.5, s * 0.68)], fill=color, width=w)
    d.polygon([(s * 0.5, s * 0.78), (s * 0.32, s * 0.56), (s * 0.68, s * 0.56)], fill=color)
    d.line([(s * 0.2, s * 0.84), (s * 0.8, s * 0.84)], fill=color, width=w)
    return _finish(img, size)


def _settings(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    cx, cy, r = s * 0.5, s * 0.5, s * 0.2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    for i in range(8):
        ang = math.radians(i * 45)
        x1, y1 = cx + math.cos(ang) * s * 0.3, cy + math.sin(ang) * s * 0.3
        x2, y2 = cx + math.cos(ang) * s * 0.42, cy + math.sin(ang) * s * 0.42
        d.line([(x1, y1), (x2, y2)], fill=color, width=w)
    return _finish(img, size)


def _info(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.ellipse([s * 0.15, s * 0.15, s * 0.85, s * 0.85], outline=color, width=w)
    d.ellipse([s * 0.46, s * 0.28, s * 0.54, s * 0.36], fill=color)
    d.line([(s * 0.5, s * 0.44), (s * 0.5, s * 0.7)], fill=color, width=w)
    return _finish(img, size)


def _users(size, color):
    img, d, s = _canvas(size)
    w = _stroke(s)
    d.ellipse([s * 0.35, s * 0.18, s * 0.65, s * 0.48], outline=color, width=w)
    d.arc([s * 0.18, s * 0.5, s * 0.82, s * 1.05], start=200, end=340, fill=color, width=w)
    return _finish(img, size)


_DRAW = {
    "plus": _plus, "x": _x, "check": _check, "edit": _edit, "trash": _trash,
    "search": _search, "undo": _undo, "upload": _upload, "download": _download,
    "settings": _settings, "info": _info, "users": _users,
}


def icon(name: str, size: int = 18, color: str = "#FFFFFF") -> Image.Image:
    return _DRAW[name](size, color)


def ctk_icon(name: str, size: int = 18, light: str = "#1B1E27", dark: str = "#F1F2F6") -> ctk.CTkImage:
    """Theme-adaptive icon: different flat color per light/dark mode."""
    return ctk.CTkImage(
        light_image=icon(name, size, light),
        dark_image=icon(name, size, dark),
        size=(size, size),
    )


def solid_icon(name: str, size: int = 18, color: str = "#FFFFFF") -> ctk.CTkImage:
    """Fixed single-color icon (e.g. white icon on a solid accent button)."""
    img = icon(name, size, color)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))