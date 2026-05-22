"""
pages/members.py
================
Tela de Membros com filtros funcionais e paginação (6 por página).
"""

import tkinter as tk
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, section_label,
    mini_stat, member_card, button, select, empty_state,
)

try:
    from core.members import GRUPOS as _GRUPOS
except Exception:
    _GRUPOS = ["Grupo de Mulheres", "Grupo dos Homens", "Grupo de Casais"]

PAGE_SIZE = 6

_MEMBERS_SAMPLE = []


def _build_filters(actions_frame, on_filter_change, callbacks):
    bg = actions_frame["bg"]

    tk.Label(actions_frame, text="Status:", bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[1]))
    select(actions_frame, value="Todos",
           options=["Todos", "Ativo", "Afastado", "Visitante"],
           on_change=lambda v: on_filter_change("status", v)
           ).pack(side=tk.LEFT, padx=(0, SPACING[3]))

    tk.Label(actions_frame, text="Função:", bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[1]))
    select(actions_frame, value="Todas",
           options=["Todas", "Membro", "Pastor(a)", "Presbítero",
                    "Diácono(a)", "Evangelista", "Líder de Célula",
                    "Louvor", "Obreiro(a)", "Secretário(a)", "Tesoureiro(a)"],
           on_change=lambda v: on_filter_change("funcao", v)
           ).pack(side=tk.LEFT, padx=(0, SPACING[3]))

    tk.Label(actions_frame, text="Grupo:", bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[1]))
    select(actions_frame, value="Todos",
           options=["Todos"] + list(_GRUPOS),
           on_change=lambda v: on_filter_change("grupo", v)
           ).pack(side=tk.LEFT, padx=(0, SPACING[4]))

    button(actions_frame, text="Novo Membro", kind="primary", icon="+",
           command=callbacks.get("new_member")).pack(side=tk.LEFT)


def _build_stats(parent, members):
    bg = parent["bg"]
    total     = len(members)
    ativos    = sum(1 for m in members if m["status"] == "Ativo")
    afastados = sum(1 for m in members if m["status"] == "Afastado")
    visitantes= sum(1 for m in members if m["status"] == "Visitante")

    row = tk.Frame(parent, bg=bg)
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="ms")

    stats = [
        (total,      "Total cadastrado", COLORS["text"]),
        (ativos,     "Ativos",           COLORS["success"]),
        (afastados,  "Afastados",        COLORS["danger"]),
        (visitantes, "Visitantes",       COLORS["warning"]),
    ]
    for i, (val, label, color) in enumerate(stats):
        cell = tk.Frame(row, bg=bg)
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 3 else SPACING[1]))
        mini_stat(cell, value=val, label=label, color=color).pack(fill=tk.BOTH, expand=True)
    return row


