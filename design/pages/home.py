"""
pages/home.py
=============
Página Inicial (Dashboard). Substitui `_page_home` da classe atual.

ESTRUTURA (de cima pra baixo):
  1. greeting_row      — saudação + versículo do dia (2 colunas)
  2. quick_actions     — 4 cards: Novo Membro / Nova Atividade / WhatsApp / Relatórios
  3. stats_row         — 4 KPIs: Membros / Aniversariantes / Eventos / Visitantes
  4. content_columns:  — 2 colunas:
       - upcoming_events (3 por página)
       - birthdays (4 por página)
"""

import tkinter as tk
from datetime import datetime

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, section_label, divider_line,
    verse_card, quick_action_card, event_card, mini_stat,
    initials_badge, button,
)
from ..ui.helpers import truncate


_USER = {"nome": "Usuário", "nivel": ""}

_VERSE_FALLBACK = {
    "text": ("Não andeis ansiosos por coisa alguma; antes em tudo "
             "fazei conhecidas as vossas petições a Deus em oração e "
             "súplica, com ações de graças."),
    "ref":  "Filipenses 4:6",
}


# ─── BLOCO 1: GREETING ROW ────────────────────────────────────────────
def _build_greeting_row(parent, user, verse=None):
    bg = parent["bg"]
    row = tk.Frame(parent, bg=bg)

    row.columnconfigure(0, weight=1, uniform="g")
    row.columnconfigure(1, weight=1, uniform="g")

    left = tk.Frame(row, bg=bg)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING[4]))

    now = datetime.now()
    dias = ["segunda-feira","terça-feira","quarta-feira",
            "quinta-feira","sexta-feira","sábado","domingo"]
    meses = ["janeiro","fevereiro","março","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    date_str = (f"{dias[now.weekday()]}, {now.day} de {meses[now.month - 1]}").upper()

    hour = now.hour
    saudacao = "BOM DIA" if hour < 12 else ("BOA TARDE" if hour < 18 else "BOA NOITE")
    first_name = user["nome"].split()[0]

    tk.Label(left, text="    ".join(list(date_str)),
             font=FONTS["section"],
             bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)

    tk.Label(left, text=f"{saudacao.title()}, {first_name}.",
             font=FONTS["display"],
             bg=bg, fg=COLORS["text"]).pack(anchor=tk.W, pady=(SPACING[2], 0))

    tk.Label(left, text="Aqui está um resumo da igreja hoje.",
             font=FONTS["body"],
             bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W,
                                                  pady=(SPACING[1], 0))

    v = verse or _VERSE_FALLBACK
    right = tk.Frame(row, bg=bg)
    right.grid(row=0, column=1, sticky="nsew")
    verse_card(right, text=v["text"],
               reference=v["ref"]).pack(fill=tk.BOTH, expand=True)
    return row


# ─── BLOCO 2: QUICK ACTIONS ───────────────────────────────────────────
def _build_quick_actions(parent, callbacks):
    bg = parent["bg"]
    wrap = tk.Frame(parent, bg=bg)
    section_label(wrap, text="Ações rápidas").pack(fill=tk.X, anchor=tk.W,
                                                    pady=(0, SPACING[3]))

    row = tk.Frame(wrap, bg=bg)
    row.pack(fill=tk.X)
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="qa")

    actions = [
        ("👥", "Novo Membro",     "Cadastrar pessoa",     COLORS["accent"],   callbacks.get("new_member")),
        ("📅", "Nova Atividade",  "Agendar evento",       COLORS["accent2"],  callbacks.get("new_activity")),
        ("💬", "Enviar Mensagem", "WhatsApp em lote",     COLORS["whatsapp"], callbacks.get("send_whatsapp")),
        ("📊", "Ver Relatórios",  "Resumo do mês",        COLORS["purple"],   callbacks.get("open_reports")),
    ]
    for i, (icon, label, hint, color, cmd) in enumerate(actions):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[2] // 2,
                        0 if i == 3 else SPACING[2] // 2))
        quick_action_card(cell, icon=icon, label=label, hint=hint,
                          color=color, command=cmd).pack(fill=tk.BOTH, expand=True)
    return wrap


