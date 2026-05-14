"""
pages/users.py
==============
Tela de Gerenciar Usuários. Tabela refinada usando o tema do app.

ESTRUTURA:
  1. screen_header com botão Novo Usuário
  2. mini_stats (Total / Ativos / Administradores)
  3. tabela custom com colunas de largura fixa (alinhamento garantido)
  4. aviso final sobre permissões
"""

import tkinter as tk
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, mini_stat,
    initials_badge, badge, pill, icon_button, button,
    divider_line,
)
from ..ui.helpers import truncate


_USERS_SAMPLE = [
    {"id": 1, "nome": "admin",
     "email": "admin@igreja.com",       "nivel": "Admin",
     "ativo": True,  "voce": False, "color": "#667eea"},
    {"id": 2, "nome": "David Cavalcante",
     "email": "deezinft@gmail.com",     "nivel": "Admin",
     "ativo": True,  "voce": True,  "color": "#00d4ff"},
]

# Larguras fixas em pixels — garantem alinhamento entre header e linhas
_W = {"nome": 260, "email": 230, "nivel": 120, "status": 110, "acoes": 130}


def _build_stats(parent, users):
    total  = len(users)
    ativos = sum(1 for u in users if u["ativo"])
    admins = sum(1 for u in users if u["nivel"] == "Admin")

    row = tk.Frame(parent, bg=parent["bg"])
    for c in range(3):
        row.columnconfigure(c, weight=1, uniform="us")

    items = [
        (total,  "Total de usuários", COLORS["text"]),
        (ativos, "Ativos",            COLORS["success"]),
        (admins, "Administradores",   COLORS["accent"]),
    ]
    for i, (val, label, color) in enumerate(items):
        cell = tk.Frame(row, bg=parent["bg"])
        cell.grid(row=0, column=i, sticky="nsew",
                  padx=(0 if i == 0 else SPACING[1],
                        0 if i == 2 else SPACING[1]))
        mini_stat(cell, value=val, label=label, color=color).pack(fill=tk.BOTH, expand=True)
    return row


def _cell(row, w, bg):
    """Frame de célula com largura fixa e pack_propagate False."""
    f = tk.Frame(row, bg=bg, width=w)
    f.pack(side=tk.LEFT)
    f.pack_propagate(False)
    return f


def _build_table_header(parent):
    bg = COLORS["bg_card_raised"]
    row = tk.Frame(parent, bg=bg)

    for key, w in _W.items():
        label = {"nome": "NOME", "email": "E-MAIL", "nivel": "NÍVEL",
                 "status": "STATUS", "acoes": "AÇÕES"}[key]
        c = _cell(row, w, bg)
        tk.Label(c, text=label, font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"],
                 anchor=tk.W).pack(anchor=tk.W, padx=SPACING[3], pady=SPACING[3])
    return row


