"""ui package — design system shared by all pages."""
from .tokens import COLORS, SPACING, FONTS, STATUS_COLORS, FONT_FAMILY
from .helpers import (
    truncate, rounded_rect_canvas,
    initials_of, lighten, darken, bind_hover,
)
from . import components

__all__ = [
    "COLORS", "SPACING", "FONTS", "STATUS_COLORS", "FONT_FAMILY",
    "truncate", "rounded_rect_canvas", "initials_of",
    "lighten", "darken", "bind_hover",
    "components",
]
