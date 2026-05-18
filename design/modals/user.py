"""
modals/user.py
==============
Modal "Novo Usuário" / "Editar Usuário" (usuários do sistema — quem faz login).

USO:
    from design.modals import UserModal

    # Criar novo
    UserModal(root, mode="new",
              on_save=lambda data: ...).show()

    # Editar existente
    UserModal(root, mode="edit", initial=existing_user,
              on_save=lambda data: ...,
              on_delete=lambda: ...).show()

`initial` (dict):
    nome, email, nivel ("Admin"|"Coordenador"|"Usuário"),
    ativo (bool), voce (bool — esconde botão excluir se for o próprio usuário).

`on_save` deve retornar None em caso de sucesso ou string de erro para exibir.
"""

import tkinter as tk

from ..ui import COLORS, SPACING, FONTS
from .base import (
    StyledDialog,
    modal_field, modal_input,
    modal_button, modal_pill_radio,
    modal_password_input, modal_password_strength,
    modal_avatar_preview,
)


NIVEL_OPTIONS = [
    {"value": "Admin",       "label": "Admin",
     "tint": "#667eea", "fg": "#ffffff",
     "desc": "Cria e altera outros usuários, acesso total."},
    {"value": "Coordenador", "label": "Coordenador",
     "tint": "#0891b2", "fg": "#ffffff",
     "desc": "Cadastra membros e agenda atividades."},
    {"value": "Usuário",     "label": "Usuário",
     "tint": "#9b59b6", "fg": "#ffffff",
     "desc": "Só visualiza dados, sem permissão de edição."},
]


def _nivel_meta(value):
    for n in NIVEL_OPTIONS:
        if n["value"] == value:
            return n
    return NIVEL_OPTIONS[2]


