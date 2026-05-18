"""
modals/prayer.py
================
Modal de criação e edição de orações.
Modos: "new" | "edit"
"""

import tkinter as tk

from ..ui import COLORS, SPACING, FONTS
from .base import (
    StyledDialog, modal_field, modal_input,
    modal_button, modal_pill_radio,
)

from core.prayers import CATEGORIAS, PRIVACIDADES, STATUS, CONTEXTOS

_CAT_TINTS = {
    "Saúde":         COLORS.get("success",  "#22a05a"),
    "Família":       COLORS.get("accent",   "#00d4ff"),
    "Finanças":      COLORS.get("warning",  "#d28200"),
    "Trabalho":      COLORS.get("accent2",  "#0891b2"),
    "Espiritual":    COLORS.get("purple",   "#9b59b6"),
    "Relacionamento": "#e07b4f",
    "Agradecimento": "#27ae60",
    "Outros":        COLORS.get("text_muted", "#888888"),
}

_PRIV_TINTS = {
    "Pública":       COLORS.get("success",  "#22a05a"),
    "Restrita":      COLORS.get("warning",  "#d28200"),
    "Confidencial":  COLORS.get("danger",   "#be2d2d"),
}

_STATUS_TINTS = {
    "Ativa":      COLORS.get("accent",   "#00d4ff"),
    "Respondida": COLORS.get("success",  "#22a05a"),
    "Arquivada":  COLORS.get("text_muted", "#888888"),
}


def _textarea(parent, *, var: tk.StringVar, rows: int = 3,
              placeholder: str = ""):
    """Campo de texto multilinha estilizado."""
    bg = COLORS["input_bg"]
    box = tk.Frame(parent, bg=bg,
                   highlightbackground=COLORS["divider"],
                   highlightcolor=COLORS["accent"],
                   highlightthickness=1, bd=0)

    txt = tk.Text(box, height=rows,
                  font=FONTS["body"],
                  bg=bg, fg=COLORS["text"],
                  insertbackground=COLORS["text"],
                  relief=tk.FLAT, bd=0,
                  wrap=tk.WORD,
                  padx=10, pady=8)
    txt.pack(fill=tk.X)

    # sincroniza Text ↔ StringVar
    def _on_change(*_):
        var.set(txt.get("1.0", tk.END).rstrip("\n"))

    def _set_placeholder():
        txt.insert("1.0", placeholder)
        txt.configure(fg=COLORS["text_very_dim"])
        box._has_placeholder = True

    def _focus_in(_e):
        if getattr(box, "_has_placeholder", False):
            txt.delete("1.0", tk.END)
            txt.configure(fg=COLORS["text"])
            box._has_placeholder = False

    def _focus_out(_e):
        if not txt.get("1.0", tk.END).strip():
            _set_placeholder()
            var.set("")

    txt.bind("<FocusIn>", _focus_in)
    txt.bind("<FocusOut>", _focus_out)
    txt.bind("<<Modified>>", lambda e: (txt.edit_modified(False), _on_change()))

    # preenche o conteúdo inicial
    init = var.get()
    if init:
        txt.insert("1.0", init)
    elif placeholder:
        _set_placeholder()

    box._txt = txt
    return box


def _pill_grid(parent, *, var: tk.StringVar, options: list,
               per_row: int = 4):
    """Pills em grade (múltiplas linhas)."""
    bg = COLORS["input_bg"]
    wrap = tk.Frame(parent, bg=parent["bg"])
    pills = []

    def _paint():
        sel = var.get()
        for btn, opt in pills:
            active = opt["value"] == sel
            tint = opt.get("tint", COLORS["accent"])
            btn.configure(
                bg=tint if active else bg,
                fg=COLORS["bg_dark"] if active else COLORS["text_dim"],
                highlightbackground=tint if active else COLORS["divider"],
            )

    def _make_click(value):
        def _click(_e=None):
            var.set(value)
            _paint()
        return _click

    for i, opt in enumerate(options):
        col = i % per_row
        row = i // per_row
        if col == 0:
            row_frame = tk.Frame(wrap, bg=parent["bg"])
            row_frame.pack(fill=tk.X, pady=(0, SPACING[1]))
        btn = tk.Button(row_frame, text=opt["label"],
                        font=FONTS["small_bold"],
                        bg=bg, fg=COLORS["text_dim"],
                        activebackground=opt.get("tint", COLORS["accent"]),
                        activeforeground=COLORS["bg_dark"],
                        relief=tk.FLAT, bd=0,
                        padx=SPACING[2], pady=SPACING[1] + 2,
                        cursor="hand2",
                        command=_make_click(opt["value"]))
        btn.configure(highlightbackground=COLORS["divider"], highlightthickness=1)
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True,
                 padx=(0, SPACING[1] if col < per_row - 1 else 0))
        pills.append((btn, opt))

    _paint()
    wrap._repaint = _paint
    return wrap


