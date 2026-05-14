"""
Interface gráfica para gerenciamento de atividades
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
from tkcalendar import DateEntry
from core.activities import (
    criar_atividade, listar_atividades, obter_atividade,
    atualizar_atividade, deletar_atividade,
    listar_status_atividade, registrar_log,
)

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#00d4ff"
BTN_COLOR  = "#667eea"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"
DIVIDER    = "#2d2d44"

STATUS_COLORS = {
    "Planejado":    ("#667eea", "#ffffff"),
    "Em Andamento": ("#00d4ff", "#0f0f23"),
    "Concluído":    ("#51cf66", "#0f0f23"),
    "Cancelado":    ("#ff6b6b", "#ffffff"),
    "Adiado":       ("#ffa94d", "#1a1a2e"),
}

_MESES_SHORT = ["JAN","FEV","MAR","ABR","MAI","JUN",
                 "JUL","AGO","SET","OUT","NOV","DEZ"]


class ActivitiesWindow:
    def __init__(self, parent_frame, root_window, current_user):
        self.root         = root_window
        self.current_user = current_user
        self._all         = []
        self._active_tab  = "proximas"

        self.frame = tk.Frame(parent_frame, bg=BG_DARK)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        outer = tk.Frame(self.frame, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=40, pady=24)

        self._build_header(outer)
        self._build_tabs(outer)

        self._list_frame = tk.Frame(outer, bg=BG_DARK)
        self._list_frame.pack(fill=tk.BOTH, expand=True)

        self.refresh_list()

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 4))

        left = tk.Frame(hdr, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Atividades e Eventos",
                 font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W)
        tk.Label(left, text="Gerencie cultos, células e eventos especiais",
                 font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(anchor=tk.W)

        _btn = dict(relief=tk.FLAT, cursor="hand2",
                    font=("Segoe UI", 10, "bold"), padx=16, pady=8)

        tk.Button(hdr, text="+ Nova Atividade",
                  command=self.show_new_activity,
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  **_btn).pack(side=tk.RIGHT)

        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(12, 0))

    def _build_tabs(self, parent):
        tab_row = tk.Frame(parent, bg=BG_DARK)
        tab_row.pack(fill=tk.X, pady=(0, 0))

        self._tab_refs = {}
        tabs = [
            ("proximas",   "Próximas"),
            ("realizadas", "Realizadas"),
            ("canceladas", "Canceladas"),
        ]
        for key, label in tabs:
            col = tk.Frame(tab_row, bg=BG_DARK)
            col.pack(side=tk.LEFT, padx=(0, 2))

            lbl_count = tk.Label(col, text="", font=("Segoe UI", 8),
                                 fg=TEXT_MUTED, bg=BG_DARK)
            lbl_count.pack(anchor=tk.CENTER)

            btn = tk.Label(col, text=label,
                           font=("Segoe UI", 10, "bold"),
                           fg=TEXT_MUTED, bg=BG_DARK,
                           padx=16, pady=8,
                           cursor="hand2")
            btn.pack(anchor=tk.CENTER)

            rail = tk.Frame(col, bg=BG_DARK, height=2)
            rail.pack(fill=tk.X)

            k = key
            btn.bind("<Button-1>", lambda _e, k=k: self._switch_tab(k))
            lbl_count.bind("<Button-1>", lambda _e, k=k: self._switch_tab(k))
            self._tab_refs[key] = {"btn": btn, "rail": rail, "count": lbl_count}

        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X)

    def _switch_tab(self, key):
        self._active_tab = key
        self._render_tabs()
        self._render_list()

    def _render_tabs(self):
        all_at = self._all
        today = datetime.now()

        counts = {"proximas": 0, "realizadas": 0, "canceladas": 0}
        for at in all_at:
            status = at["status"] or ""
            if status == "Cancelado":
                counts["canceladas"] += 1
            elif status == "Concluído":
                counts["realizadas"] += 1
            else:
                counts["proximas"] += 1

        for key, refs in self._tab_refs.items():
            active = (key == self._active_tab)
            refs["btn"].configure(
                fg=TEXT if active else TEXT_MUTED,
                font=("Segoe UI", 10, "bold") if active else ("Segoe UI", 10),
            )
            refs["rail"].configure(bg=ACCENT if active else BG_DARK)
            c = counts.get(key, 0)
            refs["count"].configure(
                text=str(c) if c > 0 else "",
                fg=ACCENT if active else TEXT_MUTED,
            )

    # ── Dados ─────────────────────────────────────────────────────────────────

    def refresh_list(self):
        self._all = list(listar_atividades())
        self._render_tabs()
        self._render_list()

    def _filtered(self):
        tab = self._active_tab
        result = []
        for at in self._all:
            status = at["status"] or ""
            if tab == "canceladas" and status == "Cancelado":
                result.append(at)
            elif tab == "realizadas" and status == "Concluído":
                result.append(at)
            elif tab == "proximas" and status not in ("Cancelado", "Concluído"):
                result.append(at)
        result.sort(key=lambda a: a["data_inicio"] or "")
        return result

    # ── Lista de atividades ───────────────────────────────────────────────────

    def _render_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        items = self._filtered()

        if not items:
            self._empty_state(self._list_frame)
            return

        # Scrollable canvas
        wrapper = tk.Frame(self._list_frame, bg=BG_DARK)
        wrapper.pack(fill=tk.BOTH, expand=True)
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(wrapper, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(wrapper, orient=tk.VERTICAL, command=canvas.yview)
        canvas.grid(row=0, column=0, sticky="nsew")

        def _update_sb(lo, hi):
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                sb.grid_remove()
            else:
                sb.grid(row=0, column=1, sticky="ns")
            sb.set(lo, hi)

        canvas.configure(yscrollcommand=_update_sb)

        inner = tk.Frame(canvas, bg=BG_DARK)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>",
                    lambda e: canvas.bind_all("<MouseWheel>",
                    lambda ev: canvas.yview_scroll(-1 * (ev.delta // 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for at in items:
            self._build_row(inner, at)

    def _empty_state(self, parent):
        f = tk.Frame(parent, bg=BG_DARK)
        f.pack(expand=True, pady=60)
        tk.Label(f, text="📋", font=("Segoe UI", 36),
                 fg=DIVIDER, bg=BG_DARK).pack()
        tk.Label(f, text="Nenhuma atividade aqui",
                 font=("Segoe UI", 13, "bold"),
                 fg="#555577", bg=BG_DARK).pack(pady=(8, 4))
        tk.Label(f, text='Clique em "+ Nova Atividade" para criar',
                 font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack()

    def _build_row(self, parent, at):
        row_outer = tk.Frame(parent, bg=BG_CARD, height=80)
        row_outer.pack(fill=tk.X, pady=(0, 2))
        row_outer.pack_propagate(False)

        row = tk.Frame(row_outer, bg=BG_CARD)
        row.pack(fill=tk.BOTH, expand=True)

        # Date column
        dt = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(at["data_inicio"][:10], fmt)
                break
            except Exception:
                pass

        day = dt.strftime("%d") if dt else "--"
        mon = _MESES_SHORT[dt.month - 1] if dt else "---"
        hora_ini = at["data_inicio"][11:16] if len(at["data_inicio"] or "") > 10 else ""
        hora_fim = (at["data_fim"][11:16]
                    if at["data_fim"] and len(at["data_fim"]) > 10 else "")
        hora_txt = hora_ini
        if hora_fim:
            hora_txt += f" → {hora_fim}"

        date_col = tk.Frame(row, bg=BG_CARD, width=80)
        date_col.pack(side=tk.LEFT, fill=tk.Y, padx=(16, 0))
        date_col.pack_propagate(False)
        date_inner = tk.Frame(date_col, bg=BG_CARD)
        date_inner.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(date_inner, text=day, font=("Segoe UI", 20, "bold"),
                 fg=ACCENT, bg=BG_CARD, anchor=tk.CENTER).pack()
        tk.Label(date_inner, text=mon, font=("Segoe UI", 8),
                 fg=TEXT_MUTED, bg=BG_CARD, anchor=tk.CENTER).pack()
        if hora_txt:
            tk.Label(date_inner, text=hora_txt, font=("Segoe UI", 7),
                     fg="#aaaaaa", bg=BG_CARD, anchor=tk.CENTER).pack()

        # Separator
        tk.Frame(row, bg=DIVIDER, width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=(12, 14), pady=12)

        # Info column
        info = tk.Frame(row, bg=BG_CARD)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)

        title_row = tk.Frame(info, bg=BG_CARD)
        title_row.pack(anchor=tk.W, fill=tk.X)

        tk.Label(title_row, text=at["titulo"],
                 font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=BG_CARD, anchor=tk.W).pack(side=tk.LEFT)

        sc_bg, sc_fg = STATUS_COLORS.get(at["status"], ("#444466", TEXT))
        tk.Label(title_row, text=f"  {at['status']}  ",
                 font=("Segoe UI", 8, "bold"),
                 bg=sc_bg, fg=sc_fg).pack(side=tk.LEFT, padx=(10, 0))

        meta = []
        if at["local"]:
            meta.append(f"📍 {at['local']}")
        if at["nome_responsavel"]:
            meta.append(f"👤 {at['nome_responsavel']}")
        if meta:
            tk.Label(info, text="   ".join(meta),
                     font=("Segoe UI", 9), fg=TEXT_MUTED,
                     bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W, pady=(4, 0))

        # Action buttons
        btn_col = tk.Frame(row, bg=BG_CARD)
        btn_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 14), pady=14)
        btn_inner = tk.Frame(btn_col, bg=BG_CARD)
        btn_inner.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        _b = dict(relief=tk.FLAT, cursor="hand2", font=("Segoe UI", 9, "bold"),
                  padx=10, pady=4)

        aid = at["id"]
        tk.Button(btn_inner, text="✏ Editar",
                  bg=BTN_COLOR, fg=TEXT,
                  activebackground="#5566cc", activeforeground=TEXT,
                  command=lambda a=aid: self._edit(a), **_b).pack(fill=tk.X)

        if at["status"] not in ("Cancelado", "Concluído"):
            tk.Button(btn_inner, text="✗ Cancelar",
                      bg="#ff6b6b", fg=TEXT,
                      activebackground="#e05555", activeforeground=TEXT,
                      command=lambda a=aid: self._confirm_delete(a),
                      **_b).pack(fill=tk.X, pady=(4, 0))

    # ── Ações ─────────────────────────────────────────────────────────────────

    def show_new_activity(self):
        self._open_dialog(None)

    def show_edit_activity(self):
        self._open_dialog(None)

    def _edit(self, activity_id):
        self._open_dialog(activity_id)

    def _confirm_delete(self, activity_id):
        at = obter_atividade(activity_id)
        titulo = at["titulo"] if at else str(activity_id)
        if messagebox.askyesno("Confirmar cancelamento",
                               f"Deseja cancelar a atividade:\n\"{titulo}\"?"):
            try:
                deletar_atividade(activity_id)
                registrar_log(self.current_user["id"],
                              f"Cancelou atividade: '{titulo}' (ID: {activity_id})")
                self.refresh_list()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao cancelar: {ex}")

    # ── Formulário Modal ──────────────────────────────────────────────────────

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                 fg="#cccccc", bg=BG_DARK,
                 anchor=tk.W).pack(anchor=tk.W, pady=(0, 5))

    def _entry(self, parent, **kw):
        e = tk.Entry(parent, bg=DIVIDER, fg=TEXT,
                     font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                     highlightthickness=2,
                     highlightbackground="#3a3a55",
                     highlightcolor=ACCENT,
                     insertbackground=TEXT, **kw)
        e.pack(fill=tk.X, ipady=9, pady=(0, 14))
        return e

    def _date_time_row(self, parent, initial_value=None):
        date_init = None
        h_init, m_init = "08", "00"
        if initial_value:
            parts = initial_value.split(" ")
            try:
                date_init = datetime.strptime(parts[0], "%Y-%m-%d").date()
            except Exception:
                pass
            if len(parts) > 1:
                t = parts[1][:5].split(":")
                h_init = t[0].zfill(2)
                m_init = t[1].zfill(2) if len(t) > 1 else "00"

        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(0, 14))

        de = DateEntry(
            row, width=11,
            locale="pt_BR",
            date_pattern="yyyy-mm-dd",
            background=SIDEBAR_BG,     foreground=TEXT,
            selectbackground=ACCENT,
            selectforeground=BG_DARK,
            normalbackground=BG_CARD,
            normalforeground=TEXT,
            headersbackground=SIDEBAR_BG,
            headersforeground=ACCENT,
            weekendbackground=BG_CARD,
            weekendforeground="#888888",
            othermonthbackground=BG_DARK,
            othermonthforeground="#555577",
            othermonthwebackground=BG_DARK,
            othermonthweforeground="#555577",
            font=("Segoe UI", 10),
            cursor="hand2",
        )
        de.pack(side=tk.LEFT, ipady=6, padx=(0, 10))
        if date_init:
            de.set_date(date_init)

        tk.Label(row, text="às", font=("Segoe UI", 10),
                 fg="#888888", bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 8))

        hour_var = tk.StringVar(value=h_init)
        ttk.Spinbox(row, from_=0, to=23, width=3,
                    textvariable=hour_var, format="%02.0f",
                    wrap=True, justify=tk.CENTER,
                    font=("Segoe UI", 10)).pack(side=tk.LEFT)

        tk.Label(row, text=":", font=("Segoe UI", 11, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(side=tk.LEFT, padx=2)

        min_var = tk.StringVar(value=m_init)
        ttk.Spinbox(row, from_=0, to=59, width=3,
                    textvariable=min_var, format="%02.0f",
                    wrap=True, justify=tk.CENTER,
                    font=("Segoe UI", 10)).pack(side=tk.LEFT)

        def get_dt():
            raw = de.get()
            date_str = raw
            for _fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    date_str = datetime.strptime(raw, _fmt).strftime("%Y-%m-%d")
                    break
                except Exception:
                    continue
            try:
                h = int(float(hour_var.get()))
                m = int(float(min_var.get()))
            except ValueError:
                h, m = 0, 0
            return f"{date_str} {h:02d}:{m:02d}"

        return get_dt

    def _open_dialog(self, activity_id):
        dialog = tk.Toplevel(self.root)
        dialog.withdraw()
        title_text = "Nova Atividade" if not activity_id else "Editar Atividade"
        dialog.title(title_text)
        dialog.configure(bg=BG_DARK)
        dialog.grab_set()
        dialog.resizable(False, False)

        at = obter_atividade(activity_id) if activity_id else None

        outer = tk.Frame(dialog, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=35, pady=28)

        tk.Label(outer, text=title_text,
                 font=("Segoe UI", 18, "bold"),
                 fg=ACCENT, bg=BG_DARK,
                 justify=tk.CENTER).pack(pady=(0, 6))

        tk.Frame(outer, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0, 20))

        self._field_label(outer, "Título *")
        titulo_e = self._entry(outer)
        if at:
            titulo_e.insert(0, at["titulo"])

        self._field_label(outer, "Descrição")
        desc_t = tk.Text(outer, height=3, bg=DIVIDER, fg=TEXT,
                         font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                         highlightthickness=0, insertbackground=TEXT,
                         wrap=tk.WORD)
        desc_t.pack(fill=tk.X, pady=(0, 14))
        if at:
            desc_t.insert(1.0, at["descricao"] or "")

        self._field_label(outer, "Data Início *")
        get_inicio = self._date_time_row(outer, at["data_inicio"] if at else None)

        data_fim_inicial = at["data_fim"] if at and at["data_fim"] else None
        has_fim = tk.BooleanVar(value=bool(data_fim_inicial))
        fim_row = tk.Frame(outer, bg=BG_DARK)
        fim_row.pack(fill=tk.X, pady=(0, 4))

        tk.Checkbutton(fim_row, text="Definir data fim",
                       variable=has_fim,
                       bg=BG_DARK, fg="#aaaaaa",
                       selectcolor=BG_CARD,
                       activebackground=BG_DARK,
                       font=("Segoe UI", 10),
                       command=lambda: _toggle_fim()).pack(side=tk.LEFT)

        fim_container = tk.Frame(outer, bg=BG_DARK)
        get_fim_fn = self._date_time_row(fim_container, data_fim_inicial)

        fim_container.pack(fill=tk.X, pady=(4, 0), after=fim_row)
        if not has_fim.get():
            fim_container.pack_forget()

        def _toggle_fim():
            if has_fim.get():
                fim_container.pack(fill=tk.X, pady=(4, 0), after=fim_row)
            else:
                fim_container.pack_forget()
            dialog.update_idletasks()
            w = 600
            h = outer.winfo_reqheight() + 60
            h = min(h, int(dialog.winfo_screenheight() * 0.88))
            dialog.geometry(f"{w}x{h}+{dialog.winfo_x()}+{dialog.winfo_y()}")

        tk.Frame(outer, bg=BG_DARK, height=10).pack()

        self._field_label(outer, "Local")
        local_e = self._entry(outer)
        if at and at["local"]:
            local_e.insert(0, at["local"])

        self._field_label(outer, "Status")
        status_var = tk.StringVar(value=at["status"] if at else "Planejado")
        status_combo = ttk.Combobox(outer, textvariable=status_var,
                                    values=listar_status_atividade(),
                                    state="readonly", font=("Segoe UI", 10))
        status_combo.pack(fill=tk.X, ipady=6, pady=(0, 20))

        tk.Frame(outer, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0, 18))

        def save():
            titulo    = titulo_e.get().strip()
            descricao = desc_t.get(1.0, tk.END).strip()
            inicio    = get_inicio()
            fim       = get_fim_fn() if has_fim.get() else None
            local     = local_e.get().strip()
            status    = status_var.get()
            tipo      = "Geral"

            if not titulo:
                messagebox.showwarning("Aviso", "O campo Título é obrigatório!")
                return

            if status == "Concluído":
                confirmar = messagebox.askyesno(
                    "Confirmar Conclusão",
                    f"Tem certeza que deseja marcar a atividade\n"
                    f"\"{titulo}\" como Concluída?\n\n"
                    "Ela será arquivada e removida da lista.\n"
                    "O registro ficará apenas nos logs.",
                )
                if not confirmar:
                    return
                try:
                    if activity_id:
                        registrar_log(self.current_user["id"],
                                      f"Concluiu e arquivou atividade: '{titulo}' (ID: {activity_id})")
                        deletar_atividade(activity_id)
                    else:
                        new_id = criar_atividade(titulo, descricao, tipo,
                                                 inicio, fim, local,
                                                 self.current_user["id"])
                        registrar_log(self.current_user["id"],
                                      f"Concluiu e arquivou atividade: '{titulo}' (ID: {new_id})")
                        deletar_atividade(new_id)
                    messagebox.showinfo("Arquivada",
                                        f"A atividade \"{titulo}\" foi concluída e arquivada.")
                    self.refresh_list()
                    dialog.destroy()
                except Exception as ex:
                    messagebox.showerror("Erro", f"Erro ao arquivar: {ex}")
                return

            try:
                if activity_id:
                    atualizar_atividade(activity_id, titulo, descricao, tipo,
                                        inicio, fim, local,
                                        self.current_user["id"], status)
                    registrar_log(self.current_user["id"],
                                  f"Editou atividade: '{titulo}' (ID: {activity_id})")
                    messagebox.showinfo("Sucesso", "Atividade atualizada!")
                else:
                    new_id = criar_atividade(titulo, descricao, tipo,
                                             inicio, fim, local,
                                             self.current_user["id"])
                    registrar_log(self.current_user["id"],
                                  f"Criou atividade: '{titulo}' (ID: {new_id})")
                    messagebox.showinfo("Sucesso", "Atividade criada!")
                self.refresh_list()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao salvar: {ex}")

        tk.Button(outer, text="  SALVAR  ",
                  command=save,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, cursor="hand2",
                  padx=30, pady=10,
                  activebackground="#00b8d9",
                  activeforeground=BG_DARK).pack()

        dialog.update_idletasks()
        w  = 600
        h  = outer.winfo_reqheight() + 60
        h  = min(h, int(dialog.winfo_screenheight() * 0.88))
        sx = dialog.winfo_screenwidth()
        sy = dialog.winfo_screenheight()
        dialog.geometry(f"{w}x{h}+{(sx-w)//2}+{max(0,(sy-h)//2)}")
        dialog.deiconify()
