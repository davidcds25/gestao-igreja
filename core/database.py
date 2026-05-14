"""
Módulo de banco de dados SQLite
Gerencia a criação e inicialização do banco de dados
"""

import sqlite3
import os
from pathlib import Path

# Banco fica sempre na raiz do projeto (um nível acima de core/)
DB_PATH = Path(__file__).parent.parent / "igreja.db"


def get_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nivel_acesso TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de níveis de acesso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS niveis_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT,
            permissoes TEXT
        )
    ''')

    # Tabela de logs (auditoria)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            acao TEXT NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabela de atividades/eventos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            tipo TEXT NOT NULL,
            data_inicio DATETIME NOT NULL,
            data_fim DATETIME,
            local TEXT,
            responsavel_id INTEGER,
            status TEXT DEFAULT 'Planejado',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(responsavel_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabela de membros da igreja
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            aniversario_dia INTEGER,
            aniversario_mes INTEGER,
            telefone TEXT,
            email TEXT,
            funcao TEXT NOT NULL DEFAULT 'Membro',
            status TEXT NOT NULL DEFAULT 'Ativo',
            observacoes TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migração: adiciona funcao_alvo à tabela atividades (bancos antigos)
    try:
        cursor.execute("ALTER TABLE atividades ADD COLUMN funcao_alvo TEXT DEFAULT NULL")
    except Exception:
        pass  # coluna já existe

    # Migração: bancos antigos têm coluna 'ativo' em vez de 'status'
    try:
        cursor.execute("ALTER TABLE membros ADD COLUMN status TEXT DEFAULT 'Ativo'")
        try:
            cursor.execute("""
                UPDATE membros SET status =
                CASE
                    WHEN funcao = 'Visitante' THEN 'Visitante'
                    WHEN ativo = 0            THEN 'Afastado'
                    ELSE 'Ativo'
                END
            """)
        except Exception:
            pass  # coluna 'ativo' não existe — banco novo, sem necessidade
    except Exception:
        pass  # coluna 'status' já existe

    # Inserir níveis de acesso padrão
    try:
        cursor.execute('''
            INSERT INTO niveis_acesso (nome, descricao, permissoes)
            VALUES (?, ?, ?)
        ''', ('Admin', 'Acesso total', 'criar_usuario,editar_usuario,deletar_usuario,relatorios'))

        cursor.execute('''
            INSERT INTO niveis_acesso (nome, descricao, permissoes)
            VALUES (?, ?, ?)
        ''', ('Coordenador', 'Gerenciar atividades', 'editar_atividades,ver_relatorios'))

        cursor.execute('''
            INSERT INTO niveis_acesso (nome, descricao, permissoes)
            VALUES (?, ?, ?)
        ''', ('Usuário', 'Acesso básico', 'ver_informacoes'))
    except sqlite3.IntegrityError:
        pass  # Níveis já existem

    # Usuário admin padrão (apenas se não existir nenhum usuário)
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        from core.auth import hash_password
        try:
            from config import ADMIN_EMAIL, ADMIN_PASSWORD
        except ImportError:
            ADMIN_EMAIL, ADMIN_PASSWORD = "admin@sistema.com", "admin123"
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, nivel_acesso) VALUES (?, ?, ?, ?)",
            ("Administrador", ADMIN_EMAIL, hash_password(ADMIN_PASSWORD), "Admin"),
        )

    conn.commit()
    conn.close()


def insert_admin_user(nome, email, senha_hash):
    """Insere um usuário administrador (usar apenas na primeira execução)"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, nivel_acesso)
            VALUES (?, ?, ?, ?)
        ''', (nome, email, senha_hash, 'Admin'))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


if __name__ == "__main__":
    init_database()
    print(f"✓ Banco de dados inicializado em: {DB_PATH}")