# ─── BLOCO 3: STATS ROW ───────────────────────────────────────────────
def _build_stats_row(parent, totals, on_reports=None):
    bg = parent["bg"]
    wrap = tk.Frame(parent, bg=bg)
    section_label(wrap, text="Resumo da igreja",
                  action="Ver relatórios →",
                  action_command=on_reports).pack(fill=tk.X, anchor=tk.W,
                                                    pady=(0, SPACING[3]))

    row = tk.Frame(wrap, bg=bg)
    row.pack(fill=tk.X)
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="s")

    stats = [
        (totals["ativos"],          "Membros Ativos",    COLORS["success"]),
        (totals["aniversariantes"], "Aniversariantes",   COLORS["warning"]),
        (totals["eventos"],         "Próximos Eventos",  COLORS["accent"]),
        (totals["visitantes"],      "Visitantes do Mês", COLORS["accent2"]),
    ]
    for i, (value, label, color) in enumerate(stats):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 3 else SPACING[1]))
        mini_stat(cell, value=value, label=label, color=color).pack(fill=tk.BOTH, expand=True)
    return wrap


# ─── BLOCO 4: PRÓXIMOS EVENTOS (com paginação) ───────────────────────
def _build_upcoming_events(parent, events, on_view_all=None):
    bg = parent["bg"]
    wrap = tk.Frame(parent, bg=bg)
    section_label(wrap, text="Próximos eventos",
                  action="Ver todas →",
                  action_command=on_view_all).pack(fill=tk.X, anchor=tk.W,
                                                    pady=(0, SPACING[3]))

    if not events:
        tk.Label(wrap, text="Nenhum evento esta semana.",
                 font=FONTS["body"], bg=bg,
                 fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=SPACING[4])
        return wrap

    PAGE_SIZE = 3
    state = {"page": 0}
    total_pages = (len(events) + PAGE_SIZE - 1) // PAGE_SIZE

    list_frame = tk.Frame(wrap, bg=bg)
    list_frame.pack(fill=tk.X)

    nav_frame = tk.Frame(wrap, bg=bg)

    def _render_page():
        for w in list_frame.winfo_children():
            w.destroy()
        start = state["page"] * PAGE_SIZE
        for ev in events[start:start + PAGE_SIZE]:
            event_card(list_frame, event=ev, compact=True).pack(
                fill=tk.X, pady=(0, SPACING[2]))

        if total_pages > 1:
            nav_frame.pack(fill=tk.X, pady=(SPACING[1], 0))
            for w in nav_frame.winfo_children():
                w.destroy()
            tk.Label(nav_frame,
                     text=f"{state['page'] + 1} / {total_pages}",
                     font=FONTS["small"], bg=bg,
                     fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[3]))
            if state["page"] > 0:
                button(nav_frame, text="← Anterior", kind="ghost",
                       command=_prev).pack(side=tk.LEFT, padx=(0, SPACING[2]))
            if state["page"] < total_pages - 1:
                button(nav_frame, text="Próximo →", kind="ghost",
                       command=_next).pack(side=tk.LEFT)

    def _prev():
        state["page"] -= 1
        _render_page()

    def _next():
        state["page"] += 1
        _render_page()

    _render_page()
    return wrap


