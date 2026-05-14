"""
modals/base.py
==============
Classe base para todos os modais do sistema.
Fornece header/body/footer padronizados com design system.
"""

import tkinter as tk
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import divider_line


class StyledModal(tk.Toplevel):
    """Modal base com header card + body + footer card."""

    WIDTH = 600

    def __init__(self, root, *, title: str, subtitle: str = ""):
        super().__init__(root)
        self.root = root
        self.withdraw()

        self.configure(bg=COLORS["bg_dark"])
        self.resizable(False, False)
        self.grab_set()
        self.title(title)

        self._build_header(title, subtitle)

        body_wrap = tk.Frame(self, bg=COLORS["bg_dark"])
        body_wrap.pack(fill=tk.BOTH, expand=True,
                       padx=SPACING[6], pady=SPACING[4])
        self._build_body(body_wrap)

        foot_outer = tk.Frame(self, bg=COLORS["bg_card"],
                              highlightbackground=COLORS["divider"],
                              highlightthickness=1)
        foot_outer.pack(fill=tk.X, side=tk.BOTTOM)
        foot_inner = tk.Frame(foot_outer, bg=COLORS["bg_card"])
        foot_inner.pack(fill=tk.X, padx=SPACING[6], pady=SPACING[3])

        foot_left = tk.Frame(foot_inner, bg=COLORS["bg_card"])
        foot_left.pack(side=tk.LEFT)
        foot_right = tk.Frame(foot_inner, bg=COLORS["bg_card"])
        foot_right.pack(side=tk.RIGHT)
        self._build_footer(foot_left, foot_right)

        self._center_and_show()

    # ── header ────────────────────────────────────────────────────────

    def _build_header(self, title: str, subtitle: str):
        bg = COLORS["bg_card"]
        hdr = tk.Frame(self, bg=bg,
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
        hdr.pack(fill=tk.X)

        inner = tk.Frame(hdr, bg=bg)
        inner.pack(fill=tk.X, padx=SPACING[6], pady=SPACING[3])

        text_col = tk.Frame(inner, bg=bg)
        text_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(text_col, text=title, font=FONTS["title"],
                 bg=bg, fg=COLORS["text"]).pack(anchor=tk.W)
        if subtitle:
            tk.Label(text_col, text=subtitle, font=FONTS["small"],
                     bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)

        close = tk.Label(inner, text="✕", font=FONTS["subtitle"],
                         bg=bg, fg=COLORS["text_muted"], cursor="hand2")
        close.pack(side=tk.RIGHT)
        close.bind("<Button-1>", lambda e: self.destroy())

        divider_line(hdr).pack(fill=tk.X)

    # ── hooks ─────────────────────────────────────────────────────────

    def _build_body(self, parent):
        """Sobrescreva para preencher o corpo do modal."""

    def _build_footer(self, left: tk.Frame, right: tk.Frame):
        """Sobrescreva para adicionar botões de ação."""

    # ── posicionamento ────────────────────────────────────────────────

    def _center_and_show(self):
        self.update_idletasks()
        w = self.WIDTH
        h = min(self.winfo_reqheight(), int(self.winfo_screenheight() * 0.90))
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        x = (sx - w) // 2
        y = max(0, (sy - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()

    def _recalc_height(self):
        self.update_idletasks()
        w = self.WIDTH
        h = min(self.winfo_reqheight(), int(self.winfo_screenheight() * 0.90))
        self.geometry(f"{w}x{h}+{self.winfo_x()}+{self.winfo_y()}")
