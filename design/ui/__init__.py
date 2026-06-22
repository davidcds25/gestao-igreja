"""ui package — design system shared by all pages."""
from .tokens import COLORS, SPACING, FONTS, STATUS_COLORS, FONT_FAMILY, set_theme, get_theme
from .helpers import (
    truncate, rounded_rect_canvas,
    initials_of, lighten, darken, bind_hover,
)
from . import components

__all__ = [
    "COLORS", "SPACING", "FONTS", "STATUS_COLORS", "FONT_FAMILY",
    "set_theme", "get_theme",
    "truncate", "rounded_rect_canvas", "initials_of",
    "lighten", "darken", "bind_hover",
    "components",
]