class PrayerModal(StyledDialog):
    def __init__(self, parent, *, mode="new", initial=None,
                 members=None, on_save=None, on_delete=None):
        self.mode     = mode
        self.initial  = initial or {}
        self.members  = members or []  # lista de (id, nome)
        self.on_save  = on_save
        self.on_delete = on_delete

        # variáveis de estado
        self._nome       = tk.StringVar(value=self.initial.get("solicitante_nome", ""))
        self._membro_id  = tk.IntVar(value=self.initial.get("membro_id") or 0)
        self._motivo     = tk.StringVar(value=self.initial.get("motivo", ""))
        self._categoria  = tk.StringVar(value=self.initial.get("categoria", "Outros"))
        self._privacidade = tk.StringVar(value=self.initial.get("privacidade", "Pública"))
        self._status     = tk.StringVar(value=self.initial.get("status", "Ativa"))
        self._contexto   = tk.StringVar(value=self.initial.get("contexto") or "")
        self._responsavel = tk.StringVar(value=self.initial.get("responsavel") or "")
        self._testemunho = tk.StringVar(value=self.initial.get("testemunho") or "")
        self._observacoes = tk.StringVar(value=self.initial.get("observacoes") or "")

        title = "Editar Oração" if mode == "edit" else "Nova Oração"
        super().__init__(
            parent,
            eyebrow="ORAÇÕES",
            title=title,
            width=700,
            height=800,
        )

    # ──────────────────────────────────────────────────────────────────
    # BODY
    # ──────────────────────────────────────────────────────────────────
    def _build_body(self, parent):
        bg = parent["bg"]
        sp = SPACING

        # ── Scroll wrapper ────────────────────────────────────────────
        # Remove right padding from body_frame so the scrollbar sits at the
        # window edge instead of floating inside the content area.
        parent.pack_configure(padx=(sp[6] + sp[1], 0))

        sb = tk.Scrollbar(parent, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0, bd=0,
                           yscrollincrement=20, yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                    padx=(0, sp[3]))  # gap between content and scrollbar
        sb.configure(command=canvas.yview)

        scroll_inner = tk.Frame(canvas, bg=bg)
        win_id = canvas.create_window((0, 0), window=scroll_inner, anchor=tk.NW)

        def _update_scroll(*_):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _resize(e):
            canvas.itemconfigure(win_id, width=e.width)
            canvas.after_idle(_update_scroll)

        canvas.bind("<Configure>", _resize)
        scroll_inner.bind("<Configure>", lambda e: canvas.after_idle(_update_scroll))

        def _wheel(e):
            lo, hi = canvas.yview()
            if hi - lo < 0.999:
                canvas.yview_scroll(-1 * (e.delta // 120) * 2, "units")

        canvas.bind("<Enter>",   lambda e: canvas.bind_all("<MouseWheel>", _wheel))
        canvas.bind("<Leave>",   lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # A partir daqui todo o conteúdo vai em scroll_inner
        p = scroll_inner

        # ── Solicitante ───────────────────────────────────────────────
        f_sol = modal_field(p, label="Solicitante", required=True)
        f_sol.pack(fill=tk.X, pady=(0, sp[3]))
        modal_input(f_sol, var=self._nome,
                    placeholder="Nome de quem pediu oração",
                    icon="🙏").pack(fill=tk.X)

        member_row = tk.Frame(f_sol, bg=bg)
        member_row.pack(fill=tk.X, pady=(sp[1] + 2, 0))
        tk.Label(member_row, text="Vincular a membro (opcional):",
                 font=FONTS["small"], bg=bg,
                 fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(2, sp[2]))
        self._build_member_select(member_row)

        # ── Motivo / Pedido ───────────────────────────────────────────
        f_motivo = modal_field(p, label="Pedido de oração", required=True)
        f_motivo.pack(fill=tk.X, pady=(0, sp[3]))
        _textarea(f_motivo, var=self._motivo, rows=3,
                  placeholder="Descreva o pedido de oração..."
                  ).pack(fill=tk.X)

        # ── Categoria ─────────────────────────────────────────────────
        f_cat = modal_field(p, label="Categoria", required=True)
        f_cat.pack(fill=tk.X, pady=(0, sp[3]))
        _pill_grid(f_cat, var=self._categoria, per_row=4, options=[
            {"value": c, "label": c, "tint": _CAT_TINTS.get(c, COLORS["accent"])}
            for c in CATEGORIAS
        ]).pack(fill=tk.X)

        # ── Privacidade + Contexto (linha dupla) ──────────────────────
        row2 = tk.Frame(p, bg=bg)
        row2.pack(fill=tk.X, pady=(0, sp[3]))
        row2.columnconfigure(0, weight=3, uniform="r2")
        row2.columnconfigure(1, weight=2, uniform="r2")

        f_priv = modal_field(row2, label="Privacidade", required=True)
        f_priv.grid(row=0, column=0, sticky="nsew", padx=(0, sp[3]))
        modal_pill_radio(f_priv, var=self._privacidade, options=[
            {"value": pv, "label": pv, "tint": _PRIV_TINTS.get(pv, COLORS["accent"])}
            for pv in PRIVACIDADES
        ]).pack(fill=tk.X)

        f_ctx = modal_field(row2, label="Contexto", hint="opcional")
        f_ctx.grid(row=0, column=1, sticky="nsew")
        self._build_contexto_select(f_ctx)

        # ── Status ────────────────────────────────────────────────────
        f_status = modal_field(p, label="Status", required=True)
        f_status.pack(fill=tk.X, pady=(0, sp[2]))
        modal_pill_radio(f_status, var=self._status, options=[
            {"value": s, "label": s, "tint": _STATUS_TINTS.get(s, COLORS["accent"])}
            for s in STATUS
        ]).pack(fill=tk.X)

        # Testemunho — visível apenas quando status = "Respondida"
        self._f_test = modal_field(p, label="Como foi respondida")
        _textarea(self._f_test, var=self._testemunho, rows=3,
                  placeholder="Registre o testemunho ou como a oração foi atendida..."
                  ).pack(fill=tk.X)

        def _toggle_testemunho(*_):
            if self._status.get() == "Respondida":
                self._f_test.pack(fill=tk.X, pady=(0, sp[3]))
            else:
                self._f_test.pack_forget()

        self._status.trace_add("write", _toggle_testemunho)
        _toggle_testemunho()

        # ── Responsável ───────────────────────────────────────────────
        f_resp = modal_field(p, label="Responsável pelo acompanhamento",
                             hint="opcional")
        f_resp.pack(fill=tk.X, pady=(0, sp[3]))
        modal_input(f_resp, var=self._responsavel,
                    placeholder="Nome do pastor ou líder responsável",
                    icon="👤").pack(fill=tk.X)

        # ── Observações internas ──────────────────────────────────────
        f_obs = modal_field(p, label="Observações internas",
                            hint="opcional — visível apenas pelos responsáveis")
        f_obs.pack(fill=tk.X)
        _textarea(f_obs, var=self._observacoes, rows=2,
                  placeholder="Notas internas sobre o acompanhamento..."
                  ).pack(fill=tk.X)

        # Espaço no final para o conteúdo não colar no footer
        tk.Frame(p, bg=bg, height=sp[4]).pack(fill=tk.X)

    # ──────────────────────────────────────────────────────────────────
    # HELPERS de campo
    # ──────────────────────────────────────────────────────────────────
    def _build_member_select(self, parent):
        bg = COLORS["input_bg"]
        options_map = {0: "— nenhum —"}
        options_map.update({mid: nome for mid, nome in self.members})
        labels = list(options_map.values())

        # OptionMenu estilizado
        menu_var = tk.StringVar()
        current_id = self._membro_id.get()
        menu_var.set(options_map.get(current_id, "— nenhum —"))

        def _on_select(val):
            for mid, nome in [(0, "— nenhum —")] + list(self.members):
                if nome == val or val == "— nenhum —":
                    self._membro_id.set(mid)
                    if mid and not self._nome.get():
                        self._nome.set(nome)
                    break

        om = tk.OptionMenu(parent, menu_var, *labels, command=_on_select)
        om.configure(
            font=FONTS["small"],
            bg=bg, fg=COLORS["text"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT, bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            padx=SPACING[2], pady=2,
        )
        om["menu"].configure(
            font=FONTS["small"],
            bg=COLORS["bg_card"], fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg_dark"],
            relief=tk.FLAT, bd=0,
        )
        om.pack(side=tk.LEFT)

    def _build_contexto_select(self, parent):
        bg = COLORS["input_bg"]
        opts = ["— selecione —"] + CONTEXTOS
        self._contexto_menu_var = tk.StringVar()
        cur = self._contexto.get()
        self._contexto_menu_var.set(cur if cur in CONTEXTOS else "— selecione —")

        def _on_select(val):
            self._contexto.set("" if val == "— selecione —" else val)

        om = tk.OptionMenu(parent, self._contexto_menu_var, *opts,
                           command=_on_select)
        om.configure(
            font=FONTS["small"],
            bg=bg, fg=COLORS["text"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT, bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            padx=SPACING[2], pady=2,
        )
        om["menu"].configure(
            font=FONTS["small"],
            bg=COLORS["bg_card"], fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg_dark"],
            relief=tk.FLAT, bd=0,
        )
        om.pack(fill=tk.X, pady=(SPACING[1] + 2, 0))

    # ──────────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────────
    def _build_footer(self, left, right):
        self._err_label = tk.Label(left, text="*  obrigatório",
                                   font=FONTS["small"],
                                   bg=left["bg"], fg=COLORS["text_muted"],
                                   wraplength=340, justify=tk.LEFT)
        self._err_label.pack(side=tk.LEFT, padx=(0, SPACING[3]))

        if self.mode == "edit":
            modal_button(left, text="Excluir", icon="🗑",
                         kind="danger",
                         command=self._handle_delete
                         ).pack(side=tk.LEFT)

        modal_button(right, text="Cancelar", kind="ghost",
                     command=self.cancel
                     ).pack(side=tk.LEFT, padx=(0, SPACING[2]))

        save_label = "Salvar alterações" if self.mode == "edit" else "Registrar oração"
        modal_button(right, text=save_label, icon="+",
                     kind="primary",
                     command=self._handle_save
                     ).pack(side=tk.LEFT)

    # ──────────────────────────────────────────────────────────────────
    # AÇÕES
    # ──────────────────────────────────────────────────────────────────
    def _collect(self):
        return {
            "solicitante_nome": self._nome.get().strip(),
            "membro_id":        self._membro_id.get() or None,
            "motivo":           self._motivo.get().strip(),
            "categoria":        self._categoria.get(),
            "privacidade":      self._privacidade.get(),
            "status":           self._status.get(),
            "contexto":         self._contexto.get() or None,
            "responsavel":      self._responsavel.get().strip() or None,
            "testemunho":       self._testemunho.get().strip() or None,
            "observacoes":      self._observacoes.get().strip() or None,
        }

    def _validate(self, data) -> str:
        if not data["solicitante_nome"]:
            return "Informe o nome de quem pediu a oração."
        if not data["motivo"]:
            return "Descreva o pedido de oração."
        if data["status"] == "Respondida" and not data["testemunho"]:
            return "Registre como a oração foi respondida antes de salvar."
        return None

    def _handle_save(self):
        data = self._collect()
        err = self._validate(data)
        if err:
            self._flash_error(err)
            return
        if self.on_save:
            cb_err = self.on_save(data)
            if cb_err:
                self._flash_error(cb_err)
                return
        self.close_with(data)

    def _handle_delete(self):
        from .confirm import ask_confirm
        ok = ask_confirm(
            self.win,
            title="Excluir esta oração?",
            message="O registro será removido permanentemente.",
            confirm_label="Sim, excluir",
            variant="danger",
        )
        if not ok:
            return
        if self.on_delete:
            self.on_delete()
        self.close_with({"_deleted": True})

    def _flash_error(self, msg):
        if hasattr(self, "_err_label") and self._err_label.winfo_exists():
            self._err_label.configure(text=f"  {msg}",
                                      fg=COLORS["danger"],
                                      font=FONTS["small_bold"])
            if hasattr(self, "_err_after"):
                self.win.after_cancel(self._err_after)
            self._err_after = self.win.after(4000, self._clear_error)

    def _clear_error(self):
        if hasattr(self, "_err_label") and self._err_label.winfo_exists():
            self._err_label.configure(text="*  obrigatório",
                                      fg=COLORS["text_muted"],
                                      font=FONTS["small"])
