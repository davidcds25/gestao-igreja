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


# ══════════════════════════════════════════════════════════════════════════
# StyledDialog — base para os novos modais (User, PasswordReset, Confirm)
# ══════════════════════════════════════════════════════════════════════════

class StyledDialog:
    """Toplevel customizada que serve de base para modais do app."""

    def __init__(self, parent, *,
                 eyebrow: str,
                 icon: str = None,
                 title: str,
                 subtitle: str = None,
                 width: int = 680,
                 height: int = None):

        self.parent = parent
        self.eyebrow = eyebrow
        self.icon = icon
        self.title_text = title
        self.subtitle = subtitle
        self.result = None

        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.configure(bg=COLORS["bg_card"])
        self.win.transient(parent)
        self.win.protocol("WM_DELETE_WINDOW", self.cancel)
        self.win.resizable(False, False)

        self._configure_geometry(width, height)
        self.win.bind("<Escape>", lambda e: self.cancel())

        self._build_header()
        self._build_separator()
        # Footer must be packed BEFORE body so side=BOTTOM claims its space
        # before body expand=True fills everything.
        self._build_footer_shell()
        self.body_frame = tk.Frame(self.win, bg=COLORS["bg_card"])
        self.body_frame.pack(fill=tk.BOTH, expand=True,
                             padx=SPACING[6] + SPACING[1],
                             pady=(SPACING[5], SPACING[5]))
        self._build_body(self.body_frame)

        self.win.update_idletasks()
        self.win.grab_set()
        self.win.focus_set()

    def _configure_geometry(self, width, height):
        self.win.geometry(f"{width}x{height}" if height else f"{width}x600")
        self.win.update_idletasks()
        try:
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - (height or 600)) // 3
            self.win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

    def _build_header(self):
        header = tk.Frame(self.win, bg=COLORS["bg_card_raised"])
        header.pack(fill=tk.X)

        inner = tk.Frame(header, bg=COLORS["bg_card_raised"])
        inner.pack(fill=tk.X, padx=SPACING[6], pady=(SPACING[5], SPACING[4]))

        if self.icon:
            icon_box = tk.Frame(inner, bg=COLORS["bg_dark"],
                                highlightbackground=COLORS["divider"],
                                highlightthickness=1,
                                width=38, height=38)
            icon_box.pack(side=tk.LEFT, anchor=tk.N)
            icon_box.pack_propagate(False)
            tk.Label(icon_box, text=self.icon,
                     font=(FONTS["body"][0], 14),
                     bg=COLORS["bg_dark"], fg=COLORS["text"]
                     ).place(relx=0.5, rely=0.5, anchor="center")

        text_col = tk.Frame(inner, bg=COLORS["bg_card_raised"])
        text_col.pack(side=tk.LEFT, fill=tk.X, expand=True,
                      padx=(SPACING[3] if self.icon else 0, SPACING[3]))

        tk.Label(text_col, text="    ".join(list(self.eyebrow.upper())),
                 font=FONTS["section"],
                 bg=COLORS["bg_card_raised"], fg=COLORS["text_muted"]
                 ).pack(anchor=tk.W)

        tk.Label(text_col, text=self.title_text,
                 font=(FONTS["body"][0], 16, "bold"),
                 bg=COLORS["bg_card_raised"], fg=COLORS["text"]
                 ).pack(anchor=tk.W, pady=(2, 0))

        if self.subtitle:
            tk.Label(text_col, text=self.subtitle,
                     font=FONTS["small"],
                     bg=COLORS["bg_card_raised"], fg=COLORS["text_muted"]
                     ).pack(anchor=tk.W, pady=(2, 0))

        close_btn = tk.Label(inner, text="✕",
                             font=(FONTS["body"][0], 11),
                             bg=COLORS["bg_card_raised"],
                             fg=COLORS["text_muted"],
                             padx=10, pady=4,
                             borderwidth=1, relief=tk.SOLID,
                             cursor="hand2")
        close_btn.configure(highlightbackground=COLORS["divider"])
        close_btn.pack(side=tk.RIGHT, anchor=tk.N)
        close_btn.bind("<Button-1>", lambda e: self.cancel())

    def _build_separator(self):
        tk.Frame(self.win, bg=COLORS["divider"], height=1).pack(fill=tk.X)

    def _build_footer_shell(self):
        footer = tk.Frame(self.win, bg=COLORS["bg_card_raised"])
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        # Separator sits just above the footer (also bottom-anchored)
        tk.Frame(self.win, bg=COLORS["divider"], height=1).pack(
            fill=tk.X, side=tk.BOTTOM)

        inner = tk.Frame(footer, bg=COLORS["bg_card_raised"])
        inner.pack(fill=tk.X, padx=SPACING[6], pady=SPACING[3])

        self.footer_left = tk.Frame(inner, bg=COLORS["bg_card_raised"])
        self.footer_left.pack(side=tk.LEFT)

        self.footer_right = tk.Frame(inner, bg=COLORS["bg_card_raised"])
        self.footer_right.pack(side=tk.RIGHT)

        self._build_footer(self.footer_left, self.footer_right)

    def _build_body(self, parent):
        raise NotImplementedError

    def _build_footer(self, left, right):
        raise NotImplementedError

    def cancel(self):
        self.result = None
        self.win.grab_release()
        self.win.destroy()

    def close_with(self, value):
        self.result = value
        self.win.grab_release()
        self.win.destroy()

    def show(self):
        self.parent.wait_window(self.win)
        return self.result


