"""
design/perfil.py
================
PerfilMenu  — dropdown customizado do chip de usuário no header
PerfilModal — modal "Meu perfil" frameless e arrastável
"""

import tkinter as tk
from .ui import COLORS, SPACING, FONTS
from .ui.helpers import rounded_rect_canvas, initials_of

def _nivel_color(nivel: str) -> str:
    return {
        "Admin":       COLORS.get("accent",  "#00d4ff"),
        "Coordenador": "#0891b2",
        "Usuário":     COLORS.get("purple",  "#9b59b6"),
    }.get(nivel, COLORS.get("accent2", "#00d4ff"))


def _avatar(parent, nome: str, nivel: str, size: int, bg: str) -> tk.Canvas:
    color = _nivel_color(nivel)
    cv = rounded_rect_canvas(parent, size, size, radius=6, fill=color, bg=bg)
    cv.create_text(
        size / 2, size / 2,
        text=initials_of(nome),
        fill="#ffffff",
        font=(FONTS["body"][0], int(size * 0.36), "bold"),
    )
    return cv


# ──────────────────────────────────────────────────────────────────────
# Ícones em Canvas (sem dependências externas)
# ──────────────────────────────────────────────────────────────────────

def _menu_icon(parent, kind: str, fg: str, bg: str) -> tk.Canvas:
    """Ícone 16×16 para itens do dropdown."""
    cv = tk.Canvas(parent, width=16, height=16,
                   bg=bg, highlightthickness=0, bd=0, cursor="hand2")
    lw = 1.5
    if kind == "person":
        cv.create_oval(5, 1, 11, 7, outline=fg, width=lw, fill="")
        cv.create_arc(1, 8, 15, 18, start=0, extent=180,
                      outline=fg, width=lw, fill="", style="arc")
    elif kind == "edit":
        cv.create_line(3, 13, 11, 5, fill=fg, width=lw)
        cv.create_line(11, 5, 13, 3, fill=fg, width=lw)
        cv.create_line(13, 3, 15, 5, fill=fg, width=lw)
        cv.create_line(15, 5, 13, 7, fill=fg, width=lw)
        cv.create_line(13, 7, 11, 5, fill=fg, width=lw)
        cv.create_line(2, 14, 3, 13, fill=fg, width=lw)
    elif kind == "logout":
        cv.create_line(8, 3, 3, 3, 3, 13, 8, 13, fill=fg, width=lw)
        cv.create_line(8, 8, 14, 8, fill=fg, width=lw)
        cv.create_line(12, 6, 14, 8, 12, 10, fill=fg, width=lw)
    elif kind == "theme":
        import math
        # Círculo central (sol)
        cv.create_oval(5, 5, 11, 11, outline=fg, width=lw, fill="")
        # 8 raios
        for i in range(8):
            rad = math.radians(i * 45)
            x1 = round(8 + 5.5 * math.cos(rad))
            y1 = round(8 + 5.5 * math.sin(rad))
            x2 = round(8 + 7.5 * math.cos(rad))
            y2 = round(8 + 7.5 * math.sin(rad))
            cv.create_line(x1, y1, x2, y2, fill=fg, width=lw)
    return cv


def _field_icon(parent, kind: str, fg: str, bg: str) -> tk.Canvas:
    """Ícone 16×16 para campos do modal."""
    cv = tk.Canvas(parent, width=16, height=16,
                   bg=bg, highlightthickness=0, bd=0)
    lw = 1.5
    if kind == "email":
        cv.create_rectangle(1, 3, 15, 13, outline=fg, width=lw, fill="")
        cv.create_line(1, 3, 8, 9, 15, 3, fill=fg, width=lw)
    elif kind == "nivel":
        cv.create_polygon(8, 2, 14, 5, 14, 10, 8, 14, 2, 10, 2, 5,
                          outline=fg, fill="", width=lw)
    elif kind == "status":
        cv.create_oval(1, 1, 15, 15, outline=fg, width=lw, fill="")
        cv.create_line(4, 8, 7, 11, 12, 5, fill=fg, width=lw)
    return cv


