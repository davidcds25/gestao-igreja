"""
Gerenciamento de usuários do sistema
"""

from core.database import get_connection
from core.auth import hash_password

NIVEIS_ACESSO = ["Admin", "Coordenador", "Usuário"]


def listar_usuarios():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT id, nome, email, nivel_acesso, ativo, criado_em
        FROM usuarios
        ORDER BY nome COLLATE NOCASE
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def obter_usuario(usuario_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT id, nome, email, nivel_acesso, ativo FROM usuarios WHERE id = ?",
                (usuario_id,))
    row = cur.fetchone()
    conn.close()
    return row


def criar_usuario(nome, email, senha, nivel_acesso):
    """Retorna (id, erro). erro=None em caso de sucesso."""
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, nivel_acesso) VALUES (?, ?, ?, ?)",
            (nome, email, hash_password(senha), nivel_acesso),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id, None
    except Exception as e:
        conn.close()
        if "UNIQUE" in str(e):
            return None, "Este e-mail já está cadastrado."
        return None, str(e)


def atualizar_usuario(usuario_id, nome, email, nivel_acesso):
    """Atualiza dados sem alterar a senha. Retorna erro ou None."""
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "UPDATE usuarios SET nome=?, email=?, nivel_acesso=? WHERE id=?",
            (nome, email, nivel_acesso, usuario_id),
        )
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        conn.close()
        if "UNIQUE" in str(e):
            return "Este e-mail já está em uso por outro usuário."
        return str(e)


def redefinir_senha(usuario_id, nova_senha):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE usuarios SET senha=? WHERE id=?",
                (hash_password(nova_senha), usuario_id))
    conn.commit()
    conn.close()


def alternar_ativo(usuario_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE usuarios SET ativo = NOT ativo WHERE id=?", (usuario_id,))
    conn.commit()
    conn.close()


def deletar_usuario(usuario_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
    conn.commit()
    conn.close()
