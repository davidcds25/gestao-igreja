"""
pages/activities.py
===================
Tela de Atividades e Eventos.

ESTRUTURA:
  1. screen_header com Ordenar + Nova Atividade
  2. tabs (Próximas | Realizadas | Canceladas) com contadores
  3. Próximas → lista plana com botões ✏ ✓ ✗
  4. Realizadas / Canceladas → agrupadas por mês, só botão ✏
"""

import tkinter as tk
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, tabs as build_tabs,
    activity_row, empty_state, button, select, section_label, divider_line,
)

_MESES_FULL = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _sort_activities(items, order):
    if order == "Data ↑":
        return sorted(items, key=lambda a: a.get("data_iso", ""))
    if order == "Data ↓":
        return sorted(items, key=lambda a: a.get("data_iso", ""), reverse=True)
    if order == "Status":
        return sorted(items, key=lambda a: a.get("status", ""))
    if order == "Local":
        return sorted(items, key=lambda a: a.get("local", "").lower())
    return items


def _group_by_month(items):
    """Retorna [(label_mes, [items]), ...] do mais recente ao mais antigo."""
    groups: dict = {}
    order: list  = []
    for item in items:
        key = (item.get("ano", 0), item.get("mes_num", 0))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(item)
    sorted_keys = sorted(groups.keys(), reverse=True)
    result = []
    for (ano, mes_num) in sorted_keys:
        if mes_num > 0:
            label = f"{_MESES_FULL[mes_num - 1]} de {ano}"
        else:
            label = "Sem data"
        result.append((label, groups[(ano, mes_num)]))
    return result


def render(parent, *, activities=None, callbacks=None):
    activities = activities if activities is not None else []
    callbacks  = callbacks or {}

    content = page_container(parent)

    # ─── Header ───────────────────────────────────────────────────
    hdr = screen_header(
        content,
        icon="📋",
        title="Atividades e Eventos",
        subtitle="Agenda da igreja — próximos 30 dias",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))

    state = {"order": "Data ↑", "tab": "proximas"}

    tk.Label(hdr["actions"], text="Ordenar:",
             bg=hdr["actions"]["bg"], fg=COLORS["text_muted"]).pack(
                 side=tk.LEFT, padx=(0, SPACING[1]))

    def _on_sort_change(value):
        state["order"] = value
        _render_list(state["tab"])

    select(hdr["actions"], value="Data ↑",
           options=["Data ↑", "Data ↓", "Status", "Local"],
           on_change=_on_sort_change).pack(side=tk.LEFT, padx=(0, SPACING[4]))

    button(hdr["actions"], text="Nova Atividade", kind="primary", icon="+",
           command=callbacks.get("new_activity")).pack(side=tk.LEFT)

    # ─── Tabs ─────────────────────────────────────────────────────
    proximas   = [a for a in activities if a["status"] == "Planejado"]
    realizadas = [a for a in activities if a["status"] == "Realizado"]
    canceladas = [a for a in activities if a["status"] == "Cancelado"]

    tab_row = tk.Frame(content, bg=COLORS["bg_dark"])
    tab_row.pack(fill=tk.X, pady=(0, SPACING[4]))

    list_container = tk.Frame(content, bg=COLORS["bg_dark"])
    list_container.pack(fill=tk.BOTH, expand=True)

    def _render_list(tab):
        state["tab"] = tab
        for w in list_container.winfo_children():
            w.destroy()

        if tab == "proximas":
            items = _sort_activities(proximas, state["order"])
            if not items:
                empty_state(
                    list_container,
                    icon="📅",
                    title="Nenhum evento agendado",
                    body="Que tal começar planejando o próximo culto ou encontro?",
                    cta_label="Criar primeira atividade",
                    cta_command=callbacks.get("new_activity"),
                ).pack(fill=tk.X)
                return
            for ev in items:
                ev_cbs = {
                    "edit":     callbacks.get("edit_activity") and
                                (lambda aid=ev["id"]: callbacks["edit_activity"](aid)),
                    "done":     callbacks.get("done_activity") and
                                (lambda aid=ev["id"]: callbacks["done_activity"](aid)),
                    "cancel":   callbacks.get("cancel_activity") and
                                (lambda aid=ev["id"]: callbacks["cancel_activity"](aid)),
                    "whatsapp": callbacks.get("whatsapp_activity") and
                                (lambda e=ev: callbacks["whatsapp_activity"](e)),
                }
                activity_row(list_container, event=ev,
                             compact=False, callbacks=ev_cbs).pack(
                                 fill=tk.X, pady=(0, SPACING[2]))

        else:
            # Realizadas ou Canceladas — agrupadas por mês, só botão editar
            raw = realizadas if tab == "realizadas" else canceladas
            items = _sort_activities(raw, state["order"])
            if not items:
                empty_state(
                    list_container,
                    icon="✓" if tab == "realizadas" else "✗",
                    title=("Nenhum evento realizado ainda"
                           if tab == "realizadas" else "Nenhum evento cancelado"),
                    body="Eventos marcados aparecerão aqui agrupados por mês.",
                ).pack(fill=tk.X)
                return

            groups = _group_by_month(items)
            for month_label, month_items in groups:
                _render_month_header(list_container, month_label)
                for ev in month_items:
                    ev_cbs = {
                        "edit": callbacks.get("edit_activity") and
                                (lambda aid=ev["id"]: callbacks["edit_activity"](aid)),
                    }
                    activity_row(list_container, event=ev,
                                 compact=False, callbacks=ev_cbs).pack(
                                     fill=tk.X, pady=(0, SPACING[2]))

    tabs_widget = build_tabs(
        tab_row,
        options=[
            ("proximas",   "Próximas",   len(proximas)),
            ("realizadas", "Realizadas", len(realizadas)),
            ("canceladas", "Canceladas", len(canceladas)),
        ],
        value="proximas",
        on_change=_render_list,
    )
    tabs_widget.pack(side=tk.LEFT)

    tk.Label(tab_row, text="  Atualizado há 2 minutos",
             font=FONTS["small"],
             bg=COLORS["bg_dark"],
             fg=COLORS["text_muted"]).pack(side=tk.RIGHT)

    _render_list("proximas")


def _render_month_header(parent, label):
    bg = COLORS["bg_dark"]
    row = tk.Frame(parent, bg=bg)
    row.pack(fill=tk.X, pady=(SPACING[4], SPACING[2]))

    tk.Frame(row, bg=COLORS["divider_soft"], height=1).pack(
        side=tk.LEFT, fill=tk.Y, expand=True, pady=8)
    tk.Label(row, text=f"  {label.upper()}  ",
             font=FONTS["section"], bg=bg,
             fg=COLORS["text_muted"]).pack(side=tk.LEFT)
    tk.Frame(row, bg=COLORS["divider_soft"], height=1).pack(
        side=tk.LEFT, fill=tk.Y, expand=True, pady=8)
