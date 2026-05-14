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
    from core.members import (
        criar_membro, atualizar_membro, obter_membro, FUNCOES, STATUS, MESES,
    )

    membro  = obter_membro(member_id) if member_id else None
    editing = membro is not None

    win = tk.Toplevel(root)
    win.title("Editar Membro" if editing else "Novo Membro")
    win.configure(bg=BG_DARK)
    win.resizable(False, False)
    win.grab_set()
    _center_win(win, root, 500, 670)

    ENTRY_KW = dict(font=("Segoe UI", 11), bg=DIVIDER, fg=TEXT,
                    relief=tk.FLAT, bd=0, insertbackground=TEXT)
    PAD = dict(padx=28)

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
    ttk.Combobox(form, textvariable=funcao_var, values=FUNCOES,
                 state="readonly", font=("Segoe UI", 11)).pack(
                     fill=tk.X, ipady=4, pady=(0, 12), **PAD)

    lbl("Status *")
    status_var = tk.StringVar(
        value=membro["status"] if (editing and membro["status"]) else "Ativo")
    st_row = tk.Frame(form, bg=BG_DARK)
    st_row.pack(anchor=tk.W, pady=(0, 12), **PAD)
    for s in STATUS:
        tk.Radiobutton(st_row, text=s, variable=status_var, value=s,
                       font=("Segoe UI", 10), fg=TEXT, bg=BG_DARK,
                       selectcolor=BG_CARD, activebackground=BG_DARK,
                       activeforeground=TEXT).pack(side=tk.LEFT, padx=(0, 20))

    lbl("Aniversário", optional=True)
    brow = tk.Frame(form, bg=BG_DARK)
    brow.pack(fill=tk.X, pady=(0, 12), **PAD)
    tk.Label(brow, text="Dia:", font=("Segoe UI", 10), fg="#aaaaaa",
             bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
    dia_var = tk.StringVar(
        value=str(membro["aniversario_dia"] or "") if editing else "")
    tk.Spinbox(brow, from_=1, to=31, textvariable=dia_var, width=4,
               font=("Segoe UI", 11), bg=DIVIDER, fg=TEXT, relief=tk.FLAT,
               buttonbackground="#3a3a5a",
               insertbackground=TEXT).pack(side=tk.LEFT, padx=(0, 16))
    tk.Label(brow, text="Mês:", font=("Segoe UI", 10), fg="#aaaaaa",
             bg=BG_DARK).pack(side=tk.LEFT, padx=(0, 4))
    mes_names = ["(nenhum)"] + MESES[1:]
    mes_var = tk.StringVar(
        value=(MESES[membro["aniversario_mes"]]
               if (editing and membro["aniversario_mes"]) else "(nenhum)"))
    ttk.Combobox(brow, textvariable=mes_var, values=mes_names,
                 state="readonly", width=12,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)

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
    obs_txt = tk.Text(form, font=("Segoe UI", 11), bg=DIVIDER, fg=TEXT,
                      relief=tk.FLAT, bd=0, height=3,
                      insertbackground=TEXT, wrap=tk.WORD)
    obs_txt.pack(fill=tk.X, pady=(0, 16), **PAD)
    if editing and membro.get("observacoes"):
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
                messagebox.showwarning("Atenção", "Data de aniversário inválida.",
                                       parent=win)
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
        if on_save:
            on_save()

    tk.Button(btn_row, text="Salvar", command=_salvar,
              bg=ACCENT, fg=BG_DARK,
              activebackground="#00b8d9", activeforeground=BG_DARK,
              **_BTN).pack(side=tk.LEFT, padx=(0, 10))
    tk.Button(btn_row, text="Cancelar", command=win.destroy,
              bg=DIVIDER, fg="#aaaaaa",
              activebackground="#3d3d54", activeforeground=TEXT,
              **_BTN).pack(side=tk.LEFT)


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