# ══════════════════════════════════════════════════════════════════════════
# Atoms reutilizáveis para modais (StyledDialog)
# ══════════════════════════════════════════════════════════════════════════

def modal_field(parent, *, label: str, required: bool = False, hint: str = None):
    wrap = tk.Frame(parent, bg=parent["bg"])
    head = tk.Frame(wrap, bg=parent["bg"])
    head.pack(fill=tk.X, pady=(0, SPACING[1] + 2))

    label_text = tk.Frame(head, bg=parent["bg"])
    label_text.pack(side=tk.LEFT)
    tk.Label(label_text, text=label,
             font=FONTS["body_strong"],
             bg=parent["bg"], fg=COLORS["text"]
             ).pack(side=tk.LEFT)
    if required:
        tk.Label(label_text, text="  *",
                 font=FONTS["body_strong"],
                 bg=parent["bg"], fg=COLORS["danger"]
                 ).pack(side=tk.LEFT)
    if hint:
        tk.Label(head, text=hint,
                 font=FONTS["small"],
                 bg=parent["bg"], fg=COLORS["text_muted"]
                 ).pack(side=tk.RIGHT)
    return wrap


def modal_input(parent, *, var, placeholder: str = "", icon: str = None,
                show: str = None):
    box = tk.Frame(parent, bg=COLORS["input_bg"],
                   highlightbackground=COLORS["divider"],
                   highlightcolor=COLORS["accent"],
                   highlightthickness=1, bd=0)
    if icon:
        tk.Label(box, text=icon,
                 font=(FONTS["body"][0], 12),
                 bg=COLORS["input_bg"], fg=COLORS["text_muted"],
                 padx=10).pack(side=tk.LEFT)

    # _disp is internal so placeholder text never leaks into the caller's `var`
    _disp = tk.StringVar()
    entry = tk.Entry(box, textvariable=_disp,
                     font=FONTS["body"],
                     bg=COLORS["input_bg"],
                     fg=COLORS["text"],
                     insertbackground=COLORS["text"],
                     relief=tk.FLAT, bd=0, show=show or "")
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
               ipady=6, padx=(0 if icon else 10, 10))

    _ph = [False]  # True while placeholder is displayed

    init = var.get()
    if init:
        _disp.set(init)
        if show:
            entry.configure(show=show)
    elif placeholder:
        _ph[0] = True
        _disp.set(placeholder)
        entry.configure(fg=COLORS["text_very_dim"], show="")

    def _sync(*_):
        if not _ph[0]:
            var.set(_disp.get())

    _disp.trace_add("write", _sync)

    def _focus_in(_e):
        if _ph[0]:
            _ph[0] = False
            _disp.set("")
            entry.configure(fg=COLORS["text"])
            if show:
                entry.configure(show=show)

    def _focus_out(_e):
        if not _disp.get():
            if placeholder:
                _ph[0] = True
                _disp.set(placeholder)
                entry.configure(fg=COLORS["text_very_dim"], show="")
            var.set("")

    entry.bind("<FocusIn>", _focus_in)
    entry.bind("<FocusOut>", _focus_out)

    box._entry = entry
    return box


