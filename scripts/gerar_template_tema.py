"""
scripts/gerar_template_tema.py
==============================
Gera um arquivo PNG de template (1920×1080) com guias visuais para criação
de temas personalizados para o display de apresentação.

Uso:
    python scripts/gerar_template_tema.py
    python scripts/gerar_template_tema.py --output meu_template.png

O arquivo gerado pode ser aberto em qualquer editor de imagem (GIMP, Photoshop,
Canva, etc.) e usado como base para criar novos temas.

PADRÃO DOS TEMAS:
  Formato  : PNG ou JPG
  Resolução: 1920 × 1080 px (Full HD / 16:9) — obrigatório
  Modo cor : sRGB
  Fundo    : escuro (preferencialmente) para que as letras brancas fiquem legíveis
  Tamanho  : até 5 MB (imagens maiores aumentam o tempo de carregamento)
  Nome     : qualquer nome sem caracteres especiais (acentos e espaços são permitidos)

ZONAS DE SEGURANÇA:
  ┌─────────────────────────────────────────────────────────────┐
  │  Zona de borda (10 %): pode ser cortada em monitores        │
  │  ┌───────────────────────────────────────────────────────┐  │
  │  │  Zona segura (80 %): arte principal, logotipos aqui   │  │
  │  │                                                       │  │
  │  │         CENTRO DA TELA                                │  │
  │  │    (Letras e versículos aparecem aqui em branco)      │  │
  │  │                                                       │  │
  │  └───────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘

DICAS:
  • Use gradientes ou texturas sutis no fundo para não distrair da letra.
  • Evite texto, logotipos e bordas vistosas na área central — as letras
    do sistema ficam sobrepostas.
  • Logotipos e marcas da igreja ficam bem no canto inferior direito,
    fora da zona central de letras.
"""

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow não instalado. Execute: pip install Pillow")
    raise SystemExit(1)

W, H = 1920, 1080
SAFE_PCT    = 0.10  # margem da zona de borda (10 % de cada lado)
CENTRAL_PCT = 0.35  # zona central onde as letras ficam (35 % da altura)


def main(output: str = "template_tema_1920x1080.png") -> None:
    img  = Image.new("RGB", (W, H), color=(18, 18, 28))
    draw = ImageDraw.Draw(img)

    # Gradiente diagonal suave (fundo escuro → azul muito escuro)
    for y in range(H):
        r = int(18  + (30  - 18)  * y / H)
        g = int(18  + (24  - 18)  * y / H)
        b = int(28  + (50  - 28)  * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Zona de borda ──────────────────────────────────────────────────
    bx = int(W * SAFE_PCT)
    by = int(H * SAFE_PCT)
    draw.rectangle(
        [bx, by, W - bx, H - by],
        outline=(255, 80, 80), width=2,
    )
    _label(draw, bx + 8, by + 8,
           "Zona de borda (10 %) — pode ser cortada em diferentes resoluções",
           (255, 80, 80))

    # ── Zona segura (dentro da borda) ──────────────────────────────────
    sx = int(W * (SAFE_PCT + 0.04))
    sy = int(H * (SAFE_PCT + 0.04))
    draw.rectangle(
        [sx, sy, W - sx, H - sy],
        outline=(255, 200, 0), width=2,
    )
    _label(draw, sx + 8, sy + 8,
           "Zona segura (80 %) — arte, logotipos e elementos visuais aqui",
           (255, 200, 0))

    # ── Zona central de letras ─────────────────────────────────────────
    cy_start = int(H * (0.5 - CENTRAL_PCT / 2))
    cy_end   = int(H * (0.5 + CENTRAL_PCT / 2))
    draw.rectangle(
        [sx + 20, cy_start, W - sx - 20, cy_end],
        outline=(80, 200, 80), width=2,
    )
    _label(draw, sx + 28, cy_start + 8,
           "Área de letras e versículos — mantenha LIMPO (texto branco aparece aqui)",
           (80, 200, 80))

    # ── Marcadores de canto ────────────────────────────────────────────
    _corner_mark(draw, 0, 0, "0, 0")
    _corner_mark(draw, W, 0, f"{W}, 0", right=True)
    _corner_mark(draw, 0, H, f"0, {H}", bottom=True)
    _corner_mark(draw, W, H, f"{W}, {H}", right=True, bottom=True)

    # ── Texto central ──────────────────────────────────────────────────
    center_text = "Coloque aqui a arte de fundo do seu tema"
    _center_text(draw, W // 2, H // 2, center_text, (180, 180, 220))

    sub_text = f"1920 × 1080 px  •  16:9  •  PNG ou JPG  •  máx. 5 MB"
    _center_text(draw, W // 2, H // 2 + 48, sub_text, (120, 120, 150), size=28)

    # ── Logo sugerido no canto inferior direito ────────────────────────
    logo_box = [W - 300, H - 120, W - bx, H - by]
    draw.rectangle(logo_box, outline=(80, 80, 140), width=1)
    _label(draw, logo_box[0] + 8, logo_box[1] + 8,
           "Logotipo / marca\n(opcional)", (80, 80, 180))

    # ── Salvar ─────────────────────────────────────────────────────────
    out = Path(output)
    img.save(out, "PNG")
    print(f"Template salvo em: {out.resolve()}")
    print(f"Tamanho: {W}×{H} px")
    print()
    print("Como usar:")
    print("  1. Abra o arquivo em qualquer editor (GIMP, Photoshop, Canva, Paint.NET).")
    print("  2. Adicione arte, textura ou foto como nova camada abaixo dos guias.")
    print("  3. Oculte ou exclua a camada de guias antes de exportar.")
    print("  4. Exporte como PNG ou JPG (máx. 5 MB).")
    print("  5. No app, va em Apresentacao > Fundo > botao [+] para importar.")


def _label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
           color: tuple, size: int = 22) -> None:
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)


def _center_text(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str,
                 color: tuple, size: int = 36) -> None:
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), text, fill=color, font=font)


def _corner_mark(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
                 right: bool = False, bottom: bool = False, size: int = 7) -> None:
    draw.rectangle([x - size, y - size, x + size, y + size], fill=(200, 200, 200))
    tx = (x - 80) if right else (x + 10)
    ty = (y - 30) if bottom else (y + 10)
    _label(draw, tx, ty, label, (200, 200, 200), size=22)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera template PNG para temas de apresentação.")
    parser.add_argument("--output", default="template_tema_1920x1080.png",
                        help="Caminho de saída do arquivo PNG")
    args = parser.parse_args()
    main(args.output)