# ══════════════════════════════════════════════════════════════════════
# DROPDOWN
# ══════════════════════════════════════════════════════════════════════

class PerfilMenu:
    def __init__(self, parent, *, user: dict, on_edit=None, on_logout=None):
        self.parent        = parent
        self.user          = user
        self.on_edit       = on_edit
        self.on_logout     = on_logout
        self._win          = None
        self._press_bid    = None   # funcid do bind_all ativo

    def toggle(self, anchor: tk.Widget):
        if self._win and self._win.winfo_exists():
            self._close()
            return
        self._open(anchor)

    # ── internals ────────────────────────────────────────────────────

    def _open(self, anchor: tk.Widget):
        root = self.parent.winfo_toplevel()
        win  = tk.Toplevel(root)
        win.overrideredirect(True)
        win.configure(bg=COLORS["divider"])
        win.attributes("-topmost", True)
        self._win = win

        self._build(win)
        win.update_idletasks()

        w  = win.winfo_reqwidth()
        ax = anchor.winfo_rootx()
        ay = anchor.winfo_rooty() + anchor.winfo_height() + 4
        # alinha a direita do menu com a direita do anchor
        x  = ax + anchor.winfo_width() - w
        win.geometry(f"+{max(x, 0)}+{ay}")

        # fecha ao clicar fora; atraso de 100ms evita fechar no próprio open
        def _check_outside(event):
            if not (self._win and self._win.winfo_exists()):
                self._unbind_press(root)
                return
            wx = self._win.winfo_rootx()
            wy = self._win.winfo_rooty()
            ww = self._win.winfo_width()
            wh = self._win.winfo_height()
            if not (wx <= event.x_root < wx + ww and
                    wy <= event.y_root < wy + wh):
                self._unbind_press(root)
                self._close()

        def _bind():
            self._press_bid = root.bind_all("<ButtonPress-1>", _check_outside, "+")

        win.after(100, _bind)

    def _build(self, win):
        bg = COLORS["bg_card"]

        # 1px borda = cor do Toplevel (divider)
        card = tk.Frame(win, bg=bg)
        card.pack(padx=1, pady=1)

        # ── Itens ─────────────────────────────────────────────────────
        self._item(card, "Ver perfil",     "person", self._open_modal)
        self._item(card, "Alterar perfil", "edit",   self._do_edit)

        tk.Frame(card, bg=COLORS["divider"], height=1).pack(fill=tk.X)

        from .ui.tokens import get_theme
        theme_label = "Tema claro ☀" if get_theme() == "dark" else "Tema escuro 🌙"
        self._item(card, theme_label, "theme", self._toggle_theme)

        tk.Frame(card, bg=COLORS["divider"], height=1).pack(fill=tk.X)

        self._item(card, "Sair", "logout", self._do_logout, danger=True)

    def _item(self, parent, label, icon_kind, command, danger=False):
        bg_normal  = COLORS["bg_card"]
        bg_hover   = COLORS["bg_card_raised"]
        bg_danger  = "#2a1818"
        bg_dhover  = "#3d1e1e"
        fg_col     = COLORS["danger"] if danger else COLORS["text"]
        icon_fg    = COLORS["danger"] if danger else COLORS["text_dim"]
        base_bg    = bg_danger if danger else bg_normal

        row = tk.Frame(parent, bg=base_bg, cursor="hand2")
        row.pack(fill=tk.X, padx=SPACING[1], pady=1)

        ic = _menu_icon(row, icon_kind, fg=icon_fg, bg=base_bg)
        ic.pack(side=tk.LEFT, padx=(SPACING[3], SPACING[2]), pady=SPACING[2])

        lbl = tk.Label(row, text=label, font=FONTS["body"],
                       bg=base_bg, fg=fg_col, anchor=tk.W,
                       cursor="hand2", pady=SPACING[2])
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING[4]))

        hover_bg = bg_dhover if danger else bg_hover

        def _enter(_):
            for w in (row, ic, lbl):
                w.configure(bg=hover_bg)

        def _leave(_):
            for w in (row, ic, lbl):
                w.configure(bg=base_bg)

        for w in (row, ic, lbl):
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)
            w.bind("<Button-1>", lambda e, cmd=command: cmd())

    def _open_modal(self):
        self._close()
        PerfilModal(self.parent, user=self.user, on_edit=self.on_edit)

    def _do_edit(self):
        self._close()
        if self.on_edit:
            self.on_edit()

    def _toggle_theme(self):
        self._close()
        from .ui.tokens import get_theme
        from core.prefs import set_pref
        import os, sys

        new_theme = "light" if get_theme() == "dark" else "dark"
        nome = "claro" if new_theme == "light" else "escuro"
        set_pref("theme", new_theme)

        root = self.parent.winfo_toplevel()
        from tkinter import messagebox
        reiniciar = messagebox.askyesno(
            "Trocar tema",
            f"Tema {nome} salvo.\n\nO tema será aplicado após reiniciar. Reiniciar agora?",
            parent=root,
        )
        if reiniciar:
            import subprocess
            subprocess.Popen([sys.executable] + sys.argv)
            root.destroy()

    def _do_logout(self):
        self._close()
        if self.on_logout:
            self.on_logout()

    def _unbind_press(self, root=None):
        if self._press_bid:
            try:
                r = root or self.parent.winfo_toplevel()
                r.unbind("<ButtonPress-1>", self._press_bid)
            except Exception:
                pass
            self._press_bid = None

    def _close(self):
        if self._win and self._win.winfo_exists():
            self._unbind_press()
            self._win.destroy()
        self._win = None


