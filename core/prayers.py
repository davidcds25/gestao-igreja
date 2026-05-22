"""
core/prayers.py
===============
CRUD de orações da comunidade.
"""

from core.database import get_connection

CATEGORIAS = [
    "Saúde", "Família", "Finanças", "Trabalho",
    "Espiritual", "Relacionamento", "Agradecimento", "Outros",
]

PRIVACIDADES = ["Pública", "Restrita", "Confidencial"]

STATUS = ["Ativa", "Respondida", "Arquivada"]

CONTEXTOS = [
    "Culto Domingo", "Culto Semana", "Célula",
    "Individual", "WhatsApp", "Outro",
]


def criar_oracao(solicitante_nome, motivo, categoria="Outros",
                 privacidade="Pública", status="Ativa",
                 membro_id=None, contexto=None, responsavel=None,
                 observacoes=None, testemunho=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO oracoes
                (solicitante_nome, membro_id, motivo, categoria,
                 privacidade, status, contexto, responsavel,
                 observacoes, testemunho)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (solicitante_nome, membro_id, motivo, categoria,
             privacidade, status, contexto or None, responsavel or None,
             observacoes or None, testemunho or None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def listar_oracoes(status=None, categoria=None, privacidade=None,
                   ano=None, mes=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT o.*, m.nome AS membro_nome
            FROM oracoes o
            LEFT JOIN membros m ON o.membro_id = m.id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND o.status = ?"
            params.append(status)
        if categoria:
            query += " AND o.categoria = ?"
            params.append(categoria)
        if privacidade:
            query += " AND o.privacidade = ?"
            params.append(privacidade)
        if ano and mes:
            query += " AND strftime('%Y-%m', o.data_cadastro) = ?"
            params.append(f"{ano:04d}-{mes:02d}")
        query += " ORDER BY o.data_cadastro DESC"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def obter_oracao(oracao_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT o.*, m.nome AS membro_nome
            FROM oracoes o
            LEFT JOIN membros m ON o.membro_id = m.id
            WHERE o.id = ?
            """,
            (oracao_id,),
        )
        return cur.fetchone()
    finally:
        conn.close()


def atualizar_oracao(oracao_id, solicitante_nome, motivo, categoria,
                     privacidade, status, membro_id=None, contexto=None,
                     responsavel=None, observacoes=None, testemunho=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE oracoes
            SET solicitante_nome=?, membro_id=?, motivo=?, categoria=?,
                privacidade=?, status=?, contexto=?, responsavel=?,
                observacoes=?, testemunho=?
            WHERE id=?
            """,
            (solicitante_nome, membro_id, motivo, categoria,
             privacidade, status, contexto or None, responsavel or None,
             observacoes or None, testemunho or None, oracao_id),
        )
        conn.commit()
    finally:
        conn.close()


def deletar_oracao(oracao_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM oracoes WHERE id = ?", (oracao_id,))
        conn.commit()
    finally:
        conn.close()


def atualizar_status_oracao(oracao_id, status, *,
                             testemunho=None, observacoes=None):
    conn = get_connection()
    try:
        sets   = ["status = ?"]
        params = [status]
        if testemunho is not None:
            sets.append("testemunho = ?")
            params.append(testemunho)
        if observacoes is not None:
            sets.append("observacoes = ?")
            params.append(observacoes)
        params.append(oracao_id)
        conn.execute(
            f"UPDATE oracoes SET {', '.join(sets)} WHERE id = ?", params
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def contar_oracoes():
    """Retorna (ativas, respondidas, arquivadas)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM oracoes WHERE status = 'Ativa'")
        ativas = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM oracoes WHERE status = 'Respondida'")
        respondidas = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM oracoes WHERE status = 'Arquivada'")
        arquivadas = cur.fetchone()[0]
        return ativas, respondidas, arquivadas
    finally:
        conn.close()
