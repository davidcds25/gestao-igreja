"""
modals/password_reset.py
========================
Modal "Redefinir Senha" — admin define uma nova senha para um usuário.

USO:
    from design.modals import PasswordResetModal

    PasswordResetModal(root,
        user={"nome": "admin", "email": "admin@igreja.com", "color": "#667eea"},
        on_save=lambda data: core.users.reset_password(uid, data["senha"]),
    ).show()

`user` (dict): nome, email, color (cor do avatar).
`on_save` recebe {"senha": "..."} e deve retornar None ou string de erro.
"""

import tkinter as tk

from ..ui import COLORS, SPACING, FONTS
from .base import (
    StyledDialog,
    modal_field, modal_button,
    modal_password_input, modal_password_strength, password_score,
    modal_avatar_preview,
)


class PasswordResetModal(StyledDialog):
    def __init__(self, parent, *, user: dict, on_save=None):
        self.user = user or {}
        self.on_save = on_save

        self._nome   = tk.StringVar(value=self.user.get("nome", "usuário"))
        self._color  = tk.StringVar(value=self.user.get("color") or COLORS["accent"])
        self._senha  = tk.StringVar()
        self._senha2 = tk.StringVar()

        super().__init__(
            parent,
            eyebrow="Redefinir senha",
            icon=None,
            title=f"Nova senha de {self.user.get('nome', 'usuário')}",
            subtitle=(f"Define uma nova senha para {self.user['email']}."
                      if self.user.get("email")
                      else "Define uma nova senha para este usuário."),
            width=520,
            height=None,
        )

        self._mount_header_avatar()

    def _mount_header_avatar(self):
        # FRAGILE: localiza o header pelo bg — se _build_header mudar a cor, o avatar some silenciosamente
        for child in self.win.winfo_children():
            if child.cget("bg") == COLORS["bg_card_raised"]:
                inner = child.winfo_children()[0]
                av = modal_avatar_preview(
                    inner, name_var=self._nome, color_var=self._color, size=38)
                av.pack(side=tk.LEFT, anchor=tk.N, padx=(0, SPACING[3]),
                        before=inner.winfo_children()[0])
                break

    # ──────────────────────────────────────────────────────────────────
    # BODY
    # ──────────────────────────────────────────────────────────────────
    def _build_body(self, parent):
        f = modal_field(parent, label="Nova senha", required=True)
        f.pack(fill=tk.X, pady=(0, SPACING[2]))
        pw1_box = modal_password_input(f, var=self._senha,
                                       placeholder="Mínimo 6 caracteres")
        pw1_box.pack(fill=tk.X)
        self.win.after(50, lambda: pw1_box._entry.focus_set())

        modal_password_strength(parent, var=self._senha
                                ).pack(fill=tk.X, pady=(0, SPACING[4]))

        f = modal_field(parent, label="Confirmar nova senha", required=True)
        f.pack(fill=tk.X, pady=(0, SPACING[2]))
        modal_password_input(f, var=self._senha2,
                             placeholder="Digite a senha novamente"
                             ).pack(fill=tk.X)

        self._feedback = tk.Label(parent, text="",
                                  font=FONTS["small_bold"],
                                  bg=parent["bg"], fg=COLORS["danger"],
                                  anchor=tk.W)
        self._feedback.pack(fill=tk.X, pady=(SPACING[2], 0))

        def _check(*_):
            a, b = self._senha.get(), self._senha2.get()
            if a and b and a != b:
                self._feedback.configure(text="⚠  As senhas não coincidem.",
                                         fg=COLORS["danger"])
            elif a and b and a == b and password_score(a) >= 1:
                self._feedback.configure(text="✓  Tudo certo, pode redefinir.",
                                         fg=COLORS["success"])
            else:
                self._feedback.configure(text="")

        self._senha.trace_add("write", _check)
        self._senha2.trace_add("write", _check)

    # ──────────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────────
    def _build_footer(self, left, right):
        tk.Label(left, text="O usuário será desconectado das outras sessões.",
                 font=FONTS["small"],
                 bg=left["bg"], fg=COLORS["text_muted"],
                 wraplength=240, justify=tk.LEFT
                 ).pack(side=tk.LEFT)

        modal_button(right, text="Cancelar", kind="ghost",
                     command=self.cancel
                     ).pack(side=tk.LEFT, padx=(0, SPACING[2]))

        modal_button(right, text="Redefinir senha", icon="🔑",
                     kind="primary",
                     command=self._handle_save
                     ).pack(side=tk.LEFT)

    # ──────────────────────────────────────────────────────────────────
    # AÇÕES
    # ──────────────────────────────────────────────────────────────────
    def _validate(self) -> str:
        pw, pw2 = self._senha.get(), self._senha2.get()
        if not pw:
            return "Informe a nova senha."
        if len(pw) < 6:
            return "A senha deve ter no mínimo 6 caracteres."
        if pw != pw2:
            return "As senhas não coincidem."
        return None

    def _handle_save(self):
        err = self._validate()
        if err:
            self._feedback.configure(text=f"⚠  {err}", fg=COLORS["danger"])
            return
        if self.on_save:
            callback_err = self.on_save({"senha": self._senha.get()})
            if callback_err:
                self._feedback.configure(text=f"⚠  {callback_err}", fg=COLORS["danger"])
                return
        self.close_with({"senha": self._senha.get()})
