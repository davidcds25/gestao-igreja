"""CRUD de músicas para o módulo de Apresentação."""

import re
from core.database import get_connection


def listar_musicas(busca: str = "") -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if busca:
            cur.execute(
                "SELECT id, titulo, artista FROM musicas "
                "WHERE titulo LIKE ? OR artista LIKE ? ORDER BY titulo COLLATE NOCASE",
                (f"%{busca}%", f"%{busca}%"),
            )
        else:
            cur.execute(
                "SELECT id, titulo, artista FROM musicas ORDER BY titulo COLLATE NOCASE"
            )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def obter_musica(mid: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM musicas WHERE id = ?", (mid,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def criar_musica(titulo: str, artista: str, letra: str) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO musicas (titulo, artista, letra) VALUES (?, ?, ?)",
            (titulo.strip(), artista.strip(), letra),
        )
        mid = cur.lastrowid
        conn.commit()
        return mid
    finally:
        conn.close()


def atualizar_musica(mid: int, titulo: str, artista: str, letra: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE musicas SET titulo=?, artista=?, letra=?, atualizado_em=CURRENT_TIMESTAMP "
            "WHERE id=?",
            (titulo.strip(), artista.strip(), letra, mid),
        )
        conn.commit()
    finally:
        conn.close()


def deletar_musica(mid: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM musicas WHERE id=?", (mid,))
        conn.commit()
    finally:
        conn.close()


def paginar_por_linhas(letra: str, linhas_por_pagina: int = 4) -> list:
    """
    Divide a letra em páginas de N linhas não-vazias, ignorando linhas em branco.
    Retorna lista de páginas; cada página é lista de strings (linhas).
    """
    linhas = [linha for linha in letra.splitlines() if linha.strip()]
    if not linhas:
        return []
    return [linhas[i : i + linhas_por_pagina]
            for i in range(0, len(linhas), linhas_por_pagina)]


def paginar_letra(letra: str, estrofes_por_pagina: int = 4) -> list:
    """
    Divide a letra em páginas de N estrofes.
    Estrofe = bloco de linhas separado por linha em branco.
    Retorna lista de páginas; cada página é lista de strings (estrofes).
    """
    blocos = [b.strip() for b in re.split(r"\n\s*\n", letra) if b.strip()]
    if not blocos:
        return [[letra.strip()]] if letra.strip() else []
    pages = []
    for i in range(0, len(blocos), estrofes_por_pagina):
        pages.append(blocos[i : i + estrofes_por_pagina])
    return pages