def modal_button(parent, *, text: str, kind: str = "primary",
                 icon: str = None, command=None):
    palette = {
        "primary":      (COLORS["accent"],          COLORS["bg_dark"], COLORS["accent"]),
        "ghost":        (COLORS["input_bg"],         COLORS["text"],    COLORS["divider"]),
        "danger":       (COLORS["bg_card_raised"],   COLORS["danger"],  COLORS["divider"]),
        "danger_solid": (COLORS["danger"],           "#ffffff",         COLORS["danger"]),
    }
    bg, fg, bd = palette.get(kind, palette["primary"])
    btn = tk.Button(parent,
                    text=(f"{icon}  {text}" if icon else text),
                    font=FONTS["btn"],
                    bg=bg, fg=fg,
                    activebackground=bg, activeforeground=fg,
                    relief=tk.FLAT, bd=0,
                    padx=SPACING[4], pady=SPACING[2] + 2,
                    cursor="hand2",
                    command=command)
    btn.configure(highlightbackground=bd, highlightthickness=1)
    return btn


def modal_pill_radio(parent, *, var: tk.StringVar, options: list):
    box = tk.Frame(parent, bg=COLORS["input_bg"],
                   highlightbackground=COLORS["divider"],
                   highlightthickness=1, bd=0)
    inner = tk.Frame(box, bg=COLORS["input_bg"])
    inner.pack(fill=tk.X, padx=3, pady=3)

    pills = []

    def _paint():
        sel = var.get()
        for frame, lbl, opt in pills:
            active = opt["value"] == sel
            tint = opt.get("tint", COLORS["accent"])
            fg = opt.get("fg", COLORS["bg_dark"])
            bg = tint if active else COLORS["input_bg"]
            fgc = fg if active else COLORS["text_dim"]
            frame.configure(bg=bg)
            lbl.configure(bg=bg, fg=fgc)

    def _make_click(value):
        def _click(_e=None):
            var.set(value)
            _paint()
        return _click

    for opt in options:
        f = tk.Frame(inner, bg=COLORS["input_bg"], cursor="hand2")
        f.pack(side=tk.LEFT, fill=tk.X, expand=True,
               padx=(0, 2 if opt is not options[-1] else 0))
        lbl = tk.Label(f, text=opt["label"],
                       font=FONTS["body_strong"],
                       bg=COLORS["input_bg"], fg=COLORS["text_dim"],
                       padx=SPACING[3], pady=SPACING[2],
                       cursor="hand2")
        lbl.pack(fill=tk.X)
        for w in (f, lbl):
            w.bind("<Button-1>", _make_click(opt["value"]))
        pills.append((f, lbl, opt))

    _paint()
    box._pills = pills
    box._repaint = _paint
    return box


