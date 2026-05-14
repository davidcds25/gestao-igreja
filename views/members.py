"""
Interface gráfica para gerenciamento de membros da igreja
"""

import tkinter as tk
from tkinter import messagebox, ttk
from core.members import (
    criar_membro, listar_membros, obter_membro,
    atualizar_membro, deletar_membro, contar_membros,
    FUNCOES, STATUS, MESES,
)

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#00d4ff"
BTN_COLOR  = "#667eea"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"
DIVIDER    = "#2d2d44"

FUNCAO_CORES = {
    "Pastor(a)":       ("#ffd700", "#1a1a2e"),
    "Presbítero":      ("#9b59b6", "#ffffff"),
    "Diácono(a)":      ("#667eea", "#ffffff"),
    "Evangelista":     ("#ffa94d", "#1a1a2e"),
    "Líder de Célula": ("#51cf66", "#0f0f23"),
    "Louvor":          ("#00d4ff", "#0f0f23"),
    "Obreiro(a)":      ("#74c0fc", "#0f0f23"),
    "Secretário(a)":   ("#e599f7", "#1a1a2e"),
    "Tesoureiro(a)":   ("#ff8787", "#1a1a2e"),
    "Membro":          ("#4a4a6a", "#ffffff"),
}

STATUS_CORES = {
    "Ativo":     ("#1a3a1a", "#51cf66"),
    "Afastado":  ("#3a1a1a", "#ff6b6b"),
    "Visitante": ("#0f2535", "#00d4ff"),
}

_FUNCAO_AVATAR_COLOR = {k: v[0] for k, v in FUNCAO_CORES.items()}


