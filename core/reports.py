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


def eventos_por_ano(ano):
    """
    Retorna totais de atividades do ano filtrado por data_inicio.
    Chaves: 'total_events', 'realizadas', 'planejadas', 'canceladas',
            'anos_disponiveis'.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT status, COUNT(*) AS total
            FROM atividades
            WHERE strftime('%Y', data_inicio) = ?
              AND data_inicio IS NOT NULL
            GROUP BY status
        """, (str(ano),))
        counts = {r["status"]: r["total"] for r in cur.fetchall()}

        cur.execute("""
            SELECT DISTINCT CAST(strftime('%Y', data_inicio) AS INTEGER) AS ano
            FROM atividades
            WHERE data_inicio IS NOT NULL
            ORDER BY ano
        """)
        anos = [r["ano"] for r in cur.fetchall()]
    finally:
        conn.close()

    realizadas = counts.get("Concluído",   0)
    planejadas = counts.get("Planejado",   0) + counts.get("Em Andamento", 0)
    canceladas = counts.get("Cancelado",   0)

    return {
        "ano":              ano,
        "total_events":     realizadas + planejadas + canceladas,
        "realizadas":       realizadas,
        "planejadas":       planejadas,
        "canceladas":       canceladas,
        "anos_disponiveis": anos or [ano],
    }


def oracoes_por_mes_ano(ano):
    """
    Retorna dict com listas mensais de orações por status para o ano dado.
    Chaves: 'pendentes', 'respondidas', 'arquivadas' (listas de 12 inteiros),
            'anos_disponiveis' (lista de ints).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT strftime('%m', data_cadastro) AS mes,
                   status,
                   COUNT(*) AS total
            FROM oracoes
            WHERE strftime('%Y', data_cadastro) = ?
              AND data_cadastro IS NOT NULL
            GROUP BY mes, status
        """, (str(ano),))
        rows = cur.fetchall()

        cur.execute("""
            SELECT DISTINCT CAST(strftime('%Y', data_cadastro) AS INTEGER) AS ano
            FROM oracoes
            WHERE data_cadastro IS NOT NULL
            ORDER BY ano
        """)
        anos = [r["ano"] for r in cur.fetchall()]
    finally:
        conn.close()

    pendentes   = [0] * 12
    respondidas = [0] * 12
    arquivadas  = [0] * 12

    for row in rows:
        idx = int(row["mes"]) - 1
        if row["status"] == "Ativa":
            pendentes[idx]   = row["total"]
        elif row["status"] == "Respondida":
            respondidas[idx] = row["total"]
        elif row["status"] == "Arquivada":
            arquivadas[idx]  = row["total"]

    return {
        "ano":             ano,
        "pendentes":       pendentes,
        "respondidas":     respondidas,
        "arquivadas":      arquivadas,
        "anos_disponiveis": anos or [ano],
    }


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