# ─── BLOCO 5: ANIVERSARIANTES (com paginação) ────────────────────────
def _build_birthdays(parent, birthdays, on_send_congrats=None):
    bg = parent["bg"]
    wrap = tk.Frame(parent, bg=bg)
    section_label(wrap, text="Aniversariantes do mês",
                  action="Enviar parabéns →",
                  action_command=on_send_congrats).pack(fill=tk.X, anchor=tk.W,
                                                    pady=(0, SPACING[3]))

    container = tk.Frame(wrap, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["divider"],
                         highlightthickness=1)
    container.pack(fill=tk.X)

    if not birthdays:
        tk.Label(container, text="Nenhum aniversariante este mês.",
                 font=FONTS["body"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(pady=SPACING[6])
        return wrap

    PAGE_SIZE = 4
    state = {"page": 0}
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE

    nav_frame = tk.Frame(wrap, bg=bg)

    def _render_page():
        for w in container.winfo_children():
            w.destroy()

        start = state["page"] * PAGE_SIZE
        page_items = birthdays[start:start + PAGE_SIZE]

        for i, b in enumerate(page_items):
            line = tk.Frame(container, bg=COLORS["bg_card"])
            line.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[2])

            initials_badge(line, b["nome"], b["color"], size=32,
                           bg=COLORS["bg_card"]).pack(side=tk.LEFT,
                                                       padx=(0, SPACING[3]))

            # date_col must be packed RIGHT before info LEFT+expand
            date_col = tk.Frame(line, bg=COLORS["bg_card"])
            date_col.pack(side=tk.RIGHT, padx=(SPACING[2], 0))
            tk.Label(date_col, text=f"{b['dia']:02d}",
                     font=(FONTS["body"][0], 16, "bold"),
                     bg=COLORS["bg_card"],
                     fg=COLORS["warning"]).pack()
            tk.Label(date_col, text=b.get("mes", "---"),
                     font=FONTS["section"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack()

            info = tk.Frame(line, bg=COLORS["bg_card"])
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=truncate(b["nome"], 22),
                     font=FONTS["body_strong"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text"]).pack(anchor=tk.W)
            tk.Label(info, text=b["funcao"], font=FONTS["small"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(anchor=tk.W)

            if i < len(page_items) - 1:
                divider_line(container, soft=True).pack(fill=tk.X,
                                                         padx=SPACING[4])

        if total_pages > 1:
            nav_frame.pack(fill=tk.X, pady=(SPACING[1], 0))
            for w in nav_frame.winfo_children():
                w.destroy()
            tk.Label(nav_frame,
                     text=f"{state['page'] + 1} / {total_pages}",
                     font=FONTS["small"], bg=bg,
                     fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[3]))
            if state["page"] > 0:
                button(nav_frame, text="← Ant", kind="ghost",
                       command=_prev).pack(side=tk.LEFT, padx=(0, SPACING[2]))
            if state["page"] < total_pages - 1:
                button(nav_frame, text="Próx →", kind="ghost",
                       command=_next).pack(side=tk.LEFT)

    def _prev():
        state["page"] -= 1
        _render_page()

    def _next():
        state["page"] += 1
        _render_page()

    _render_page()
    return wrap


# ─── COMPOSIÇÃO PRINCIPAL ─────────────────────────────────────────────
def render(parent, *, user=None, totals=None, callbacks=None,
           events=None, birthdays=None, verse=None):
    user      = user or _USER
    totals    = totals or {"ativos": 0, "aniversariantes": 0, "eventos": 0, "visitantes": 0}
    callbacks = callbacks or {}
    events    = events or []
    birthdays = birthdays or []

    content = page_container(parent)

    _build_greeting_row(content, user, verse=verse).pack(fill=tk.X, pady=(0, SPACING[8]))
    _build_quick_actions(content, callbacks).pack(fill=tk.X, pady=(0, SPACING[8]))
    _build_stats_row(content, totals,
                     on_reports=callbacks.get("open_reports")).pack(fill=tk.X,
                                                                    pady=(0, SPACING[8]))

    cols = tk.Frame(content, bg=COLORS["bg_dark"])
    cols.pack(fill=tk.X)
    cols.columnconfigure(0, weight=3, uniform="cols")
    cols.columnconfigure(1, weight=2, uniform="cols")

    left = tk.Frame(cols, bg=COLORS["bg_dark"])
    left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING[5]))
    _build_upcoming_events(left, events,
                           on_view_all=callbacks.get("view_activities")).pack(fill=tk.X)

    right = tk.Frame(cols, bg=COLORS["bg_dark"])
    right.grid(row=0, column=1, sticky="nsew")
    _build_birthdays(right, birthdays,
                     on_send_congrats=callbacks.get("send_whatsapp")).pack(fill=tk.X)
