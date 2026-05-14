"""
pages/reports.py
================
Tela de Relatórios. 4 abas:
  - Membros          → KPIs + barras horizontais por função
  - Aniversariantes  → seletor de mês + lista do mês
  - Eventos          → KPIs + barras por status
  - Crescimento      → KPIs + gráfico de barras 12 meses (Canvas)
"""

import tkinter as tk
from datetime import datetime

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, tabs as build_tabs,
    big_stat, bar_chart, section_label,
    initials_badge, button, divider_line,
)
from ..ui.helpers import truncate


def render(parent, *, data=None, callbacks=None):
    data      = data or {}
    callbacks = callbacks or {}
    content   = page_container(parent)

    hdr = screen_header(
        content,
        icon="📊",
        title="Relatórios e Estatísticas",
        subtitle="Visão geral da igreja",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))
    button(hdr["actions"], text="Exportar PDF",
           kind="ghost", icon="📄",
           command=callbacks.get("export_pdf")).pack(side=tk.LEFT)

    # ─── Tabs ─────────────────────────────────────────────────────
    tab_row = tk.Frame(content, bg=COLORS["bg_dark"])
    tab_row.pack(fill=tk.X, pady=(0, SPACING[5]))

    body = tk.Frame(content, bg=COLORS["bg_dark"])
    body.pack(fill=tk.BOTH, expand=True)

    def _show(tab):
        for w in body.winfo_children():
            w.destroy()
        if tab == "membros":
            _render_membros(body, data)
        elif tab == "aniversariantes":
            _render_aniversariantes(body)
        elif tab == "eventos":
            _render_eventos(body, data)
        elif tab == "crescimento":
            _render_crescimento(body)

    tabs_widget = build_tabs(
        tab_row,
        options=[
            ("membros",         "👥  Membros",        None),
            ("aniversariantes", "🎂  Aniversariantes", None),
            ("eventos",         "📋  Eventos",        None),
            ("crescimento",     "📈  Crescimento",    None),
        ],
        value="membros",
        on_change=_show,
    )
    tabs_widget.pack(side=tk.LEFT)
    _show("membros")


# ─── ABA: MEMBROS ─────────────────────────────────────────────────
def _render_membros(parent, data):
    bg = parent["bg"]

    total      = data.get("total",      0)
    ativos     = data.get("ativos",     0)
    afastados  = data.get("afastados",  0)
    visitantes = data.get("visitantes", 0)

    row = tk.Frame(parent, bg=bg)
    row.pack(fill=tk.X, pady=(0, SPACING[6]))
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="bs")

    stats = [
        (total,      "Total de Membros", "Todos os cadastros",         COLORS["text"]),
        (ativos,     "Ativos",           "Membros regulares",          COLORS["success"]),
        (afastados,  "Afastados",        "Temporariamente afastados",  COLORS["danger"]),
        (visitantes, "Visitantes",       "Visitantes cadastrados",     COLORS["warning"]),
    ]
    for i, (v, l, s, c) in enumerate(stats):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 3 else SPACING[1]))
        big_stat(cell, value=v, label=l, sub=s, color=c).pack(fill=tk.BOTH, expand=True)

    funcao_counts = data.get("funcao_counts", {})
    if funcao_counts:
        chart_colors = [
            COLORS["accent"], COLORS["accent2"], COLORS["purple"],
            COLORS["warning"], COLORS["success"], COLORS["danger"],
        ]
        bar_data = [
            (f, c, chart_colors[i % len(chart_colors)])
            for i, (f, c) in enumerate(
                sorted(funcao_counts.items(), key=lambda x: -x[1])
            )
        ]
    else:
        bar_data = [("Sem dados", 0, COLORS["accent"])]

    bar_chart(parent, title="Distribuição por função",
              data=bar_data).pack(fill=tk.X)


# ─── ABA: ANIVERSARIANTES ─────────────────────────────────────────
_MESES = ["Jan","Fev","Mar","Abr","Mai","Jun",
          "Jul","Ago","Set","Out","Nov","Dez"]


