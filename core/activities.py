"""
Módulo de gerenciamento de atividades/eventos
CRUD para atividades da igreja
"""

from core.database import get_connection


def criar_atividade(titulo, descricao, tipo, data_inicio, data_fim, local, responsavel_id, funcao_alvo=None, grupo_alvo=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO atividades (titulo, descricao, tipo, data_inicio, data_fim, local, responsavel_id, funcao_alvo, grupo_alvo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, tipo, data_inicio, data_fim, local, responsavel_id, funcao_alvo, grupo_alvo))
        conn.commit()
        atividade_id = cursor.lastrowid
        conn.close()
        return atividade_id
    except Exception as e:
        conn.close()
        raise e


def listar_atividades():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.*, u.nome as nome_responsavel
        FROM atividades a
        LEFT JOIN usuarios u ON a.responsavel_id = u.id
        ORDER BY a.data_inicio DESC
    ''')

    atividades = cursor.fetchall()
    conn.close()
    return atividades


def obter_atividade(atividade_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.*, u.nome as nome_responsavel
        FROM atividades a
        LEFT JOIN usuarios u ON a.responsavel_id = u.id
        WHERE a.id = ?
    ''', (atividade_id,))

    atividade = cursor.fetchone()
    conn.close()
    return atividade


def atualizar_atividade(atividade_id, titulo, descricao, tipo, data_inicio, data_fim, local, responsavel_id, status, funcao_alvo=None, grupo_alvo=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE atividades
            SET titulo = ?, descricao = ?, tipo = ?, data_inicio = ?,
                data_fim = ?, local = ?, responsavel_id = ?, status = ?,
                funcao_alvo = ?, grupo_alvo = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (titulo, descricao, tipo, data_inicio, data_fim, local, responsavel_id, status, funcao_alvo, grupo_alvo, atividade_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False


def deletar_atividade(atividade_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM atividades WHERE id = ?', (atividade_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False


def listar_tipos_atividade():
    return [
        "Culto", "Reunião", "Evento Social", "Estudo Bíblico",
        "Oração", "Treinamento", "Confraternização",
        "Visita", "Trabalho Voluntário", "Outro",
    ]


def listar_status_atividade():
    return ["Planejado", "Em Andamento", "Concluído", "Cancelado", "Adiado"]


def auto_concluir_passadas():
    """Marca como Concluído atividades cujo prazo já expirou (data_fim < hoje)."""
    from datetime import date
    hoje = date.today().isoformat()
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE atividades
            SET status = 'Concluído', atualizado_em = CURRENT_TIMESTAMP
            WHERE status IN ('Planejado', 'Em Andamento')
              AND COALESCE(data_fim, data_inicio) < ?
        """, (hoje,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def registrar_log(usuario_id, acao):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO logs (usuario_id, acao) VALUES (?, ?)",
            (usuario_id, acao),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def atualizar_status_atividade(atividade_id, status):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE atividades SET status = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            (status, atividade_id),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def listar_proximas_atividades(dias=30):
    from datetime import datetime, timedelta
    conn = get_connection()
    cursor = conn.cursor()

    hoje   = datetime.now().strftime("%Y-%m-%d")
    limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d 23:59")

    cursor.execute('''
        SELECT a.*, u.nome as nome_responsavel
        FROM atividades a
        LEFT JOIN usuarios u ON a.responsavel_id = u.id
        WHERE a.data_inicio >= ?
          AND a.data_inicio <= ?
          AND a.status NOT IN ('Cancelado', 'Concluído')
        ORDER BY a.data_inicio ASC
        LIMIT 10
    ''', (hoje, limite))

    atividades = cursor.fetchall()
    conn.close()
    return atividades
