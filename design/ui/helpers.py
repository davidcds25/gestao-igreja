"""
ui/helpers.py
=============
Utilitários que resolvem limitações reais do tkinter:
  - cantos arredondados (via Canvas polygon)
  - truncate de texto longo
  - cores derivadas (tint/shade) para hover

NÃO importe widgets aqui — só funções puras.
"""

import tkinter as tk


def truncate(text: str, max_chars: int) -> str:
    """Corta um texto e adiciona '…' se passar do limite.

    >>> truncate("Maria Aparecida da Conceição dos Santos", 20)
    'Maria Aparecida da …'
    """
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def rounded_rect_canvas(
    parent,
    width: int,
    height: int,
    radius: int = 4,
    fill: str = "#1a1a2e",
    outline: str = "",
    outline_width: int = 0,
    bg: str = None,
):
    """Cria um Canvas que desenha um retângulo com cantos arredondados.

    tkinter não tem border-radius nativo. Esta é a forma "honesta" de
    simular: um Canvas com smooth polygon.

    Retorna o widget Canvas (já desenhado). Você ainda pode .create_text(),
    .create_image() etc por cima.

    Use para: botões com radius, badges, cards.

        canvas = rounded_rect_canvas(parent, 120, 36,
                                     radius=4,
                                     fill=COLORS["accent"],
                                     bg=COLORS["bg_dark"])
        canvas.pack()

    Importante: `bg` deve combinar com o fundo do PAI, senão aparecem
    cantos retos por baixo.
    """
    cv = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=bg or parent["bg"],
        highlightthickness=0,
        bd=0,
    )
    r = radius
    # 8 pontos + smooth=True desenha um retângulo arredondado convincente
    points = [
        r, 0,
        width - r, 0,
        width, 0,
        width, r,
        width, height - r,
        width, height,
        width - r, height,
        r, height,
        0, height,
        0, height - r,
        0, r,
        0, 0,
    ]
    cv.create_polygon(
        points,
        smooth=True,
        splinesteps=12,
        fill=fill,
        outline=outline,
        width=outline_width,
    )
    return cv


def hex_to_rgb(hx: str):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def lighten(hex_color: str, amount: float = 0.1) -> str:
    """Devolve uma versão mais clara da cor. amount entre 0..1.

    Use para hover de botões em vez de inventar cores.
    """
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, r + (255 - r) * amount)
    g = min(255, g + (255 - g) * amount)
    b = min(255, b + (255 - b) * amount)
    return rgb_to_hex(r, g, b)


def darken(hex_color: str, amount: float = 0.1) -> str:
    """Devolve uma versão mais escura."""
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, r * (1 - amount))
    g = max(0, g * (1 - amount))
    b = max(0, b * (1 - amount))
    return rgb_to_hex(r, g, b)


def initials_of(full_name: str) -> str:
    """Devolve 2 letras com as iniciais (primeiro + último nome)."""
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def bind_hover(widget, *, normal_bg, hover_bg):
    """Adiciona efeito de hover trocando o bg.

    Funciona com tk.Frame, tk.Label, tk.Button.

        bind_hover(btn, normal_bg=COLORS["accent"],
                        hover_bg=lighten(COLORS["accent"], 0.1))
    """
    widget.bind("<Enter>", lambda e: widget.configure(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.configure(bg=normal_bg))
