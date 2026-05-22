"""
ui/components.py
================
Biblioteca completa de componentes reutilizáveis. Cada função aqui
mapeia 1:1 para um pedaço visual do mockup HTML.

CONVENÇÃO:
  - Todas as funções recebem `parent` como primeiro argumento.
  - Todas devolvem o widget criado (ou um dict com sub-widgets úteis).
  - NENHUMA função chama .pack()/.grid() — a página que monta é quem decide
    como posicionar. Isso evita acoplamento.

Mapeamento ↔ mockup React (screens.jsx / dashboard.jsx):

    Cross()           → cross_icon()
    Initials          → initials_badge()
    Header            → header_bar()
    Sidebar/NavItem   → sidebar(), _nav_item()
    SectionLabel      → section_label()
    Badge             → badge()
    Pill              → pill()
    Btn               → button()
    IconBtn           → icon_button()
    Select            → select()
    Tabs              → tabs()
    EmptyState        → empty_state()
    MiniStat          → mini_stat()
    BigStat           → big_stat()
    BarChart          → bar_chart()
    Field/TextInput   → field(), text_input()
    Textarea          → textarea()
    ConnectionCard    → connection_card()
    EventCard         → event_card()       (dashboard)
    ActivityRow       → activity_row()     (tela de atividades)
    MemberCard        → member_card()
    VerseCard         → verse_card()
    QuickActions      → quick_actions()
    ScreenHeader      → screen_header()
"""

import tkinter as tk
from tkinter import ttk

from .tokens import (
    COLORS, SPACING, FONTS,
    STATUS_COLORS,
    SIDEBAR_WIDTH, ACTIVE_RAIL_PX,
)
from .helpers import (
    rounded_rect_canvas, truncate, initials_of,
    lighten, darken, bind_hover,
)

try:
    from config import APP_NAME as _APP_NAME
except ImportError:
    _APP_NAME = "Sistema de Gestão"


# ══════════════════════════════════════════════════════════════════════
# 1. BUILDING BLOCKS — átomos
# ══════════════════════════════════════════════════════════════════════

