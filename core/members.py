"""
Módulo de gerenciamento de membros da igreja
"""

from core.database import get_connection

FUNCOES = [
    "Membro",
    "Pastor(a)",
    "Presbítero",
    "Diácono(a)",
    "Evangelista",
    "Líder de Célula",
    "Louvor",
    "Obreiro(a)",
    "Secretário(a)",
    "Tesoureiro(a)",
]

STATUS = ["Ativo", "Afastado", "Visitante"]

MESES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def criar_membro(nome, funcao, status="Ativo", aniversario_dia=None,
                 aniversario_mes=None, telefone=None, email=None,
                 observacoes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO membros
            (nome, funcao, status, aniversario_dia, aniversario_mes,
             telefone, email, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nome, funcao, status, aniversario_dia, aniversario_mes,
         telefone or None, email or None, observacoes or None),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def listar_membros(status=None, funcao=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM membros WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if funcao:
        query += " AND funcao = ?"
        params.append(funcao)
    query += " ORDER BY nome COLLATE NOCASE"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def obter_membro(membro_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM membros WHERE id = ?", (membro_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def atualizar_membro(membro_id, nome, funcao, status, aniversario_dia=None,
                     aniversario_mes=None, telefone=None, email=None,
                     observacoes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE membros
        SET nome=?, funcao=?, status=?, aniversario_dia=?, aniversario_mes=?,
            telefone=?, email=?, observacoes=?
        WHERE id=?
        """,
        (nome, funcao, status, aniversario_dia, aniversario_mes,
         telefone or None, email or None, observacoes or None, membro_id),
    )
    conn.commit()
    conn.close()


def deletar_membro(membro_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM membros WHERE id = ?", (membro_id,))
    conn.commit()
    conn.close()


def contar_membros():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM membros WHERE status = 'Ativo'")
    ativos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM membros WHERE status = 'Afastado'")
    afastados = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM membros WHERE status = 'Visitante'")
    visitantes = cursor.fetchone()[0]
    conn.close()
    return ativos, afastados, visitantes


def contar_visitantes_mes():
    """Conta visitantes cadastrados no mês corrente."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM membros
        WHERE status = 'Visitante'
          AND strftime('%Y-%m', data_cadastro) = strftime('%Y-%m', 'now')
        """
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def aniversariantes_do_mes(mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM membros WHERE aniversario_mes = ? AND status = 'Ativo' ORDER BY aniversario_dia",
        (mes,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
