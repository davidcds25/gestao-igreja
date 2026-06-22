"""
Módulo de autenticação e criptografia de senhas
Gerencia login e verificação de credenciais
"""

import bcrypt
from core.database import get_connection


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(email: str, password: str) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, email, nivel_acesso, ativo, senha
            FROM usuarios
            WHERE email = ? AND ativo = 1
        ''', (email,))
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    if not verify_password(password, row['senha']):
        return None

    user = dict(row)
    user.pop('senha', None)
    return user


def create_user(nome: str, email: str, password: str, nivel_acesso: str) -> bool:
    from core.database import insert_admin_user
    return insert_admin_user(nome, email, hash_password(password))
