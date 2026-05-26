"""
themes.py — Paletas de cor dos temas do Display de Apresentação.

Cada tema traz:
  - palette_bg  : cores usadas para gerar o PNG de fundo do Display.
  - palette_ui  : cores para a interface do app (topbar, botões, accents).
  - bg_file     : o PNG pronto em assets/

Uso simples:
    from themes import THEMES, aplicar_tema

    aplicar_tema(root, "navy")

Uso direto das cores:
    from themes import THEMES
    t = THEMES["navy"]
    btn = tk.Button(..., bg=t["palette_ui"]["accent"], fg=t["palette_ui"]["text_strong"])
"""

THEMES = {

    # ── Dourado / Sépia (elegante, atemporal) ────────────────────────────
    "dourado": {
        "name":    "Dourado",
        "bg_file": "assets/bg_display_dourado.png",
        "palette_bg": {
            "bg_center": "#5a3a14",
            "bg_edge":   "#2f1d06",
            "bg_far":    "#120800",
            "shadow":    "#0a0500",
            "highlight": "#e3b86a",
            "base":      "#52340e",
            "swoosh":    "#f0c97a",
        },
        "palette_ui": {
            "bg":          "#15100a",
            "panel":       "#241a10",
            "panel_alt":   "#100a05",
            "border":      "#332514",
            "text":        "#f1e8d8",
            "text_strong": "#ffffff",
            "text_sub":    "#b29e7c",
            "accent":      "#d4a14a",
            "accent_dark": "#a17626",
            "accent_soft": "#2e2010",
            "danger":      "#ef6b6b",
        },
    },

    # ── Navy (clássico, cinematográfico) ─────────────────────────────────
    "navy": {
        "name":    "Navy",
        "bg_file": "assets/bg_display_navy.png",
        "palette_bg": {
            "bg_center": "#1a4e8c",
            "bg_edge":   "#0c2a55",
            "bg_far":    "#040d22",
            "shadow":    "#020812",
            "highlight": "#6b9adb",
            "base":      "#0e3460",
            "swoosh":    "#7eb5ff",
        },
        "palette_ui": {
            "bg":          "#0e1a2e",
            "panel":       "#152442",
            "panel_alt":   "#0b1426",
            "border":      "#1f3158",
            "text":        "#e7ebf3",
            "text_strong": "#ffffff",
            "text_sub":    "#8a9bbf",
            "accent":      "#5b8def",
            "accent_dark": "#3461d1",
            "accent_soft": "#1d2d52",
            "danger":      "#ef6b6b",
        },
    },

    # ── Vinho (solene, de altar) ──────────────────────────────────────────
    "vinho": {
        "name":    "Vinho",
        "bg_file": "assets/bg_display_vinho.png",
        "palette_bg": {
            "bg_center": "#5a1820",
            "bg_edge":   "#36090f",
            "bg_far":    "#180305",
            "shadow":    "#0c0102",
            "highlight": "#d2828a",
            "base":      "#4a0a13",
            "swoosh":    "#e09a9e",
        },
        "palette_ui": {
            "bg":          "#1a0a0d",
            "panel":       "#2a1014",
            "panel_alt":   "#150608",
            "border":      "#3a181d",
            "text":        "#f3e7e9",
            "text_strong": "#ffffff",
            "text_sub":    "#b69399",
            "accent":      "#c93a48",
            "accent_dark": "#8f1f2a",
            "accent_soft": "#3a151a",
            "danger":      "#ef6b6b",
        },
    },

    # ── Verde Mata (sóbrio, ministério e celebração) ──────────────────────
    "mata": {
        "name":    "Verde Mata",
        "bg_file": "assets/bg_display_mata.png",
        "palette_bg": {
            "bg_center": "#1f4a2b",
            "bg_edge":   "#0e2818",
            "bg_far":    "#020e07",
            "shadow":    "#01080a",
            "highlight": "#7fc796",
            "base":      "#173a22",
            "swoosh":    "#9fdfb0",
        },
        "palette_ui": {
            "bg":          "#0a1810",
            "panel":       "#11261a",
            "panel_alt":   "#06120a",
            "border":      "#1c3525",
            "text":        "#e3efe6",
            "text_strong": "#ffffff",
            "text_sub":    "#84a692",
            "accent":      "#4ea870",
            "accent_dark": "#2c7549",
            "accent_soft": "#12281b",
            "danger":      "#ef6b6b",
        },
    },

    # ── Roxo (espiritual, adoração) ───────────────────────────────────────
    "roxo": {
        "name":    "Roxo",
        "bg_file": "assets/bg_display_roxo.png",
        "palette_bg": {
            "bg_center": "#3d1a5c",
            "bg_edge":   "#210d36",
            "bg_far":    "#0c0318",
            "shadow":    "#060110",
            "highlight": "#a87dd4",
            "base":      "#32154e",
            "swoosh":    "#c49ee8",
        },
        "palette_ui": {
            "bg":          "#130a1e",
            "panel":       "#1f1030",
            "panel_alt":   "#0d0616",
            "border":      "#2e1848",
            "text":        "#ede7f5",
            "text_strong": "#ffffff",
            "text_sub":    "#a08dbf",
            "accent":      "#8b45d4",
            "accent_dark": "#5e2399",
            "accent_soft": "#251240",
            "danger":      "#ef6b6b",
        },
    },

    # ── Petróleo (profundo, contemporâneo) ────────────────────────────────
    "petroleo": {
        "name":    "Petróleo",
        "bg_file": "assets/bg_display_petroleo.png",
        "palette_bg": {
            "bg_center": "#0d3d40",
            "bg_edge":   "#062225",
            "bg_far":    "#010c0e",
            "shadow":    "#000809",
            "highlight": "#4da8ad",
            "base":      "#0a3235",
            "swoosh":    "#6fcdd2",
        },
        "palette_ui": {
            "bg":          "#071518",
            "panel":       "#0e2426",
            "panel_alt":   "#040f11",
            "border":      "#163638",
            "text":        "#e2eff0",
            "text_strong": "#ffffff",
            "text_sub":    "#7aaeb0",
            "accent":      "#2fa8ad",
            "accent_dark": "#1a7478",
            "accent_soft": "#0c2628",
            "danger":      "#ef6b6b",
        },
    },
}


def aplicar_tema(root, tema_id: str) -> dict:
    """Aplica as cores UI do tema na janela principal e devolve a paleta.

    Exemplo:
        ui = aplicar_tema(root, "navy")
        tk.Button(root, bg=ui["accent"], fg=ui["text_strong"])
    """
    if tema_id not in THEMES:
        raise ValueError(
            f"Tema desconhecido: {tema_id!r}. Disponíveis: {list(THEMES)}"
        )
    ui = THEMES[tema_id]["palette_ui"]
    root.configure(bg=ui["bg"])
    return ui
