"""
modals/activity.py
==================
Modal de Nova/Editar Atividade com design system.

Três seções:
  1. Informações Básicas — título + descrição
  2. Data e Local        — início, fim opcional, local
  3. Configurações       — status + função alvo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime as _dt

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    field, text_input, textarea, select, button,
    section_label, divider_line,
)
from .base import StyledModal


class ActivityModal(StyledModal):
    WIDTH = 620

    def __init__(self, root, *, activity_id=None, current_user_id=None, on_save=None):
        from core.activities import obter_atividade
        row = obter_atividade(activity_id) if activity_id else None
        self._at = dict(row) if row else None
        self._activity_id = activity_id
        self._current_user_id = current_user_id
        self._on_save = on_save
        self._editing = self._at is not None

        title = "Editar Atividade" if self._editing else "Nova Atividade"
        subtitle = "Preencha os dados e salve." if not self._editing else ""

        super().__init__(root, title=title, subtitle=subtitle)

    # ── posicionamento — janela próxima ao topo para não cortar rodapé ──

    def _center_and_show(self):
        self.update_idletasks()
        w  = self.WIDTH
        sh = self.winfo_screenheight()
        sw = self.winfo_screenwidth()
        # With a scroll canvas, winfo_reqheight() on self is tiny.
        # Compute real height: (modal overhead) + (form content height).
        if hasattr(self, '_scroll_canvas') and hasattr(self, '_form_frame'):
            overhead = self.winfo_reqheight() - self._scroll_canvas.winfo_reqheight()
            h = min(overhead + self._form_frame.winfo_reqheight(), int(sh * 0.88))
        else:
            h = min(self.winfo_reqheight(), int(sh * 0.88))
        x  = (sw - w) // 2
        y  = max(10, sh // 20)   # ~5 % do topo (≈54px em 1080p)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()

    # ── corpo com scroll — mesmo padrão do MemberModal ────────────────

    def _build_body(self, parent):
        bg = COLORS["bg_dark"]

        # Remove padding direito para scrollbar ficar rente à borda
        parent.pack_configure(padx=(SPACING[6], 0))

        sb = tk.Scrollbar(parent, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0, bd=0,
                           yscrollincrement=20, yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                    padx=(0, SPACING[3]))
        sb.configure(command=canvas.yview)

        p = tk.Frame(canvas, bg=bg)
        _wid = canvas.create_window((0, 0), window=p, anchor=tk.NW)

        p.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(_wid, width=e.width))

        def _wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            return "break"  # consume event so Spinbox/DateEntry don't also handle it

        def _bind_scroll(widget):
            """Bind scroll wheel directly to every widget — widget-level bindings
            fire before class-level ones (e.g. Spinbox) so break is respected."""
            widget.bind("<MouseWheel>", _wheel)
            for child in widget.winfo_children():
                _bind_scroll(child)

        self._build_form(p)

        # Save refs for height calculation in _center_and_show
        self._scroll_canvas = canvas
        self._form_frame    = p

        # Direct binding to canvas + every form widget (avoids bind_all/class conflicts)
        canvas.bind("<MouseWheel>", _wheel)
        _bind_scroll(p)

    def _build_form(self, parent):
        at = self._at
        bg = COLORS["bg_dark"]
        from datetime import date as _date
        _min = _date.today() if not self._editing else None

        # ── SEÇÃO 1: INFORMAÇÕES BÁSICAS ──────────────────────────────
        section_label(parent, text="Informações Básicas").pack(
            fill=tk.X, anchor=tk.W, pady=(0, SPACING[2]))

        f_titulo = field(parent, label="Título *")
        f_titulo.pack(fill=tk.X, pady=(0, SPACING[2]))
        self._titulo_e = text_input(f_titulo,
                                    value=(at["titulo"] if at else ""))
        self._titulo_e.pack(fill=tk.X, ipady=6)

        f_desc = field(parent, label="Descrição", hint="opcional")
        f_desc.pack(fill=tk.X, pady=(0, SPACING[3]))
        self._desc_t = textarea(f_desc, lines=2,
                                value=(at.get("descricao") or "" if at else ""))
        self._desc_t.pack(fill=tk.X)

        divider_line(parent, soft=True).pack(fill=tk.X, pady=(0, SPACING[3]))

        # ── SEÇÃO 2: DATA E LOCAL ──────────────────────────────────────
        section_label(parent, text="Data e Local").pack(
            fill=tk.X, anchor=tk.W, pady=(0, SPACING[2]))

        f_inicio = field(parent, label="Data e Hora de Início *")
        f_inicio.pack(fill=tk.X, pady=(0, SPACING[2]))
        self._get_inicio = self._date_time_row(f_inicio,
                                               at["data_inicio"] if at else None,
                                               min_date=_min)

        self._has_fim = tk.BooleanVar(value=bool(at and at.get("data_fim")))
        self._fim_toggle_frame = tk.Frame(parent, bg=bg)
        self._fim_toggle_frame.pack(fill=tk.X, pady=(0, SPACING[2]))
        tk.Checkbutton(
            self._fim_toggle_frame,
            text="Definir data/hora de término",
            variable=self._has_fim,
            bg=bg, fg=COLORS["text_muted"],
            selectcolor=COLORS["bg_card"],
            activebackground=bg,
            activeforeground=COLORS["text_muted"],
            font=FONTS["small"],
            command=self._toggle_fim,
        ).pack(side=tk.LEFT)

        self._fim_frame = tk.Frame(parent, bg=bg)
        f_fim = field(self._fim_frame, label="Data e Hora de Término")
        f_fim.pack(fill=tk.X)
        self._get_fim = self._date_time_row(f_fim,
                                            at.get("data_fim") if at else None,
                                            min_date=_min)
        if self._has_fim.get():
            self._fim_frame.pack(fill=tk.X, pady=(0, SPACING[2]),
                                 after=self._fim_toggle_frame)

        f_local = field(parent, label="Local", hint="opcional")
        f_local.pack(fill=tk.X, pady=(SPACING[2], SPACING[3]))
        self._local_e = text_input(f_local,
                                   value=(at.get("local") or "" if at else ""))
        self._local_e.pack(fill=tk.X, ipady=6)

        divider_line(parent, soft=True).pack(fill=tk.X, pady=(0, SPACING[3]))

        # ── SEÇÃO 3: CONFIGURAÇÕES ─────────────────────────────────────
        section_label(parent, text="Configurações").pack(
            fill=tk.X, anchor=tk.W, pady=(0, SPACING[2]))

        two_col = tk.Frame(parent, bg=bg)
        two_col.pack(fill=tk.X, pady=(0, SPACING[2]))
        two_col.columnconfigure(0, weight=1, uniform="c")
        two_col.columnconfigure(1, weight=1, uniform="c")

        from core.members import FUNCOES as _FUNCOES, GRUPOS as _GRUPOS
        _fa_options = ["(nenhum)", "Toda a Igreja"] + list(_FUNCOES)
        _fa_inicial = (at.get("funcao_alvo") or "(nenhum)") if at else "(nenhum)"
        _ga_options = ["(nenhum)"] + list(_GRUPOS) + ["Grupo de Casais"]
        _ga_inicial = (at.get("grupo_alvo") or "(nenhum)") if at else "(nenhum)"

        _status_atual = (at.get("status") or "Planejado") if at else "Planejado"
        _status_opts  = (["Planejado"] if not self._editing
                         else sorted({_status_atual, "Planejado"}))
        f_status = field(two_col, label="Status")
        f_status.grid(row=0, column=0, sticky="ew", padx=(0, SPACING[3]))
        self._status_cb = select(f_status, value=_status_atual, options=_status_opts)
        self._status_cb.pack(fill=tk.X)

        f_fa = field(two_col, label="Função Alvo", hint="para WhatsApp")
        f_fa.grid(row=0, column=1, sticky="ew")
        self._fa_cb = select(f_fa, value=_fa_inicial, options=_fa_options)
        self._fa_cb.pack(fill=tk.X)

        three_col = tk.Frame(parent, bg=bg)
        three_col.pack(fill=tk.X, pady=(SPACING[2], 0))
        three_col.columnconfigure(0, weight=1, uniform="gc")

        f_ga = field(three_col, label="Grupo Alvo", hint="para WhatsApp")
        f_ga.grid(row=0, column=0, sticky="ew")
        self._ga_cb = select(f_ga, value=_ga_inicial, options=_ga_options)
        self._ga_cb.pack(fill=tk.X)

    # ── data/hora ─────────────────────────────────────────────────────

    def _date_time_row(self, parent, initial_value=None, min_date=None):
        bg = parent["bg"]

        try:
            from tkcalendar import DateEntry as _DateEntry
            _HAS_CAL = True
        except ImportError:
            _HAS_CAL = False

        h_init, m_init = "08", "00"
        date_init = None

        if initial_value:
            parts = (initial_value or "").split(" ")
            try:
                date_init = _dt.strptime(parts[0], "%Y-%m-%d").date()
            except Exception:
                pass
            if len(parts) > 1:
                t = parts[1][:5].split(":")
                h_init = t[0].zfill(2)
                m_init = t[1].zfill(2) if len(t) > 1 else "00"

        row = tk.Frame(parent, bg=bg)
        row.pack(fill=tk.X)

        if _HAS_CAL:
            _cal_kwargs = {}
            if min_date:
                _cal_kwargs["mindate"] = min_date
            de = _DateEntry(
                row, width=11, locale="pt_BR", date_pattern="yyyy-mm-dd",
                background=COLORS["bg_card"], foreground=COLORS["text"],
                selectbackground=COLORS["accent"],
                selectforeground=COLORS["bg_dark"],
                normalbackground=COLORS["bg_card"],
                normalforeground=COLORS["text"],
                font=FONTS["body"], cursor="hand2",
                **_cal_kwargs,
            )
            de.pack(side=tk.LEFT, ipady=6, padx=(0, SPACING[3]))
            if date_init:
                de.set_date(date_init)
            get_raw_date = de.get
        else:
            sv = tk.StringVar(value=str(date_init or ""))
            de_e = tk.Entry(
                row, textvariable=sv,
                bg=COLORS["input_bg"], fg=COLORS["text"],
                font=FONTS["body"], relief=tk.FLAT, bd=0,
                insertbackground=COLORS["text"], width=12,
                highlightthickness=1,
                highlightbackground=COLORS["divider"],
                highlightcolor=COLORS["accent"],
            )
            de_e.pack(side=tk.LEFT, ipady=6, padx=(0, SPACING[3]))
            get_raw_date = sv.get

        tk.Label(row, text="às", font=FONTS["body"],
                 fg=COLORS["text_muted"], bg=bg).pack(side=tk.LEFT,
                                                      padx=(0, SPACING[2]))

        hour_var = tk.StringVar(value=h_init)
        min_var  = tk.StringVar(value=m_init)

        ttk.Spinbox(row, from_=0, to=23, width=3, textvariable=hour_var,
                    format="%02.0f", wrap=True, justify=tk.CENTER,
                    font=FONTS["body"]).pack(side=tk.LEFT)
        tk.Label(row, text=":", font=FONTS["body_strong"],
                 fg=COLORS["text"], bg=bg).pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(row, from_=0, to=59, width=3, textvariable=min_var,
                    format="%02.0f", wrap=True, justify=tk.CENTER,
                    font=FONTS["body"]).pack(side=tk.LEFT)

        def _get_dt():
            raw = get_raw_date()
            date_str = raw
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    date_str = _dt.strptime(raw, fmt).strftime("%Y-%m-%d")
                    break
                except Exception:
                    continue
            try:
                h = int(float(hour_var.get()))
                m = int(float(min_var.get()))
            except ValueError:
                h, m = 0, 0
            return f"{date_str} {h:02d}:{m:02d}"

        return _get_dt

    # ── toggle fim ────────────────────────────────────────────────────

    def _toggle_fim(self):
        if self._has_fim.get():
            # after= garante que o frame aparece logo abaixo do checkbox,
            # não no final do stack de pack
            self._fim_frame.pack(fill=tk.X, pady=(0, SPACING[2]),
                                 after=self._fim_toggle_frame)
        else:
            self._fim_frame.pack_forget()

    # ── footer ────────────────────────────────────────────────────────

    def _build_footer(self, left: tk.Frame, right: tk.Frame):
        button(left, text="Cancelar", kind="ghost",
               command=self.destroy).pack(side=tk.LEFT)
        label = "Salvar Alterações" if self._editing else "Criar Atividade"
        button(right, text=label, kind="primary",
               command=self._save).pack(side=tk.LEFT)

    # ── salvar ────────────────────────────────────────────────────────

    def _save(self):
        from core.activities import (
            criar_atividade, atualizar_atividade, registrar_log,
        )

        titulo = self._titulo_e.get().strip()
        if not titulo:
            messagebox.showwarning("Aviso", "O campo Título é obrigatório!",
                                   parent=self)
            return

        descricao   = self._desc_t.get("1.0", tk.END).strip()
        inicio      = self._get_inicio()
        fim         = self._get_fim() if self._has_fim.get() else None
        local       = self._local_e.get().strip() or None
        fa          = self._fa_cb.get()
        funcao_alvo = None if fa == "(nenhum)" else fa
        ga          = self._ga_cb.get()
        grupo_alvo  = None if ga == "(nenhum)" else ga
        uid         = self._current_user_id

        try:
            if self._editing:
                atualizar_atividade(
                    self._activity_id, titulo, descricao, "Geral",
                    inicio, fim, local, uid,
                    self._at.get("status", "Planejado"), funcao_alvo, grupo_alvo,
                )
                if uid:
                    registrar_log(
                        uid,
                        f"Editou atividade: '{titulo}' (ID: {self._activity_id})",
                    )
                messagebox.showinfo("Sucesso", "Atividade atualizada!", parent=self)
            else:
                new_id = criar_atividade(titulo, descricao, "Geral",
                                         inicio, fim, local, uid, funcao_alvo, grupo_alvo)
                if uid:
                    registrar_log(uid, f"Criou atividade: '{titulo}' (ID: {new_id})")
                messagebox.showinfo("Sucesso", "Atividade criada!", parent=self)

            self.destroy()
            if self._on_save:
                self._on_save()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar: {ex}", parent=self)