# ══════════════════════════════════════════════════════════════════════
# MODAL VER PERFIL
# ══════════════════════════════════════════════════════════════════════

class PerfilModal:
    WIDTH  = 360

    def __init__(self, parent, *, user: dict, on_edit=None):
        self.parent  = parent
        self.user    = user
        self.on_edit = on_edit
        self._drag   = (0, 0)

        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.configure(bg=COLORS["divider"])
        self.win.attributes("-topmost", True)
        self.win.resizable(False, False)

        self._build()
        self._center()
        self.win.grab_set()
        self.win.focus_set()
        self.win.bind("<Escape>", lambda e: self.win.destroy())

    def _center(self):
        self.win.update_idletasks()
        h  = self.win.winfo_reqheight()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x  = (sw - self.WIDTH) // 2
        y  = (sh - h) // 2
        self.win.geometry(f"{self.WIDTH}x{h}+{x}+{y}")

    def _build(self):
        bg  = COLORS["bg_card"]
        bgr = COLORS["bg_card_raised"]
        div = COLORS["divider"]
        sp  = SPACING

        # 1px borda externa via cor do Toplevel (divider)
        card = tk.Frame(self.win, bg=bg)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        # ── Barra de título arrastável ────────────────────────────────
        tb = tk.Frame(card, bg=bgr, height=44)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)

        tb_in = tk.Frame(tb, bg=bgr)
        tb_in.pack(fill=tk.BOTH, expand=True, padx=sp[4])

        tk.Label(tb_in, text="Meu perfil",
                 font=FONTS["body_strong"],
                 bg=bgr, fg=COLORS["text"]
                 ).pack(side=tk.LEFT, pady=sp[3])

        close = tk.Label(tb_in, text="✕",
                         font=(FONTS["body"][0], 11),
                         bg=bgr, fg=COLORS["text_muted"],
                         padx=8, pady=4, cursor="hand2")
        close.pack(side=tk.RIGHT, pady=sp[2])
        close.bind("<Button-1>", lambda e: self.win.destroy())

        for w in (tb, tb_in):
            w.bind("<Button-1>",  self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)

        # ── Separador ─────────────────────────────────────────────────
        tk.Frame(card, bg=div, height=1).pack(fill=tk.X)

        # ── Avatar + nome + badge ─────────────────────────────────────
        av_sec = tk.Frame(card, bg=bg)
        av_sec.pack(fill=tk.X, padx=sp[5], pady=(sp[5], sp[3]))

        nivel = self.user.get("nivel", "")
        _avatar(av_sec, self.user["nome"], nivel, 52, bg
                ).pack(side=tk.LEFT, padx=(0, sp[3]))

        av_info = tk.Frame(av_sec, bg=bg)
        av_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(av_info, text=self.user["nome"],
                 font=(FONTS["body"][0], 14, "bold"),
                 bg=bg, fg=COLORS["text"], anchor=tk.W
                 ).pack(fill=tk.X)

        badge_row = tk.Frame(av_info, bg=bg)
        badge_row.pack(anchor=tk.W, pady=(3, 0))
        nc = _nivel_color(nivel)
        tk.Label(badge_row, text="●",
                 font=(FONTS["body"][0], 7),
                 bg=bg, fg=nc
                 ).pack(side=tk.LEFT, padx=(0, 4))
        label_nivel = "ADMINISTRADOR" if nivel == "Admin" else nivel.upper()
        tk.Label(badge_row, text=label_nivel,
                 font=FONTS["tiny_bold"],
                 bg=bg, fg=COLORS["text_muted"]
                 ).pack(side=tk.LEFT)

        # ── Separador ─────────────────────────────────────────────────
        tk.Frame(card, bg=div, height=1).pack(fill=tk.X, padx=sp[3], pady=(sp[2], 0))

        # ── Campos ────────────────────────────────────────────────────
        fields = tk.Frame(card, bg=bg)
        fields.pack(fill=tk.X, padx=sp[5], pady=sp[4])

        self._field(fields, "email",  "EMAIL",  self.user.get("email", "—"))
        self._field(fields, "nivel",  "NÍVEL",  nivel)
        self._field(fields, "status", "STATUS", "Ativo")

        # ── Separador ─────────────────────────────────────────────────
        tk.Frame(card, bg=div, height=1).pack(fill=tk.X)

        # ── Footer ────────────────────────────────────────────────────
        foot = tk.Frame(card, bg=bg)
        foot.pack(fill=tk.X, padx=sp[4], pady=sp[3])

        from .modals.base import modal_button
        modal_button(foot, text="Editar perfil", kind="primary",
                     command=self._do_edit
                     ).pack(side=tk.RIGHT)
        modal_button(foot, text="Fechar", kind="ghost",
                     command=self.win.destroy
                     ).pack(side=tk.RIGHT, padx=(0, sp[2]))

    def _field(self, parent, icon_kind: str, label: str, value: str):
        bg = COLORS["bg_card"]
        row = tk.Frame(parent, bg=bg)
        row.pack(fill=tk.X, pady=(0, SPACING[3]))

        _field_icon(row, icon_kind, fg=COLORS["text_muted"], bg=bg
                    ).pack(side=tk.LEFT, padx=(0, SPACING[3]), pady=(4, 0), anchor=tk.N)

        col = tk.Frame(row, bg=bg)
        col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(col, text=label,
                 font=FONTS["tiny"],
                 bg=bg, fg=COLORS["text_muted"], anchor=tk.W
                 ).pack(fill=tk.X)
        tk.Label(col, text=value,
                 font=FONTS["body_strong"],
                 bg=bg, fg=COLORS["text"], anchor=tk.W
                 ).pack(fill=tk.X)

    def _do_edit(self):
        self.win.destroy()
        if self.on_edit:
            self.on_edit()

    def _drag_start(self, e):
        self._drag = (e.x_root - self.win.winfo_x(),
                      e.y_root - self.win.winfo_y())

    def _drag_move(self, e):
        dx, dy = self._drag
        self.win.geometry(f"+{e.x_root - dx}+{e.y_root - dy}")