def modal_password_input(parent, *, var: tk.StringVar, placeholder: str = ""):
    box = tk.Frame(parent, bg=COLORS["input_bg"],
                   highlightbackground=COLORS["divider"],
                   highlightcolor=COLORS["accent"],
                   highlightthickness=1, bd=0)

    tk.Label(box, text="🔒",
             font=(FONTS["body"][0], 12),
             bg=COLORS["input_bg"], fg=COLORS["text_muted"],
             padx=10).pack(side=tk.LEFT)

    entry = tk.Entry(box, textvariable=var,
                     font=FONTS["body"],
                     bg=COLORS["input_bg"],
                     fg=COLORS["text"],
                     insertbackground=COLORS["text"],
                     relief=tk.FLAT, bd=0, show="•")
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))

    state = {"show": False}
    eye = tk.Label(box, text="⊘",
                   font=(FONTS["body"][0], 12),
                   bg=COLORS["input_bg"], fg=COLORS["text_muted"],
                   padx=10, cursor="hand2")
    eye.pack(side=tk.RIGHT)

    def _toggle(_e=None):
        state["show"] = not state["show"]
        if state["show"]:
            entry.configure(show="")
            eye.configure(text="👁", fg=COLORS["accent"])
        else:
            entry.configure(show="•")
            eye.configure(text="⊘", fg=COLORS["text_muted"])

    eye.bind("<Button-1>", _toggle)

    if placeholder and not var.get():
        entry.configure(show="")
        entry.insert(0, placeholder)
        entry.configure(fg=COLORS["text_very_dim"])

        def _focus_in(_e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(fg=COLORS["text"])
                entry.configure(show="" if state["show"] else "•")

        def _focus_out(_e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(fg=COLORS["text_very_dim"], show="")

        entry.bind("<FocusIn>", _focus_in)
        entry.bind("<FocusOut>", _focus_out)

    box._entry = entry
    return box


def password_score(pw: str) -> int:
    if not pw:
        return 0
    s = 0
    if len(pw) >= 6:
        s += 1
    if len(pw) >= 10:
        s += 1
    has_upper = any(c.isupper() for c in pw)
    has_lower = any(c.islower() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_sym   = any(not c.isalnum() for c in pw)
    if has_upper and has_lower:
        s += 1
    if has_digit and has_sym:
        s += 1
    return min(s, 4)


def modal_password_strength(parent, *, var: tk.StringVar):
    row = tk.Frame(parent, bg=parent["bg"])

    bars_frame = tk.Frame(row, bg=parent["bg"])
    bars_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

    bars = []
    for i in range(4):
        b = tk.Frame(bars_frame, bg=COLORS["divider"], height=4)
        b.pack(side=tk.LEFT, fill=tk.X, expand=True,
               padx=(0, 4 if i < 3 else 0))
        b.pack_propagate(False)
        bars.append(b)

    label = tk.Label(row, text="Informe uma senha",
                     font=FONTS["small_bold"],
                     bg=parent["bg"], fg=COLORS["text_muted"],
                     width=14, anchor=tk.E)
    label.pack(side=tk.RIGHT, padx=(SPACING[2], 0))

    _LABELS = ["Informe uma senha", "Muito fraca", "Fraca", "Boa", "Forte"]
    _COLORS = [COLORS["text_muted"], COLORS["danger"], COLORS["warning"],
               COLORS["accent"], COLORS["success"]]

    def _redraw(*_):
        score = password_score(var.get())
        for i, b in enumerate(bars):
            b.configure(bg=_COLORS[score] if i < score else COLORS["divider"])
        label.configure(text=_LABELS[score], fg=_COLORS[score])

    var.trace_add("write", _redraw)
    _redraw()
    return row


def modal_avatar_preview(parent, *, name_var: tk.StringVar,
                         color_var: tk.StringVar, size: int = 38):
    canvas = tk.Canvas(parent, width=size, height=size,
                       bg=parent["bg"], highlightthickness=0, bd=0)

    def _initials(name):
        parts = (name or "").strip().split()
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][:1] + parts[-1][:1]).upper()

    def _redraw(*_):
        canvas.delete("all")
        c = color_var.get() or COLORS["accent2"]
        canvas.create_oval(1, 1, size - 1, size - 1, fill=c, outline="")
        canvas.create_text(size / 2, size / 2,
                           text=_initials(name_var.get()),
                           font=(FONTS["body"][0], int(size * 0.32), "bold"),
                           fill="#ffffff")

    name_var.trace_add("write", _redraw)
    color_var.trace_add("write", _redraw)
    _redraw()
    return canvas
