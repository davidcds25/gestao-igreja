"""
pages/prayers.py
================
Tela de Orações — abas Pendentes / Respondidas / Arquivadas, KPIs e cards.
"""

import tkinter as tk
from datetime import datetime, date as _date_cls

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, mini_stat,
    button, select, empty_state, divider_line,
    tabs as build_tabs,
)
from ..ui.helpers import truncate

PAGE_SIZE = 3

_MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]

_CANCELLED = object()


def _ask_comment(root, *, title, field_label, confirm_text, confirm_kind="primary"):
    """Small blocking dialog to capture an optional comment before a status change.
    Returns (confirmed: bool, comment: str | None)."""
    result = [_CANCELLED]
    bg = COLORS["bg_card"]

    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=bg)
    win.resizable(False, False)
    win.grab_set()

    w, h = 480, 290
    win.update_idletasks()
    px = root.winfo_rootx() + (root.winfo_width()  - w) // 2
    py = root.winfo_rooty() + (root.winfo_height() - h) // 2
    win.geometry(f"{w}x{h}+{px}+{py}")

    body = tk.Frame(win, bg=bg, padx=SPACING[6], pady=SPACING[5])
    body.pack(fill=tk.BOTH, expand=True)

    tk.Label(body, text=title,
             font=FONTS["body_strong"], bg=bg, fg=COLORS["text"]
             ).pack(anchor=tk.W, pady=(0, SPACING[3]))

    tk.Label(body, text=f"{field_label} (opcional):",
             font=FONTS["small"], bg=bg, fg=COLORS["text_muted"]
             ).pack(anchor=tk.W, pady=(0, SPACING[1]))

    txt_bg = COLORS["input_bg"]
    txt_frame = tk.Frame(body, bg=txt_bg,
                         highlightbackground=COLORS["divider"],
                         highlightthickness=1)
    txt_frame.pack(fill=tk.X, pady=(0, SPACING[4]))
    txt = tk.Text(txt_frame, height=4,
                  font=FONTS["body"],
                  bg=txt_bg, fg=COLORS["text"],
                  insertbackground=COLORS["text"],
                  relief=tk.FLAT, bd=0, wrap=tk.WORD,
                  padx=10, pady=8)
    txt.pack(fill=tk.X)

    btn_row = tk.Frame(body, bg=bg)
    btn_row.pack(fill=tk.X)

    def _cancel(_e=None):
        result[0] = _CANCELLED
        win.destroy()

    def _confirm():
        result[0] = txt.get("1.0", tk.END).strip()
        win.destroy()

    button(btn_row, text="Cancelar", kind="ghost",
           command=_cancel).pack(side=tk.RIGHT, padx=(SPACING[2], 0))
    button(btn_row, text=confirm_text, kind=confirm_kind,
           command=_confirm).pack(side=tk.RIGHT)

    win.bind("<Escape>", _cancel)
    txt.focus_set()
    win.wait_window()

    if result[0] is _CANCELLED:
        return False, None
    return True, result[0] or None

_STATUS_COLOR = {
    "Ativa":      COLORS["accent"],
    "Respondida": COLORS["success"],
    "Arquivada":  COLORS["text_muted"],
}

_CAT_COLOR = {
    "Saúde":          COLORS.get("success",  "#22a05a"),
    "Família":        COLORS.get("accent",   "#00d4ff"),
    "Finanças":       COLORS.get("warning",  "#d28200"),
    "Trabalho":       COLORS.get("accent2",  "#0891b2"),
    "Espiritual":     COLORS.get("purple",   "#9b59b6"),
    "Relacionamento": "#e07b4f",
    "Agradecimento":  "#27ae60",
    "Outros":         COLORS.get("text_muted", "#888888"),
}

_PRIV_ICON = {
    "Pública":      "🌐",
    "Restrita":     "🔒",
    "Confidencial": "🔐",
}


def _pill(parent, text, color, bg=None):
    bg = bg or COLORS["bg_card"]
    lbl = tk.Label(parent, text=text,
                   font=FONTS["section"],
                   bg=bg, fg=color,
                   padx=SPACING[2], pady=2,
                   relief=tk.FLAT)
    lbl.configure(highlightbackground=color, highlightthickness=1)
    return lbl


