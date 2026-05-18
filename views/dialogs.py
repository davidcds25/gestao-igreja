"""
Funções de diálogo standalone para CRUD de Membros, Atividades e Usuários.
Chamadas a partir de views/login.py — sem dependência de instâncias de classe.
"""

import tkinter as tk
from tkinter import messagebox

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

_NIVEL_COLOR = {
    "Admin":       "#667eea",
    "Coordenador": "#0891b2",
    "Usuário":     "#9b59b6",
}


def open_user_form(root, *, uid=None, on_save=None, current_user_id=None):
    from core.users import (criar_usuario, atualizar_usuario, obter_usuario,
                            alternar_ativo, deletar_usuario)
    from design.modals import UserModal

    usuario = obter_usuario(uid) if uid else None
    editing = usuario is not None

    if editing:
        initial = {
            "nome":  usuario["nome"],
            "email": usuario["email"],
            "nivel": usuario["nivel_acesso"],
            "ativo": bool(usuario["ativo"]),
            "voce":  bool(current_user_id and usuario["id"] == current_user_id),
        }
        original_ativo = bool(usuario["ativo"])

        def _on_save(data):
            err = atualizar_usuario(usuario["id"], data["nome"], data["email"], data["nivel"])
            if err:
                return err
            if bool(data["ativo"]) != original_ativo:
                alternar_ativo(usuario["id"])
            if on_save:
                on_save()
            return None

        def _on_delete():
            deletar_usuario(usuario["id"])
            if on_save:
                on_save()

        result = UserModal(root, mode="edit", initial=initial,
                           on_save=_on_save, on_delete=_on_delete).show()
        if result and result.get("_deleted"):
            messagebox.showinfo("Excluído", "Usuário excluído com sucesso.", parent=root)
        elif result:
            messagebox.showinfo("Salvo", "Dados do usuário atualizados com sucesso.", parent=root)
    else:
        def _on_save(data):
            _, err = criar_usuario(data["nome"], data["email"], data["senha"], data["nivel"])
            if err:
                return err
            if on_save:
                on_save()
            return None

        result = UserModal(root, mode="new", on_save=_on_save).show()
        if result:
            messagebox.showinfo("Salvo", "Usuário criado com sucesso.", parent=root)


def open_reset_password_form(root, *, uid, username, on_save=None):
    from core.users import redefinir_senha, obter_usuario
    from design.modals import PasswordResetModal

    usuario = obter_usuario(uid)
    color = _NIVEL_COLOR.get(usuario["nivel_acesso"] if usuario else "", "#667eea")
    email = usuario["email"] if usuario else ""

    def _on_save(data):
        try:
            redefinir_senha(uid, data["senha"])
        except Exception as exc:
            return str(exc)
        if on_save:
            on_save()
        return None

    result = PasswordResetModal(root,
                               user={"nome": username, "email": email, "color": color},
                               on_save=_on_save).show()
    if result:
        messagebox.showinfo("Salvo", f"Senha de {username} redefinida com sucesso.", parent=root)


def toggle_user_active(*, uid, root=None, on_done=None):
    from core.users import alternar_ativo, obter_usuario
    from design.modals import ask_confirm

    usuario = obter_usuario(uid)
    nome  = usuario["nome"] if usuario else "este usuário"
    ativo = bool(usuario["ativo"]) if usuario else True

    if ativo:
        ok = ask_confirm(
            root,
            title=f"Desativar '{nome}'?",
            message="O login será bloqueado mas a conta poderá ser reativada depois.",
            confirm_label="Desativar",
            variant="warning",
        )
    else:
        ok = ask_confirm(
            root,
            title=f"Ativar '{nome}'?",
            message="O usuário voltará a conseguir fazer login normalmente.",
            confirm_label="Ativar",
            variant="info",
        )

    if ok:
        alternar_ativo(uid)
        if on_done:
            on_done()


def confirm_delete_user(root, *, usuario, on_confirm=None):
    from core.users import deletar_usuario
    from design.modals import ask_confirm
    ok = ask_confirm(
        root,
        title=f"Excluir o usuário '{usuario['nome']}'?",
        message="Essa pessoa perderá o acesso ao sistema imediatamente.",
        detail="Os registros que ela criou permanecem, mas a conta de login "
               "será removida em definitivo. Essa ação não pode ser desfeita.",
        confirm_label="Sim, excluir",
        variant="danger",
    )
    if ok:
        deletar_usuario(usuario["id"])
        if on_confirm:
            on_confirm()
        messagebox.showinfo("Excluído", f"Usuário '{usuario['nome']}' excluído com sucesso.", parent=root)


# ══════════════════════════════════════════════════════════════════════════
# ORAÇÕES
# ══════════════════════════════════════════════════════════════════════════

def open_prayer_form(root, *, oracao_id=None, on_save=None):
    from core.prayers import criar_oracao, atualizar_oracao, obter_oracao
    from core.members import listar_membros
    from design.modals import PrayerModal

    mode    = "edit" if oracao_id else "new"
    initial = {}
    if oracao_id:
        row = obter_oracao(oracao_id)
        if row:
            initial = dict(row)

    # lista de membros ativos para o seletor de vínculo
    try:
        members = [(m["id"], m["nome"]) for m in listar_membros(status="Ativo")]
    except Exception:
        members = []

    def _on_save(data):
        try:
            if mode == "new":
                criar_oracao(
                    solicitante_nome=data["solicitante_nome"],
                    motivo=data["motivo"],
                    categoria=data["categoria"],
                    privacidade=data["privacidade"],
                    status=data["status"],
                    membro_id=data.get("membro_id"),
                    contexto=data.get("contexto"),
                    responsavel=data.get("responsavel"),
                    observacoes=data.get("observacoes"),
                    testemunho=data.get("testemunho"),
                )
            else:
                atualizar_oracao(
                    oracao_id,
                    solicitante_nome=data["solicitante_nome"],
                    motivo=data["motivo"],
                    categoria=data["categoria"],
                    privacidade=data["privacidade"],
                    status=data["status"],
                    membro_id=data.get("membro_id"),
                    contexto=data.get("contexto"),
                    responsavel=data.get("responsavel"),
                    observacoes=data.get("observacoes"),
                    testemunho=data.get("testemunho"),
                )
        except Exception as exc:
            return str(exc)
        if on_save:
            on_save()
        return None

    def _on_delete():
        from core.prayers import deletar_oracao
        if oracao_id:
            deletar_oracao(oracao_id)
        if on_save:
            on_save()

    result = PrayerModal(root, mode=mode, initial=initial,
                         members=members,
                         on_save=_on_save,
                         on_delete=_on_delete).show()

    if result and not result.get("_deleted"):
        label = "registrada" if mode == "new" else "atualizada"
        messagebox.showinfo("Salvo", f"Oração {label} com sucesso.", parent=root)


def confirm_delete_prayer(root, *, oracao_id, solicitante, on_confirm=None):
    from core.prayers import deletar_oracao
    from design.modals import ask_confirm
    ok = ask_confirm(
        root,
        title="Excluir este pedido de oração?",
        message=f"O registro de '{solicitante}' será removido permanentemente.",
        confirm_label="Sim, excluir",
        variant="danger",
    )
    if ok:
        deletar_oracao(oracao_id)
        if on_confirm:
            on_confirm()
