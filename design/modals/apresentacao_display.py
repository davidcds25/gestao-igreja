"""
Janela de display para projetor/TV — módulo Apresentação.
Criada uma vez e mantida viva; use show/hide para controle de visibilidade.
Suporta fundos temáticos da marca via PIL (pillow).
"""

import tkinter as tk
from tkinter import font as tkfont

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

_BG      = "#000000"
_FG      = "#ffffff"
_FG_DIM  = "#a0a4ad"
_FG_GOLD = "#f3c43a"
_FONT    = "Segoe UI"


class DisplayWindow:
    """Janela separada para exibição no projetor. Pode ser movida para outro monitor."""

    def __init__(self, root, tema: str | None = "auto"):
        self._root = root
        self._win  = tk.Toplevel(root)
        self._win.withdraw()   # começa oculto; show() o traz ao foco
        self._win.title("Display — Apresentação")
        self._win.configure(bg=_BG)
        self._win.geometry("1280x720")
        self._win.protocol("WM_DELETE_WINDOW", self._on_close)
        self._win.bind("<F11>", self._toggle_fullscreen)
        self._win.bind("<Escape>", self._exit_fullscreen)
        self._fullscreen = False

        # Canvas ocupa toda a janela — renderiza fundo + conteúdo
        self._canvas = tk.Canvas(self._win, bg=_BG, highlightthickness=0, bd=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._canvas.bind("<Configure>", lambda _e: self._redesenhar())

        # Estado do fundo
        self._bg_src  = None   # PIL.Image original
        self._bg_img  = None   # ImageTk.PhotoImage (mantém ref)

        # Estado do conteúdo
        self._modo           = None   # 'letra' | 'versiculo'
        self._payload        = None
        self._verse_pages    = []     # páginas do versículo atual
        self._verse_page_idx = 0
        self._verse_ref      = ""

        # Cache de fontes — evita recriar objetos Tcl a cada redesenho
        self._font_cache: dict = {}

        # Escolhe tema inicial
        if tema == "auto":
            from core.assets import temas_display_disponiveis
            available = temas_display_disponiveis()
            tema = available[0] if available else None

        self._tema = None
        self.set_tema(tema)

    # ── Tema / fundo ───────────────────────────────────────────────────

    def set_tema(self, tema: str | None) -> None:
        """Troca o fundo do display. tema=None → preto puro."""
        self._tema = tema
        self._bg_src = None
        if tema and _HAS_PIL:
            from core.assets import bg_display_path
            path = bg_display_path(tema)
            if path:
                try:
                    self._bg_src = Image.open(path).convert("RGB")
                except Exception:
                    pass
        self._redesenhar()

    # ── Render interno ─────────────────────────────────────────────────

    def _redesenhar(self) -> None:
        """Refaz fundo + conteúdo ajustados ao tamanho atual do Canvas."""
        c = self._canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return

        # 1) Fundo
        if self._bg_src is not None:
            src_w, src_h = self._bg_src.size
            scale = max(w / src_w, h / src_h)
            nw = int(src_w * scale)
            nh = int(src_h * scale)
            img = self._bg_src.resize((nw, nh), Image.LANCZOS)
            x0  = (nw - w) // 2
            y0  = (nh - h) // 2
            img = img.crop((x0, y0, x0 + w, y0 + h))
            self._bg_img = ImageTk.PhotoImage(img)
            c.create_image(0, 0, anchor="nw", image=self._bg_img)

        # 2) Conteúdo
        if self._modo == "letra":
            self._desenhar_letra(*self._payload)
        elif self._modo == "versiculo" and self._verse_pages:
            self._desenhar_versiculo(
                self._verse_pages[self._verse_page_idx],
                self._verse_ref,
                self._verse_page_idx + 1,
                len(self._verse_pages),
            )

    def _font_main(self, h: int) -> tkfont.Font:
        key = ("main", max(24, int(h * 0.055)))
        if key not in self._font_cache:
            self._font_cache[key] = tkfont.Font(family=_FONT, size=key[1], weight="bold")
        return self._font_cache[key]

    def _font_ref(self, h: int) -> tkfont.Font:
        key = ("ref", max(18, int(h * 0.036)))
        if key not in self._font_cache:
            self._font_cache[key] = tkfont.Font(family=_FONT, size=key[1], weight="bold")
        return self._font_cache[key]

    def _contorno(self, x, y, text, font, fill, ow=3, anchor="center", width=None) -> None:
        """Desenha texto com contorno preto em 8 direções — essencial para projetor."""
        c = self._canvas
        offsets = [(dx, dy) for dx in (-ow, 0, ow) for dy in (-ow, 0, ow) if not (dx == 0 and dy == 0)]
        offsets += [(ow + 1, 0), (-(ow + 1), 0), (0, ow + 1), (0, -(ow + 1))]
        kw = dict(text=text, fill="#000000", font=font, anchor=anchor)
        if width:
            kw["width"] = width
            kw["justify"] = "center"
        for dx, dy in offsets:
            c.create_text(x + dx, y + dy, **kw)
        kw["fill"] = fill
        c.create_text(x, y, **kw)

    @staticmethod
    def _split_verse(text: str, words_per_page: int = 45) -> list[str]:
        """Divide texto longo em páginas de até words_per_page palavras."""
        words = text.split()
        if not words:
            return [""]
        return [" ".join(words[i:i + words_per_page])
                for i in range(0, len(words), words_per_page)]

    def _nav_verse_page(self, delta: int) -> bool:
        """Move entre páginas do versículo. Retorna True se mudou, False se está no limite."""
        if len(self._verse_pages) <= 1:
            return False
        new_idx = self._verse_page_idx + delta
        if new_idx < 0 or new_idx >= len(self._verse_pages):
            return False
        self._verse_page_idx = new_idx
        self._redesenhar()
        return True

    def _desenhar_letra(self, pagina: list, info: str, page_str: str) -> None:
        c = self._canvas
        w = c.winfo_width()
        h = c.winfo_height()
        f      = self._font_main(h)
        line_h = f.metrics("linespace") + 10
        total  = line_h * len(pagina)
        y0     = (h - total) / 2 + line_h / 2 - 20
        for i, linha in enumerate(pagina):
            self._contorno(w / 2, y0 + i * line_h, linha, font=f, fill=_FG)
        self._rodape(info, page_str + "   ←→ navegar  |  F11 = tela cheia")

    def _desenhar_versiculo(self, text: str, reference: str,
                            page: int = 1, total: int = 1) -> None:
        c = self._canvas
        w = c.winfo_width()
        h = c.winfo_height()
        f_txt = self._font_main(h)
        f_ref = self._font_ref(h)
        wrap  = int(w * 0.82)
        self._contorno(w / 2, h * 0.40, f'"{text}"',
                       font=f_txt, fill=_FG, width=wrap)
        self._contorno(w / 2, h * 0.86, f"— {reference}",
                       font=f_ref, fill=_FG_GOLD)
        dir_ = (f"{page} / {total}   |   F11 = tela cheia" if total > 1
                else "F11 = tela cheia")
        self._rodape("Versículo ao Vivo", dir_)

    def _font_footer(self, h: int) -> tkfont.Font:
        key = ("footer", max(9, int(h * 0.013)))
        if key not in self._font_cache:
            self._font_cache[key] = tkfont.Font(family=_FONT, size=key[1])
        return self._font_cache[key]

    def _rodape(self, esq: str, dir_: str) -> None:
        c = self._canvas
        w = c.winfo_width()
        h = c.winfo_height()
        f = self._font_footer(h)
        if esq:
            c.create_text(20, h - 18, text=esq, fill=_FG_DIM, font=f, anchor="w")
        if dir_:
            c.create_text(w - 20, h - 18, text=dir_, fill=_FG_DIM, font=f, anchor="e")

    # ── API pública ─────────────────────────────────────────────────────

    def show_letra(self, pagina: list, info: str, page_str: str) -> None:
        """
        pagina: lista de linhas da página atual (ex: ["linha 1", "linha 2"]).
        info: "Título · Artista"
        page_str: "Slide 2 / 9"
        """
        self._modo    = "letra"
        self._payload = (pagina, info, page_str)
        self._redesenhar()

    def show_versiculo(self, text: str, reference: str) -> None:
        """Exibe versículo bíblico. Pagina automaticamente se o texto for longo."""
        self._verse_pages    = self._split_verse(text)
        self._verse_page_idx = 0
        self._verse_ref      = reference
        self._modo           = "versiculo"
        self._payload        = None
        self._redesenhar()

    def bind_nav(self, on_prev, on_next) -> None:
        """Vincula ←/→/Espaço/PgDn à navegação no display.
        Para versículos multipágina navega as páginas primeiro; só troca de
        versículo ao chegar no limite. Para músicas, comportamento normal."""
        def _prev(_e):
            if not self._nav_verse_page(-1):
                on_prev()
            return "break"

        def _next(_e):
            if not self._nav_verse_page(+1):
                on_next()
            return "break"

        self._win.bind("<Left>",  _prev)
        self._win.bind("<Prior>", _prev)
        self._win.bind("<Right>", _next)
        self._win.bind("<Next>",  _next)
        self._win.bind("<space>", _next)

    def limpar(self) -> None:
        """Limpa o display (tela preta)."""
        self._modo           = None
        self._payload        = None
        self._verse_pages    = []
        self._verse_page_idx = 0
        self._redesenhar()

    def show(self) -> None:
        """Traz a janela ao foco."""
        if not self.exists():
            return
        self._win.deiconify()
        self._win.lift()
        self._win.focus_force()

    def exists(self) -> bool:
        try:
            return bool(self._win.winfo_exists())
        except Exception:
            return False

    # ── Fullscreen ──────────────────────────────────────────────────────

    def _toggle_fullscreen(self, _=None) -> None:
        self._fullscreen = not self._fullscreen
        self._win.attributes("-fullscreen", self._fullscreen)

    def _exit_fullscreen(self, _=None) -> None:
        if self._fullscreen:
            self._fullscreen = False
            self._win.attributes("-fullscreen", False)

    def _on_close(self) -> None:
        if self._fullscreen:
            self._fullscreen = False
            self._win.attributes("-fullscreen", False)
        self._win.withdraw()