def _prayer_card(parent, oracao, *, on_edit=None, on_delete=None,
                 on_respond=None, on_archive=None):
    bg    = COLORS["bg_card"]
    outer = tk.Frame(parent, bg=bg,
                     highlightbackground=COLORS["divider"],
                     highlightthickness=1)

    inner = tk.Frame(outer, bg=bg)
    inner.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[4])

    # ── Linha superior: data + pills + status ─────────────────────────
    top = tk.Frame(inner, bg=bg)
    top.pack(fill=tk.X, pady=(0, SPACING[2]))

    try:
        raw = oracao["data_cadastro"] or ""
        dt  = datetime.fromisoformat(raw[:10])
        date_str = dt.strftime("%d/%m/%Y")
    except Exception:
        date_str = "--"

    tk.Label(top, text=date_str,
             font=FONTS["small"],
             bg=bg, fg=COLORS["text_muted"]
             ).pack(side=tk.LEFT, padx=(0, SPACING[3]))

    cat   = oracao["categoria"] or "Outros"
    color = _CAT_COLOR.get(cat, COLORS["accent"])
    _pill(top, cat, color, bg=bg).pack(side=tk.LEFT, padx=(0, SPACING[1]))

    priv      = oracao["privacidade"] or "Pública"
    priv_icon = _PRIV_ICON.get(priv, "")
    priv_col  = {"Pública": COLORS["success"],
                 "Restrita": COLORS["warning"],
                 "Confidencial": COLORS["danger"]}.get(priv, COLORS["text_muted"])
    _pill(top, f"{priv_icon} {priv}", priv_col, bg=bg).pack(side=tk.LEFT)

    st     = oracao["status"] or "Ativa"
    st_col = _STATUS_COLOR.get(st, COLORS["text_muted"])
    tk.Label(top, text=f"● {st}",
             font=FONTS["small_bold"],
             bg=bg, fg=st_col
             ).pack(side=tk.RIGHT)

    # ── Linha do solicitante ──────────────────────────────────────────
    mid = tk.Frame(inner, bg=bg)
    mid.pack(fill=tk.X, pady=(0, SPACING[1]))

    nome = oracao["solicitante_nome"] or "—"
    tk.Label(mid, text=truncate(nome, 40),
             font=FONTS["body_strong"],
             bg=bg, fg=COLORS["text"]
             ).pack(side=tk.LEFT)

    membro_nome = oracao["membro_nome"]
    if membro_nome and membro_nome != nome:
        tk.Label(mid, text=f"  ·  membro: {truncate(membro_nome, 25)}",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]
                 ).pack(side=tk.LEFT)

    ctx = oracao["contexto"]
    if ctx:
        tk.Label(mid, text=ctx,
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_dim"]
                 ).pack(side=tk.RIGHT)

    # ── Motivo ────────────────────────────────────────────────────────
    motivo = oracao["motivo"] or ""
    tk.Label(inner, text=truncate(motivo, 120),
             font=FONTS["body"],
             bg=bg, fg=COLORS["text_muted"],
             anchor=tk.W, justify=tk.LEFT
             ).pack(fill=tk.X, pady=(0, SPACING[2]))

    # ── Testemunho (só quando Respondida) ─────────────────────────────
    if st == "Respondida" and oracao["testemunho"]:
        test_frame = tk.Frame(inner, bg=COLORS["bg_card_raised"],
                              highlightbackground=COLORS["success"],
                              highlightthickness=1)
        test_frame.pack(fill=tk.X, pady=(0, SPACING[2]))
        tk.Label(test_frame,
                 text=f"Resposta: {truncate(oracao['testemunho'], 100)}",
                 font=FONTS["small"],
                 bg=COLORS["bg_card_raised"],
                 fg=COLORS["success"],
                 anchor=tk.W, justify=tk.LEFT,
                 padx=SPACING[3], pady=SPACING[1]
                 ).pack(fill=tk.X)

    # ── Ações ─────────────────────────────────────────────────────────
    act = tk.Frame(inner, bg=bg)
    act.pack(fill=tk.X)

    resp = oracao["responsavel"]
    if resp:
        tk.Label(act, text=f"Responsável: {resp}",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_dim"]
                 ).pack(side=tk.LEFT)

    # CRUD buttons (right, packed right-to-left so Excluir stays rightmost)
    if on_delete:
        button(act, text="Excluir", kind="ghost",
               command=on_delete).pack(side=tk.RIGHT, padx=(SPACING[2], 0))
    if on_edit:
        button(act, text="Editar", kind="ghost",
               command=on_edit).pack(side=tk.RIGHT, padx=(SPACING[2], 0))

    # Separator between CRUD and quick-action buttons
    if (on_respond or on_archive) and (on_edit or on_delete):
        tk.Frame(act, bg=COLORS["divider"], width=1
                 ).pack(side=tk.RIGHT, fill=tk.Y, padx=SPACING[2])

    # Quick-action buttons — shown based on current status
    if st in ("Ativa", "Respondida") and on_archive:
        button(act, text="Arquivar", kind="ghost", icon="📁",
               command=on_archive).pack(side=tk.RIGHT, padx=(SPACING[2], 0))
    if st == "Ativa" and on_respond:
        button(act, text="Respondida", kind="success", icon="✓",
               command=on_respond).pack(side=tk.RIGHT)

    return outer


