"""
pages/members.py
================
Tela de Membros. Substitui a `MembersWindow` atual.

ESTRUTURA:
  1. screen_header com filtros (Status, Função) + botões (Editar, Novo Membro)
  2. mini_stats row (Total, Ativos, Afastados, Visitantes)
  3. lista de member_card em grid 2-col COM scroll
  4. empty_state se a query não retornar nada
"""

import tkinter as tk
from ..ui import COLORS, SPACING
from ..ui.components import (
    page_container, screen_header, section_label,
    mini_stat, member_card, button, select, empty_state,
)


def _build_filters(actions_frame, on_filter_change, callbacks):
    """Adiciona Status + Função + botões dentro do actions_frame do header."""
    bg = actions_frame["bg"]

    # Status
    tk.Label(actions_frame, text="Status:", bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[1]))
    status_cb = select(actions_frame, value="Todos",
                       options=["Todos", "Ativo", "Afastado", "Visitante"],
                       on_change=lambda v: on_filter_change("status", v))
    status_cb.pack(side=tk.LEFT, padx=(0, SPACING[3]))

    # Função
    tk.Label(actions_frame, text="Função:", bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, SPACING[1]))
    funcao_cb = select(actions_frame, value="Todas",
                       options=["Todas", "Membro", "Diácono", "Presbítero"],
                       on_change=lambda v: on_filter_change("funcao", v))
    funcao_cb.pack(side=tk.LEFT, padx=(0, SPACING[4]))

    # Botões
    button(actions_frame, text="Novo Membro", kind="primary",
           icon="+",
           command=callbacks.get("new_member")).pack(side=tk.LEFT)


def _build_stats(parent, members):
    total = len(members)
    ativos = sum(1 for m in members if m["status"] == "Ativo")
    afastados = sum(1 for m in members if m["status"] == "Afastado")
    visitantes = sum(1 for m in members if m["status"] == "Visitante")

    row = tk.Frame(parent, bg=parent["bg"])
    for c in range(4):
        row.columnconfigure(c, weight=1, uniform="ms")

    stats = [
        (total,      "Total cadastrado", COLORS["text"]),
        (ativos,     "Ativos",           COLORS["success"]),
        (afastados,  "Afastados",        COLORS["danger"]),
        (visitantes, "Visitantes",       COLORS["warning"]),
    ]
    for i, (val, label, color) in enumerate(stats):
        cell = tk.Frame(row, bg=parent["bg"])
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 3 else SPACING[1]))
        mini_stat(cell, value=val, label=label, color=color).pack(fill=tk.BOTH, expand=True)
    return row


def _build_list(parent, members, callbacks):
    if not members:
        empty_state(
            parent,
            icon="👥",
            title="Nenhum membro corresponde aos filtros",
            body=("Tente limpar os filtros, ou cadastre o primeiro membro "
                  "para começar."),
            cta_label="Cadastrar primeiro membro",
            cta_command=callbacks.get("new_member"),
        ).pack(fill=tk.X)
        return

    grid = tk.Frame(parent, bg=parent["bg"])
    grid.pack(fill=tk.BOTH, expand=True)
    grid.columnconfigure(0, weight=1, uniform="g")
    grid.columnconfigure(1, weight=1, uniform="g")

    for i, m in enumerate(members):
        cell = tk.Frame(grid, bg=parent["bg"])
        cell.grid(row=i // 2, column=i % 2, sticky="nsew",
                  padx=(0 if i % 2 == 0 else SPACING[2] // 2,
                        SPACING[2] // 2 if i % 2 == 0 else 0),
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


# ─── DATA EXEMPLO — substituir pela query real ─────────────────────────
_MEMBERS_SAMPLE = [
    {"id": 1, "nome": "David Cavalcante Dos Santos",  "funcao": "Diácono",
     "status": "Ativo",     "tel": "(11) 95272-0101",
     "email": "deezinft@gmail.com",   "niver_dia": 8,  "niver_mes": "Nov",
     "color": "#667eea"},
    {"id": 2, "nome": "Tamiris Gomes da Silva",       "funcao": "Membro",
     "status": "Ativo",     "tel": "(11) 94664-3699",
     "email": "tamygomes142@gmail.com","niver_dia": 12, "niver_mes": "Abr",
     "color": "#51cf66"},
    {"id": 3, "nome": "Pr. Marcos Oliveira de Lima",  "funcao": "Presbítero",
     "status": "Ativo",     "tel": "(11) 97781-2030",
     "email": "marcos.lima@vidaplena.com", "niver_dia": 22, "niver_mes": "Fev",
     "color": "#9b59b6"},
    {"id": 4, "nome": "Lucas Pereira",                "funcao": "Diácono",
     "status": "Afastado",  "tel": "(11) 99445-1278",
     "email": "lucasp@gmail.com",      "niver_dia": 17, "niver_mes": "Mai",
     "color": "#667eea"},
]


def render(parent, *, members=None, callbacks=None):
    members   = members if members is not None else _MEMBERS_SAMPLE
    callbacks = callbacks or {}

    content = page_container(parent)

    hdr = screen_header(
        content,
        icon="👥",
        title="Membros da Igreja",
        subtitle=f"{len(members)} pessoas cadastradas no sistema",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))
    _build_filters(hdr["actions"], on_filter_change=lambda k, v: None,
                   callbacks=callbacks)

    _build_stats(content, members).pack(fill=tk.X, pady=(0, SPACING[6]))

    section_label(content, text="Lista de membros",
                  action="Página 1 de 1").pack(fill=tk.X,
                                                pady=(0, SPACING[3]))
    _build_list(content, members, callbacks)
