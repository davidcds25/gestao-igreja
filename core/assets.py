"""
core/assets.py
==============
Carregamento centralizado dos assets da marca.

Para personalizar para outra organização, basta colocar seus arquivos
na pasta assets/ usando os nomes abaixo. O app detecta e aplica
automaticamente, sem precisar alterar código.

Nomes por função (substitua com seus próprios arquivos):
  icone_janela.png             — ícone na barra de tarefas e alt-tab (256×256)
  logo_transparent_h32.png     — marca pequena no cabeçalho do app (fundo transparente)
  logo_transparent_h400.png    — logotipo na tela de login (fundo transparente, fundo escuro)
  logo_transparent_h220.png    — logotipo na tela "Sobre" (fundo transparente)
  logo_transparent.png         — logotipo geral / relatórios PDF (fundo transparente)
  logo_transparent_light.png   — logotipo para fundos claros (ex: PDF impresso)

  bg_display_dourado.png   — fundo do display: tons sépia/dourados
  bg_display_navy.png      — fundo do display: azul-marinho cinematográfico
  bg_display_vinho.png     — fundo do display: vinho profundo/altar
  bg_display_mata.png      — fundo do display: verde mata/ministério
  bg_display_roxo.png      — fundo do display: roxo/adoração
  bg_display_petroleo.png  — fundo do display: azul-petróleo contemporâneo
  bg_display_natal.png     — fundo do display: tema natalino (sazonal)
  bg_display_pascoa.png    — fundo do display: tema pascal (sazonal)
  bg_display_ceia.png      — fundo do display: tema santa ceia (sazonal)
  bg_display_infantil.png  — fundo do display: ministério infantil

Se o arquivo personalizado não existir, o sistema usa o arquivo original
da pasta assets/ como fallback automático.
"""

from pathlib import Path
import tkinter as tk

_DIR = Path(__file__).parent.parent / "assets"


def _find(*names: str) -> Path | None:
    """Retorna o caminho do primeiro arquivo existente dentre os candidatos."""
    for name in names:
        p = _DIR / name
        if p.exists():
            return p
    return None


# ── Backgrounds do display de apresentação ────────────────────────────

_TEMAS_DISPLAY: dict[str, str] = {
    "dourado":  "bg_display_dourado.png",
    "navy":     "bg_display_navy.png",
    "vinho":    "bg_display_vinho.png",
    "mata":     "bg_display_mata.png",
    "roxo":     "bg_display_roxo.png",
    "petroleo": "bg_display_petroleo.png",
    "natal":    "bg_display_natal.png",
    "pascoa":   "bg_display_pascoa.png",
    "ceia":     "bg_display_ceia.png",
    "infantil": "bg_display_infantil.png",
}


def bg_display_path(tema: str) -> str | None:
    """Caminho do PNG de fundo para o display de apresentação.
    Retorna None se o arquivo do tema não existir (display usa preto puro)."""
    arquivo = _TEMAS_DISPLAY.get(tema)
    if not arquivo:
        return None
    p = _find(arquivo)
    return str(p) if p else None


def temas_display_disponiveis() -> list:
    """Lista de temas cujo arquivo de fundo existe em assets/."""
    return [t for t, f in _TEMAS_DISPLAY.items() if _find(f)]


# ── API pública ────────────────────────────────────────────────────────

def aplicar_icone_janela(root: tk.Tk) -> None:
    """Define o ícone da janela (barra de tarefas / alt-tab).

    Estratégia:
      1) Windows: tenta icon.ico (multi-tamanho nativo — melhor qualidade).
      2) Fallback: iconphoto com PNGs em todas as resoluções disponíveis.
    Silencioso se não houver nenhum arquivo."""
    import sys
    if sys.platform.startswith("win"):
        ico = _find("icon.ico")
        if ico:
            try:
                root.iconbitmap(default=str(ico))
                return
            except tk.TclError:
                pass   # cai para o fallback PNG abaixo

    paths = [
        _find("icon_256.png"),
        _find("icon_128.png"),
        _find("icon_64.png"),
        _find("icon_48.png"),
        _find("icon_32.png"),
        _find("icon_16.png"),
        _find("icone_janela.png"),   # nome role-based legado
    ]
    imgs = [tk.PhotoImage(file=str(p)) for p in paths if p]
    if imgs:
        root.iconphoto(True, *imgs)
        root._brand_icons = imgs  # mantém referência para evitar GC


def logo_topo(parent: tk.Widget, height: int = 28) -> tk.Label | None:
    """Retorna Label com a marca para o cabeçalho do app.
    None se nenhum arquivo de logo estiver disponível."""
    p = _find(
        "logo_topo.png",
        "logo_transparent_h32.png",
        "logo_transparent_h64.png",
        "icon_circ_blue.png",
    )
    if not p:
        return None
    try:
        img = tk.PhotoImage(file=str(p))
        if img.height() > height:
            factor = max(1, img.height() // height)
            img = img.subsample(factor, factor)
        lbl = tk.Label(parent, image=img, bd=0)
        lbl._img = img  # evita GC
        return lbl
    except Exception:
        return None


def logo_login(parent: tk.Widget, max_width: int = 300) -> tk.Label | None:
    """Retorna Label com o logotipo para a tela de login (fundo escuro).
    None se nenhum arquivo de logo estiver disponível."""
    p = _find(
        "logo_login.png",
        "logo_transparent_h400.png",
        "logo_transparent.png",
        "logo_color_dark_bg.png",
        "logo_color.png",
    )
    if not p:
        return None
    try:
        img = tk.PhotoImage(file=str(p))
        if img.width() > max_width:
            factor = max(1, img.width() // max_width)
            img = img.subsample(factor, factor)
        lbl = tk.Label(parent, image=img, bd=0)
        lbl._img = img  # evita GC
        return lbl
    except Exception:
        return None


def logo_relatorio_path() -> str | None:
    """Caminho absoluto do logo para inserção no header de PDF via fpdf2.
    None se nenhum arquivo disponível."""
    p = _find(
        "logo_relatorio.png",
        "logo_transparent_h64.png",    # tamanho ideal para header de relatório
        "logo_transparent.png",
        "logo_transparent_light.png",
        "logo_mono.png",
        "logo_color.png",
    )
    return str(p) if p else None