def render(parent, *, callbacks=None, current_user_id=None):
    callbacks = callbacks or {}
    bg        = COLORS["bg_dark"]

    content = page_container(parent)

    _SORT_MAP = {
        "Data ↓":    "data_desc",
        "Data ↑":    "data_asc",
        "Categoria": "categoria",
        "Nome A→Z":  "nome",
    }

    state = {
        "tab":       "ativas",
        "categoria": "Todas",
        "sort":      "data_desc",
        "page":      0,
        "mes":       _date_cls.today().replace(day=1),
        "lists":     {"ativas": [], "respondidas": [], "arquivadas": []},
    }

    # ── Header ────────────────────────────────────────────────────────
    hdr = screen_header(
        content,
        icon="🙏",
        title="Orações",
        subtitle="Pedidos e registros de oração da comunidade",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))
    button(hdr["actions"], text="Nova Oração", kind="primary", icon="+",
           command=callbacks.get("new_prayer")).pack(side=tk.LEFT)

    # ── KPIs ──────────────────────────────────────────────────────────
    kpi_wrap = tk.Frame(content, bg=bg)
    kpi_wrap.pack(fill=tk.X, pady=(0, SPACING[4]))

    # Month navigation bar
    mes_bar = tk.Frame(content, bg=bg)
    mes_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    _mes_lbl = tk.Label(mes_bar, text="",
                        font=FONTS["body_strong"], bg=bg, fg=COLORS["text"])

    button(mes_bar, text="◄ Anterior", kind="ghost",
           command=lambda: _go_mes(-1)).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    _mes_lbl.pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(mes_bar, text="Próximo ►", kind="ghost",
           command=lambda: _go_mes(+1)).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(mes_bar, text="Hoje", kind="ghost",
           command=lambda: _go_hoje()).pack(side=tk.LEFT, padx=(SPACING[3], 0))

    tab_row = tk.Frame(content, bg=bg)
    tab_row.pack(fill=tk.X, pady=(0, SPACING[4]))

    tabs_holder = tk.Frame(tab_row, bg=bg)
    tabs_holder.pack(side=tk.LEFT)

    from core.prayers import CATEGORIAS
    select(tab_row, value="Todas",
           options=["Todas"] + CATEGORIAS,
           on_change=lambda v: _on_filter("categoria", v)
           ).pack(side=tk.RIGHT)
    tk.Label(tab_row, text="Categoria:",
             bg=bg, fg=COLORS["text_muted"]
             ).pack(side=tk.RIGHT, padx=(0, SPACING[1]))

    select(tab_row, value="Data ↓",
           options=list(_SORT_MAP),
           on_change=lambda v: _on_filter("sort", _SORT_MAP[v])
           ).pack(side=tk.RIGHT, padx=(0, SPACING[3]))
    tk.Label(tab_row, text="Ordenar:",
             bg=bg, fg=COLORS["text_muted"]
             ).pack(side=tk.RIGHT, padx=(0, SPACING[1]))

    # ── Lista + navegação ─────────────────────────────────────────────
    list_box = tk.Frame(content, bg=bg)
    list_box.pack(fill=tk.BOTH, expand=True)

    nav_frame = tk.Frame(content, bg=bg)

    # ── helpers ───────────────────────────────────────────────────────
    def _update_mes_nav():
        m    = state["mes"]
        hoje = _date_cls.today().replace(day=1)
        txt  = f"{_MESES_PT[m.month - 1]} {m.year}"
        if m == hoje:
            txt += "  ●"
        _mes_lbl.configure(text=txt)

    def _go_mes(delta):
        m     = state["mes"]
        month = m.month + delta
        year  = m.year
        while month > 12: month -= 12; year += 1
        while month < 1:  month += 12; year -= 1
        state["mes"]  = _date_cls(year, month, 1)
        state["page"] = 0
        _refresh()

    def _go_hoje():
        state["mes"]  = _date_cls.today().replace(day=1)
        state["page"] = 0
        _refresh()

    def _quick_status(oracao_id, novo_status):
        from core.prayers import atualizar_status_oracao
        from core.activities import registrar_log

        kwargs = {}
        if novo_status == "Respondida":
            ok, comment = _ask_comment(
                content,
                title="Marcar como Respondida",
                field_label="Testemunho ou como a oração foi atendida",
                confirm_text="Confirmar",
                confirm_kind="success",
            )
            if not ok:
                return
            kwargs["testemunho"] = comment
        elif novo_status == "Arquivada":
            ok, comment = _ask_comment(
                content,
                title="Arquivar oração",
                field_label="Motivo ou comentário de arquivamento",
                confirm_text="Arquivar",
                confirm_kind="ghost",
            )
            if not ok:
                return
            kwargs["observacoes"] = comment

        atualizar_status_oracao(oracao_id, novo_status, **kwargs)
        if current_user_id:
            registrar_log(current_user_id,
                          f"Alterou status de oração ID {oracao_id} para '{novo_status}'")
        _refresh()

    def _sort_list(rows):
        s = state["sort"]
        if s == "data_asc":
            return sorted(rows, key=lambda r: r["data_cadastro"] or "")
        if s == "categoria":
            return sorted(rows, key=lambda r: (r["categoria"] or "").lower())
        if s == "nome":
            return sorted(rows, key=lambda r: (r["solicitante_nome"] or "").lower())
        return sorted(rows, key=lambda r: r["data_cadastro"] or "", reverse=True)

    def _load_all():
        try:
            from core.prayers import listar_oracoes
            cat = None if state["categoria"] == "Todas" else state["categoria"]
            m   = state["mes"]
            return list(listar_oracoes(categoria=cat, ano=m.year, mes=m.month))
        except Exception:
            return []

    def _render_list(rows):
        for w in list_box.winfo_children():
            w.destroy()
        for w in nav_frame.winfo_children():
            w.destroy()
        nav_frame.pack_forget()

        if not rows:
            tab = state["tab"]
            _icons  = {"ativas": "🙏", "respondidas": "✓", "arquivadas": "📁"}
            _titles = {
                "ativas":      "Nenhum pedido pendente",
                "respondidas": "Nenhuma oração respondida",
                "arquivadas":  "Nenhuma oração arquivada",
            }
            _bodies = {
                "ativas":      "Clique em \"Nova Oração\" para registrar o primeiro pedido.",
                "respondidas": "Orações marcadas como respondidas aparecerão aqui.",
                "arquivadas":  "Orações arquivadas aparecerão aqui.",
            }
            empty_state(
                list_box,
                icon=_icons[tab],
                title=_titles[tab],
                body=_bodies[tab],
                cta_label="Nova Oração" if tab == "ativas" else None,
                cta_command=callbacks.get("new_prayer") if tab == "ativas" else None,
            ).pack(fill=tk.X)
            return

        total_pages = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(state["page"], total_pages - 1)
        state["page"] = page
        page_items = rows[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

        for i, row in enumerate(page_items):
            oid  = row["id"]
            card = _prayer_card(
                list_box, row,
                on_edit=callbacks.get("edit_prayer") and
                        (lambda _id=oid: callbacks["edit_prayer"](_id)),
                on_delete=callbacks.get("delete_prayer") and
                          (lambda _id=oid: callbacks["delete_prayer"](_id)),
                on_respond=(lambda _id=oid: _quick_status(_id, "Respondida")),
                on_archive=(lambda _id=oid: _quick_status(_id, "Arquivada")),
            )
            card.pack(fill=tk.X, pady=(0, SPACING[2]))
            if i < len(page_items) - 1:
                divider_line(list_box, soft=True).pack(fill=tk.X,
                                                        pady=(0, SPACING[2]))

        if total_pages > 1:
            nav_frame.pack(fill=tk.X, pady=(SPACING[3], 0))
            tk.Label(nav_frame,
                     text=f"Página {page + 1} de {total_pages}",
                     font=FONTS["small"], bg=bg,
                     fg=COLORS["text_muted"]
                     ).pack(side=tk.LEFT, padx=(0, SPACING[3]))
            if page > 0:
                button(nav_frame, text="← Anterior", kind="ghost",
                       command=lambda: _go(-1)).pack(side=tk.LEFT,
                                                     padx=(0, SPACING[2]))
            if page < total_pages - 1:
                button(nav_frame, text="Próximo →", kind="ghost",
                       command=lambda: _go(+1)).pack(side=tk.LEFT)

    def _go(delta):
        state["page"] += delta
        _render_list(state["lists"][state["tab"]])
        content.scroll_top()

    def _switch_tab(key):
        state["tab"] = key
        state["page"] = 0
        _render_list(state["lists"][key])
        content.scroll_top()

    def _refresh():
        _update_mes_nav()
        rows        = _load_all()
        ativas      = _sort_list([r for r in rows if r["status"] == "Ativa"])
        respondidas = _sort_list([r for r in rows if r["status"] == "Respondida"])
        arquivadas  = _sort_list([r for r in rows if r["status"] == "Arquivada"])
        state["lists"] = {"ativas": ativas, "respondidas": respondidas,
                          "arquivadas": arquivadas}

        # KPIs
        for w in kpi_wrap.winfo_children():
            w.destroy()
        for c in range(4):
            kpi_wrap.columnconfigure(c, weight=1, uniform="kp")
        total = len(ativas) + len(respondidas) + len(arquivadas)
        kpis = [
            (total,            "Total",       COLORS["text"]),
            (len(ativas),      "Pendentes",   COLORS["accent"]),
            (len(respondidas), "Respondidas", COLORS["success"]),
            (len(arquivadas),  "Arquivadas",  COLORS["text_muted"]),
        ]
        for i, (val, lbl, col) in enumerate(kpis):
            cell = tk.Frame(kpi_wrap, bg=bg)
            cell.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACING[1],
                            0 if i == 3 else SPACING[1]))
            mini_stat(cell, value=val, label=lbl, color=col
                      ).pack(fill=tk.BOTH, expand=True)

        # Abas com contadores atualizados
        for w in tabs_holder.winfo_children():
            w.destroy()
        build_tabs(
            tabs_holder,
            options=[
                ("ativas",      "Pendentes",   len(ativas)),
                ("respondidas", "Respondidas", len(respondidas)),
                ("arquivadas",  "Arquivadas",  len(arquivadas)),
            ],
            value=state["tab"],
            on_change=_switch_tab,
        ).pack(fill=tk.X)

        _render_list(state["lists"][state["tab"]])

    def _on_filter(key, val):
        state[key] = val
        state["page"] = 0
        _refresh()

    _refresh()

    content._refresh = _refresh
    return content
