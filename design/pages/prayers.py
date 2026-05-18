"""
pages/prayers.py
================
Tela de Orações — em construção.
"""

import tkinter as tk

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import page_container, screen_header


def render(parent, *, callbacks=None):
    content = page_container(parent)

    hdr = screen_header(
        content,
        icon="🙏",
        title="Orações",
        subtitle="Pedidos e registros de oração da comunidade",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))

    placeholder = tk.Frame(content, bg=COLORS["bg_card"],
                           highlightbackground=COLORS["divider"],
                           highlightthickness=1)
    placeholder.pack(fill=tk.BOTH, expand=True)

    inner = tk.Frame(placeholder, bg=COLORS["bg_card"])
    inner.place(relx=0.5, rely=0.45, anchor="center")

    tk.Label(inner, text="🙏",
             font=(FONTS["body"][0], 48),
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]
             ).pack(pady=(0, SPACING[3]))

    tk.Label(inner, text="Em breve",
             font=(FONTS["body"][0], 20, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text"]
             ).pack()

    tk.Label(inner,
             text="A funcionalidade de Orações está sendo preparada\ne estará disponível em breve.",
             font=FONTS["body"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"],
             justify=tk.CENTER
             ).pack(pady=(SPACING[2], 0))
