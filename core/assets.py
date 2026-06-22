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

import sys as _sys
from pathlib import Path
import tkinter as tk

_DIR = Path(__file__).parent.parent / "assets"

# Pasta gravável pelo usuário: ao lado do .exe em produção, ou em assets/ em dev.
_CUSTOM_DIR = (
    Path(_sys.executable).parent / "assets" / "temas_custom"
    if getattr(_sys, "frozen", False)
    else _DIR / "temas_custom"
)


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


def _custom_temas() -> dict[str, Path]:
    """Retorna {slug: path} de todos os temas personalizados em temas_custom/."""
    if not _CUSTOM_DIR.exists():
        return {}
    result: dict[str, Path] = {}
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        for p in sorted(_CUSTOM_DIR.glob(ext)):
            result[p.stem] = p
    return result


def bg_display_path(tema: str) -> str | None:
    """Caminho do PNG de fundo para o display de apresentação.
    Retorna None se o arquivo do tema não existir (display usa preto puro)."""
    arquivo = _TEMAS_DISPLAY.get(tema)
    if arquivo:
        p = _find(arquivo)
        return str(p) if p else None
    # Tema personalizado
    custom = _custom_temas()
    p = custom.get(tema)
    return str(p) if p else None


def temas_display_disponiveis() -> list:
    """Lista de temas cujo arquivo de fundo existe (embutidos + personalizados)."""
    built_in = [t for t, f in _TEMAS_DISPLAY.items() if _find(f)]
    custom   = list(_custom_temas().keys())
    return built_in + custom


def importar_tema_custom(source_path: str, nome: str | None = None) -> str:
    """Copia imagem para temas_custom/ e retorna o slug do tema.

    O slug é o nome do arquivo sem extensão, com caracteres especiais
    substituídos por _. Se `nome` não for fornecido, usa o nome do arquivo."""
    import shutil, re
    _CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
    src = Path(source_path)
    slug_base = re.sub(r"[^\w\-]", "_", nome or src.stem).strip("_") or "tema"
    ext  = src.suffix.lower()
    dest = _CUSTOM_DIR / f"{slug_base}{ext}"
    # evita sobrescrever: acrescenta sufixo numérico se necessário
    counter = 1
    while dest.exists() and dest != src.resolve():
        dest = _CUSTOM_DIR / f"{slug_base}_{counter}{ext}"
        counter += 1
    shutil.copy2(src, dest)
    return dest.stem


def remover_tema_custom(slug: str) -> bool:
    """Remove um tema personalizado pelo slug. Retorna True se removido."""
    custom = _custom_temas()
    p = custom.get(slug)
    if not p:
        return False
    p.unlink(missing_ok=True)
    return True


def gerar_template_tema(output_path: str) -> None:
    """Gera um PNG 1920×1080 com guias visuais para criação de temas personalizados.

    O arquivo pode ser aberto em qualquer editor de imagem (GIMP, Photoshop,
    Canva, Paint.NET) e usado como base — basta colocar a arte abaixo dos guias
    e exportar sem eles."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Pillow não está instalado. Execute: pip install Pillow"
        ) from exc

    W, H = 1920, 1080

    img  = Image.new("RGB", (W, H), color=(18, 18, 28))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        r = int(18 + (30 - 18) * y / H)
        g = int(18 + (24 - 18) * y / H)
        b = int(28 + (50 - 28) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    def _font(size: int):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

    def _label(x, y, text, color, size=22):
        draw.text((x, y), text, fill=color, font=_font(size))

    def _center_text(cx, cy, text, color, size=36):
        f = _font(size)
        bbox = draw.textbbox((0, 0), text, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2), text, fill=color, font=f)

    def _corner(x, y, label, right=False, bottom=False):
        s = 7
        draw.rectangle([x - s, y - s, x + s, y + s], fill=(200, 200, 200))
        tx = (x - 90) if right else (x + 10)
        ty = (y - 30) if bottom else (y + 10)
        _label(tx, ty, label, (200, 200, 200), 22)

    bx, by   = int(W * 0.10), int(H * 0.10)
    sx, sy   = int(W * 0.14), int(H * 0.14)
    cy_start = int(H * 0.325)
    cy_end   = int(H * 0.675)

    draw.rectangle([bx, by, W - bx, H - by], outline=(255, 80, 80),  width=2)
    _label(bx + 8, by + 8,
           "Zona de borda (10%) — pode ser cortada em diferentes resolucoes",
           (255, 80, 80))

    draw.rectangle([sx, sy, W - sx, H - sy], outline=(255, 200, 0), width=2)
    _label(sx + 8, sy + 8,
           "Zona segura (80%) — arte, logotipos e elementos visuais aqui",
           (255, 200, 0))

    draw.rectangle([sx + 20, cy_start, W - sx - 20, cy_end],
                   outline=(80, 200, 80), width=2)
    _label(sx + 28, cy_start + 8,
           "Area de letras e versiculos — mantenha LIMPO (texto branco aparece aqui)",
           (80, 200, 80))

    _corner(0, 0, "0, 0")
    _corner(W, 0, f"{W}, 0", right=True)
    _corner(0, H, f"0, {H}", bottom=True)
    _corner(W, H, f"{W}, {H}", right=True, bottom=True)

    _center_text(W // 2, H // 2,
                 "Coloque aqui a arte de fundo do seu tema",
                 (180, 180, 220))
    _center_text(W // 2, H // 2 + 52,
                 "1920 x 1080 px  |  16:9  |  PNG ou JPG  |  max. 5 MB",
                 (120, 120, 150), size=28)

    logo_box = [W - 300, H - 120, W - bx, H - by]
    draw.rectangle(logo_box, outline=(80, 80, 140), width=1)
    _label(logo_box[0] + 8, logo_box[1] + 8,
           "Logotipo / marca\n(opcional)", (80, 80, 180))

    img.save(str(output_path), "PNG")


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
