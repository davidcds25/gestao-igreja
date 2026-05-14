"""
Queries para relatórios e estatísticas
"""

from core.database import get_connection


def membros_por_funcao():
    """Retorna [(funcao, total)] ordenado por total desc."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT funcao, COUNT(*) as total
        FROM membros
        GROUP BY funcao
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [(r["funcao"], r["total"]) for r in rows]


def membros_por_status():
    """Retorna {status: total}."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*) as total
        FROM membros
        GROUP BY status
    """)
    rows = cur.fetchall()
    conn.close()
    return {r["status"]: r["total"] for r in rows}


def aniversariantes_mes(mes):
    """Retorna lista de membros ativos com aniversário no mês dado."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT nome, aniversario_dia, aniversario_mes, telefone, funcao
        FROM membros
        WHERE aniversario_mes = ? AND status = 'Ativo'
        ORDER BY aniversario_dia
    """, (mes,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def eventos_por_status():
    """Retorna [(status, total)] ordenado por total desc."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*) as total
        FROM atividades
        GROUP BY status
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [(r["status"], r["total"]) for r in rows]


def crescimento_membros(meses=12):
    """
    Retorna [(ano_mes, total)] dos últimos N meses em ordem cronológica.
    ano_mes no formato 'YYYY-MM'.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', data_cadastro) AS mes, COUNT(*) AS total
        FROM membros
        WHERE data_cadastro IS NOT NULL
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT ?
    """, (meses,))
    rows = cur.fetchall()
    conn.close()
    return [(r["mes"], r["total"]) for r in reversed(rows)]
