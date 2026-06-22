"""
scripts/gerar_template_tema.py
==============================
CLI para gerar o template PNG de tema personalizado para o display de apresentação.

Uso:
    python scripts/gerar_template_tema.py
    python scripts/gerar_template_tema.py --output meu_template.png

A lógica de geração está em core/assets.py (gerar_template_tema).
Dentro do app, o botão "Gerar Template PNG" no popup de especificações
chama essa mesma função diretamente, sem precisar deste script.
"""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera template PNG 1920x1080 com guias visuais para temas de apresentação."
    )
    parser.add_argument(
        "--output", default="template_tema_1920x1080.png",
        help="Caminho de saída do arquivo PNG (padrão: template_tema_1920x1080.png)",
    )
    args = parser.parse_args()

    from core.assets import gerar_template_tema
    gerar_template_tema(args.output)

    out = Path(args.output)
    print(f"Template salvo em: {out.resolve()}")
    print(f"Tamanho: 1920x1080 px")
    print()
    print("Como usar:")
    print("  1. Abra o arquivo em qualquer editor (GIMP, Photoshop, Canva, Paint.NET).")
    print("  2. Adicione arte ou textura como camada abaixo dos guias.")
    print("  3. Oculte ou exclua a camada de guias antes de exportar.")
    print("  4. Exporte como PNG ou JPG (max. 5 MB).")
    print("  5. No app: Apresentacao > Fundo > botao [+] para importar.")


if __name__ == "__main__":
    main()
