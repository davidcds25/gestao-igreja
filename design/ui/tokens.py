"""
ui/tokens.py
============
Design tokens centralizados. IMPORTE estes valores em vez de digitar
cores/tamanhos hardcoded espalhados pelo código.

USO:
    from ui.tokens import COLORS, SPACING, FONTS, STATUS_COLORS

    label = tk.Label(parent, text="Olá",
                     font=FONTS["title"],
                     fg=COLORS["text"],
                     bg=COLORS["bg_card"])
    label.pack(padx=SPACING[6], pady=SPACING[5])

Trocar tema é só trocar a função `theme()` para retornar `_LIGHT`.
"""

# ─── Espaçamento — escala de 4 ─────────────────────────────────────────
SPACING = {
    1:  4,
    2:  8,
    3: 12,
    4: 16,
    5: 20,
    6: 24,
    8: 32,
    10: 40,
    12: 48,
}

# ─── Paleta DARK (padrão) ──────────────────────────────────────────────
_DARK = {
    # superfícies
    "bg_dark":        "#0f0f23",  # fundo principal da app
    "bg_card":        "#1a1a2e",  # cards, painéis
    "bg_card_raised": "#1f2042",  # cards um nível acima (header de tabela)
    "sidebar_bg":     "#16213e",  # sidebar e header
    "sidebar_hover":  "#1e2d50",  # hover do nav item
    "sidebar_active": "#1f2f56",  # bg do nav item ativo
    "divider":        "#2d2d44",  # divisores fortes, bordas, inputs
    "divider_soft":   "#222237",  # divisores internos (ex: linhas de tabela)
    "input_bg":       "#2d2d44",  # bg de entry/text/combobox

    # marca
    "accent":         "#00d4ff",  # ciano — CTAs primários
    "accent2":        "#667eea",  # roxo-azul — botões secundários
    "verse_gold":     "#ffd700",  # dourado do card de versículo
    "whatsapp":       "#25D366",

    # texto
    "text":           "#ffffff",
    "text_dim":       "#cccccc",  # itens de menu, labels
    "text_muted":     "#8a8aa3",  # textos auxiliares
    "text_very_dim":  "#5a5a75",  # placeholders, hints

    # estado
    "success":        "#51cf66",  # ativo, realizado
    "danger":         "#ff6b6b",  # erro, afastado, cancelado
    "warning":        "#ffd700",  # aviso, aguardando
    "orange":         "#ffa94d",
    "purple":         "#9b59b6",  # presbítero
}

# ─── Paleta LIGHT (alternativa) ────────────────────────────────────────
_LIGHT = {
    "bg_dark":        "#f5f4ef",
    "bg_card":        "#ffffff",
    "bg_card_raised": "#ffffff",
    "sidebar_bg":     "#ffffff",
    "sidebar_hover":  "#f0eee8",
    "sidebar_active": "#eaf7fc",
    "divider":        "#e6e3da",
    "divider_soft":   "#efece4",
    "input_bg":       "#f0eee8",

    "accent":         "#0891b2",
    "accent2":        "#5b6dd6",
    "verse_gold":     "#b45309",
    "whatsapp":       "#16a34a",

    "text":           "#1a1a2e",
    "text_dim":       "#3d3a35",
    "text_muted":     "#7a7368",
    "text_very_dim":  "#a8a195",

    "success":        "#15803d",
    "danger":         "#dc2626",
    "warning":        "#b45309",
    "orange":         "#c2410c",
    "purple":         "#7c3aed",
}

COLORS = _DARK  # ← troque para _LIGHT para tema claro

# ─── Tipografia ────────────────────────────────────────────────────────
# Segoe UI é nativa do Windows desde Vista. tk faz fallback para Arial
# automaticamente se não encontrar — mas nas máquinas que rodam Windows
# a fonte SEMPRE vai existir.
FONT_FAMILY      = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"  # também nativa do Windows

FONTS = {
    "display":      (FONT_FAMILY, 26, "bold"),    # saudação do dashboard
    "title":        (FONT_FAMILY, 20, "bold"),    # título de tela
    "subtitle":     (FONT_FAMILY, 14, "bold"),    # título de card/seção visual
    "section":      (FONT_FAMILY, 10, "bold"),    # eyebrow de seção (UPPERCASE)
    "body_strong":  (FONT_FAMILY, 12, "bold"),    # labels de field, nomes em cards
    "body":         (FONT_FAMILY, 12),            # corpo
    "body_italic":  (FONT_FAMILY, 12, "italic"),  # versículo
    "small":        (FONT_FAMILY, 11),            # auxiliar
    "small_bold":   (FONT_FAMILY, 11, "bold"),
    "tiny":         (FONT_FAMILY, 10),            # hints, datas em cards
    "tiny_bold":    (FONT_FAMILY, 10, "bold"),
    "badge":        (FONT_FAMILY, 9,  "bold"),    # texto dentro de badge
    "metric_large": (FONT_FAMILY, 36, "bold"),    # números grandes (KPIs)
    "metric_xl":    (FONT_FAMILY, 40, "bold"),
    "metric_small": (FONT_FAMILY, 24, "bold"),
    "btn":          (FONT_FAMILY, 10, "bold"),    # botão padrão
    "mono":         (FONT_FAMILY_MONO, 11),
}

# ─── Mapeamentos de cor por estado ─────────────────────────────────────
# Use estes em vez de if/elif espalhados. Cada tupla é (bg, fg).
STATUS_COLORS = {
    "Ativo":      (_DARK["success"], _DARK["bg_dark"]),
    "Afastado":   (_DARK["danger"],  "#ffffff"),
    "Visitante":  (_DARK["warning"], _DARK["bg_dark"]),
    "Planejado":  (_DARK["accent2"], "#ffffff"),
    "Realizado":  (_DARK["success"], _DARK["bg_dark"]),
    "Cancelado":  (_DARK["danger"],  "#ffffff"),
    "Concluído":  (_DARK["success"], _DARK["bg_dark"]),
    # Função do membro:
    "Membro":     (_DARK["input_bg"], _DARK["text_dim"]),
    "Diácono":    (_DARK["accent2"],  "#ffffff"),
    "Presbítero": (_DARK["purple"],   "#ffffff"),
}

# ─── Constantes de layout ──────────────────────────────────────────────
SIDEBAR_WIDTH    = 230
HEADER_HEIGHT    = 58
ACTIVE_RAIL_PX   = 3       # largura da barra accent à esquerda do nav ativo
CARD_RADIUS      = 4       # radius padrão (via Canvas polygon)
PAGE_PAD_X       = SPACING[8]   # 32px — padx externo de todas as views
PAGE_PAD_Y       = SPACING[6]   # 24px — pady externo de todas as views
SECTION_GAP      = SPACING[8]   # 32px — gap entre seções dentro de uma view