class UserModal(StyledDialog):
    def __init__(self, parent, *, mode: str = "new",
                 initial: dict = None,
                 on_save=None, on_delete=None):
        self.mode = mode
        self.initial = initial or {}
        self.on_save = on_save
        self.on_delete = on_delete

        seed = self.initial
        self._nome   = tk.StringVar(value=seed.get("nome", ""))
        self._email  = tk.StringVar(value=seed.get("email", ""))
        self._senha  = tk.StringVar(value="")
        self._senha2 = tk.StringVar(value="")
        self._nivel  = tk.StringVar(value=seed.get("nivel", "Usuário"))
        self._ativo  = tk.BooleanVar(value=seed.get("ativo", True))

        self._color = tk.StringVar(value=_nivel_meta(self._nivel.get())["tint"])
        self._nivel.trace_add("write",
                              lambda *_: self._color.set(_nivel_meta(self._nivel.get())["tint"]))

        is_edit = mode == "edit"
        super().__init__(
            parent,
            eyebrow="Editar usuário" if is_edit else "Novo usuário",
            icon=None,
            title=(seed.get("nome") or "Editar usuário") if is_edit
                  else "Adicionar usuário ao sistema",
            subtitle=("Atualize permissões e dados de acesso."
                      if is_edit
                      else "Quem cadastrar aqui poderá fazer login no sistema."),
            width=620,
            height=740 if not is_edit else 760,
        )

        self._mount_header_avatar()

    def _mount_header_avatar(self):
        # FRAGILE: localiza o header pelo bg — se _build_header mudar a cor, o avatar some silenciosamente
        for child in self.win.winfo_children():
            if child.cget("bg") == COLORS["bg_card_raised"]:
                inner = child.winfo_children()[0]
                av = modal_avatar_preview(
                    inner, name_var=self._nome, color_var=self._color, size=42)
                av.pack(side=tk.LEFT, anchor=tk.N, padx=(0, SPACING[3]),
                        before=inner.winfo_children()[0])
                break

    # ──────────────────────────────────────────────────────────────────
    # BODY
    # ──────────────────────────────────────────────────────────────────
    def _build_body(self, parent):
        is_edit = self.mode == "edit"

        f = modal_field(parent, label="Nome completo", required=True)
        f.pack(fill=tk.X, pady=(0, SPACING[4]))
        modal_input(f, var=self._nome,
                    placeholder="Ex: David Cavalcante"
                    ).pack(fill=tk.X)

        f = modal_field(parent, label="E-mail", required=True, hint="usado para login")
        f.pack(fill=tk.X, pady=(0, SPACING[4]))
        modal_input(f, var=self._email, icon="✉",
                    placeholder="usuario@igreja.com"
                    ).pack(fill=tk.X)

        if not is_edit:
            self._build_password_block(parent).pack(fill=tk.X, pady=(0, SPACING[4]))
        else:
            self._build_password_notice(parent).pack(fill=tk.X, pady=(0, SPACING[4]))

        f = modal_field(parent, label="Nível de acesso", required=True)
        f.pack(fill=tk.X, pady=(0, SPACING[2]))
        modal_pill_radio(f, var=self._nivel, options=[
            {"value": n["value"], "label": n["label"],
             "tint": n["tint"], "fg": n["fg"]}
            for n in NIVEL_OPTIONS
        ]).pack(fill=tk.X)

        self._nivel_desc_row = tk.Frame(parent, bg=parent["bg"])
        self._nivel_desc_row.pack(fill=tk.X, pady=(SPACING[1], SPACING[4]))
        self._nivel_dot = tk.Canvas(self._nivel_desc_row, width=8, height=8,
                                    bg=parent["bg"], highlightthickness=0)
        self._nivel_dot.pack(side=tk.LEFT, padx=(0, SPACING[2]))
        self._nivel_desc = tk.Label(self._nivel_desc_row, text="",
                                    font=FONTS["small"],
                                    bg=parent["bg"], fg=COLORS["text_muted"])
        self._nivel_desc.pack(side=tk.LEFT)
        self._nivel.trace_add("write", lambda *_: self._refresh_nivel_desc())
        self._refresh_nivel_desc()

        if is_edit:
            f = modal_field(parent, label="Status da conta")
            f.pack(fill=tk.X)
            self._build_status_row(f).pack(fill=tk.X)

    def _refresh_nivel_desc(self):
        n = _nivel_meta(self._nivel.get())
        self._nivel_dot.delete("all")
        self._nivel_dot.create_oval(0, 0, 8, 8, fill=n["tint"], outline="")
        self._nivel_desc.configure(text=n["desc"])

    def _build_password_block(self, parent):
        block = tk.Frame(parent, bg=COLORS["bg_dark"],
                         highlightbackground=COLORS["divider"],
                         highlightthickness=1)
        inner = tk.Frame(block, bg=COLORS["bg_dark"])
        inner.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[3])

        head = tk.Frame(inner, bg=COLORS["bg_dark"])
        head.pack(fill=tk.X)
        tk.Label(head, text="Senha de acesso",
                 font=FONTS["body_strong"],
                 bg=COLORS["bg_dark"], fg=COLORS["text"]
                 ).pack(side=tk.LEFT)
        tk.Label(head, text="  *",
                 font=FONTS["body_strong"],
                 bg=COLORS["bg_dark"], fg=COLORS["danger"]
                 ).pack(side=tk.LEFT)

        line = tk.Frame(inner, bg=COLORS["bg_dark"])
        line.pack(fill=tk.X, pady=(SPACING[2], SPACING[2]))
        line.columnconfigure(0, weight=1, uniform="pw")
        line.columnconfigure(1, weight=1, uniform="pw")

        modal_password_input(line, var=self._senha,
                             placeholder="Mínimo 6 caracteres"
                             ).grid(row=0, column=0, sticky="ew",
                                    padx=(0, SPACING[2]))
        modal_password_input(line, var=self._senha2,
                             placeholder="Confirmar senha"
                             ).grid(row=0, column=1, sticky="ew")

        modal_password_strength(inner, var=self._senha).pack(fill=tk.X)

        self._pw_mismatch = tk.Label(inner, text="",
                                     font=FONTS["small_bold"],
                                     bg=COLORS["bg_dark"], fg=COLORS["danger"])
        self._pw_mismatch.pack(fill=tk.X, pady=(SPACING[1], 0))

        def _check_match(*_):
            a, b = self._senha.get(), self._senha2.get()
            if a and b and a != b:
                self._pw_mismatch.configure(text="⚠  As senhas não coincidem.")
            else:
                self._pw_mismatch.configure(text="")

        self._senha.trace_add("write", _check_match)
        self._senha2.trace_add("write", _check_match)
        return block

    def _build_password_notice(self, parent):
        box = tk.Frame(parent, bg=COLORS["bg_dark"],
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
        inner = tk.Frame(box, bg=COLORS["bg_dark"])
        inner.pack(fill=tk.X, padx=SPACING[3], pady=SPACING[3])
        tk.Label(inner, text="🔑",
                 font=(FONTS["body"][0], 14),
                 bg=COLORS["bg_dark"], fg=COLORS["accent"]
                 ).pack(side=tk.LEFT, padx=(0, SPACING[2]))
        tk.Label(inner,
                 text='A senha só pode ser alterada pela ação\n"Redefinir senha" na linha do usuário.',
                 font=FONTS["small"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                 justify=tk.LEFT, anchor=tk.W
                 ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        return box

    def _build_status_row(self, parent):
        box = tk.Frame(parent, bg=COLORS["input_bg"],
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
        inner = tk.Frame(box, bg=COLORS["input_bg"])
        inner.pack(fill=tk.X, padx=SPACING[3], pady=SPACING[2] + 2)

        dot = tk.Canvas(inner, width=10, height=10,
                        bg=COLORS["input_bg"], highlightthickness=0)
        dot.pack(side=tk.LEFT, padx=(0, SPACING[2]))

        label = tk.Label(inner, text="",
                         font=FONTS["body_strong"],
                         bg=COLORS["input_bg"])
        label.pack(side=tk.LEFT)

        toggle_btn = tk.Button(inner, text="",
                               font=FONTS["btn"],
                               relief=tk.FLAT, bd=0,
                               cursor="hand2",
                               padx=SPACING[3], pady=SPACING[1] + 2,
                               highlightthickness=1)
        toggle_btn.pack(side=tk.RIGHT)

        def _redraw(*_):
            ativo = self._ativo.get()
            color = COLORS["success"] if ativo else COLORS["text_muted"]
            dot.delete("all")
            dot.create_oval(0, 0, 10, 10, fill=color, outline="")
            label.configure(
                text="Ativo — pode acessar o sistema" if ativo else "Inativo — login bloqueado",
                fg=color)
            if ativo:
                toggle_btn.configure(text="Desativar",
                                     fg=COLORS["warning"],
                                     bg=COLORS["input_bg"],
                                     activebackground=COLORS["input_bg"],
                                     activeforeground=COLORS["warning"],
                                     highlightbackground=COLORS["warning"])
            else:
                toggle_btn.configure(text="Ativar",
                                     fg=COLORS["success"],
                                     bg=COLORS["input_bg"],
                                     activebackground=COLORS["input_bg"],
                                     activeforeground=COLORS["success"],
                                     highlightbackground=COLORS["success"])

        def _toggle():
            from .confirm import ask_confirm
            ativo = self._ativo.get()
            if ativo:
                ok = ask_confirm(
                    self.win,
                    title="Desativar esta conta?",
                    message="O usuário não conseguirá fazer login enquanto a conta estiver inativa.",
                    confirm_label="Desativar",
                    variant="warning",
                )
            else:
                ok = ask_confirm(
                    self.win,
                    title="Ativar esta conta?",
                    message="O usuário voltará a conseguir fazer login normalmente.",
                    confirm_label="Ativar",
                    variant="info",
                )
            if ok:
                self._ativo.set(not ativo)

        toggle_btn.configure(command=_toggle)
        self._ativo.trace_add("write", _redraw)
        _redraw()
        return box

    # ──────────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────────
    def _build_footer(self, left, right):
        # label de erro persistente — texto vazio quando não há erro
        self._err_label = tk.Label(left, text="*  obrigatório",
                                   font=FONTS["small"],
                                   bg=left["bg"], fg=COLORS["text_muted"],
                                   wraplength=340, justify=tk.LEFT)
        self._err_label.pack(side=tk.LEFT, padx=(0, SPACING[3]))

        if self.mode == "edit" and not self.initial.get("voce", False):
            modal_button(left, text="Excluir usuário", icon="🗑",
                         kind="danger",
                         command=self._handle_delete
                         ).pack(side=tk.LEFT)

        modal_button(right, text="Cancelar", kind="ghost",
                     command=self.cancel
                     ).pack(side=tk.LEFT, padx=(0, SPACING[2]))

        save_label = "Salvar alterações" if self.mode == "edit" else "Criar usuário"
        save_icon  = "+" if self.mode == "new" else None
        modal_button(right, text=save_label, icon=save_icon,
                     kind="primary",
                     command=self._handle_save
                     ).pack(side=tk.LEFT)

    # ──────────────────────────────────────────────────────────────────
    # AÇÕES
    # ──────────────────────────────────────────────────────────────────
    def _collect(self):
        return {
            "nome":  self._nome.get().strip(),
            "email": self._email.get().strip(),
            "senha": self._senha.get(),  # usado só em mode == "new"; ignorado no edit
            "nivel": self._nivel.get().strip(),
            "ativo": bool(self._ativo.get()),
        }

    def _validate(self, data) -> str:
        if not data["nome"] or len(data["nome"]) < 3:
            return "Informe o nome completo do usuário."
        if not data["email"] or "@" not in data["email"] or "." not in data["email"]:
            return "Email inválido — confira o endereço."
        if not data["nivel"]:
            return "Selecione um nível de acesso."
        if self.mode == "new":
            pw, pw2 = self._senha.get(), self._senha2.get()
            if not pw:
                return "Informe uma senha de acesso."
            if len(pw) < 6:
                return "A senha deve ter no mínimo 6 caracteres."
            if pw != pw2:
                return "As senhas não coincidem."
        return None

    def _handle_save(self):
        data = self._collect()
        err = self._validate(data)
        if err:
            self._flash_error(err)
            return
        if self.on_save:
            callback_err = self.on_save(data)
            if callback_err:
                self._flash_error(callback_err)
                return
        self.close_with(data)

    def _handle_delete(self):
        from .confirm import ask_confirm
        ok = ask_confirm(
            self.win,
            title=f"Excluir o usuário \"{self.initial.get('nome', '')}\"?",
            message="Essa pessoa perderá o acesso ao sistema imediatamente.",
            detail="Os registros que ela criou permanecem no sistema, "
                   "mas a conta de login será removida em definitivo. "
                   "Essa ação não pode ser desfeita.",
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
            self._err_label.configure(text=f"  {msg}", fg=COLORS["danger"],
                                      font=FONTS["small_bold"])
            if hasattr(self, "_err_after"):
                self.win.after_cancel(self._err_after)
            self._err_after = self.win.after(4000, self._clear_error)

    def _clear_error(self):
        if hasattr(self, "_err_label") and self._err_label.winfo_exists():
            self._err_label.configure(text="*  obrigatório",
                                      fg=COLORS["text_muted"],
                                      font=FONTS["small"])