class MembersWindow:
    def __init__(self, parent_frame, root_window, current_user):
        self.root         = root_window
        self.current_user = current_user

        self.selected_member = None
        self._all_membros    = []
        self._page           = 0
        self._PAGE_SIZE      = 10

        self.frame = tk.Frame(parent_frame, bg=BG_DARK)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._setup_ui()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _setup_ui(self):
        outer = tk.Frame(self.frame, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=40, pady=24)

        self._build_header(outer)
        self._stats_frame = tk.Frame(outer, bg=BG_DARK)
        self._stats_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Frame(outer, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0, 12))

        self._cards_frame = tk.Frame(outer, bg=BG_DARK)
        self._cards_frame.pack(fill=tk.BOTH, expand=True)

        self._pag_bar = tk.Frame(outer, bg=BG_DARK)
        self._pag_bar.pack(fill=tk.X, pady=(10, 0))

        self.refresh_list()

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 12))

        left = tk.Frame(hdr, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Membros da Igreja",
                 font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W)
        self._subtitle_lbl = tk.Label(left, text="Carregando…",
                                      font=("Segoe UI", 10),
                                      fg=TEXT_MUTED, bg=BG_DARK)
        self._subtitle_lbl.pack(anchor=tk.W)

        _btn = dict(relief=tk.FLAT, cursor="hand2",
                    font=("Segoe UI", 10, "bold"), padx=14, pady=7)

        tk.Button(hdr, text="+ Novo Membro",
                  command=self._show_new,
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  **_btn).pack(side=tk.RIGHT, padx=(6, 0))

        # Filters
        filter_frame = tk.Frame(hdr, bg=BG_DARK)
        filter_frame.pack(side=tk.RIGHT, padx=(0, 10))

        tk.Label(filter_frame, text="Função:",
                 font=("Segoe UI", 9), fg=TEXT_MUTED,
                 bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
        self._filter_funcao = tk.StringVar(value="Todas")
        funcao_cb = ttk.Combobox(filter_frame, textvariable=self._filter_funcao,
                                 values=["Todas"] + FUNCOES,
                                 state="readonly", width=14, font=("Segoe UI", 9))
        funcao_cb.pack(side=tk.LEFT, padx=(0, 12))
        funcao_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh_list())

        tk.Label(filter_frame, text="Status:",
                 font=("Segoe UI", 9), fg=TEXT_MUTED,
                 bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
        self._filter_status = tk.StringVar(value="Todos")
        status_cb = ttk.Combobox(filter_frame, textvariable=self._filter_status,
                                 values=["Todos", "Ativos", "Afastados", "Visitantes"],
                                 state="readonly", width=10, font=("Segoe UI", 9))
        status_cb.pack(side=tk.LEFT)
        status_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh_list())

    # ── Dados ─────────────────────────────────────────────────────────────────

    def refresh_list(self):
        status_map = {"Ativos": "Ativo", "Afastados": "Afastado", "Visitantes": "Visitante"}
        status = status_map.get(self._filter_status.get())
        funcao = self._filter_funcao.get()

        self._all_membros = list(listar_membros(
            status=status,
            funcao=None if funcao == "Todas" else funcao,
        ))
        self._page = 0
        self._render_stats()
        self._render_page()

    def _render_stats(self):
        for w in self._stats_frame.winfo_children():
            w.destroy()

        ativos, afastados, visitantes = contar_membros()
        total = ativos + afastados + visitantes

        self._subtitle_lbl.configure(
            text=f"{total} pessoa{'s' if total != 1 else ''} cadastrada{'s' if total != 1 else ''}")

        stats = [
            ("Total",      total,      "#888888"),
            ("Ativos",     ativos,     "#51cf66"),
            ("Afastados",  afastados,  "#ff6b6b"),
            ("Visitantes", visitantes, "#00d4ff"),
        ]
        for label, value, color in stats:
            card = tk.Frame(self._stats_frame, bg=BG_CARD)
            card.pack(side=tk.LEFT, padx=(0, 10))
            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(padx=16, pady=10)
            tk.Label(inner, text=str(value),
                     font=("Segoe UI", 18, "bold"),
                     fg=color, bg=BG_CARD).pack(anchor=tk.W)
            tk.Label(inner, text=label,
                     font=("Segoe UI", 9),
                     fg=TEXT_MUTED, bg=BG_CARD).pack(anchor=tk.W)
            tk.Frame(card, bg=color, height=2).pack(fill=tk.X, side=tk.BOTTOM)

    # ── Cards de membro ───────────────────────────────────────────────────────

    def _render_page(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()
        self.selected_member = None

        start = self._page * self._PAGE_SIZE
        page  = self._all_membros[start:start + self._PAGE_SIZE]

        if not page:
            self._empty_state()
        else:
            cols = tk.Frame(self._cards_frame, bg=BG_DARK)
            cols.pack(fill=tk.BOTH, expand=True)
            col_a = tk.Frame(cols, bg=BG_DARK)
            col_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
            col_b = tk.Frame(cols, bg=BG_DARK)
            col_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            for i, membro in enumerate(page):
                target = col_a if i % 2 == 0 else col_b
                self._build_card(target, membro)

        self._render_pagination()

    def _empty_state(self):
        f = tk.Frame(self._cards_frame, bg=BG_DARK)
        f.pack(expand=True, pady=60)
        tk.Label(f, text="👥", font=("Segoe UI", 36),
                 fg=DIVIDER, bg=BG_DARK).pack()
        tk.Label(f, text="Nenhum membro encontrado",
                 font=("Segoe UI", 13, "bold"),
                 fg="#555577", bg=BG_DARK).pack(pady=(8, 4))
        tk.Label(f, text='Ajuste os filtros ou cadastre um novo membro',
                 font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack()

    def _build_card(self, parent, membro):
        outer = tk.Frame(parent, bg=BG_DARK,
                         highlightthickness=2,
                         highlightbackground=BG_DARK)
        outer.pack(fill=tk.X, pady=(0, 8))

        card = tk.Frame(outer, bg=BG_CARD, cursor="hand2")
        card.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=14, pady=12)

        # Avatar row
        top = tk.Frame(inner, bg=BG_CARD)
        top.pack(fill=tk.X)

        nome   = membro["nome"] or ""
        funcao = membro["funcao"] or "Membro"
        color  = _FUNCAO_AVATAR_COLOR.get(funcao, "#4a4a6a")
        inits  = "".join(p[0].upper() for p in nome.split()[:2]) if nome else "?"

        av = tk.Canvas(top, width=36, height=36,
                       bg=BG_CARD, highlightthickness=0)
        av.pack(side=tk.LEFT, padx=(0, 10))
        av.create_oval(2, 2, 34, 34, fill=color, outline="")
        av.create_text(18, 18, text=inits,
                       font=("Segoe UI", 11, "bold"), fill=TEXT)

        name_status = tk.Frame(top, bg=BG_CARD)
        name_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Name (truncated)
        display_name = nome[:30] + "…" if len(nome) > 30 else nome
        tk.Label(name_status, text=display_name,
                 font=("Segoe UI", 11, "bold"),
                 fg=TEXT, bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W)

        badge_row = tk.Frame(name_status, bg=BG_CARD)
        badge_row.pack(anchor=tk.W, pady=(2, 0))

        fc_bg, fc_fg = FUNCAO_CORES.get(funcao, ("#4a4a6a", "#ffffff"))
        tk.Label(badge_row, text=f"  {funcao}  ",
                 font=("Segoe UI", 7, "bold"),
                 bg=fc_bg, fg=fc_fg).pack(side=tk.LEFT)

        status = membro["status"] if membro["status"] else "Ativo"
        st_bg, st_fg = STATUS_CORES.get(status, (DIVIDER, "#aaaaaa"))
        tk.Label(badge_row, text=f"  {status}  ",
                 font=("Segoe UI", 7, "bold"),
                 bg=st_bg, fg=st_fg).pack(side=tk.LEFT, padx=(6, 0))

        # Info line
        info_parts = []
        if membro["telefone"]:
            info_parts.append(f"📞 {membro['telefone']}")
        if membro["aniversario_dia"] and membro["aniversario_mes"]:
            mes_nome = MESES[membro["aniversario_mes"]]
            info_parts.append(f"🎂 {membro['aniversario_dia']:02d}/{mes_nome[:3]}")
        if membro["email"]:
            info_parts.append(f"✉ {membro['email']}")

        if info_parts:
            tk.Label(inner, text="   ".join(info_parts),
                     font=("Segoe UI", 8), fg=TEXT_MUTED,
                     bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W, pady=(6, 0))

        if membro["observacoes"]:
            obs = membro["observacoes"]
            if len(obs) > 60:
                obs = obs[:57] + "…"
            tk.Label(inner, text=obs,
                     font=("Segoe UI", 8, "italic"), fg="#666688",
                     bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W, pady=(2, 0))

        # Action buttons
        btn_row = tk.Frame(inner, bg=BG_CARD)
        btn_row.pack(anchor=tk.E, pady=(6, 0))

        _ib = dict(relief=tk.FLAT, cursor="hand2",
                   font=("Segoe UI", 10), padx=6, pady=2)

        tk.Button(btn_row, text="✏",
                  bg=BG_CARD, fg=BTN_COLOR,
                  activebackground=DIVIDER, activeforeground=BTN_COLOR,
                  command=lambda m=membro: self._edit_member(m), **_ib
                  ).pack(side=tk.LEFT, padx=(0, 2))

        tk.Button(btn_row, text="🗑",
                  bg=BG_CARD, fg="#ff6b6b",
                  activebackground="#2d1e1e", activeforeground="#ff6b6b",
                  command=lambda m=membro: self._confirm_delete(m), **_ib
                  ).pack(side=tk.LEFT)

        # Click to select
        for widget in (outer, card, inner, top, av, name_status, badge_row):
            widget.bind("<Button-1>",
                        lambda _e, m=membro, o=outer: self._select(m, o))

    def _select(self, membro, outer):
        if self.selected_member:
            # Clear previous selection highlight if widget still exists
            try:
                pass
            except Exception:
                pass
        self.selected_member = membro
        outer.configure(highlightbackground=ACCENT)

    def _edit_member(self, membro):
        fresh = obter_membro(membro["id"])
        self._open_form(membro=fresh)

    def _render_pagination(self):
        for w in self._pag_bar.winfo_children():
            w.destroy()

        total       = len(self._all_membros)
        total_pages = max(1, (total + self._PAGE_SIZE - 1) // self._PAGE_SIZE)
        if total_pages <= 1:
            return

        _btn = dict(relief=tk.FLAT, cursor="hand2",
                    font=("Segoe UI", 10, "bold"), pady=4, padx=14)

        can_prev = self._page > 0
        tk.Button(self._pag_bar, text="← Anterior",
                  command=self._prev_page,
                  state=tk.NORMAL if can_prev else tk.DISABLED,
                  bg=BG_CARD,
                  fg=TEXT if can_prev else "#555577",
                  activebackground=DIVIDER, activeforeground=TEXT,
                  **_btn).pack(side=tk.LEFT)

        tk.Label(self._pag_bar,
                 text=f"Página {self._page + 1} de {total_pages}",
                 font=("Segoe UI", 10), fg=TEXT_MUTED,
                 bg=BG_DARK).pack(side=tk.LEFT, padx=20)

        can_next = self._page < total_pages - 1
        tk.Button(self._pag_bar, text="Próximo →",
                  command=self._next_page,
                  state=tk.NORMAL if can_next else tk.DISABLED,
                  bg=BG_CARD,
                  fg=TEXT if can_next else "#555577",
                  activebackground=DIVIDER, activeforeground=TEXT,
                  **_btn).pack(side=tk.LEFT)

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def _next_page(self):
        total_pages = max(1, (len(self._all_membros) + self._PAGE_SIZE - 1) // self._PAGE_SIZE)
        if self._page < total_pages - 1:
            self._page += 1
            self._render_page()

    # ── Formulário ────────────────────────────────────────────────────────────

    def _show_new(self):
        self._open_form(membro=None)

    def _show_edit(self):
        if not self.selected_member:
            messagebox.showwarning("Atenção", "Clique em um membro para selecioná-lo antes de editar.")
            return
        fresh = obter_membro(self.selected_member["id"])
        self._open_form(membro=fresh)

    def _open_form(self, membro=None):
        editing = membro is not None

        win = tk.Toplevel(self.root)
        win.title("Editar Membro" if editing else "Novo Membro")
        win.configure(bg=BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        W_WIN, H_WIN = 500, 670
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width()  - W_WIN) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - H_WIN) // 2
        win.geometry(f"{W_WIN}x{H_WIN}+{x}+{y}")

        BG_IN    = DIVIDER
        PAD      = dict(padx=28)
        ENTRY_KW = dict(font=("Segoe UI", 11), bg=BG_IN, fg=TEXT,
                        relief=tk.FLAT, bd=0, insertbackground=TEXT)

        form = tk.Frame(win, bg=BG_DARK)
        form.pack(fill=tk.BOTH, expand=True)

        def lbl(text, optional=False):
            color = TEXT_MUTED if optional else TEXT
            txt   = f"{text}  (opcional)" if optional else text
            tk.Label(form, text=txt, font=("Segoe UI", 10, "bold"),
                     fg=color, bg=BG_DARK).pack(anchor=tk.W, pady=(0, 4), **PAD)

        tk.Label(form, text="Editar Membro" if editing else "Novo Membro",
                 font=("Segoe UI", 16, "bold"), fg=ACCENT,
                 bg=BG_DARK).pack(anchor=tk.W, pady=(20, 16), **PAD)

        lbl("Nome completo *")
        nome_e = tk.Entry(form, **ENTRY_KW)
        nome_e.pack(fill=tk.X, ipady=8, pady=(0, 12), **PAD)
        if editing:
            nome_e.insert(0, membro["nome"] or "")

        lbl("Função *")
        funcao_var = tk.StringVar(value=membro["funcao"] if editing else "Membro")
        funcao_cb = ttk.Combobox(form, textvariable=funcao_var,
                                 values=FUNCOES, state="readonly", font=("Segoe UI", 11))
        funcao_cb.pack(fill=tk.X, ipady=4, pady=(0, 12), **PAD)

        lbl("Status *")
        current_st = membro["status"] if (editing and membro["status"]) else "Ativo"
        status_var = tk.StringVar(value=current_st)
        st_row = tk.Frame(form, bg=BG_DARK)
        st_row.pack(anchor=tk.W, pady=(0, 12), **PAD)
        for s in STATUS:
            tk.Radiobutton(st_row, text=s, variable=status_var, value=s,
                           font=("Segoe UI", 10), fg=TEXT, bg=BG_DARK,
                           selectcolor=BG_CARD,
                           activebackground=BG_DARK,
                           activeforeground=TEXT).pack(side=tk.LEFT, padx=(0, 20))

        lbl("Aniversário", optional=True)
        brow = tk.Frame(form, bg=BG_DARK)
        brow.pack(fill=tk.X, pady=(0, 12), **PAD)
        tk.Label(brow, text="Dia:", font=("Segoe UI", 10), fg="#aaaaaa",
                 bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
        dia_var = tk.StringVar(value=str(membro["aniversario_dia"] or "") if editing else "")
        tk.Spinbox(brow, from_=1, to=31, textvariable=dia_var, width=4,
                   font=("Segoe UI", 11), bg=BG_IN, fg=TEXT,
                   relief=tk.FLAT, buttonbackground="#3a3a5a",
                   insertbackground=TEXT).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(brow, text="Mês:", font=("Segoe UI", 10), fg="#aaaaaa",
                 bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
        mes_names = ["(nenhum)"] + MESES[1:]
        mes_var = tk.StringVar(
            value=MESES[membro["aniversario_mes"]] if (editing and membro["aniversario_mes"]) else "(nenhum)")
        ttk.Combobox(brow, textvariable=mes_var, values=mes_names,
                     state="readonly", width=12, font=("Segoe UI", 10)).pack(side=tk.LEFT)

        lbl("Telefone / WhatsApp", optional=True)
        tel_e = tk.Entry(form, **ENTRY_KW)
        tel_e.pack(fill=tk.X, ipady=8, pady=(0, 12), **PAD)
        if editing:
            tel_e.insert(0, membro["telefone"] or "")

        lbl("Email", optional=True)
        email_e = tk.Entry(form, **ENTRY_KW)
        email_e.pack(fill=tk.X, ipady=8, pady=(0, 12), **PAD)
        if editing:
            email_e.insert(0, membro["email"] or "")

        lbl("Observações", optional=True)
        obs_txt = tk.Text(form, font=("Segoe UI", 11), bg=BG_IN, fg=TEXT,
                          relief=tk.FLAT, bd=0, height=3,
                          insertbackground=TEXT, wrap=tk.WORD)
        obs_txt.pack(fill=tk.X, pady=(0, 16), **PAD)
        if editing and membro["observacoes"]:
            obs_txt.insert("1.0", membro["observacoes"])

        btn_row = tk.Frame(form, bg=BG_DARK)
        btn_row.pack(anchor=tk.W, pady=(4, 24), **PAD)

        def _salvar():
            nome = nome_e.get().strip()
            if not nome:
                messagebox.showwarning("Atenção", "O nome é obrigatório.", parent=win)
                return

            funcao  = funcao_var.get()
            status  = status_var.get()
            dia_str = dia_var.get().strip()
            mes_str = mes_var.get()
            aniv_dia = aniv_mes = None
            if dia_str and mes_str != "(nenhum)":
                try:
                    aniv_dia = int(dia_str)
                    aniv_mes = MESES.index(mes_str)
                    if not (1 <= aniv_dia <= 31) or not (1 <= aniv_mes <= 12):
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Atenção", "Data de aniversário inválida.", parent=win)
                    return

            tel   = tel_e.get().strip() or None
            email = email_e.get().strip() or None
            obs   = obs_txt.get("1.0", tk.END).strip() or None

            if editing:
                atualizar_membro(membro["id"], nome, funcao, status,
                                 aniv_dia, aniv_mes, tel, email, obs)
                messagebox.showinfo("Sucesso", "Membro atualizado!", parent=win)
            else:
                criar_membro(nome, funcao, status, aniv_dia, aniv_mes, tel, email, obs)
                messagebox.showinfo("Sucesso", "Membro cadastrado!", parent=win)

            win.destroy()
            self.refresh_list()

        _b = dict(relief=tk.FLAT, cursor="hand2",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8)
        tk.Button(btn_row, text="Salvar", command=_salvar,
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  **_b).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="Cancelar", command=win.destroy,
                  bg=DIVIDER, fg="#aaaaaa",
                  activebackground="#3d3d54", activeforeground=TEXT,
                  **_b).pack(side=tk.LEFT)

    # ── Deletar ───────────────────────────────────────────────────────────────

    def _confirm_delete(self, membro):
        ok = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja remover '{membro['nome']}' do cadastro?\n\n"
            "Esta ação não pode ser desfeita.",
        )
        if ok:
            deletar_membro(membro["id"])
            self.selected_member = None
            self.refresh_list()
