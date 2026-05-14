"""
Tela de Relatórios e Estatísticas
"""

import tkinter as tk
from datetime import datetime

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#00d4ff"
BTN_COLOR  = "#667eea"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"
DIVIDER    = "#2d2d44"

MESES       = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
MESES_ABREV = ["JAN","FEV","MAR","ABR","MAI","JUN",
               "JUL","AGO","SET","OUT","NOV","DEZ"]

_FUNCAO_CORES = [
    "#00d4ff","#51cf66","#ffd700","#667eea","#ffa94d",
    "#e599f7","#ff8787","#74c0fc","#ff6b6b","#a9e34b",
]
_EVENTO_CORES = {
    "Planejado":    "#667eea",
    "Em Andamento": "#00d4ff",
    "Concluído":    "#51cf66",
    "Adiado":       "#ffa94d",
    "Cancelado":    "#ff6b6b",
}


class ReportsWindow:
    def __init__(self, parent, root, current_user):
        self.parent       = parent
        self.root         = root
        self.current_user = current_user
        self._active_tab  = "membros"
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        outer = tk.Frame(self.parent, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=40, pady=24)

        self._build_header(outer)
        self._build_tabs(outer)

        # Scrollable content area
        wrapper = tk.Frame(outer, bg=BG_DARK)
        wrapper.pack(fill=tk.BOTH, expand=True)
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(wrapper, bg=BG_DARK, highlightthickness=0)
        self._sb     = tk.Scrollbar(wrapper, orient=tk.VERTICAL,
                                    command=self._canvas.yview)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        def _update_sb(lo, hi):
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                self._sb.grid_remove()
            else:
                self._sb.grid(row=0, column=1, sticky="ns")
            self._sb.set(lo, hi)

        self._canvas.configure(yscrollcommand=_update_sb)

        self._content = tk.Frame(self._canvas, bg=BG_DARK)
        self._win_id  = self._canvas.create_window((0, 0), window=self._content,
                                                   anchor="nw")

        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._win_id, width=e.width))
        self._content.bind("<Configure>",
                           lambda e: self._canvas.configure(
                               scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Enter>",
                          lambda e: self._canvas.bind_all(
                              "<MouseWheel>",
                              lambda ev: self._canvas.yview_scroll(
                                  -1 * (ev.delta // 120), "units")))
        self._canvas.bind("<Leave>",
                          lambda e: self._canvas.unbind_all("<MouseWheel>"))

        self._switch_tab("membros")

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 4))

        left = tk.Frame(hdr, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Relatórios e Estatísticas",
                 font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W)
        tk.Label(left, text="Visão geral do sistema e membros",
                 font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(anchor=tk.W)

        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(12, 0))

    def _build_tabs(self, parent):
        tab_row = tk.Frame(parent, bg=BG_DARK)
        tab_row.pack(fill=tk.X, pady=(0, 0))

        self._tab_refs = {}
        abas = [
            ("membros",         "Membros"),
            ("aniversariantes", "Aniversariantes"),
            ("eventos",         "Eventos"),
            ("crescimento",     "Crescimento"),
        ]
        for key, label in abas:
            col = tk.Frame(tab_row, bg=BG_DARK)
            col.pack(side=tk.LEFT, padx=(0, 2))

            btn = tk.Label(col, text=label,
                           font=("Segoe UI", 10, "bold"),
                           fg=TEXT_MUTED, bg=BG_DARK,
                           padx=16, pady=10,
                           cursor="hand2")
            btn.pack()

            rail = tk.Frame(col, bg=BG_DARK, height=2)
            rail.pack(fill=tk.X)

            k = key
            btn.bind("<Button-1>", lambda _e, k=k: self._switch_tab(k))
            self._tab_refs[key] = {"btn": btn, "rail": rail}

        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X)

    def _switch_tab(self, aba):
        self._active_tab = aba

        for k, refs in self._tab_refs.items():
            active = (k == aba)
            refs["btn"].configure(
                fg=TEXT if active else TEXT_MUTED,
                font=("Segoe UI", 10, "bold") if active else ("Segoe UI", 10),
            )
            refs["rail"].configure(bg=ACCENT if active else BG_DARK)

        for w in self._content.winfo_children():
            w.destroy()

        self._canvas.yview_moveto(0)
        self._canvas.configure(scrollregion=(0, 0, 0, 0))

        {
            "membros":         self._aba_membros,
            "aniversariantes": self._aba_aniversariantes,
            "eventos":         self._aba_eventos,
            "crescimento":     self._aba_crescimento,
        }[aba]()

    # ── Helpers visuais ───────────────────────────────────────────────────────

    def _secao(self, parent, texto):
        tk.Label(parent, text=texto,
                 font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W, pady=(20, 8))

    def _stat_card(self, row, valor, titulo, subtitulo, cor):
        card  = tk.Frame(row, bg=BG_CARD)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=20, pady=16)
        tk.Label(inner, text=str(valor),
                 font=("Segoe UI", 30, "bold"),
                 fg=cor, bg=BG_CARD).pack(anchor=tk.W)
        tk.Label(inner, text=titulo,
                 font=("Segoe UI", 11, "bold"),
                 fg=TEXT, bg=BG_CARD).pack(anchor=tk.W)
        tk.Label(inner, text=subtitulo,
                 font=("Segoe UI", 9),
                 fg="#666688", bg=BG_CARD).pack(anchor=tk.W)
        tk.Frame(card, bg=cor, height=3).pack(fill=tk.X, side=tk.BOTTOM)

    def _barras_h(self, parent, data, cores, altura=None):
        n  = len(data)
        h  = altura or max(120, n * 44 + 20)
        cv = tk.Canvas(parent, bg=BG_CARD, highlightthickness=0, height=h)
        cv.pack(fill=tk.X)

        def _draw(_ev=None):
            cv.delete("all")
            W = cv.winfo_width()
            if W < 20:
                cv.after(40, _draw)
                return
            label_w  = 180
            val_w    = 46
            bar_area = max(10, W - label_w - val_w - 24)
            max_val  = max((v for _, v in data), default=1) or 1
            bar_h    = 26
            gap      = 12

            for i, (label, val) in enumerate(data):
                y   = 14 + i * (bar_h + gap)
                bw  = int((val / max_val) * bar_area)
                cor = cores[i % len(cores)]
                cv.create_text(label_w - 8, y + bar_h // 2, text=label,
                               anchor="e", fill="#aaaaaa",
                               font=("Segoe UI", 9))
                cv.create_rectangle(label_w, y, label_w + bar_area, y + bar_h,
                                    fill=DIVIDER, outline="")
                if bw > 0:
                    cv.create_rectangle(label_w, y, label_w + bw, y + bar_h,
                                        fill=cor, outline="")
                cv.create_text(label_w + bar_area + 8, y + bar_h // 2,
                               text=str(val), anchor="w",
                               fill=TEXT, font=("Segoe UI", 9, "bold"))

        cv.bind("<Configure>", _draw)
        cv.after(60, _draw)

    def _barras_v(self, parent, data, cor=ACCENT):
        cv = tk.Canvas(parent, bg=BG_CARD, highlightthickness=0, height=240)
        cv.pack(fill=tk.X)

        def _draw(_ev=None):
            cv.delete("all")
            W, H = cv.winfo_width(), cv.winfo_height()
            if W < 20 or not data:
                cv.after(40, _draw)
                return

            n       = len(data)
            pad_l   = 36
            pad_r   = 16
            pad_top = 20
            pad_bot = 36
            aw      = W - pad_l - pad_r
            ah      = H - pad_top - pad_bot
            bar_w   = max(6, aw // n - 8)
            gap     = (aw - bar_w * n) // (n + 1)
            max_val = max((v for _, v in data), default=1) or 1

            for pct in (0.25, 0.5, 0.75, 1.0):
                y = pad_top + ah - int(pct * ah)
                cv.create_line(pad_l, y, W - pad_r, y,
                               fill=DIVIDER, dash=(3, 4))
                cv.create_text(pad_l - 4, y, anchor="e",
                               text=str(int(pct * max_val)),
                               fill="#555577", font=("Segoe UI", 8))

            for i, (label, val) in enumerate(data):
                x    = pad_l + gap + i * (bar_w + gap)
                bh   = int((val / max_val) * ah)
                y_top = pad_top + ah - bh
                y_bot = pad_top + ah
                cv.create_rectangle(x, y_top, x + bar_w, y_bot,
                                    fill=cor, outline="")
                if bh > 12:
                    cv.create_text(x + bar_w // 2, y_top - 5,
                                   text=str(val), fill=TEXT,
                                   font=("Segoe UI", 8, "bold"), anchor="s")
                cv.create_text(x + bar_w // 2, H - pad_bot + 8,
                               text=label, fill=TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="n")

        cv.bind("<Configure>", _draw)
        cv.after(60, _draw)

    # ── Aba: Membros ──────────────────────────────────────────────────────────

    def _aba_membros(self):
        from core.reports import membros_por_funcao, membros_por_status

        f = tk.Frame(self._content, bg=BG_DARK)
        f.pack(fill=tk.X, pady=(4, 20))

        por_status = membros_por_status()
        total      = sum(por_status.values())

        row = tk.Frame(f, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(0, 8))
        self._stat_card(row, total,
                        "Total de Membros", "Todos os cadastros", TEXT_MUTED)
        self._stat_card(row, por_status.get("Ativo", 0),
                        "Ativos", "Membros regulares", "#51cf66")
        self._stat_card(row, por_status.get("Afastado", 0),
                        "Afastados", "Temporariamente afastados", "#ff6b6b")
        self._stat_card(row, por_status.get("Visitante", 0),
                        "Visitantes", "Visitantes cadastrados", ACCENT)

        self._secao(f, "Distribuição por Função")
        card  = tk.Frame(f, bg=BG_CARD)
        card.pack(fill=tk.X)
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=16, pady=16)

        por_funcao = membros_por_funcao()
        if por_funcao:
            self._barras_h(inner, por_funcao, _FUNCAO_CORES,
                           altura=len(por_funcao) * 44 + 20)
        else:
            tk.Label(inner, text="Nenhum membro cadastrado.",
                     fg="#555577", bg=BG_CARD,
                     font=("Segoe UI", 11)).pack()

    # ── Aba: Aniversariantes ──────────────────────────────────────────────────

    def _aba_aniversariantes(self):
        f = tk.Frame(self._content, bg=BG_DARK)
        f.pack(fill=tk.X, pady=(4, 20))

        mes_atual = datetime.now().month

        # Seletor de meses em grid 4×3
        sel_card = tk.Frame(f, bg=BG_CARD)
        sel_card.pack(fill=tk.X, pady=(0, 16))
        sel_inner = tk.Frame(sel_card, bg=BG_CARD)
        sel_inner.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(sel_inner, text="Selecione o mês",
                 font=("Segoe UI", 10, "bold"),
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor=tk.W, pady=(0, 8))

        grid = tk.Frame(sel_inner, bg=BG_CARD)
        grid.pack(fill=tk.X)

        self._mes_btns = {}
        for i, abrev in enumerate(MESES_ABREV):
            mes_num = i + 1
            col = i % 6
            row = i // 6

            btn = tk.Label(grid, text=abrev,
                           font=("Segoe UI", 9, "bold"),
                           width=6, padx=6, pady=6,
                           bg=BG_CARD, fg=TEXT_MUTED,
                           cursor="hand2", relief=tk.FLAT)
            btn.grid(row=row, column=col, padx=(0, 4), pady=(0, 4), sticky="ew")
            grid.columnconfigure(col, weight=1)

            m = mes_num
            btn.bind("<Button-1>", lambda _e, m=m: self._render_aniversariantes(m))
            self._mes_btns[mes_num] = btn

        self._aniv_frame = tk.Frame(f, bg=BG_DARK)
        self._aniv_frame.pack(fill=tk.X)

        self._render_aniversariantes(mes_atual)

    def _render_aniversariantes(self, mes):
        from core.reports import aniversariantes_mes

        for m, btn in self._mes_btns.items():
            active = (m == mes)
            btn.configure(
                bg=ACCENT if active else DIVIDER,
                fg=BG_DARK if active else TEXT_MUTED,
                font=("Segoe UI", 9, "bold") if active else ("Segoe UI", 9),
            )

        for w in self._aniv_frame.winfo_children():
            w.destroy()

        membros  = aniversariantes_mes(mes)
        nome_mes = MESES[mes - 1]

        header_row = tk.Frame(self._aniv_frame, bg=BG_DARK)
        header_row.pack(fill=tk.X, pady=(0, 10))
        tk.Label(header_row,
                 text=f"Aniversariantes de {nome_mes}",
                 font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(side=tk.LEFT)
        tk.Label(header_row,
                 text=f"  {len(membros)}",
                 font=("Segoe UI", 12, "bold"),
                 fg=ACCENT, bg=BG_DARK).pack(side=tk.LEFT)

        if not membros:
            empty = tk.Frame(self._aniv_frame, bg=BG_CARD)
            empty.pack(fill=tk.X)
            tk.Label(empty, text=f"Nenhum aniversariante em {nome_mes}.",
                     font=("Segoe UI", 11), fg="#555577",
                     bg=BG_CARD, pady=20).pack()
            return

        for m in membros:
            card = tk.Frame(self._aniv_frame, bg=BG_CARD, height=64)
            card.pack(fill=tk.X, pady=(0, 2))
            card.pack_propagate(False)

            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(fill=tk.BOTH, expand=True)

            # Day badge
            day_col = tk.Frame(inner, bg=BG_CARD, width=60)
            day_col.pack(side=tk.LEFT, fill=tk.Y)
            day_col.pack_propagate(False)
            day_inner = tk.Frame(day_col, bg=BG_CARD)
            day_inner.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            tk.Label(day_inner,
                     text=f"{m['aniversario_dia']:02d}",
                     font=("Segoe UI", 20, "bold"),
                     fg=ACCENT, bg=BG_CARD).pack()

            tk.Frame(inner, bg=DIVIDER, width=1).pack(
                side=tk.LEFT, fill=tk.Y, pady=10)

            info = tk.Frame(inner, bg=BG_CARD)
            info.pack(side=tk.LEFT, fill=tk.X, padx=14, pady=10)

            tk.Label(info, text=m["nome"],
                     font=("Segoe UI", 11, "bold"),
                     fg=TEXT, bg=BG_CARD).pack(anchor=tk.W)

            meta_parts = [m["funcao"] or "Membro"]
            if m["telefone"]:
                meta_parts.append(f"📞 {m['telefone']}")
            tk.Label(info, text="   •   ".join(meta_parts),
                     font=("Segoe UI", 9),
                     fg=TEXT_MUTED, bg=BG_CARD).pack(anchor=tk.W)

            # Parabenizar button
            tel = m["telefone"]
            if tel:
                tk.Button(inner, text="💬 Parabenizar",
                          font=("Segoe UI", 9, "bold"),
                          bg="#25D366", fg=TEXT,
                          relief=tk.FLAT, cursor="hand2",
                          padx=10, pady=4,
                          activebackground="#1da851",
                          activeforeground=TEXT,
                          command=lambda t=tel, n=m["nome"]: self._parabenizar(t, n)
                          ).pack(side=tk.RIGHT, padx=14, pady=14)

    def _parabenizar(self, telefone, nome):
        from tkinter import messagebox
        messagebox.showinfo(
            "Parabenizar",
            f"Abra o WhatsApp e envie uma mensagem para:\n{nome}\n{telefone}",
            parent=self.root,
        )

    # ── Aba: Eventos ──────────────────────────────────────────────────────────

    def _aba_eventos(self):
        from core.reports import eventos_por_status

        f = tk.Frame(self._content, bg=BG_DARK)
        f.pack(fill=tk.X, pady=(4, 20))

        data  = eventos_por_status()
        total = sum(v for _, v in data)
        dmap  = dict(data)

        row = tk.Frame(f, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(0, 8))
        self._stat_card(row, total,
                        "Total de Eventos", "Todos os registros", TEXT_MUTED)
        for status, cor in _EVENTO_CORES.items():
            val = dmap.get(status, 0)
            self._stat_card(row, val, status, f"de {total} eventos", cor)

        self._secao(f, "Distribuição por Status")
        card  = tk.Frame(f, bg=BG_CARD)
        card.pack(fill=tk.X)
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=16, pady=16)

        if data:
            cores = [_EVENTO_CORES.get(s, BTN_COLOR) for s, _ in data]
            self._barras_h(inner, data, cores, altura=len(data) * 44 + 20)
        else:
            tk.Label(inner, text="Nenhum evento cadastrado.",
                     fg="#555577", bg=BG_CARD,
                     font=("Segoe UI", 11)).pack()

    # ── Aba: Crescimento ──────────────────────────────────────────────────────

    def _aba_crescimento(self):
        from core.reports import crescimento_membros

        f = tk.Frame(self._content, bg=BG_DARK)
        f.pack(fill=tk.X, pady=(4, 20))

        raw   = crescimento_membros(12)
        total = sum(v for _, v in raw)
        media = round(total / 12, 1) if raw else 0
        pico  = max((v for _, v in raw), default=0)

        row = tk.Frame(f, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(0, 8))
        self._stat_card(row, total,
                        "Cadastros (12 meses)", "Total acumulado", ACCENT)
        self._stat_card(row, media,
                        "Média por mês", "Novos cadastros / mês", BTN_COLOR)
        self._stat_card(row, pico,
                        "Mês recorde", "Maior número em um mês", "#51cf66")

        def _fmt(s):
            try:
                ano, m = s.split("-")
                return f"{MESES_ABREV[int(m)-1]}/{ano[2:]}"
            except Exception:
                return s

        data_fmt = [(_fmt(m), v) for m, v in raw]

        self._secao(f, "Novos Cadastros por Mês")
        card  = tk.Frame(f, bg=BG_CARD)
        card.pack(fill=tk.X)
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=16, pady=16)

        if data_fmt:
            self._barras_v(inner, data_fmt, cor=ACCENT)
        else:
            tk.Label(inner, text="Sem dados de cadastro no período.",
                     fg="#555577", bg=BG_CARD,
                     font=("Segoe UI", 11)).pack()