def _render_aniversariantes(parent):
    bg = parent["bg"]
    current = datetime.now().month - 1
    state   = {"active": current}

    selector = tk.Frame(parent, bg=bg)
    selector.pack(fill=tk.X, pady=(0, SPACING[5]))
    for c in range(12):
        selector.columnconfigure(c, weight=1, uniform="ms")

    list_box = tk.Frame(parent, bg=bg)
    list_box.pack(fill=tk.X)

    def _set_month(idx):
        state["active"] = idx
        _render_buttons()
        _render_list()

    def _render_buttons():
        for w in selector.winfo_children():
            w.destroy()
        for i, m in enumerate(_MESES):
            is_active = i == state["active"]
            btn = tk.Label(
                selector, text=m, font=FONTS["small_bold"],
                bg=COLORS["accent"] if is_active else COLORS["bg_card"],
                fg=COLORS["bg_dark"] if is_active else COLORS["text_dim"],
                cursor="hand2",
                padx=SPACING[2], pady=SPACING[2],
                highlightbackground=COLORS["divider"], highlightthickness=1,
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            btn.bind("<Button-1>", lambda e, i=i: _set_month(i))

    def _render_list():
        for w in list_box.winfo_children():
            w.destroy()

        try:
            from core.members import aniversariantes_do_mes
            raw = list(aniversariantes_do_mes(state["active"] + 1))
            data_list = [
                {"dia": r["aniversario_dia"], "nome": r["nome"],
                 "funcao": r["funcao"] or "Membro", "color": "#667eea"}
                for r in raw
            ]
        except Exception:
            data_list = []

        mes_nome = _MESES[state["active"]]

        section_label(list_box, text=f"Aniversariantes de {mes_nome}",
                      action=f"{len(data_list)} pessoas"
                      ).pack(fill=tk.X, anchor=tk.W, pady=(0, SPACING[3]))

        card = tk.Frame(list_box, bg=COLORS["bg_card"],
                        highlightbackground=COLORS["divider"],
                        highlightthickness=1)
        card.pack(fill=tk.X)

        if not data_list:
            tk.Label(card,
                     text=f"Nenhum aniversariante em {mes_nome}.",
                     font=FONTS["body"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(pady=SPACING[6])
            return

        for i, b in enumerate(data_list):
            line = tk.Frame(card, bg=COLORS["bg_card"])
            line.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[2])

            date_col = tk.Frame(line, bg=COLORS["bg_card"], width=52)
            date_col.pack(side=tk.LEFT, padx=(0, SPACING[3]))
            date_col.pack_propagate(False)
            tk.Label(date_col, text=f"{b['dia']:02d}",
                     font=(FONTS["body"][0], 22, "bold"),
                     bg=COLORS["bg_card"],
                     fg=COLORS["warning"]).pack()
            tk.Label(date_col, text=mes_nome.upper(),
                     font=FONTS["section"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack()

            tk.Frame(line, bg=COLORS["divider_soft"], width=1).pack(
                side=tk.LEFT, fill=tk.Y, padx=(0, SPACING[3]))

            initials_badge(line, b["nome"], b["color"], size=32,
                           bg=COLORS["bg_card"]).pack(side=tk.LEFT,
                                                       padx=(0, SPACING[3]))

            info = tk.Frame(line, bg=COLORS["bg_card"])
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=truncate(b["nome"], 30),
                     font=FONTS["body_strong"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text"]).pack(anchor=tk.W)
            tk.Label(info, text=b["funcao"], font=FONTS["small"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(anchor=tk.W)

            button(line, text="Parabenizar",
                   kind="whatsapp", icon="💬").pack(side=tk.RIGHT)

            if i < len(data_list) - 1:
                divider_line(card, soft=True).pack(fill=tk.X, padx=SPACING[4])

    _render_buttons()
    _render_list()


# ─── ABA: EVENTOS ─────────────────────────────────────────────────
def _render_eventos(parent, data):
    bg = parent["bg"]
    row = tk.Frame(parent, bg=bg)
    row.pack(fill=tk.X, pady=(0, SPACING[6]))
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="ev")

    total_ev    = data.get("total_events",  0)
    realizadas  = data.get("realizadas",    0)
    planejadas  = data.get("planejadas",    0)
    canceladas  = data.get("canceladas",    0)

    stats = [
        (total_ev,   "Total de Eventos", "Nos últimos 12 meses",   COLORS["text"]),
        (realizadas, "Realizados",       "Concluídos com sucesso", COLORS["success"]),
        (planejadas, "Planejados",       "Agenda futura",          COLORS["accent"]),
        (canceladas, "Cancelados",       "Não aconteceram",        COLORS["danger"]),
    ]
    for i, (v, l, s, c) in enumerate(stats):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 3 else SPACING[1]))
        big_stat(cell, value=v, label=l, sub=s, color=c).pack(fill=tk.BOTH, expand=True)

    bar_chart(parent, title="Distribuição por status", data=[
        ("Planejados", max(planejadas, 0),  COLORS["accent"]),
        ("Realizados", max(realizadas, 0),  COLORS["success"]),
        ("Cancelados", max(canceladas, 0),  COLORS["danger"]),
    ]).pack(fill=tk.X)


# ─── ABA: CRESCIMENTO ─────────────────────────────────────────────
def _render_crescimento(parent):
    bg = parent["bg"]
    row = tk.Frame(parent, bg=bg)
    row.pack(fill=tk.X, pady=(0, SPACING[6]))
    for c in range(3):
        row.columnconfigure(c, weight=1, uniform="cr")

    stats = [
        ("+28",  "Crescimento no ano",  "Membros adicionados líquido", COLORS["success"]),
        ("+12",  "Novos este trimestre", "Abr → Mai",                  COLORS["accent"]),
        ("2.3%", "Taxa mensal média",   "Crescimento composto",        COLORS["accent2"]),
    ]
    for i, (v, l, s, c) in enumerate(stats):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 2 else SPACING[1]))
        big_stat(cell, value=v, label=l, sub=s, color=c).pack(fill=tk.BOTH, expand=True)

    section_label(parent, text="Membros ao longo do tempo").pack(
        fill=tk.X, anchor=tk.W, pady=(0, SPACING[3]))

    chart_card = tk.Frame(parent, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    chart_card.pack(fill=tk.X)
    _draw_growth_chart(chart_card)


def _draw_growth_chart(parent):
    data = [
        ("Jun", 96),  ("Jul", 99),  ("Ago", 101), ("Set", 104),
        ("Out", 108), ("Nov", 110), ("Dez", 112), ("Jan", 115),
        ("Fev", 118), ("Mar", 120), ("Abr", 122), ("Mai", 124),
    ]
    width   = 940
    height  = 240
    pad_x   = 24
    pad_y   = 32
    bar_gap = 8

    cv = tk.Canvas(parent, width=width, height=height,
                   bg=COLORS["bg_card"], highlightthickness=0, bd=0)
    cv.pack(padx=SPACING[5], pady=SPACING[5])

    chart_w = width  - pad_x * 2
    chart_h = height - pad_y * 2
    bar_w   = (chart_w - bar_gap * (len(data) - 1)) / len(data)
    max_v   = max(v for _, v in data)
    min_v   = min(v for _, v in data)
    span    = (max_v - min_v) + 4

    cv.create_line(pad_x, pad_y + chart_h, pad_x + chart_w, pad_y + chart_h,
                   fill=COLORS["divider"], width=1)

    for i, (label, value) in enumerate(data):
        h  = ((value - min_v + 4) / span) * chart_h
        x0 = pad_x + i * (bar_w + bar_gap)
        x1 = x0 + bar_w
        y1 = pad_y + chart_h
        y0 = y1 - h
        cv.create_rectangle(x0, y0, x1, y1, fill=COLORS["accent"], outline="")
        cv.create_text((x0 + x1) / 2, y0 - 10,
                       text=str(value), font=FONTS["tiny_bold"],
                       fill=COLORS["text_muted"])
        cv.create_text((x0 + x1) / 2, y1 + 14,
                       text=label, font=FONTS["tiny_bold"],
                       fill=COLORS["text_muted"])
