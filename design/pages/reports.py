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

    # Estado compartilhado para exportação
    export_state = {
        "tab":         "membros",
        "aniv_mes":    datetime.now().month - 1,
        "cresc_ano":   datetime.now().year,
        "eventos_ano": datetime.now().year,
        "oracoes_ano": datetime.now().year,
    }

    hdr = screen_header(
        content,
        icon="📊",
        title="Relatórios e Estatísticas",
        subtitle="Visão geral da igreja",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))

    def _export():
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
            title="Salvar relatório como PDF",
            initialfile=f"relatorio_{export_state['tab']}_{datetime.now():%Y%m%d}",
        )
        if not path:
            return
        try:
            from core.pdf_export import export_tab
            export_tab(
                tab=export_state["tab"],
                data=data,
                aniv_mes=export_state["aniv_mes"],
                cresc_ano=export_state["cresc_ano"],
                eventos_ano=export_state["eventos_ano"],
                oracoes_ano=export_state["oracoes_ano"],
                filepath=path,
            )
            import os, sys, subprocess
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])
            except Exception:
                messagebox.showinfo("PDF gerado", f"Arquivo salvo em:\n{path}",
                                    parent=content)
        except Exception as exc:
            messagebox.showerror("Erro ao exportar",
                                 f"Não foi possível gerar o PDF:\n{exc}",
                                 parent=content)

    button(hdr["actions"], text="Exportar PDF",
           kind="ghost", icon="📄",
           command=_export).pack(side=tk.LEFT)

    # ─── Tabs ─────────────────────────────────────────────────────
    tab_row = tk.Frame(content, bg=COLORS["bg_dark"])
    tab_row.pack(fill=tk.X, pady=(0, SPACING[5]))

    body = tk.Frame(content, bg=COLORS["bg_dark"])
    body.pack(fill=tk.BOTH, expand=True)

    def _show(tab):
        export_state["tab"] = tab
        for w in body.winfo_children():
            w.destroy()
        if tab == "membros":
            _render_membros(body, data)
        elif tab == "aniversariantes":
            _render_aniversariantes(body,
                                    on_congrats=callbacks.get("send_birthday"),
                                    export_state=export_state)
        elif tab == "eventos":
            _render_eventos(body, export_state=export_state)
        elif tab == "crescimento":
            _render_crescimento(body, export_state=export_state)
        elif tab == "oracoes":
            _render_oracoes(body, export_state=export_state)
        content.scroll_top()

    tabs_widget = build_tabs(
        tab_row,
        options=[
            ("membros",         "👥  Membros",        None),
            ("aniversariantes", "🎂  Aniversariantes", None),
            ("eventos",         "📋  Eventos",        None),
            ("crescimento",     "📈  Crescimento",    None),
            ("oracoes",         "🙏  Orações",        None),
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
              data=bar_data).pack(fill=tk.X, pady=(0, SPACING[4]))

    grupo_counts = data.get("grupo_counts", {})
    if grupo_counts:
        grupo_colors = [COLORS["purple"], COLORS["accent2"], COLORS["warning"]]
        grupo_data = [
            (g, c, grupo_colors[i % len(grupo_colors)])
            for i, (g, c) in enumerate(
                sorted(grupo_counts.items(), key=lambda x: -x[1])
            )
        ]
        bar_chart(parent, title="Distribuição por grupo",
                  data=grupo_data).pack(fill=tk.X)


# ─── ABA: ANIVERSARIANTES ─────────────────────────────────────────
_MESES = ["Jan","Fev","Mar","Abr","Mai","Jun",
          "Jul","Ago","Set","Out","Nov","Dez"]


def _render_aniversariantes(parent, *, on_congrats=None, export_state=None):
    bg    = parent["bg"]
    today = datetime.now().day
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
        if export_state is not None:
            export_state["aniv_mes"] = idx
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

        _load_error = None
        try:
            from core.members import aniversariantes_do_mes
            raw = list(aniversariantes_do_mes(state["active"] + 1))
            data_list = [
                {
                    "dia":      r["aniversario_dia"],
                    "mes":      state["active"] + 1,
                    "nome":     r["nome"],
                    "telefone": r["telefone"] or "",
                    "funcao":   r["funcao"] or "Membro",
                    "color":    "#667eea",
                }
                for r in raw
            ]
        except Exception as _e:
            data_list = []
            _load_error = str(_e)

        mes_nome = _MESES[state["active"]]

        section_label(list_box, text=f"Aniversariantes de {mes_nome}",
                      action=f"{len(data_list)} pessoas"
                      ).pack(fill=tk.X, anchor=tk.W, pady=(0, SPACING[3]))

        card = tk.Frame(list_box, bg=COLORS["bg_card"],
                        highlightbackground=COLORS["divider"],
                        highlightthickness=1)
        card.pack(fill=tk.X)

        if _load_error:
            tk.Label(card,
                     text=f"Não foi possível carregar os dados. ({_load_error})",
                     font=FONTS["body"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["danger"]).pack(pady=SPACING[6])
            return

        if not data_list:
            tk.Label(card,
                     text=f"Nenhum aniversariante em {mes_nome}.",
                     font=FONTS["body"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack(pady=SPACING[6])
            return

        for i, b in enumerate(data_list):
            line = tk.Frame(card, bg=COLORS["bg_card"])
            line.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[3])

            # Coluna da data — sem pack_propagate para que o frame cresça
            # naturalmente até o tamanho dos labels internos.
            date_col = tk.Frame(line, bg=COLORS["bg_card"])
            date_col.pack(side=tk.LEFT, padx=(0, SPACING[3]))
            dia_txt = f"{b['dia']:02d}" if b.get("dia") else "--"
            tk.Label(date_col, text=dia_txt,
                     font=(FONTS["body"][0], 22, "bold"),
                     bg=COLORS["bg_card"],
                     fg=COLORS["warning"]).pack()
            tk.Label(date_col, text=mes_nome.upper(),
                     font=FONTS["section"],
                     bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"]).pack()

            tk.Frame(line, bg=COLORS["divider"],
                     width=1).pack(side=tk.LEFT, fill=tk.Y,
                                   padx=(0, SPACING[3]))

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

            if b.get("dia") == today and on_congrats:
                button(line, text="🎂 Parabenizar", kind="whatsapp",
                       command=lambda _b=b: on_congrats(_b)
                       ).pack(side=tk.RIGHT)

            if i < len(data_list) - 1:
                divider_line(card, soft=True).pack(fill=tk.X, padx=SPACING[4])

    _render_buttons()
    _render_list()


# ─── ABA: EVENTOS ─────────────────────────────────────────────────
def _render_eventos(parent, *, export_state=None):
    from datetime import datetime
    from core.reports import eventos_por_ano

    bg        = parent["bg"]
    ano_atual = datetime.now().year
    state     = {"ano": ano_atual, "data": None}

    top_bar       = tk.Frame(parent, bg=bg)
    top_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    kpi_container = tk.Frame(parent, bg=bg)
    kpi_container.pack(fill=tk.X, pady=(0, SPACING[6]))

    chart_container = tk.Frame(parent, bg=bg)
    chart_container.pack(fill=tk.X)

    def _load(ano):
        try:
            return eventos_por_ano(ano)
        except Exception:
            return {"ano": ano, "total_events": 0,
                    "realizadas": 0, "planejadas": 0, "canceladas": 0,
                    "anos_disponiveis": [ano_atual]}

    def _refresh(ano):
        state["ano"]  = ano
        state["data"] = _load(ano)
        if export_state is not None:
            export_state["eventos_ano"] = ano
        _render_top_bar()
        _render_kpis()
        _render_chart()

    def _render_top_bar():
        for w in top_bar.winfo_children():
            w.destroy()
        tk.Label(top_bar, text="Eventos por ano",
                 font=FONTS["subtitle"],
                 bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)

        anos = list(state["data"]["anos_disponiveis"]) if state["data"] else [ano_atual]
        if ano_atual not in anos:
            anos = [ano_atual] + anos

        btn_frame = tk.Frame(top_bar, bg=bg)
        btn_frame.pack(side=tk.RIGHT)
        for a in sorted(anos):
            ativo = (a == state["ano"])
            lbl = tk.Label(btn_frame, text=str(a),
                           font=FONTS["small_bold"],
                           bg=COLORS["accent"] if ativo else COLORS["bg_card"],
                           fg=COLORS["bg_dark"] if ativo else COLORS["text_dim"],
                           padx=SPACING[3], pady=SPACING[1] + 2,
                           highlightbackground=COLORS["divider"],
                           highlightthickness=1,
                           cursor="hand2")
            lbl.pack(side=tk.LEFT, padx=2)
            lbl.bind("<Button-1>", lambda e, _a=a: _refresh(_a))

    def _render_kpis():
        for w in kpi_container.winfo_children():
            w.destroy()
        for c in range(4):
            kpi_container.columnconfigure(c, weight=1, uniform="ev")
        d          = state["data"] or {}
        total_ev   = d.get("total_events", 0)
        realizadas = d.get("realizadas",   0)
        planejadas = d.get("planejadas",   0)
        canceladas = d.get("canceladas",   0)
        stats = [
            (total_ev,   "Total de Eventos", f"no ano de {state['ano']}",  COLORS["text"]),
            (realizadas, "Realizados",        "Concluídos com sucesso",     COLORS["success"]),
            (planejadas, "Planejados",        "Agendados / em andamento",   COLORS["accent"]),
            (canceladas, "Cancelados",        "Não aconteceram",            COLORS["danger"]),
        ]
        for i, (v, l, s, c) in enumerate(stats):
            cell = tk.Frame(kpi_container, bg=bg)
            cell.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACING[1],
                            0 if i == 3 else SPACING[1]))
            big_stat(cell, value=v, label=l, sub=s, color=c).pack(fill=tk.BOTH, expand=True)

    def _render_chart():
        for w in chart_container.winfo_children():
            w.destroy()
        d          = state["data"] or {}
        realizadas = d.get("realizadas", 0)
        planejadas = d.get("planejadas", 0)
        canceladas = d.get("canceladas", 0)
        bar_chart(chart_container, title="Distribuição por status", data=[
            ("Planejados", max(planejadas, 0), COLORS["accent"]),
            ("Realizados", max(realizadas, 0), COLORS["success"]),
            ("Cancelados", max(canceladas, 0), COLORS["danger"]),
        ]).pack(fill=tk.X)

    state["data"] = _load(ano_atual)
    _render_top_bar()
    _render_kpis()
    _render_chart()


# ─── ABA: CRESCIMENTO ─────────────────────────────────────────────
_MESES_FULL = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _render_crescimento(parent, *, export_state=None):
    from datetime import datetime
    from core.members import crescimento_mensal

    bg   = parent["bg"]
    ano_atual = datetime.now().year
    state = {"ano": ano_atual, "data": None}

    # ── containers ────────────────────────────────────────────────
    top_bar  = tk.Frame(parent, bg=bg)
    top_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    kpi_row  = tk.Frame(parent, bg=bg)
    kpi_row.pack(fill=tk.X, pady=(0, SPACING[5]))

    chart_card = tk.Frame(parent, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    chart_card.pack(fill=tk.X)

    legend_row = tk.Frame(parent, bg=bg)
    legend_row.pack(fill=tk.X, pady=(SPACING[3], 0))

    # ── helpers ───────────────────────────────────────────────────
    def _load(ano):
        try:
            return crescimento_mensal(ano)
        except Exception:
            return {"ano": ano, "membros": [0]*12,
                    "visitantes": [0]*12, "afastados": [0]*12,
                    "anos_disponiveis": [ano_atual]}

    def _refresh(ano):
        state["ano"]  = ano
        state["data"] = _load(ano)
        if export_state is not None:
            export_state["cresc_ano"] = ano
        _render_top_bar()
        _render_kpis()
        _render_chart()
        _render_legend()

    # ── top bar: seletor de ano ────────────────────────────────────
    def _render_top_bar():
        for w in top_bar.winfo_children():
            w.destroy()
        tk.Label(top_bar, text="Crescimento mensal",
                 font=FONTS["subtitle"],
                 bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)

        anos = state["data"]["anos_disponiveis"] if state["data"] else [ano_atual]
        # Garante que ao menos o ano atual aparece
        if ano_atual not in anos:
            anos = [ano_atual] + list(anos)

        btn_frame = tk.Frame(top_bar, bg=bg)
        btn_frame.pack(side=tk.RIGHT)
        for a in sorted(anos):
            ativo = (a == state["ano"])
            lbl = tk.Label(btn_frame, text=str(a),
                           font=FONTS["small_bold"],
                           bg=COLORS["accent"] if ativo else COLORS["bg_card"],
                           fg=COLORS["bg_dark"] if ativo else COLORS["text_dim"],
                           padx=SPACING[3], pady=SPACING[1] + 2,
                           highlightbackground=COLORS["divider"],
                           highlightthickness=1,
                           cursor="hand2")
            lbl.pack(side=tk.LEFT, padx=2)
            lbl.bind("<Button-1>", lambda e, _a=a: _refresh(_a))

    # ── KPIs ──────────────────────────────────────────────────────
    def _render_kpis():
        for w in kpi_row.winfo_children():
            w.destroy()
        d = state["data"] or {}
        m = d.get("membros",    [0]*12)
        v = d.get("visitantes", [0]*12)
        a = d.get("afastados",  [0]*12)

        total_m  = sum(m)
        total_v  = sum(v)
        total_a  = sum(a)
        total    = total_m + total_v + total_a

        combined = [m[i] + v[i] for i in range(12)]
        mes_pico = combined.index(max(combined)) if any(combined) else -1
        pico_txt = _MESES_FULL[mes_pico] if mes_pico >= 0 and max(combined) > 0 else "—"

        kpis = [
            (total,    "Total cadastrado", f"no ano de {state['ano']}",      COLORS["text"]),
            (total_m,  "Membros",          "adicionados como ativos",         COLORS["accent"]),
            (total_v,  "Visitantes",       "cadastrados no período",          COLORS["warning"]),
            (pico_txt, "Mês de pico",      "maior número de entradas",        COLORS["success"]),
        ]
        for c in range(4):
            kpi_row.columnconfigure(c, weight=1, uniform="kpi")
        for i, (val, lbl, sub, cor) in enumerate(kpis):
            cell = tk.Frame(kpi_row, bg=bg)
            cell.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACING[1],
                            0 if i == 3 else SPACING[1]))
            big_stat(cell, value=val, label=lbl, sub=sub,
                     color=cor).pack(fill=tk.BOTH, expand=True)

    # ── Canvas chart ──────────────────────────────────────────────
    CHART_H     = 220
    PAD_L       = 48   # espaço para labels do eixo Y
    PAD_R       = 16
    PAD_T       = 16
    PAD_B       = 36   # espaço para labels do eixo X
    BAR_GAP     = 6    # espaço entre grupos
    BAR_INNER   = 2    # espaço entre barras do mesmo grupo
    COLOR_M     = COLORS["accent"]
    COLOR_V     = COLORS["warning"]
    COLOR_A     = COLORS["danger"]

    canvas_ref = [None]

    def _render_chart():
        for w in chart_card.winfo_children():
            w.destroy()

        cv = tk.Canvas(chart_card, bg=COLORS["bg_card"],
                       highlightthickness=0, height=CHART_H)
        cv.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[4])
        canvas_ref[0] = cv

        def _draw(event=None):
            cv.delete("all")
            W = cv.winfo_width()
            if W < 50:
                return

            d  = state["data"] or {}
            m  = d.get("membros",    [0]*12)
            v  = d.get("visitantes", [0]*12)
            a  = d.get("afastados",  [0]*12)

            draw_w  = W - PAD_L - PAD_R
            draw_h  = CHART_H - PAD_T - PAD_B
            n_meses = 12
            slot_w  = draw_w / n_meses
            n_bars  = 3   # membros, visitantes, afastados
            bar_w   = max(4, (slot_w - BAR_GAP * 2) / n_bars - BAR_INNER)

            max_val = max(max(m), max(v), max(a), 1)
            # Round up to a nice ceiling
            step = max(1, max_val // 5)
            y_max = (max_val // step + 1) * step

            # eixo Y (linhas de grade + labels)
            for tick in range(0, y_max + 1, step):
                y = PAD_T + draw_h - (tick / y_max) * draw_h
                cv.create_line(PAD_L, y, W - PAD_R, y,
                               fill=COLORS["divider"], dash=(4, 4))
                cv.create_text(PAD_L - 4, y,
                               text=str(tick),
                               font=(FONTS["small"][0], 8),
                               fill=COLORS["text_muted"],
                               anchor="e")

            # eixo X + barras
            for i in range(n_meses):
                x_center = PAD_L + (i + 0.5) * slot_w
                group_w  = bar_w * n_bars + BAR_INNER * (n_bars - 1)
                x_start  = x_center - group_w / 2

                pairs = [(m[i], COLOR_M), (v[i], COLOR_V), (a[i], COLOR_A)]
                for j, (val, color) in enumerate(pairs):
                    x0 = x_start + j * (bar_w + BAR_INNER)
                    x1 = x0 + bar_w
                    if val > 0:
                        bar_h = (val / y_max) * draw_h
                        y0 = PAD_T + draw_h - bar_h
                        y1 = PAD_T + draw_h
                        cv.create_rectangle(x0, y0, x1, y1,
                                            fill=color, outline="", width=0)
                        if bar_h > 14:
                            cv.create_text((x0 + x1) / 2, y0 + 6,
                                           text=str(val),
                                           font=(FONTS["small"][0], 8, "bold"),
                                           fill="#ffffff")

                # label do mês
                cv.create_text(x_center, CHART_H - PAD_B + 8,
                               text=_MESES_FULL[i],
                               font=(FONTS["small"][0], 8),
                               fill=COLORS["text_muted"])

        cv.bind("<Configure>", _draw)
        cv.after(50, _draw)

    # ── Legenda ───────────────────────────────────────────────────
    def _render_legend():
        for w in legend_row.winfo_children():
            w.destroy()
        items = [
            (COLOR_M, "Membros Ativos"),
            (COLOR_V, "Visitantes"),
            (COLOR_A, "Afastados"),
        ]
        for color, label in items:
            dot = tk.Canvas(legend_row, width=10, height=10,
                            bg=bg, highlightthickness=0)
            dot.create_oval(0, 0, 10, 10, fill=color, outline="")
            dot.pack(side=tk.LEFT, padx=(0, SPACING[1]))
            tk.Label(legend_row, text=label,
                     font=FONTS["small"],
                     bg=bg, fg=COLORS["text_muted"]
                     ).pack(side=tk.LEFT, padx=(0, SPACING[4]))

    # ── primeiro carregamento ──────────────────────────────────────
    state["data"] = _load(ano_atual)
    _render_top_bar()
    _render_kpis()
    _render_chart()
    _render_legend()


# ─── ABA: ORAÇÕES ─────────────────────────────────────────────────
_MESES_OR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _render_oracoes(parent, *, export_state=None):
    from datetime import datetime
    from core.reports import oracoes_por_mes_ano

    bg        = parent["bg"]
    ano_atual = datetime.now().year
    state     = {"ano": ano_atual, "data": None}

    COLOR_P = COLORS["accent"]       # Pendentes
    COLOR_R = COLORS["success"]      # Respondidas
    COLOR_A = COLORS.get("text_muted", "#888888")  # Arquivadas

    CHART_H   = 220
    PAD_L     = 48
    PAD_R     = 16
    PAD_T     = 16
    PAD_B     = 36
    BAR_GAP   = 6
    BAR_INNER = 2

    # ── containers ────────────────────────────────────────────────
    top_bar    = tk.Frame(parent, bg=bg)
    top_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    kpi_row    = tk.Frame(parent, bg=bg)
    kpi_row.pack(fill=tk.X, pady=(0, SPACING[5]))

    chart_card = tk.Frame(parent, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    chart_card.pack(fill=tk.X)

    legend_row = tk.Frame(parent, bg=bg)
    legend_row.pack(fill=tk.X, pady=(SPACING[3], 0))

    # ── helpers ───────────────────────────────────────────────────
    def _load(ano):
        try:
            return oracoes_por_mes_ano(ano)
        except Exception:
            return {"ano": ano, "pendentes": [0]*12,
                    "respondidas": [0]*12, "arquivadas": [0]*12,
                    "anos_disponiveis": [ano_atual]}

    def _refresh(ano):
        state["ano"]  = ano
        state["data"] = _load(ano)
        if export_state is not None:
            export_state["oracoes_ano"] = ano
        _render_top_bar()
        _render_kpis()
        _render_chart()
        _render_legend()

    # ── top bar: seletor de ano ────────────────────────────────────
    def _render_top_bar():
        for w in top_bar.winfo_children():
            w.destroy()
        tk.Label(top_bar, text="Orações por mês",
                 font=FONTS["subtitle"],
                 bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)

        anos = list(state["data"]["anos_disponiveis"]) if state["data"] else [ano_atual]
        if ano_atual not in anos:
            anos = [ano_atual] + anos

        btn_frame = tk.Frame(top_bar, bg=bg)
        btn_frame.pack(side=tk.RIGHT)
        for a in sorted(anos):
            ativo = (a == state["ano"])
            lbl = tk.Label(btn_frame, text=str(a),
                           font=FONTS["small_bold"],
                           bg=COLORS["accent"] if ativo else COLORS["bg_card"],
                           fg=COLORS["bg_dark"] if ativo else COLORS["text_dim"],
                           padx=SPACING[3], pady=SPACING[1] + 2,
                           highlightbackground=COLORS["divider"],
                           highlightthickness=1,
                           cursor="hand2")
            lbl.pack(side=tk.LEFT, padx=2)
            lbl.bind("<Button-1>", lambda e, _a=a: _refresh(_a))

    # ── KPIs ──────────────────────────────────────────────────────
    def _render_kpis():
        for w in kpi_row.winfo_children():
            w.destroy()
        d = state["data"] or {}
        p = d.get("pendentes",   [0]*12)
        r = d.get("respondidas", [0]*12)
        a = d.get("arquivadas",  [0]*12)

        total_p = sum(p)
        total_r = sum(r)
        total_a = sum(a)
        total   = total_p + total_r + total_a

        taxa = f"{round(total_r / total * 100)}%" if total > 0 else "—"

        kpis = [
            (total,   "Total registrado",  f"no ano de {state['ano']}",  COLORS["text"]),
            (total_p, "Pendentes",         "ainda aguardando resposta",  COLOR_P),
            (total_r, "Respondidas",       "orações atendidas",          COLOR_R),
            (taxa,    "Taxa de resposta",  "respondidas ÷ total",        COLORS["success"]),
        ]
        for c in range(4):
            kpi_row.columnconfigure(c, weight=1, uniform="okpi")
        for i, (val, lbl, sub, cor) in enumerate(kpis):
            cell = tk.Frame(kpi_row, bg=bg)
            cell.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACING[1],
                            0 if i == 3 else SPACING[1]))
            big_stat(cell, value=val, label=lbl, sub=sub,
                     color=cor).pack(fill=tk.BOTH, expand=True)

    # ── Canvas chart ──────────────────────────────────────────────
    def _render_chart():
        for w in chart_card.winfo_children():
            w.destroy()

        cv = tk.Canvas(chart_card, bg=COLORS["bg_card"],
                       highlightthickness=0, height=CHART_H)
        cv.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[4])

        def _draw(event=None):
            cv.delete("all")
            W = cv.winfo_width()
            if W < 50:
                return

            d = state["data"] or {}
            p = d.get("pendentes",   [0]*12)
            r = d.get("respondidas", [0]*12)
            a = d.get("arquivadas",  [0]*12)

            draw_w = W - PAD_L - PAD_R
            draw_h = CHART_H - PAD_T - PAD_B
            slot_w = draw_w / 12
            n_bars = 3
            bar_w  = max(4, (slot_w - BAR_GAP * 2) / n_bars - BAR_INNER)

            max_val = max(max(p), max(r), max(a), 1)
            step    = max(1, max_val // 5)
            y_max   = (max_val // step + 1) * step

            for tick in range(0, y_max + 1, step):
                y = PAD_T + draw_h - (tick / y_max) * draw_h
                cv.create_line(PAD_L, y, W - PAD_R, y,
                               fill=COLORS["divider"], dash=(4, 4))
                cv.create_text(PAD_L - 4, y, text=str(tick),
                               font=(FONTS["small"][0], 8),
                               fill=COLORS["text_muted"], anchor="e")

            for i in range(12):
                x_center = PAD_L + (i + 0.5) * slot_w
                group_w  = bar_w * n_bars + BAR_INNER * (n_bars - 1)
                x_start  = x_center - group_w / 2

                for j, (val, color) in enumerate(
                        [(p[i], COLOR_P), (r[i], COLOR_R), (a[i], COLOR_A)]):
                    x0 = x_start + j * (bar_w + BAR_INNER)
                    x1 = x0 + bar_w
                    if val > 0:
                        bh = (val / y_max) * draw_h
                        y0 = PAD_T + draw_h - bh
                        cv.create_rectangle(x0, y0, x1, PAD_T + draw_h,
                                            fill=color, outline="", width=0)
                        if bh > 14:
                            cv.create_text((x0 + x1) / 2, y0 + 6,
                                           text=str(val),
                                           font=(FONTS["small"][0], 8, "bold"),
                                           fill="#ffffff")

                cv.create_text(x_center, CHART_H - PAD_B + 8,
                               text=_MESES_OR[i],
                               font=(FONTS["small"][0], 8),
                               fill=COLORS["text_muted"])

        cv.bind("<Configure>", _draw)
        cv.after(50, _draw)

    # ── Legenda ───────────────────────────────────────────────────
    def _render_legend():
        for w in legend_row.winfo_children():
            w.destroy()
        for color, label in [
            (COLOR_P, "Pendentes"),
            (COLOR_R, "Respondidas"),
            (COLOR_A, "Arquivadas"),
        ]:
            dot = tk.Canvas(legend_row, width=10, height=10,
                            bg=bg, highlightthickness=0)
            dot.create_oval(0, 0, 10, 10, fill=color, outline="")
            dot.pack(side=tk.LEFT, padx=(0, SPACING[1]))
            tk.Label(legend_row, text=label,
                     font=FONTS["small"],
                     bg=bg, fg=COLORS["text_muted"]
                     ).pack(side=tk.LEFT, padx=(0, SPACING[4]))

    # ── primeiro carregamento ──────────────────────────────────────
    state["data"] = _load(ano_atual)
    _render_top_bar()
    _render_kpis()
    _render_chart()
    _render_legend()
