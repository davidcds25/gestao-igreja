"""
Funções de diálogo standalone para CRUD de Membros, Atividades e Usuários.
Chamadas a partir de views/login.py — sem dependência de instâncias de classe.
"""

import tkinter as tk
from tkinter import messagebox, ttk

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
ACCENT     = "#00d4ff"
DIVIDER    = "#2d2d44"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"

_BTN = dict(relief=tk.FLAT, cursor="hand2",
            font=("Segoe UI", 11, "bold"), padx=20, pady=8)


def _center_win(win, root, w, h):
    win.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width()  - w) // 2
    y = root.winfo_rooty() + (root.winfo_height() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ══════════════════════════════════════════════════════════════════════════
# MEMBROS
# ══════════════════════════════════════════════════════════════════════════

def open_member_form(root, *, member_id=None, on_save=None):
    from design.modals.member import MemberModal
    MemberModal(root, member_id=member_id, on_save=on_save)


def confirm_delete_member(root, *, membro, on_confirm=None):
    from core.members import deletar_membro
    ok = messagebox.askyesno(
        "Confirmar exclusão",
        f"Deseja remover '{membro['nome']}' do cadastro?\n"
        "Esta ação não pode ser desfeita.",
        parent=root,
    )
    if ok:
        deletar_membro(membro["id"])
        if on_confirm:
            on_confirm()


# ══════════════════════════════════════════════════════════════════════════
# ATIVIDADES
# ══════════════════════════════════════════════════════════════════════════

def open_activity_form(root, *, activity_id=None, current_user_id=None, on_save=None):
    from design.modals.activity import ActivityModal
    ActivityModal(
        root,
        activity_id=activity_id,
        current_user_id=current_user_id,
        on_save=on_save,
    )


def confirm_done_activity(root, *, activity_id, current_user_id=None, on_confirm=None):
    from core.activities import obter_atividade, atualizar_status_atividade, registrar_log
    at     = obter_atividade(activity_id)
    titulo = at["titulo"] if at else str(activity_id)
    if messagebox.askyesno(
            "Confirmar conclusão",
            f"Deseja marcar como realizada:\n\"{titulo}\"?\n\n"
            "Ela será movida para a aba Realizadas.",
            parent=root):
        try:
            atualizar_status_atividade(activity_id, "Concluído")
            if current_user_id:
                registrar_log(current_user_id,
                              f"Concluiu atividade: '{titulo}' (ID: {activity_id})")
            if on_confirm:
                on_confirm()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao concluir: {ex}", parent=root)


def confirm_cancel_activity(root, *, activity_id, current_user_id=None, on_confirm=None):
    from core.activities import obter_atividade, atualizar_status_atividade, registrar_log
    at     = obter_atividade(activity_id)
    titulo = at["titulo"] if at else str(activity_id)
    if messagebox.askyesno(
            "Confirmar cancelamento",
            f"Deseja cancelar a atividade:\n\"{titulo}\"?\n\n"
            "Ela será movida para a aba Canceladas.",
            parent=root):
        try:
            atualizar_status_atividade(activity_id, "Cancelado")
            if current_user_id:
                registrar_log(current_user_id,
                              f"Cancelou atividade: '{titulo}' (ID: {activity_id})")
            if on_confirm:
                on_confirm()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao cancelar: {ex}", parent=root)


# ══════════════════════════════════════════════════════════════════════════
# USUÁRIOS
# ══════════════════════════════════════════════════════════════════════════

def open_user_form(root, *, uid=None, on_save=None):
    from core.users import criar_usuario, atualizar_usuario, obter_usuario, NIVEIS_ACESSO

    usuario = obter_usuario(uid) if uid else None
    editing = usuario is not None
    titulo  = "Editar Usuário" if editing else "Novo Usuário"

    win = tk.Toplevel(root)
    win.title(titulo)
    win.configure(bg=BG_DARK)
    win.resizable(False, False)
    win.grab_set()
    _center_win(win, root, 460, 480 if editing else 560)

    card = tk.Frame(win, bg=BG_CARD)
    card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

    tk.Label(card, text=titulo, font=("Segoe UI", 14, "bold"),
             fg=ACCENT, bg=BG_CARD).pack(anchor=tk.W, pady=(0, 18))

    entry_kw = dict(bg=DIVIDER, fg=TEXT, relief=tk.FLAT, bd=0,
                    font=("Segoe UI", 11), insertbackground=TEXT)

    def campo(label, show=None, valor=""):
        tk.Label(card, text=label, font=("Segoe UI", 10, "bold"),
                 fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(8, 2))
        kw = dict(entry_kw)
        if show:
            kw["show"] = show
        e = tk.Entry(card, **kw)
        e.pack(fill=tk.X, ipady=7)
        if valor:
            e.insert(0, valor)
        return e

    e_nome  = campo("Nome Completo", valor=usuario["nome"]  if editing else "")
    e_email = campo("E-mail",        valor=usuario["email"] if editing else "")

    e_senha = e_conf = None
    if not editing:
        e_senha = campo("Senha",           show="•")
        e_conf  = campo("Confirmar Senha", show="•")

    tk.Label(card, text="Nível de Acesso", font=("Segoe UI", 10, "bold"),
             fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(8, 2))
    nivel_var = tk.StringVar(
        value=usuario["nivel_acesso"] if editing else "Usuário")
    ttk.Combobox(card, values=NIVEIS_ACESSO, textvariable=nivel_var,
                 state="readonly", font=("Segoe UI", 11)).pack(fill=tk.X, ipady=4)

    err_lbl = tk.Label(card, text="", font=("Segoe UI", 10),
                       fg="#ff6b6b", bg=BG_CARD)
    err_lbl.pack(anchor=tk.W, pady=(8, 0))

    btn_row = tk.Frame(card, bg=BG_CARD)
    btn_row.pack(fill=tk.X, pady=(16, 0))

    def _salvar():
        nome  = e_nome.get().strip()
        email = e_email.get().strip()
        nivel = nivel_var.get()
        if not nome or not email:
            err_lbl.configure(text="Nome e e-mail são obrigatórios.")
            return
        if editing:
            err = atualizar_usuario(usuario["id"], nome, email, nivel)
            if err:
                err_lbl.configure(text=err)
                return
        else:
            senha   = e_senha.get()
            confirm = e_conf.get()
            if not senha:
                err_lbl.configure(text="Informe uma senha.")
                return
            if len(senha) < 6:
                err_lbl.configure(text="Mínimo 6 caracteres.")
                return
            if senha != confirm:
                err_lbl.configure(text="As senhas não coincidem.")
                return
            _, err = criar_usuario(nome, email, senha, nivel)
            if err:
                err_lbl.configure(text=err)
                return
        win.destroy()
        if on_save:
            on_save()

    tk.Button(btn_row, text="Salvar",
              bg=ACCENT, fg=BG_DARK,
              activebackground="#00b8d9", activeforeground=BG_DARK,
              command=_salvar, **_BTN).pack(side=tk.LEFT, padx=(0, 10))
    tk.Button(btn_row, text="Cancelar",
              bg=DIVIDER, fg="#aaaaaa",
              activebackground="#3d3d54", activeforeground=TEXT,
              command=win.destroy, **_BTN).pack(side=tk.LEFT)


def open_reset_password_form(root, *, uid, username, on_save=None):
    from core.users import redefinir_senha

    win = tk.Toplevel(root)
    win.title("Redefinir Senha")
    win.configure(bg=BG_DARK)
    win.resizable(False, False)
    win.grab_set()
    _center_win(win, root, 400, 300)

    card = tk.Frame(win, bg=BG_CARD)
    card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

    tk.Label(card, text=f"Redefinir senha de\n{username}",
             font=("Segoe UI", 13, "bold"), fg=ACCENT, bg=BG_CARD,
             justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 16))

    kw = dict(bg=DIVIDER, fg=TEXT, relief=tk.FLAT, bd=0,
              font=("Segoe UI", 11), show="•", insertbackground=TEXT)

    tk.Label(card, text="Nova Senha", font=("Segoe UI", 10, "bold"),
             fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(0, 2))
    e_nova = tk.Entry(card, **kw)
    e_nova.pack(fill=tk.X, ipady=7)

    tk.Label(card, text="Confirmar Senha", font=("Segoe UI", 10, "bold"),
             fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(10, 2))
    e_conf = tk.Entry(card, **kw)
    e_conf.pack(fill=tk.X, ipady=7)

    err_lbl = tk.Label(card, text="", font=("Segoe UI", 10),
                       fg="#ff6b6b", bg=BG_CARD)
    err_lbl.pack(anchor=tk.W, pady=(6, 0))

    btn_row = tk.Frame(card, bg=BG_CARD)
    btn_row.pack(fill=tk.X, pady=(12, 0))

    def _salvar():
        nova    = e_nova.get()
        confirm = e_conf.get()
        if len(nova) < 6:
            err_lbl.configure(text="Mínimo 6 caracteres.")
            return
        if nova != confirm:
            err_lbl.configure(text="As senhas não coincidem.")
            return
        redefinir_senha(uid, nova)
        win.destroy()
        messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!", parent=root)
        if on_save:
            on_save()

    tk.Button(btn_row, text="Salvar",
              bg=ACCENT, fg=BG_DARK,
              activebackground="#00b8d9", activeforeground=BG_DARK,
              command=_salvar, **_BTN).pack(side=tk.LEFT, padx=(0, 10))
    tk.Button(btn_row, text="Cancelar",
              bg=DIVIDER, fg="#aaaaaa",
              activebackground="#3d3d54", activeforeground=TEXT,
              command=win.destroy, **_BTN).pack(side=tk.LEFT)


def toggle_user_active(*, uid, on_done=None):
    from core.users import alternar_ativo
    alternar_ativo(uid)
    if on_done:
        on_done()


def confirm_delete_user(root, *, usuario, on_confirm=None):
    from core.users import deletar_usuario
    if messagebox.askyesno(
        "Confirmar exclusão",
        f"Excluir o usuário '{usuario['nome']}'?\nEsta ação não pode ser desfeita.",
        parent=root,
    ):
        deletar_usuario(usuario["id"])
        if on_confirm:
            on_confirm()