def _build_page(list_frame, nav_frame, members, callbacks, state):
    bg = COLORS["bg_dark"]

    # limpa área anterior
    for w in list_frame.winfo_children():
        w.destroy()
    for w in nav_frame.winfo_children():
        w.destroy()

    if not members:
        empty_state(
            list_frame, icon="👥",
            title="Nenhum membro corresponde aos filtros",
            body="Tente limpar os filtros ou cadastre o primeiro membro.",
            cta_label="Cadastrar primeiro membro",
            cta_command=callbacks.get("new_member"),
        ).pack(fill=tk.X)
        return

    total_pages = max(1, (len(members) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = state["page"]
    start = page * PAGE_SIZE
    page_items = members[start:start + PAGE_SIZE]

    grid = tk.Frame(list_frame, bg=bg)
    grid.pack(fill=tk.BOTH, expand=True)
    grid.columnconfigure(0, weight=1, uniform="g")
    grid.columnconfigure(1, weight=1, uniform="g")

    for i, m in enumerate(page_items):
        cell = tk.Frame(grid, bg=bg)
        cell.grid(row=i // 2, column=i % 2, sticky="nsew",
                  padx=(0 if i % 2 == 0 else SPACING[1],
                        SPACING[1] if i % 2 == 0 else 0),
                  pady=SPACING[2])
        card_cbs = {
            "edit":     callbacks.get("edit_member") and
                        (lambda mid=m["id"]: callbacks["edit_member"](mid)),
            "delete":   callbacks.get("delete_member") and
                        (lambda member=m: callbacks["delete_member"](member)),
            "whatsapp": callbacks.get("whatsapp_member") and
                        (lambda mid=m["id"]: callbacks["whatsapp_member"](mid)),
        }
        member_card(cell, member=m, callbacks=card_cbs).pack(fill=tk.BOTH, expand=True)

    # Navegação de páginas
    if total_pages > 1:
        nav_frame.pack(fill=tk.X, pady=(SPACING[3], 0))
        tk.Label(nav_frame,
                 text=f"Página {page + 1} de {total_pages}",
                 font=FONTS["small"], bg=bg,
                 fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[3]))
        if page > 0:
            button(nav_frame, text="← Anterior", kind="ghost",
                   command=lambda: _go(state, -1, list_frame, nav_frame, members, callbacks)
                   ).pack(side=tk.LEFT, padx=(0, SPACING[2]))
        if page < total_pages - 1:
            button(nav_frame, text="Próximo →", kind="ghost",
                   command=lambda: _go(state, +1, list_frame, nav_frame, members, callbacks)
                   ).pack(side=tk.LEFT)


def _go(state, delta, list_frame, nav_frame, members, callbacks):
    state["page"] += delta
    _build_page(list_frame, nav_frame, members, callbacks, state)


def render(parent, *, members=None, callbacks=None):
    all_members = members if members is not None else _MEMBERS_SAMPLE
    callbacks   = callbacks or {}
    bg          = COLORS["bg_dark"]

    state = {"status": "Todos", "funcao": "Todas", "grupo": "Todos", "page": 0}

    content = page_container(parent)

    # Header
    hdr = screen_header(
        content, icon="👥",
        title="Membros da Igreja",
        subtitle=f"{len(all_members)} pessoas cadastradas no sistema",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))
    _build_filters(hdr["actions"],
                   on_filter_change=lambda k, v: _on_filter(k, v),
                   callbacks=callbacks)

    # Stats (sempre mostra totais gerais)
    stats_wrap = tk.Frame(content, bg=bg)
    stats_wrap.pack(fill=tk.X, pady=(0, SPACING[5]))

    # Cabeçalho da lista + paginação label
    list_header = tk.Frame(content, bg=bg)
    list_header.pack(fill=tk.X, pady=(0, SPACING[3]))
    list_title_lbl = tk.Label(list_header, text="LISTA DE MEMBROS",
                               font=FONTS["section"], bg=bg,
                               fg=COLORS["text_muted"])
    list_title_lbl.pack(side=tk.LEFT)
    page_lbl = tk.Label(list_header, text="",
                         font=FONTS["small"], bg=bg,
                         fg=COLORS["accent"])
    page_lbl.pack(side=tk.RIGHT)

    # Área de cards
    list_frame = tk.Frame(content, bg=bg)
    list_frame.pack(fill=tk.BOTH, expand=True)

    nav_frame = tk.Frame(content, bg=bg)

    def _filtered():
        result = all_members
        if state["status"] != "Todos":
            result = [m for m in result if m["status"] == state["status"]]
        if state["funcao"] != "Todas":
            result = [m for m in result if m["funcao"] == state["funcao"]]
        if state["grupo"] != "Todos":
            result = [m for m in result if m.get("grupo") == state["grupo"]]
        return result

    def _refresh():
        filtered = _filtered()
        total_pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
        page_lbl.config(text=f"Página {state['page'] + 1} de {total_pages}")

        for w in stats_wrap.winfo_children():
            w.destroy()
        _build_stats(stats_wrap, filtered).pack(fill=tk.X)

        _build_page(list_frame, nav_frame, filtered, callbacks, state)

    def _on_filter(key, value):
        state[key] = value
        state["page"] = 0
        _refresh()

    _refresh()