def _build_user_row(parent, user, callbacks):
    bg = COLORS["bg_card"]
    row = tk.Frame(parent, bg=bg)

    # ── Nome ──────────────────────────────────────────────
    nome_cell = _cell(row, _W["nome"], bg)
    nome_inner = tk.Frame(nome_cell, bg=bg)
    nome_inner.pack(side=tk.LEFT, padx=SPACING[3], pady=SPACING[3])
    initials_badge(nome_inner, user["nome"], user["color"],
                   size=28, bg=bg).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    tk.Label(nome_inner, text=truncate(user["nome"], 18),
             font=FONTS["body_strong"], bg=bg,
             fg=COLORS["text"]).pack(side=tk.LEFT)
    if user["voce"]:
        tk.Label(nome_inner, text="(você)",
                 font=FONTS["small_bold"], bg=bg,
                 fg=COLORS["accent"]).pack(side=tk.LEFT, padx=(SPACING[2], 0))

    # ── E-mail ────────────────────────────────────────────
    email_cell = _cell(row, _W["email"], bg)
    tk.Label(email_cell, text=truncate(user["email"], 26),
             font=FONTS["mono"], bg=bg,
             fg=COLORS["text_dim"],
             anchor=tk.W).pack(anchor=tk.W, padx=SPACING[3], pady=SPACING[3])

    # ── Nível ─────────────────────────────────────────────
    nivel_cell = _cell(row, _W["nivel"], bg)
    nivel_inner = tk.Frame(nivel_cell, bg=bg)
    nivel_inner.pack(side=tk.LEFT, padx=SPACING[3], pady=SPACING[3])
    nivel_kind = "Planejado" if user["nivel"] == "Admin" else "Membro"
    badge(nivel_inner, user["nivel"], kind=nivel_kind).pack(side=tk.LEFT)

    # ── Status ────────────────────────────────────────────
    status_cell = _cell(row, _W["status"], bg)
    status_inner = tk.Frame(status_cell, bg=bg)
    status_inner.pack(side=tk.LEFT, padx=SPACING[3], pady=SPACING[3])
    pill(status_inner,
         "Ativo" if user["ativo"] else "Inativo",
         dot_color=COLORS["success"] if user["ativo"] else COLORS["text_muted"],
         text_color=COLORS["success"] if user["ativo"] else COLORS["text_muted"],
         ).pack(side=tk.LEFT)

    # ── Ações ─────────────────────────────────────────────
    acoes_cell = _cell(row, _W["acoes"], bg)
    acoes_inner = tk.Frame(acoes_cell, bg=bg)
    acoes_inner.pack(side=tk.LEFT, padx=SPACING[3], pady=SPACING[3])

    uid = user["id"]
    icon_button(acoes_inner, icon="✏", tooltip="Editar", size=30,
                command=callbacks.get("edit_user") and
                        (lambda u=user: callbacks["edit_user"](u["id"]))
                ).pack(side=tk.LEFT, padx=2)
    icon_button(acoes_inner, icon="🔑", tooltip="Resetar senha", size=30,
                command=callbacks.get("reset_password") and
                        (lambda u=user: callbacks["reset_password"](u["id"], u["nome"]))
                ).pack(side=tk.LEFT, padx=2)
    if not user["voce"]:
        icon_button(
            acoes_inner,
            icon="⏸" if user["ativo"] else "▶",
            tooltip="Desativar" if user["ativo"] else "Ativar",
            size=30,
            color=COLORS["warning"] if user["ativo"] else COLORS["success"],
            command=callbacks.get("toggle_active") and
                    (lambda u=user: callbacks["toggle_active"](u["id"])),
        ).pack(side=tk.LEFT, padx=2)
        icon_button(acoes_inner, icon="🗑", tooltip="Excluir", size=30,
                    color=COLORS["danger"],
                    command=callbacks.get("delete_user") and
                            (lambda u=user: callbacks["delete_user"](u))
                    ).pack(side=tk.LEFT, padx=2)

    return row


def render(parent, *, users=None, callbacks=None):
    users     = users if users is not None else _USERS_SAMPLE
    callbacks = callbacks or {}

    content = page_container(parent)

    # ─── Header ───────────────────────────────────────────────────
    hdr = screen_header(
        content,
        icon="👤",
        title="Gerenciar Usuários",
        subtitle="Quem pode acessar o sistema",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))
    button(hdr["actions"], text="Novo Usuário", kind="primary",
           icon="+",
           command=callbacks.get("new_user")).pack(side=tk.LEFT)

    # ─── Stats ────────────────────────────────────────────────────
    _build_stats(content, users).pack(fill=tk.X, pady=(0, SPACING[6]))

    # ─── Tabela ───────────────────────────────────────────────────
    table = tk.Frame(content, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["divider"],
                     highlightthickness=1)
    table.pack(fill=tk.X, pady=(0, SPACING[5]))

    _build_table_header(table).pack(fill=tk.X)
    divider_line(table).pack(fill=tk.X)

    for i, u in enumerate(users):
        _build_user_row(table, u, callbacks).pack(fill=tk.X)
        if i < len(users) - 1:
            divider_line(table, soft=True).pack(fill=tk.X)

    # ─── Aviso final ──────────────────────────────────────────────
    notice = tk.Frame(content, bg=COLORS["bg_card"],
                      highlightbackground=COLORS["divider"],
                      highlightthickness=1)
    notice.pack(fill=tk.X)
    notice_inner = tk.Frame(notice, bg=COLORS["bg_card"])
    notice_inner.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[3])
    tk.Label(notice_inner, text="ℹ", font=(FONTS["body"][0], 14),
             bg=COLORS["bg_card"], fg=COLORS["warning"]).pack(side=tk.LEFT,
                                                               padx=(0, SPACING[2]))
    tk.Label(notice_inner,
             text=("Apenas usuários com nível Admin podem criar ou "
                   "alterar outros usuários."),
             font=FONTS["small"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)