def cross_icon(parent, size=14, color=None, bg=None):
    """A cruz cristã usada no logo e no card do versículo.

    Desenhada com Canvas rectangles (nunca SVG). 2px de espessura para
    tamanhos pequenos; cresce com size.
    """
    color = color or COLORS["accent"]
    bg = bg or parent["bg"]
    thickness = max(2, size // 6)
    cv = tk.Canvas(parent, width=size, height=size + 4,
                   bg=bg, highlightthickness=0, bd=0)
    # vertical
    cv.create_rectangle(
        size // 2 - thickness // 2, 0,
        size // 2 + (thickness + 1) // 2, size + 4,
        fill=color, outline="")
    # horizontal
    cv.create_rectangle(
        0, int(size * 0.32),
        size, int(size * 0.32) + thickness,
        fill=color, outline="")
    return cv


def initials_badge(parent, name: str, color: str, size: int = 36, bg=None):
    """Avatar quadrado com as iniciais. Use sempre que precisar mostrar
    uma pessoa antes de ter foto real."""
    bg = bg or parent["bg"]
    cv = rounded_rect_canvas(
        parent, size, size,
        radius=4, fill=color, bg=bg,
    )
    cv.create_text(
        size / 2, size / 2,
        text=initials_of(name),
        fill="#ffffff",
        font=(FONTS["body"][0], int(size * 0.4), "bold"),
    )
    return cv


# ══════════════════════════════════════════════════════════════════════
# 2. BOTÕES
# ══════════════════════════════════════════════════════════════════════

_BTN_STYLES = {
    "primary":   {"bg": "accent",   "fg": "bg_dark"},
    "secondary": {"bg": "accent2",  "fg": "text"},
    "success":   {"bg": "success",  "fg": "bg_dark"},
    "danger":    {"bg": "danger",   "fg": "text"},
    "ghost":     {"bg": "input_bg", "fg": "text"},
    "whatsapp":  {"bg": "whatsapp", "fg": "text"},
}


def button(parent, *, text: str, kind: str = "primary",
           icon: str = None, command=None, width: int = None):
    """Botão padrão. 5 kinds: primary, secondary, danger, ghost, whatsapp.

    Implementação simples (sem radius) — usa relief=FLAT e padding interno.
    Para versão com cantos arredondados, use button_rounded() abaixo.
    """
    s = _BTN_STYLES[kind]
    bg, fg = COLORS[s["bg"]], COLORS[s["fg"]]
    label = f"  {icon}   {text}  " if icon else f"  {text}  "
    btn = tk.Button(
        parent,
        text=label,
        font=FONTS["btn"],
        bg=bg, fg=fg,
        activebackground=lighten(bg, 0.12),
        activeforeground=fg,
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        command=command,
        padx=SPACING[3],
        pady=SPACING[2],
        width=width,
    )
    bind_hover(btn, normal_bg=bg, hover_bg=lighten(bg, 0.08))
    return btn


def icon_button(parent, *, icon: str, tooltip: str = "",
                color: str = None, command=None, size: int = 28):
    """Botão pequeno só com ícone — para ações inline em cards/linhas.

    Renderiza como um Label clicável (não Button) para ter mais controle
    do tamanho exato.
    """
    fg = color or COLORS["text_dim"]
    bg = COLORS["input_bg"]
    f = tk.Frame(parent, bg=bg, width=size, height=size,
                 highlightbackground=COLORS["divider"],
                 highlightthickness=1)
    f.pack_propagate(False)
    lbl = tk.Label(f, text=icon, bg=bg, fg=fg,
                   font=(FONTS["body"][0], int(size * 0.38)),
                   cursor="hand2")
    lbl.pack(expand=True)
    if command:
        for w in (f, lbl):
            w.bind("<Button-1>", lambda e: command())
    bind_hover(f, normal_bg=bg, hover_bg=lighten(bg, 0.12))
    bind_hover(lbl, normal_bg=bg, hover_bg=lighten(bg, 0.12))
    return f


# ══════════════════════════════════════════════════════════════════════
# 3. BADGES & PILLS
# ══════════════════════════════════════════════════════════════════════

def badge(parent, text: str, kind: str = None, bg=None, fg=None):
    """Badge pequeno UPPERCASE para status (Ativo, Planejado, etc).

    Passe `kind` com o nome do status para usar as cores de STATUS_COLORS,
    OU `bg`/`fg` para custom.
    """
    if kind and kind in STATUS_COLORS:
        bg, fg = STATUS_COLORS[kind]
    elif bg is None:
        bg, fg = COLORS["input_bg"], COLORS["text_dim"]
    lbl = tk.Label(
        parent,
        text=f"  {text.upper()}  ",
        font=FONTS["badge"],
        bg=bg, fg=fg,
        padx=SPACING[1], pady=2,
    )
    return lbl


def pill(parent, text: str, dot_color: str = None, text_color: str = None):
    """Indicador de estado com bolinha colorida + texto. Use em tabelas:

        pill(parent, "Ativo", dot_color=COLORS["success"])
    """
    text_color = text_color or COLORS["text_dim"]
    bg = parent["bg"]
    f = tk.Frame(parent, bg=bg)
    if dot_color:
        # bolinha — desenhada via Canvas (oval pequeno)
        cv = tk.Canvas(f, width=10, height=10, bg=bg,
                       highlightthickness=0, bd=0)
        cv.create_oval(1, 1, 9, 9, fill=dot_color, outline="")
        cv.pack(side=tk.LEFT, padx=(0, 6))
    tk.Label(f, text=text, font=FONTS["body"],
             bg=bg, fg=text_color).pack(side=tk.LEFT)
    return f


# ══════════════════════════════════════════════════════════════════════
# 4. INPUTS
# ══════════════════════════════════════════════════════════════════════

def field(parent, *, label: str, hint: str = None):
    """Container de um campo de formulário. Devolve um Frame onde você
    deve adicionar o input (text_input, textarea, etc) depois.

    Uso:
        wrap = field(parent, label="Telefone", hint="com DDD")
        wrap.pack(fill=tk.X, pady=SPACING[3])
        text_input(wrap, value="").pack(fill=tk.X)
    """
    wrap = tk.Frame(parent, bg=parent["bg"])
    row = tk.Frame(wrap, bg=parent["bg"])
    row.pack(fill=tk.X)
    tk.Label(row, text=label, font=FONTS["body_strong"],
             bg=parent["bg"], fg=COLORS["text"]).pack(side=tk.LEFT)
    if hint:
        tk.Label(row, text=hint, font=FONTS["small"],
                 bg=parent["bg"], fg=COLORS["text_muted"]).pack(side=tk.RIGHT)
    # gap
    tk.Frame(wrap, bg=parent["bg"], height=SPACING[1]).pack(fill=tk.X)
    return wrap


def text_input(parent, *, value: str = "", placeholder: str = ""):
    """Entry estilizado: bg input_bg, relief flat, ipady para altura."""
    var = tk.StringVar(value=value)
    e = tk.Entry(
        parent,
        textvariable=var,
        font=FONTS["body"],
        bg=COLORS["input_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief=tk.FLAT,
        bd=0,
    )
    e.configure(highlightthickness=1,
                highlightbackground=COLORS["divider"],
                highlightcolor=COLORS["accent"])
    # placeholder behavior
    if placeholder and not value:
        e.insert(0, placeholder)
        e.configure(fg=COLORS["text_very_dim"])
        def _on_focus_in(_):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.configure(fg=COLORS["text"])
        def _on_focus_out(_):
            if not e.get():
                e.insert(0, placeholder)
                e.configure(fg=COLORS["text_very_dim"])
        e.bind("<FocusIn>", _on_focus_in)
        e.bind("<FocusOut>", _on_focus_out)
    e._var = var  # acessível como entry._var.get()
    return e


def textarea(parent, *, value: str = "", placeholder: str = "", lines: int = 5):
    """Text widget multilinhas."""
    t = tk.Text(
        parent,
        font=FONTS["body"],
        bg=COLORS["input_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief=tk.FLAT,
        bd=0,
        height=lines,
        wrap=tk.WORD,
        padx=12, pady=10,
    )
    t.configure(highlightthickness=1,
                highlightbackground=COLORS["divider"],
                highlightcolor=COLORS["accent"])
    if value:
        t.insert("1.0", value)
    elif placeholder:
        t.insert("1.0", placeholder)
        t.configure(fg=COLORS["text_very_dim"])
        def _clear(_):
            if t.get("1.0", "end-1c") == placeholder:
                t.delete("1.0", tk.END)
                t.configure(fg=COLORS["text"])
        t.bind("<FocusIn>", _clear)
    return t


def select(parent, *, value: str, options: list, on_change=None):
    """ttk.Combobox estilizada."""
    var = tk.StringVar(value=value)
    cb = ttk.Combobox(parent, textvariable=var, values=options,
                      state="readonly", font=FONTS["body"])
    cb.configure(width=max(12, max(len(o) for o in options) + 2))
    if on_change:
        cb.bind("<<ComboboxSelected>>", lambda e: on_change(var.get()))
    cb._var = var
    return cb


# ══════════════════════════════════════════════════════════════════════
# 5. LAYOUT — cards, dividers, section labels
# ══════════════════════════════════════════════════════════════════════

def card(parent, *, padding=SPACING[4]):
    """Frame estilizado como card: bg bg_card + borda 1px divider.

    Retorna o Frame INTERNO (já com padding). Quem chama deve .pack/.grid
    o wrapper externo (acessível como result.master)."""
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
    return inner   # use inner para empilhar conteúdo; .master é o wrap


def divider_line(parent, *, soft: bool = False):
    """Linha horizontal de 1px. soft=True usa a cor mais sutil."""
    color = COLORS["divider_soft"] if soft else COLORS["divider"]
    return tk.Frame(parent, bg=color, height=1)


def section_label(parent, *, text: str, action: str = None, action_command=None):
    """Eyebrow label de uma seção. Texto vai pra UPPERCASE com letter-spacing.

    Como tk não tem letter-spacing, simulamos com espaços entre letras.
    """
    f = tk.Frame(parent, bg=parent["bg"])
    spaced = "  ".join(list(text.upper()))   # simula tracking
    tk.Label(f, text=spaced, font=FONTS["section"],
             bg=parent["bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)
    if action:
        lbl = tk.Label(f, text=action, font=FONTS["section"],
                       bg=parent["bg"], fg=COLORS["accent"], cursor="hand2")
        lbl.pack(side=tk.RIGHT)
        if action_command:
            lbl.bind("<Button-1>", lambda e: action_command())
    return f


def screen_header(parent, *, icon: str, title: str, subtitle: str = ""):
    """Cabeçalho padrão de TODAS as views (Membros, Atividades, etc).

    Retorna um dict com:
        {"frame": frame_principal,
         "actions": frame_à_direita_para_botões}
    """
    bg = parent["bg"]
    wrap = tk.Frame(parent, bg=bg)

    body = tk.Frame(wrap, bg=bg)
    body.pack(fill=tk.X, pady=(0, SPACING[4]))

    # ícone em quadrado
    left = tk.Frame(body, bg=bg)
    left.pack(side=tk.LEFT, fill=tk.X, expand=True)

    icon_row = tk.Frame(left, bg=bg)
    icon_row.pack(anchor=tk.W)

    icon_box = tk.Frame(
        icon_row, bg=COLORS["bg_card"],
        width=36, height=36,
        highlightbackground=COLORS["divider"], highlightthickness=1,
    )
    icon_box.pack(side=tk.LEFT, padx=(0, SPACING[3]))
    icon_box.pack_propagate(False)
    tk.Label(icon_box, text=icon, font=(FONTS["body"][0], 16),
             bg=COLORS["bg_card"], fg=COLORS["text"]).pack(expand=True)

    tk.Label(icon_row, text=title, font=FONTS["title"],
             bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)

    if subtitle:
        tk.Label(left, text=subtitle, font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W,
                                                     padx=(48, 0),
                                                     pady=(SPACING[1], 0))

    actions = tk.Frame(body, bg=bg)
    actions.pack(side=tk.RIGHT)

    # divisor abaixo
    divider_line(wrap).pack(fill=tk.X)
    return {"frame": wrap, "actions": actions}


# ══════════════════════════════════════════════════════════════════════
# 6. TABS — controle segmentado
# ══════════════════════════════════════════════════════════════════════

def tabs(parent, *, options, value: str, on_change):
    """Tabs segmentadas. `options` é uma lista de tuplas:
        [("key", "Label", count_or_None), ...]
    """
    bg = parent["bg"]
    container = tk.Frame(
        parent,
        bg=COLORS["bg_card"],
        highlightbackground=COLORS["divider"], highlightthickness=1,
    )
    state = {"value": value, "buttons": {}}

    def _render():
        for w in container.winfo_children():
            w.destroy()
        state["buttons"].clear()
        for opt in options:
            key, label, count = opt if len(opt) == 3 else (*opt, None)
            is_active = key == state["value"]
            btn_bg = COLORS["accent"] if is_active else COLORS["bg_card"]
            btn_fg = COLORS["bg_dark"] if is_active else COLORS["text_dim"]
            txt = f"  {label}  "
            if count is not None:
                txt = f"  {label}  ({count})  "
            b = tk.Label(container, text=txt, font=FONTS["btn"],
                         bg=btn_bg, fg=btn_fg, cursor="hand2",
                         padx=SPACING[3], pady=SPACING[2])
            b.pack(side=tk.LEFT, padx=2, pady=2)
            b.bind("<Button-1>", lambda e, k=key: _switch(k))
            state["buttons"][key] = b

    def _switch(key):
        state["value"] = key
        _render()
        on_change(key)

    _render()
    container.set_active = _switch
    return container


# ══════════════════════════════════════════════════════════════════════
# 7. ESTADOS
# ══════════════════════════════════════════════════════════════════════

def empty_state(parent, *, icon: str, title: str, body: str,
                cta_label: str = None, cta_command=None):
    """Estado vazio amigável. SEMPRE use em vez de listas em branco."""
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(pady=SPACING[10], padx=SPACING[8])

    tk.Label(inner, text=icon,
             font=(FONTS["body"][0], 36),
             bg=COLORS["bg_card"],
             fg=COLORS["text_muted"]).pack()

    tk.Label(inner, text=title,
             font=FONTS["subtitle"],
             bg=COLORS["bg_card"],
             fg=COLORS["text"]).pack(pady=(SPACING[3], SPACING[1]))

    tk.Label(inner, text=body,
             font=FONTS["body"],
             bg=COLORS["bg_card"],
             fg=COLORS["text_muted"],
             wraplength=420,
             justify=tk.CENTER).pack(pady=(0, SPACING[5]))

    if cta_label:
        button(inner, text=cta_label, kind="primary",
               icon="+", command=cta_command).pack()
    return wrap


# ══════════════════════════════════════════════════════════════════════
# 8. KPIs / Métricas
# ══════════════════════════════════════════════════════════════════════

def mini_stat(parent, *, value, label: str, color: str = None):
    """Card pequeno horizontal: número grande + label.
    Use em rows de filtros (Total/Ativos/Afastados/Visitantes)."""
    color = color or COLORS["text"]
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(fill=tk.BOTH, expand=True, padx=SPACING[4], pady=SPACING[3])
    tk.Label(inner, text=str(value), font=FONTS["metric_small"],
             bg=COLORS["bg_card"], fg=color).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    tk.Label(inner, text=label, font=FONTS["small_bold"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)
    return wrap


def big_stat(parent, *, value, label: str, sub: str = "", color: str = None):
    """KPI grande usado nos Relatórios. Número 40px + barra accent no rodapé."""
    color = color or COLORS["text"]
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)

    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(fill=tk.BOTH, expand=True, padx=SPACING[4],
               pady=(SPACING[4], 0))

    tk.Label(inner, text=label.upper(), font=FONTS["section"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor=tk.W)
    tk.Label(inner, text=str(value), font=FONTS["metric_xl"],
             bg=COLORS["bg_card"], fg=color).pack(anchor=tk.W, pady=(2, 2))
    if sub:
        tk.Label(inner, text=sub, font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor=tk.W)
    tk.Frame(inner, bg=COLORS["bg_card"], height=SPACING[2]).pack(fill=tk.X)
    # barra accent no rodapé (full-bleed)
    tk.Frame(wrap, bg=color, height=3).pack(fill=tk.X, side=tk.BOTTOM)
    return wrap


def bar_chart(parent, *, title: str, data: list):
    """Gráfico de barras horizontal. `data` é lista de tuplas:
        [(label, value, color), ...]
    """
    section_label(parent, text=title).pack(fill=tk.X, anchor=tk.W,
                                           pady=(0, SPACING[3]))
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(fill=tk.BOTH, expand=True,
               padx=SPACING[5], pady=SPACING[5])

    max_val = max((v for _, v, _ in data), default=1)
    for label_txt, value, color in data:
        row = tk.Frame(inner, bg=COLORS["bg_card"])
        row.pack(fill=tk.X, pady=SPACING[1])

        tk.Label(row, text=label_txt, font=FONTS["body_strong"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dim"],
                 width=18, anchor=tk.W).pack(side=tk.LEFT)

        track = tk.Frame(row, bg=COLORS["input_bg"], height=18)
        track.pack(side=tk.LEFT, fill=tk.X, expand=True,
                   padx=(SPACING[3], SPACING[3]))
        track.pack_propagate(False)

        # fill da barra usando place + relwidth
        fill = tk.Frame(track, bg=color)
        fill.place(x=0, y=0, relheight=1.0, relwidth=value / max_val)

        tk.Label(row, text=str(value), font=FONTS["body_strong"],
                 bg=COLORS["bg_card"], fg=COLORS["text"],
                 width=4, anchor=tk.E).pack(side=tk.RIGHT)
    return wrap


# ══════════════════════════════════════════════════════════════════════
# 9. SHELL — Header + Sidebar (chrome global)
# ══════════════════════════════════════════════════════════════════════

def header_bar(parent, *, user: dict, on_profile=None, on_edit_profile=None, on_logout=None):
    """Top bar com cruz + nome da igreja à esquerda + user chip à direita.
    Altura fixa de 58px (HEADER_HEIGHT)."""
    bg = COLORS["sidebar_bg"]
    f = tk.Frame(parent, bg=bg, height=58)
    f.pack_propagate(False)

    left = tk.Frame(f, bg=bg)
    left.pack(side=tk.LEFT, padx=SPACING[6])
    cross_icon(left, size=16, color=COLORS["accent"], bg=bg).pack(side=tk.LEFT, padx=(0, SPACING[3]))
    tk.Label(left, text=_APP_NAME, font=FONTS["subtitle"],
             bg=bg, fg=COLORS["accent"]).pack(side=tk.LEFT)

    right = tk.Frame(f, bg=bg)
    right.pack(side=tk.RIGHT, padx=SPACING[4])

    # User chip
    chip = tk.Frame(right, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"], highlightthickness=1,
                    cursor="hand2")
    chip.pack(side=tk.RIGHT, padx=SPACING[2])
    inner = tk.Frame(chip, bg=COLORS["bg_card"], cursor="hand2")
    inner.pack(padx=SPACING[2], pady=SPACING[1])

    badge_w = initials_badge(inner, user["nome"], COLORS["accent2"], size=28,
                             bg=COLORS["bg_card"])
    badge_w.pack(side=tk.LEFT, padx=(SPACING[1], SPACING[2]))

    info = tk.Frame(inner, bg=COLORS["bg_card"], cursor="hand2")
    info.pack(side=tk.LEFT)
    lbl_nome = tk.Label(info, text=user["nome"], font=FONTS["body_strong"],
                        bg=COLORS["bg_card"], fg=COLORS["text"], cursor="hand2")
    lbl_nome.pack(anchor=tk.W)
    lbl_nivel = tk.Label(info, text=user.get("nivel", ""), font=FONTS["tiny"],
                         bg=COLORS["bg_card"], fg=COLORS["text_muted"], cursor="hand2")
    lbl_nivel.pack(anchor=tk.W)
    lbl_arrow = tk.Label(inner, text="▾", font=FONTS["tiny"],
                         bg=COLORS["bg_card"], fg=COLORS["text_muted"], cursor="hand2")
    lbl_arrow.pack(side=tk.LEFT, padx=SPACING[2])

    from ..perfil import PerfilMenu
    _menu = PerfilMenu(parent, user=user,
                       on_edit=on_edit_profile,
                       on_logout=on_logout)

    def _show_dropdown(event=None):
        _menu.toggle(chip)

    # Bind all widgets — tkinter events don't bubble up from children
    for w in (chip, inner, info, lbl_nome, lbl_nivel, lbl_arrow):
        w.bind("<Button-1>", _show_dropdown)
    # badge children need binding too
    for w in badge_w.winfo_children():
        w.bind("<Button-1>", _show_dropdown)
    badge_w.bind("<Button-1>", _show_dropdown)

    return f


def sidebar(parent, *, items, active_key, on_select, on_logout):
    """Sidebar de 230px com nav items e botão Sair fixo no rodapé.

    items: lista de dicts {"key": str, "icon": str, "label": str}
    """
    bg = COLORS["sidebar_bg"]
    f = tk.Frame(parent, bg=bg, width=SIDEBAR_WIDTH)
    f.pack_propagate(False)

    top = tk.Frame(f, bg=bg)
    top.pack(fill=tk.X, side=tk.TOP, pady=(SPACING[3], 0))

    for item in items:
        _nav_item(top, item=item,
                  active=(item["key"] == active_key),
                  on_click=lambda k=item["key"]: on_select(k))

    # rodapé com Sair
    bottom = tk.Frame(f, bg=bg)
    bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, SPACING[3]))
    divider_line(bottom).pack(fill=tk.X, padx=SPACING[4], pady=(0, SPACING[2]))
    _nav_item(bottom,
              item={"key": "logout", "icon": "🚪", "label": "Sair"},
              danger=True,
              on_click=on_logout)
    return f


def _nav_item(parent, *, item, active=False, danger=False, on_click=None):
    """Linha clicável da sidebar. Item ativo ganha:
       1) barra accent de 3px à esquerda
       2) bg ligeiramente mais claro
       3) texto bold
    """
    color = COLORS["danger"] if danger else (
        COLORS["text"] if active else COLORS["text_dim"]
    )
    bg = COLORS["sidebar_active"] if active else COLORS["sidebar_bg"]

    row = tk.Frame(parent, bg=bg, height=44)
    row.pack(fill=tk.X, pady=1)
    row.pack_propagate(False)

    # barra accent (3px) — pinta só se ativo
    rail = tk.Frame(row, bg=COLORS["accent"] if active else bg,
                    width=ACTIVE_RAIL_PX)
    rail.pack(side=tk.LEFT, fill=tk.Y)

    icon_lbl = tk.Label(row, text=item["icon"],
                        font=FONTS["body"],
                        bg=bg, fg=color, width=2)
    icon_lbl.pack(side=tk.LEFT, padx=(SPACING[3], SPACING[2]))

    text_lbl = tk.Label(row, text=item["label"],
                        font=(FONTS["body"][0], 11, "bold" if active else "normal"),
                        bg=bg, fg=color, anchor=tk.W)
    text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # hover (só se NÃO ativo)
    if not active and not danger:
        hover_bg = COLORS["sidebar_hover"]
        def _on_enter(e):
            for w in (row, icon_lbl, text_lbl):
                w.configure(bg=hover_bg)
        def _on_leave(e):
            for w in (row, icon_lbl, text_lbl):
                w.configure(bg=bg)
        for w in (row, icon_lbl, text_lbl):
            w.bind("<Enter>", _on_enter)
            w.bind("<Leave>", _on_leave)

    if on_click:
        for w in (row, icon_lbl, text_lbl, rail):
            w.bind("<Button-1>", lambda e: on_click())
            w.configure(cursor="hand2")

    return row


# ══════════════════════════════════════════════════════════════════════
# 10. CARDS DE DOMÍNIO — Member, Activity, Event
# ══════════════════════════════════════════════════════════════════════

def event_card(parent, *, event: dict, compact: bool = True, callbacks: dict = None):
    """Card de evento para o dashboard (compact=True) ou para a tela de
    atividades (compact=False com botões de ação).

    event: {dia, mes, hora, titulo, local, resp, status, desc?}
    callbacks (non-compact): {"edit": fn, "done": fn, "cancel": fn}
    """
    callbacks = callbacks or {}
    bg = COLORS["bg_card"]
    wrap = tk.Frame(parent, bg=bg,
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)

    # coluna da data — só dia e mês (hora fica no corpo para não ser cortada)
    date_col = tk.Frame(wrap, bg=bg, width=90)
    date_col.pack(side=tk.LEFT, fill=tk.Y)
    date_col.pack_propagate(False)
    date_inner = tk.Frame(date_col, bg=bg)
    date_inner.pack(expand=True)
    tk.Label(date_inner, text=str(event["dia"]),
             font=(FONTS["body"][0], 26, "bold"),
             bg=bg, fg=COLORS["accent"]).pack()
    tk.Label(date_inner, text=event["mes"],
             font=FONTS["section"],
             bg=bg, fg=COLORS["accent"]).pack()

    tk.Frame(wrap, bg=COLORS["divider"], width=1).pack(side=tk.LEFT, fill=tk.Y)

    # corpo
    body = tk.Frame(wrap, bg=bg)
    body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
              padx=SPACING[4], pady=SPACING[3])

    title_row = tk.Frame(body, bg=bg)
    title_row.pack(fill=tk.X, anchor=tk.W)
    tk.Label(title_row, text=truncate(event["titulo"], 50),
             font=FONTS["subtitle"], bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)
    badge(title_row, event["status"], kind=event["status"]).pack(
        side=tk.LEFT, padx=(SPACING[2], 0))

    meta = tk.Frame(body, bg=bg)
    meta.pack(fill=tk.X, anchor=tk.W, pady=(SPACING[1], 0))
    if event.get("hora"):
        tk.Label(meta, text=f"🕐 {event['hora']}", font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT,
                                                      padx=(0, SPACING[4]))
    tk.Label(meta, text=f"📍 {event['local']}", font=FONTS["small"],
             bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT,
                                                  padx=(0, SPACING[4]))
    tk.Label(meta, text=f"👤 {event['resp']}", font=FONTS["small"],
             bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT,
                                                  padx=(0, SPACING[4]))
    if event.get("funcao_alvo"):
        tk.Label(meta, text=f"🎯 {event['funcao_alvo']}", font=FONTS["small"],
                 bg=bg, fg=COLORS["accent2"]).pack(side=tk.LEFT,
                                                   padx=(0, SPACING[4]))
    if event.get("grupo_alvo"):
        tk.Label(meta, text=f"🏷 {event['grupo_alvo']}", font=FONTS["small"],
                 bg=bg, fg=COLORS["purple"]).pack(side=tk.LEFT)

    # ações à direita (só no modo expandido, só botões com comando definido)
    if not compact:
        edit_cb      = callbacks.get("edit")
        done_cb      = callbacks.get("done")
        cancel_cb    = callbacks.get("cancel")
        whatsapp_cb  = callbacks.get("whatsapp")
        if any([edit_cb, done_cb, cancel_cb, whatsapp_cb]):
            actions = tk.Frame(wrap, bg=bg)
            actions.pack(side=tk.RIGHT, padx=SPACING[3], pady=SPACING[3])
            if whatsapp_cb:
                icon_button(actions, icon="💬", tooltip="Enviar lembrete WhatsApp",
                            color=COLORS["whatsapp"], size=32,
                            command=whatsapp_cb).pack(side=tk.LEFT, padx=2)
            if edit_cb:
                icon_button(actions, icon="✏", tooltip="Editar", size=32,
                            command=edit_cb).pack(side=tk.LEFT, padx=2)
            if done_cb:
                icon_button(actions, icon="✓", tooltip="Marcar como realizado",
                            color=COLORS["success"], size=32,
                            command=done_cb).pack(side=tk.LEFT, padx=2)
            if cancel_cb:
                icon_button(actions, icon="✗", tooltip="Cancelar",
                            color=COLORS["danger"], size=32,
                            command=cancel_cb).pack(side=tk.LEFT, padx=2)
    return wrap


# alias semântico
activity_row = event_card


def member_card(parent, *, member: dict, callbacks: dict = None):
    """Card de membro 2-col. Estrutura fixa de altura para nunca quebrar.

    member: {nome, funcao, status, tel, email, niver_dia, niver_mes,
             obs (opcional), color}
    callbacks: {"whatsapp": fn, "edit": fn, "delete": fn}
    """
    callbacks = callbacks or {}
    bg = COLORS["bg_card"]
    wrap = tk.Frame(parent, bg=bg,
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1,
                    height=186)
    wrap.pack_propagate(False)
    inner = tk.Frame(wrap, bg=bg)
    inner.pack(fill=tk.BOTH, expand=True,
               padx=SPACING[4], pady=SPACING[3])

    # cabeçalho: avatar + nome + função + status à direita
    head = tk.Frame(inner, bg=bg)
    head.pack(fill=tk.X)

    initials_badge(head, member["nome"], member.get("color", COLORS["accent2"]),
                   size=40, bg=bg).pack(side=tk.LEFT, padx=(0, SPACING[3]))

    name_col = tk.Frame(head, bg=bg)
    name_col.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
    tk.Label(name_col, text=truncate(member["nome"], 32),
             font=FONTS["subtitle"], bg=bg, fg=COLORS["text"],
             anchor=tk.W).pack(anchor=tk.W, fill=tk.X)
    badge_row = tk.Frame(name_col, bg=bg)
    badge_row.pack(anchor=tk.W, pady=(2, 0))
    _GROUP_COLORS = {
        "Grupo dos Homens":   ("#1d4ed8", "#ffffff"),
        "Grupo de Mulheres":  (COLORS["purple"], "#ffffff"),
        "Grupo de Jovens":    ("#475569", "#ffffff"),
        "Grupo Infantil":     ("#eab308", COLORS["bg_dark"]),
    }
    badge(badge_row, member["funcao"], kind=member["funcao"]).pack(side=tk.LEFT)
    if member.get("grupo"):
        gbg, gfg = _GROUP_COLORS.get(member["grupo"], (COLORS["purple"], "#ffffff"))
        badge(badge_row, member["grupo"],
              bg=gbg, fg=gfg).pack(side=tk.LEFT, padx=(4, 0))
    if member.get("grupo_casais"):
        badge(badge_row, "Casais",
              bg=COLORS["danger"], fg="#ffffff").pack(side=tk.LEFT, padx=(4, 0))

    badge(head, member["status"], kind=member["status"]).pack(side=tk.RIGHT)

    # info row
    info = tk.Frame(inner, bg=bg)
    info.pack(fill=tk.X, pady=(SPACING[2], 0))
    tk.Label(info, text=f"📞 {member['tel']}", font=FONTS["small"],
             bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT,
                                                  padx=(0, SPACING[4]))
    if member.get("niver_dia") and member.get("niver_mes"):
        tk.Label(info,
                 text=f"🎂 {member['niver_dia']:02d}/{member['niver_mes']}",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    email_row = tk.Frame(inner, bg=bg)
    email_row.pack(fill=tk.X, pady=(SPACING[1], 0))
    tk.Label(email_row, text=f"✉ {truncate(member['email'], 36)}",
             font=FONTS["small"],
             bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    actions = tk.Frame(inner, bg=bg)
    actions.pack(side=tk.BOTTOM, anchor=tk.E, pady=(SPACING[3], 0))
    icon_button(actions, icon="💬", tooltip="Enviar mensagem", size=44,
                command=callbacks.get("whatsapp")).pack(side=tk.LEFT, padx=2)
    icon_button(actions, icon="✏", tooltip="Editar", size=44,
                command=callbacks.get("edit")).pack(side=tk.LEFT, padx=2)
    icon_button(actions, icon="✗", tooltip="Excluir", size=44,
                color=COLORS["danger"],
                command=callbacks.get("delete")).pack(side=tk.LEFT, padx=2)
    return wrap


# ══════════════════════════════════════════════════════════════════════
# 11. CARDS ESPECIAIS — verso, ações rápidas, conexão WhatsApp
# ══════════════════════════════════════════════════════════════════════

def verse_card(parent, *, text: str, reference: str):
    """Card do versículo do dia. Borda dourada à esquerda + cruz + texto
    em itálico + referência alinhada à direita."""
    bg = COLORS["bg_card"]
    gold = COLORS["verse_gold"]
    wrap = tk.Frame(parent, bg=bg,
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)

    # barra dourada
    tk.Frame(wrap, bg=gold, width=4).pack(side=tk.LEFT, fill=tk.Y)

    inner = tk.Frame(wrap, bg=bg)
    inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
               padx=SPACING[4], pady=SPACING[3])

    head = tk.Frame(inner, bg=bg)
    head.pack(fill=tk.X)
    cross_icon(head, size=11, color=gold, bg=bg).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    tk.Label(head, text="VERSÍCULO DO DIA",
             font=FONTS["tiny_bold"], bg=bg, fg=gold).pack(side=tk.LEFT)

    tk.Label(inner, text=f'"{text}"',
             font=FONTS["body_italic"], bg=bg, fg=COLORS["text"],
             wraplength=420, justify=tk.LEFT,
             anchor=tk.W).pack(anchor=tk.W, pady=(SPACING[2], SPACING[2]))

    tk.Label(inner, text=f"— {reference}",
             font=FONTS["tiny_bold"],
             bg=bg, fg=gold).pack(anchor=tk.E)
    return wrap


def quick_action_card(parent, *, icon, label, hint, color, command=None):
    """Card pequeno de ação rápida. Usado em row de 4 no dashboard."""
    bg = COLORS["bg_card"]
    wrap = tk.Frame(parent, bg=bg,
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1, cursor="hand2")
    inner = tk.Frame(wrap, bg=bg)
    inner.pack(fill=tk.BOTH, expand=True,
               padx=SPACING[4], pady=SPACING[3])

    icon_box = tk.Frame(inner, bg=color, width=36, height=36)
    icon_box.pack(side=tk.LEFT, padx=(0, SPACING[3]))
    icon_box.pack_propagate(False)
    icon_lbl = tk.Label(icon_box, text=icon, font=(FONTS["body"][0], 16),
                        bg=color, fg=COLORS["bg_dark"])
    icon_lbl.pack(expand=True)

    text_col = tk.Frame(inner, bg=bg)
    text_col.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
    lbl_label = tk.Label(text_col, text=label, font=FONTS["body_strong"],
                         bg=bg, fg=COLORS["text"], anchor=tk.W)
    lbl_label.pack(anchor=tk.W, fill=tk.X)
    lbl_hint = tk.Label(text_col, text=hint, font=FONTS["small"],
                        bg=bg, fg=COLORS["text_muted"], anchor=tk.W)
    lbl_hint.pack(anchor=tk.W, fill=tk.X)

    if command:
        # Bind all widgets including Labels — tkinter events don't bubble up
        def _call(e=None):
            command()
        for w in (wrap, inner, icon_box, icon_lbl, text_col, lbl_label, lbl_hint):
            w.bind("<Button-1>", _call)
    return wrap


def connection_card(parent, *, connected: bool, session_info: str = "",
                    on_toggle=None):
    """Card de status da conexão do WhatsApp. Verde = conectado, vermelho
    = desconectado."""
    bg = COLORS["bg_card"]
    color = COLORS["success"] if connected else COLORS["danger"]

    wrap = tk.Frame(parent, bg=bg,
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=bg)
    inner.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[4])

    # ícone
    icon_box = tk.Frame(inner, bg=bg, width=44, height=44,
                        highlightbackground=color, highlightthickness=1)
    icon_box.pack(side=tk.LEFT, padx=(0, SPACING[4]))
    icon_box.pack_propagate(False)
    tk.Label(icon_box, text="✓" if connected else "⚠",
             font=(FONTS["body"][0], 18),
             bg=bg, fg=color).pack(expand=True)

    text_col = tk.Frame(inner, bg=bg)
    text_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Label(text_col, text="STATUS  DA  CONEXÃO",
             font=FONTS["section"],
             bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)
    status_row = tk.Frame(text_col, bg=bg)
    status_row.pack(anchor=tk.W, pady=(2, 0))
    pill(status_row, "Conectado" if connected else "Desconectado",
         dot_color=color, text_color=color).pack(side=tk.LEFT)
    if connected and session_info:
        tk.Label(status_row, text=f"  ·  {session_info}", font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    action = tk.Label(
        inner,
        text="Desconectar" if connected else "Conectar agora",
        font=FONTS["section"],
        bg=bg, fg=COLORS["accent"],
        cursor="hand2",
    )
    action.pack(side=tk.RIGHT)
    if on_toggle:
        action.bind("<Button-1>", lambda e: on_toggle())
    return wrap


# ══════════════════════════════════════════════════════════════════════
# 12. PAGE CONTAINER — padding consistente em TODAS as views
# ══════════════════════════════════════════════════════════════════════

def page_container(parent):
    """Container externo de uma página. Padding consistente (32px x 24px)
    + scroll vertical. Use sempre como root da view.

    Retorna o frame INTERNO onde você adiciona o conteúdo.
    O frame retornado expõe `scroll_top()` para redefinir a posição ao topo.

    Regras de scroll:
      - Nunca rola acima do topo (scrollregion sempre começa em y=0).
      - Só rola para baixo se houver conteúdo além da área visível.
      - Velocidade natural: ~40 px por tick de mouse wheel.
    """
    from .tokens import PAGE_PAD_X, PAGE_PAD_Y

    outer = tk.Frame(parent, bg=COLORS["bg_dark"])
    outer.pack(fill=tk.BOTH, expand=True)

    # scrollbar — sempre presente mas invisível quando não há overflow
    sb = tk.Scrollbar(outer, orient=tk.VERTICAL)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(outer, bg=COLORS["bg_dark"],
                       highlightthickness=0, bd=0,
                       yscrollincrement=20,
                       yscrollcommand=sb.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.configure(command=canvas.yview)

    inner = tk.Frame(canvas, bg=COLORS["bg_dark"])
    win_id = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

    def _update_scrollregion(*_):
        # Garante que o layout do inner esteja completo antes de medir
        canvas.update_idletasks()
        content_h = inner.winfo_reqheight()
        canvas_h  = canvas.winfo_height()
        canvas_w  = canvas.winfo_width()
        # scrollregion começa em 0 (nunca rola acima do topo)
        # altura = max(conteúdo, viewport) → sem scroll quando conteúdo cabe
        scroll_h = max(content_h, canvas_h)
        canvas.configure(scrollregion=(0, 0, canvas_w, scroll_h))

    def _on_canvas_resize(e):
        canvas.itemconfigure(win_id, width=e.width)
        canvas.after_idle(_update_scrollregion)

    canvas.bind("<Configure>", _on_canvas_resize)
    inner.bind("<Configure>", lambda e: canvas.after_idle(_update_scrollregion))

    # Mouse wheel — só ativa se o conteúdo ultrapassa a área visível
    def _scroll(e):
        lo, hi = canvas.yview()
        if hi - lo < 0.999:
            canvas.yview_scroll(-1 * (e.delta // 120) * 2, "units")

    canvas.bind("<Enter>",   lambda e: canvas.bind_all("<MouseWheel>", _scroll))
    canvas.bind("<Leave>",   lambda e: canvas.unbind_all("<MouseWheel>"))
    canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # padding interno
    content = tk.Frame(inner, bg=COLORS["bg_dark"])
    content.pack(fill=tk.BOTH, expand=True,
                 padx=PAGE_PAD_X, pady=PAGE_PAD_Y)

    # API para páginas com abas redefinirem o scroll ao trocar de aba
    content.scroll_top = lambda: canvas.yview_moveto(0.0)

    return content
