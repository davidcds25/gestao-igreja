"""
modals/member.py
================
Modal de Novo/Editar Membro com design system completo.

Secoes:
  1. Avatar preview (cor aleatoria) + Nome
  2. Identificacao — funcao, grupo
  3. Status — pills coloridas (Ativo / Afastado / Visitante)
  4. Contato — telefone/WhatsApp e e-mail
  5. Aniversario — dia (Spinbox) + mes (Combobox)
  6. Observacoes — textarea livre
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import button, section_label, divider_line
from .base import StyledModal


_AVATAR_COLORS = [
    "#e74c3c",
    "#e67e22",
    "#f1c40f",
    "#2ecc71",
    "#1abc9c",
    "#3498db",
    "#9b59b6",
    "#e91e8c",
    "#00d4ff",
]

_STATUS_BG = {
    "Ativo":     COLORS["success"],
    "Afastado":  COLORS["danger"],
    "Visitante": COLORS["warning"],
}
_STATUS_FG = {
    "Ativo":     COLORS["bg_dark"],
    "Afastado":  "#ffffff",
    "Visitante": COLORS["bg_dark"],
}

# Seed by member id hash so the same member always gets the same color
def _pick_color(member_id=None):
    if member_id is not None:
        return _AVATAR_COLORS[int(member_id) % len(_AVATAR_COLORS)]
    return random.choice(_AVATAR_COLORS)


class MemberModal(StyledModal):
    WIDTH = 660

    def __init__(self, root, *, member_id=None, on_save=None):
        from core.members import obter_membro
        _raw = obter_membro(member_id) if member_id else None
        self._m = dict(_raw) if _raw else None
        self._member_id = member_id
        self._on_save = on_save
        self._editing = self._m is not None
        self._avatar_color = _pick_color(member_id)

        title    = "Editar Membro" if self._editing else "Novo Membro"
        subtitle = "" if self._editing else "Preencha os dados e salve."
        super().__init__(root, title=title, subtitle=subtitle)

    # ── posicionamento — garante altura minima ─────────────────────────

    def _center_and_show(self):
        self.update_idletasks()
        w    = self.WIDTH
        max_h = int(self.winfo_screenheight() * 0.90)
        h    = min(max(660, self.winfo_reqheight()), max_h)
        sx   = self.winfo_screenwidth()
        sy   = self.winfo_screenheight()
        x    = (sx - w) // 2
        y    = max(0, (sy - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()

    # ── corpo ─────────────────────────────────────────────────────────

    def _build_body(self, parent):
        bg = COLORS["bg_dark"]

        # Remove right padding so scrollbar can sit flush against the window edge
        parent.pack_configure(padx=(SPACING[6], 0))

        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SPACING[3]))

        inner = tk.Frame(canvas, bg=bg)
        _wid = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(_wid, width=e.width))

        def _wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def _register(e=None):
            canvas.bind_all("<MouseWheel>", _wheel)

        def _unregister(e=None):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

        # Registra imediatamente e re-registra ao entrar no modal
        # (page_container dispara <Leave> → unbind_all ao abrir o Toplevel)
        _register()
        self.bind("<Enter>",   _register)
        canvas.bind("<Enter>", _register)
        inner.bind("<Enter>",  _register)

        canvas.bind("<Destroy>", lambda e: _unregister())
        self.bind("<Destroy>",   lambda e: _unregister())

        self._build_form(inner)

    # ── formulario ────────────────────────────────────────────────────

    def _build_form(self, p):
        m  = self._m
        bg = COLORS["bg_dark"]
        S  = SPACING

        # ── Avatar + Nome (linha unica) ────────────────────────────────
        top_row = tk.Frame(p, bg=bg)
        top_row.pack(fill=tk.X, pady=(0, S[4]))

        AVATAR_SIZE = 72
        av_cv = tk.Canvas(top_row, width=AVATAR_SIZE, height=AVATAR_SIZE,
                          bg=bg, highlightthickness=0)
        av_cv.pack(side=tk.LEFT, padx=(0, S[4]))

        def _draw_avatar(*_):
            av_cv.delete("all")
            color = self._avatar_color
            name  = getattr(self, "_nome_var", tk.StringVar()).get().strip()
            parts = [w for w in name.split() if w]
            if parts:
                init = parts[0][0].upper()
                if len(parts) > 1:
                    init += parts[1][0].upper()
            else:
                init = "?"
            r = AVATAR_SIZE - 4
            av_cv.create_oval(2, 2, r, r, fill=color, outline="")
            av_cv.create_text(AVATAR_SIZE // 2, AVATAR_SIZE // 2,
                              text=init, fill="#ffffff",
                              font=(FONTS["body"][0], int(AVATAR_SIZE * 0.29), "bold"))

        self._draw_avatar = _draw_avatar

        nome_col = tk.Frame(top_row, bg=bg)
        nome_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(nome_col, text="Nome Completo *", font=FONTS["tiny_bold"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 2))
        self._nome_var = tk.StringVar(value=m["nome"] if m else "")
        nome_e = tk.Entry(
            nome_col, textvariable=self._nome_var,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            font=FONTS["body"], relief=tk.FLAT, bd=0,
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            highlightcolor=COLORS["accent"],
        )
        nome_e.pack(fill=tk.X, ipady=8)
        self._nome_var.trace_add("write", lambda *_: _draw_avatar())

        divider_line(p, soft=True).pack(fill=tk.X, pady=(0, S[3]))

        # ── SECAO 1: IDENTIFICACAO ────────────────────────────────────
        section_label(p, text="Identificacao").pack(
            fill=tk.X, anchor=tk.W, pady=(0, S[2]))

        two_col = tk.Frame(p, bg=bg)
        two_col.pack(fill=tk.X, pady=(0, S[3]))
        two_col.columnconfigure(0, weight=1, uniform="tc")
        two_col.columnconfigure(1, weight=1, uniform="tc")

        from core.members import FUNCOES, GRUPOS, STATUS, MESES

        f_funcao = tk.Frame(two_col, bg=bg)
        f_funcao.grid(row=0, column=0, sticky="nsew", padx=(0, S[3]))
        tk.Label(f_funcao, text="Funcao *", font=FONTS["tiny_bold"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 2))
        self._funcao_var = tk.StringVar(value=m["funcao"] if m else "Membro")
        ttk.Combobox(f_funcao, textvariable=self._funcao_var, values=FUNCOES,
                     state="readonly", font=FONTS["body"]).pack(fill=tk.X, ipady=SPACING[1])

        f_grupo = tk.Frame(two_col, bg=bg)
        f_grupo.grid(row=0, column=1, sticky="nsew")
        tk.Label(f_grupo, text="Grupo  (opcional)", font=FONTS["tiny_bold"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 2))
        _grupo_opts = ["(nenhum)"] + list(GRUPOS)
        _grupo_init = (m.get("grupo") or "(nenhum)") if m else "(nenhum)"
        self._grupo_var = tk.StringVar(value=_grupo_init)
        ttk.Combobox(f_grupo, textvariable=self._grupo_var, values=_grupo_opts,
                     state="readonly", font=FONTS["body"]).pack(fill=tk.X, ipady=SPACING[1])

        # Checkbox Grupo de Casais — pode combinar com qualquer grupo acima
        # O checkbox e o label ficam separados: fg escuro no checkbox para o
        # checkmark ficar visível sobre o fundo branco (selectcolor="white").
        _casais_init = bool(m.get("grupo_casais")) if m else False
        self._casais_var = tk.BooleanVar(value=_casais_init)
        casais_row = tk.Frame(two_col, bg=bg)
        casais_row.grid(row=1, column=1, sticky="w", pady=(S[2], 0))
        tk.Checkbutton(
            casais_row,
            variable=self._casais_var,
            text="",
            bg=bg, fg=COLORS["bg_dark"],   # fg escuro → checkmark visível no branco
            selectcolor="white",
            activebackground=bg,
        ).pack(side=tk.LEFT)
        tk.Label(
            casais_row, text="Grupo de Casais",
            bg=bg, fg=COLORS["text"],
            font=FONTS["body"],
        ).pack(side=tk.LEFT)

        divider_line(p, soft=True).pack(fill=tk.X, pady=(0, S[3]))

        # ── SECAO 2: STATUS ───────────────────────────────────────────
        section_label(p, text="Status").pack(
            fill=tk.X, anchor=tk.W, pady=(0, S[2]))

        _status_init = (m["status"] if m and m.get("status") else "Ativo")
        self._status_var = tk.StringVar(value=_status_init)

        pill_row = tk.Frame(p, bg=bg)
        pill_row.pack(anchor=tk.W, pady=(0, S[3]))
        _pills = {}

        def _select_status(val):
            self._status_var.set(val)
            for v2, pill2 in _pills.items():
                sel = v2 == val
                pill2.configure(
                    bg=_STATUS_BG.get(v2, COLORS["accent"]) if sel else COLORS["bg_card"],
                    fg=_STATUS_FG.get(v2, "#ffffff") if sel else COLORS["text_muted"],
                )

        for s in STATUS:
            pill = tk.Label(
                pill_row, text=s, font=FONTS["small_bold"],
                bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                padx=SPACING[4], pady=SPACING[2], cursor="hand2", relief=tk.FLAT,
            )
            pill.pack(side=tk.LEFT, padx=(0, S[2]))
            _pills[s] = pill
            pill.bind("<Button-1>", lambda e, v=s: _select_status(v))

        _select_status(_status_init)

        divider_line(p, soft=True).pack(fill=tk.X, pady=(0, S[3]))

        # ── SECAO 3: CONTATO ──────────────────────────────────────────
        section_label(p, text="Contato").pack(
            fill=tk.X, anchor=tk.W, pady=(0, S[2]))

        two_contact = tk.Frame(p, bg=bg)
        two_contact.pack(fill=tk.X, pady=(0, S[3]))
        two_contact.columnconfigure(0, weight=1, uniform="ct")
        two_contact.columnconfigure(1, weight=1, uniform="ct")

        f_tel = tk.Frame(two_contact, bg=bg)
        f_tel.grid(row=0, column=0, sticky="nsew", padx=(0, S[3]))
        tk.Label(f_tel, text="Telefone / WhatsApp  (opcional)",
                 font=FONTS["tiny_bold"], bg=bg,
                 fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 2))
        self._tel_e = tk.Entry(
            f_tel,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            font=FONTS["body"], relief=tk.FLAT, bd=0,
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            highlightcolor=COLORS["accent"],
        )
        self._tel_e.pack(fill=tk.X, ipady=SPACING[2])
        if m and m.get("telefone"):
            self._tel_e.insert(0, m["telefone"])

        f_email = tk.Frame(two_contact, bg=bg)
        f_email.grid(row=0, column=1, sticky="nsew")
        tk.Label(f_email, text="E-mail  (opcional)", font=FONTS["tiny_bold"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 2))
        self._email_e = tk.Entry(
            f_email,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            font=FONTS["body"], relief=tk.FLAT, bd=0,
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            highlightcolor=COLORS["accent"],
        )
        self._email_e.pack(fill=tk.X, ipady=SPACING[2])
        if m and m.get("email"):
            self._email_e.insert(0, m["email"])

        divider_line(p, soft=True).pack(fill=tk.X, pady=(0, S[3]))

        # ── SECAO 4: ANIVERSARIO ──────────────────────────────────────
        section_label(p, text="Aniversario").pack(
            fill=tk.X, anchor=tk.W, pady=(0, S[2]))

        brow = tk.Frame(p, bg=bg)
        brow.pack(anchor=tk.W, pady=(0, S[3]))

        tk.Label(brow, text="Dia:", font=FONTS["body"],
                 fg=COLORS["text_muted"], bg=bg).pack(side=tk.LEFT, padx=(0, S[1]))
        self._dia_var = tk.StringVar(
            value=str(m["aniversario_dia"]) if (m and m.get("aniversario_dia")) else "")
        ttk.Spinbox(
            brow, from_=1, to=31, textvariable=self._dia_var,
            width=4, font=FONTS["body"], justify=tk.CENTER,
        ).pack(side=tk.LEFT, padx=(0, S[4]))

        tk.Label(brow, text="Mes:", font=FONTS["body"],
                 fg=COLORS["text_muted"], bg=bg).pack(side=tk.LEFT, padx=(0, S[1]))
        _mes_names = ["(nenhum)"] + MESES[1:]
        _mes_init = (
            MESES[m["aniversario_mes"]]
            if (m and m.get("aniversario_mes")) else "(nenhum)"
        )
        self._mes_var = tk.StringVar(value=_mes_init)
        ttk.Combobox(
            brow, textvariable=self._mes_var, values=_mes_names,
            state="readonly", width=13, font=FONTS["body"],
        ).pack(side=tk.LEFT)

        divider_line(p, soft=True).pack(fill=tk.X, pady=(0, S[3]))

        # ── SECAO 5: OBSERVACOES ──────────────────────────────────────
        section_label(p, text="Observacoes").pack(
            fill=tk.X, anchor=tk.W, pady=(0, S[2]))

        self._obs_t = tk.Text(
            p,
            bg=COLORS["input_bg"], fg=COLORS["text"],
            font=FONTS["body"], relief=tk.FLAT, bd=0,
            height=3, wrap=tk.WORD,
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
            highlightcolor=COLORS["accent"],
        )
        self._obs_t.pack(fill=tk.X, pady=(0, S[2]))
        if m and m.get("observacoes"):
            self._obs_t.insert("1.0", m["observacoes"])

        _draw_avatar()

    # ── footer ────────────────────────────────────────────────────────

    def _build_footer(self, left: tk.Frame, right: tk.Frame):
        button(left, text="Cancelar", kind="ghost",
               command=self.destroy).pack(side=tk.LEFT)
        label = "Salvar Alteracoes" if self._editing else "Cadastrar Membro"
        button(right, text=label, kind="primary",
               command=self._save).pack(side=tk.LEFT)

    # ── salvar ────────────────────────────────────────────────────────

    def _save(self):
        from core.members import criar_membro, atualizar_membro, MESES

        nome = self._nome_var.get().strip()
        if not nome:
            messagebox.showwarning("Atencao", "O nome e obrigatorio.", parent=self)
            return

        funcao       = self._funcao_var.get()
        status       = self._status_var.get()
        grupo        = self._grupo_var.get()
        grupo        = None if grupo == "(nenhum)" else grupo
        grupo_casais = self._casais_var.get()

        dia_str  = self._dia_var.get().strip()
        mes_str  = self._mes_var.get()
        aniv_dia = aniv_mes = None
        if dia_str and mes_str != "(nenhum)":
            try:
                aniv_dia = int(float(dia_str))
                aniv_mes = MESES.index(mes_str)
                if not (1 <= aniv_dia <= 31) or not (1 <= aniv_mes <= 12):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Atencao", "Data de aniversario invalida.",
                                       parent=self)
                return

        tel   = self._tel_e.get().strip() or None
        email = self._email_e.get().strip() or None
        obs   = self._obs_t.get("1.0", tk.END).strip() or None

        try:
            if self._editing:
                atualizar_membro(self._member_id, nome, funcao, status,
                                 aniv_dia, aniv_mes, tel, email, obs,
                                 grupo, grupo_casais)
                messagebox.showinfo("Sucesso", "Membro atualizado!", parent=self)
            else:
                criar_membro(nome, funcao, status, aniv_dia, aniv_mes,
                             tel, email, obs, grupo, grupo_casais)
                messagebox.showinfo("Sucesso", "Membro cadastrado!", parent=self)

            self.destroy()
            if self._on_save:
                self._on_save()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar: {ex}", parent=self)
