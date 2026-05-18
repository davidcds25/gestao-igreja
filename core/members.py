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

GRUPOS = [
    "Grupo de Mulheres",
    "Grupo dos Homens",
    "Grupo de Jovens",
    "Grupo Infantil",
]

MESES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def criar_membro(nome, funcao, status="Ativo", aniversario_dia=None,
                 aniversario_mes=None, telefone=None, email=None,
                 observacoes=None, grupo=None, grupo_casais=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO membros
            (nome, funcao, status, aniversario_dia, aniversario_mes,
             telefone, email, observacoes, grupo, grupo_casais)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nome, funcao, status, aniversario_dia, aniversario_mes,
         telefone or None, email or None, observacoes or None,
         grupo or None, 1 if grupo_casais else 0),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def listar_membros(status=None, funcao=None, grupo=None, grupo_casais=None):
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
    if grupo is not None:
        query += " AND grupo = ?"
        params.append(grupo)
    if grupo_casais is not None:
        query += " AND grupo_casais = ?"
        params.append(1 if grupo_casais else 0)
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
                     observacoes=None, grupo=None, grupo_casais=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE membros
        SET nome=?, funcao=?, status=?, aniversario_dia=?, aniversario_mes=?,
            telefone=?, email=?, observacoes=?, grupo=?, grupo_casais=?
        WHERE id=?
        """,
        (nome, funcao, status, aniversario_dia, aniversario_mes,
         telefone or None, email or None, observacoes or None,
         grupo or None, 1 if grupo_casais else 0, membro_id),
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


def crescimento_mensal(ano: int = None) -> dict:
    """Retorna registros novos por mês e status para o ano informado.

    Retorno:
        {
          "ano": 2026,
          "membros":    [0..11],   # Ativo por mês
          "visitantes": [0..11],   # Visitante por mês
          "afastados":  [0..11],   # Afastado por mês
          "anos_disponiveis": [2025, 2026],
        }
    """
    from datetime import datetime
    if ano is None:
        ano = datetime.now().year

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT CAST(strftime('%m', data_cadastro) AS INTEGER) AS mes,
               status,
               COUNT(*) AS total
        FROM membros
        WHERE strftime('%Y', data_cadastro) = ?
        GROUP BY mes, status
        ORDER BY mes
    """, (str(ano),))
    rows = cur.fetchall()

    cur.execute("""
        SELECT DISTINCT CAST(strftime('%Y', data_cadastro) AS INTEGER) AS ano
        FROM membros
        WHERE data_cadastro IS NOT NULL
        ORDER BY ano DESC
    """)
    anos = [r["ano"] for r in cur.fetchall() if r["ano"]]
    conn.close()

    membros    = [0] * 12
    visitantes = [0] * 12
    afastados  = [0] * 12

    for r in rows:
        idx = (r["mes"] or 1) - 1
        if 0 <= idx < 12:
            status = (r["status"] or "").strip()
            if status == "Ativo":
                membros[idx] = r["total"]
            elif status == "Visitante":
                visitantes[idx] = r["total"]
            elif status == "Afastado":
                afastados[idx] = r["total"]

    return {
        "ano":              ano,
        "membros":          membros,
        "visitantes":       visitantes,
        "afastados":        afastados,
        "anos_disponiveis": anos or [ano],
    }
