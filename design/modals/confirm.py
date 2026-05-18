"""
modals/confirm.py
=================
Modal de confirmação genérico — substitui tkinter.messagebox.askyesno
com o mesmo estilo visual do app.

VARIANTES:
    "danger"  — vermelho, botão sólido vermelho
    "warning" — dourado, botão primary
    "info"    — accent, botão primary
"""

import tkinter as tk

from ..ui import COLORS, SPACING, FONTS
from .base import StyledDialog, modal_button


_VARIANTS = {
    "danger":  {"tint": "danger",  "icon": "🗑", "eyebrow": "Excluir",   "btn": "danger_solid"},
    "warning": {"tint": "warning", "icon": "⚠",  "eyebrow": "Atenção",   "btn": "primary"},
    "info":    {"tint": "accent",  "icon": "ℹ",  "eyebrow": "Confirmar", "btn": "primary"},
}


class ConfirmModal(StyledDialog):
    def __init__(self, parent, *,
                 title: str,
                 message: str,
                 detail: str = None,
                 variant: str = "danger",
                 icon: str = None,
                 eyebrow: str = None,
                 confirm_label: str = "Confirmar",
                 cancel_label: str = "Cancelar",
                 on_confirm=None):
        self.variant = variant
        self.message = message
        self.detail = detail
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.on_confirm = on_confirm

        v = _VARIANTS.get(variant, _VARIANTS["danger"])
        self._v = v
        self._tint_color = COLORS[v["tint"]]

        super().__init__(
            parent,
            eyebrow=eyebrow or v["eyebrow"],
            icon=None,
            title=title,
            subtitle=None,
            width=460,
            height=None,
        )

        self._mount_colored_icon(icon or v["icon"], self._tint_color)
        self.win.bind("<Return>", lambda e: self._handle_confirm())

    def _mount_colored_icon(self, icon, tint):
        for child in self.win.winfo_children():
            if child.cget("bg") == COLORS["bg_card_raised"]:
                inner = child.winfo_children()[0]
                cv = tk.Canvas(inner, width=32, height=32,
                               bg=COLORS["bg_card_raised"],
                               highlightthickness=0, bd=0)
                cv.create_oval(1, 1, 31, 31,
                               fill=COLORS["bg_card"], outline=tint, width=1)
                cv.create_text(16, 16, text=icon,
                               font=(FONTS["body"][0], 13),
                               fill=tint)
                cv.pack(side=tk.LEFT, anchor=tk.N, padx=(0, SPACING[3]),
                        before=inner.winfo_children()[0])
                break

    def _build_body(self, parent):
        tk.Label(parent, text=self.message,
                 font=FONTS["body"],
                 bg=parent["bg"], fg=COLORS["text"],
                 wraplength=400, justify=tk.LEFT, anchor=tk.W
                 ).pack(fill=tk.X, pady=(0, SPACING[3] if self.detail else 0))

        if self.detail:
            detail_box = tk.Frame(parent, bg=COLORS["bg_dark"],
                                  highlightbackground=COLORS["divider"],
                                  highlightthickness=1)
            detail_box.pack(fill=tk.X)
            tk.Label(detail_box, text=self.detail,
                     font=FONTS["small"],
                     bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                     wraplength=380, justify=tk.LEFT, anchor=tk.W,
                     padx=SPACING[3], pady=SPACING[3]
                     ).pack(fill=tk.X)

    def _build_footer(self, left, right):
        modal_button(right, text=self.cancel_label, kind="ghost",
                     command=self.cancel
                     ).pack(side=tk.LEFT, padx=(0, SPACING[2]))

        confirm_icon = self._v["icon"]
        modal_button(right, text=self.confirm_label,
                     kind=self._v["btn"],
                     icon=confirm_icon,
                     command=self._handle_confirm
                     ).pack(side=tk.LEFT)

    def _handle_confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.close_with(True)


def ask_confirm(parent, *, title: str, message: str,
                detail: str = None,
                variant: str = "danger",
                confirm_label: str = "Confirmar",
                cancel_label: str = "Cancelar",
                icon: str = None) -> bool:
    modal = ConfirmModal(parent,
                         title=title, message=message, detail=detail,
                         variant=variant,
                         confirm_label=confirm_label,
                         cancel_label=cancel_label,
                         icon=icon)
    result = modal.show()
    return bool(result)
