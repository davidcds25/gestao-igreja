"""
Janela de display para projetor/TV — módulo Apresentação.
Criada uma vez e mantida viva; use show/hide para controle de visibilidade.
Suporta fundos temáticos da marca via PIL (pillow).
Suporte a vídeo via python-vlc (requer VLC instalado na máquina).
"""

import sys as _sys
import ctypes as _ct
import ctypes.wintypes as _wt
import tkinter as tk
from tkinter import font as tkfont

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

try:
    import vlc as _vlc
    _HAS_VLC = True
except Exception:
    _HAS_VLC = False


# ── Enumeração de monitores (Win32) ─────────────────────────────────────────

class _MONITORINFO(_ct.Structure):
    _fields_ = [
        ("cbSize",    _ct.c_uint32),
        ("rcMonitor", _wt.RECT),
        ("rcWork",    _wt.RECT),
        ("dwFlags",   _ct.c_uint32),
    ]

def enumerate_monitors() -> list[dict]:
    """Retorna lista de monitors: {x, y, w, h, primary}. Funciona no Windows."""
    if _sys.platform != "win32":
        return [{"x": 0, "y": 0, "w": 1920, "h": 1080, "primary": True}]
    monitors: list[dict] = []
    _PROC = _ct.WINFUNCTYPE(
        _ct.c_bool, _ct.c_ulong, _ct.c_ulong,
        _ct.POINTER(_wt.RECT), _ct.c_long,
    )

    def _cb(hMon, _hDC, _lpRect, _data):
        info = _MONITORINFO()
        info.cbSize = _ct.sizeof(_MONITORINFO)
        _ct.windll.user32.GetMonitorInfoW(hMon, _ct.byref(info))
        r = info.rcMonitor
        monitors.append({
            "x": r.left, "y": r.top,
            "w": r.right - r.left, "h": r.bottom - r.top,
            "primary": bool(info.dwFlags & 1),
        })
        return True

    _ct.windll.user32.EnumDisplayMonitors(None, None, _PROC(_cb), 0)
    return monitors or [{"x": 0, "y": 0, "w": 1920, "h": 1080, "primary": True}]


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
        self._win.withdraw()
        self._win.title("Display — Apresentação")
        self._win.configure(bg=_BG)
        self._win.geometry("1280x720")
        self._win.protocol("WM_DELETE_WINDOW", self._on_close)
        self._win.bind("<F11>", self._toggle_fullscreen)
        self._win.bind("<Escape>", self._exit_fullscreen)
        self._fullscreen        = False
        self._current_monitor   = 0   # índice do monitor em uso para tela cheia
        self._pre_fs_geometry   = "1280x720+100+100"  # restaurado ao sair do fullscreen
        self._fs_change_cb      = None  # callback(is_fullscreen: bool)

        # Canvas — renderiza texto, imagens e fundo temático
        self._canvas = tk.Canvas(self._win, bg=_BG, highlightthickness=0, bd=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._canvas.bind("<Configure>",
                          lambda e: self._redesenhar(e.width, e.height))

        # Frame opaco que o VLC usa para renderizar vídeo diretamente
        # Fica oculto até show_video() ser chamado
        self._video_frame = tk.Frame(self._win, bg=_BG)

        # Estado do fundo
        self._bg_src = None
        self._bg_img = None

        # Estado do conteúdo
        self._modo           = None   # 'letra' | 'versiculo' | 'imagem' | 'video'
        self._payload        = None
        self._verse_pages    = []
        self._verse_page_idx = 0
        self._verse_ref      = ""

        # Mídia — imagem
        self._media_img_src = None
        self._media_tk      = None

        # Mídia — vídeo VLC
        self._vlc_instance  = None
        self._vlc_player    = None

        self._font_cache: dict = {}

        if tema == "auto":
            from core.assets import temas_display_disponiveis
            available = temas_display_disponiveis()
            tema = available[0] if available else None

        self._tema = None
        self.set_tema(tema)

    # ── Tema / fundo ───────────────────────────────────────────────────

    def set_tema(self, tema: str | None) -> None:
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

    def _redesenhar(self, w: int = 0, h: int = 0) -> None:
        """Redesenha o canvas. Aceita w/h explícitos para evitar timing race
        logo após mudanças de geometry (go_fullscreen, troca de monitor)."""
        if self._modo == "video":
            return  # VLC gerencia seu próprio render

        c = self._canvas
        c.delete("all")
        if not w:
            w = c.winfo_width()
        if not h:
            h = c.winfo_height()
        if w <= 1 or h <= 1:
            return

        # Fundo temático (só nos modos que não são imagem/vídeo)
        if self._modo not in ("imagem",) and self._bg_src is not None:
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

        if self._modo == "letra":
            self._desenhar_letra(*self._payload)
        elif self._modo == "versiculo" and self._verse_pages:
            self._desenhar_versiculo(
                self._verse_pages[self._verse_page_idx],
                self._verse_ref,
                self._verse_page_idx + 1,
                len(self._verse_pages),
            )
        elif self._modo == "imagem" and self._media_img_src is not None:
            self._desenhar_imagem()

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

    def _font_footer(self, h: int) -> tkfont.Font:
        key = ("footer", max(9, int(h * 0.013)))
        if key not in self._font_cache:
            self._font_cache[key] = tkfont.Font(family=_FONT, size=key[1])
        return self._font_cache[key]

    def _contorno(self, x, y, text, font, fill, ow=3, anchor="center", width=None) -> None:
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
        words = text.split()
        if not words:
            return [""]
        return [" ".join(words[i:i + words_per_page])
                for i in range(0, len(words), words_per_page)]

    def _nav_verse_page(self, delta: int) -> bool:
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
        f = self._font_main(h)

        # Reduz a fonte até a linha mais longa caber em 92% da largura
        max_w = int(w * 0.92)
        linhas_validas = [l for l in pagina if l]
        while linhas_validas and any(f.measure(l) > max_w for l in linhas_validas):
            novo = max(16, f.cget("size") - 2)
            if novo == f.cget("size"):
                break
            f = tkfont.Font(family=_FONT, size=novo, weight="bold")

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

    def _desenhar_imagem(self) -> None:
        c = self._canvas
        w = c.winfo_width()
        h = c.winfo_height()
        img = self._media_img_src
        src_w, src_h = img.size
        scale = max(w / src_w, h / src_h)
        nw = int(src_w * scale)
        nh = int(src_h * scale)
        resized = img.resize((nw, nh), Image.LANCZOS)
        x0 = (nw - w) // 2
        y0 = (nh - h) // 2
        cropped = resized.crop((x0, y0, x0 + w, y0 + h))
        self._media_tk = ImageTk.PhotoImage(cropped)
        c.create_image(0, 0, anchor="nw", image=self._media_tk)
        self._rodape("", "F11 = tela cheia")

    def _rodape(self, esq: str, dir_: str) -> None:
        c = self._canvas
        w = c.winfo_width()
        h = c.winfo_height()
        f = self._font_footer(h)
        if esq:
            c.create_text(20, h - 18, text=esq, fill=_FG_DIM, font=f, anchor="w")
        if dir_:
            c.create_text(w - 20, h - 18, text=dir_, fill=_FG_DIM, font=f, anchor="e")

    # ── VLC — vídeo com áudio ───────────────────────────────────────────

    def _ativar_canvas(self) -> None:
        """Garante que o canvas está visível e o video_frame oculto."""
        self._video_frame.pack_forget()
        if not self._canvas.winfo_ismapped():
            self._canvas.pack(fill=tk.BOTH, expand=True)

    def _ativar_video_frame(self) -> None:
        """Troca canvas pelo frame nativo que o VLC renderiza."""
        self._canvas.pack_forget()
        self._video_frame.pack(fill=tk.BOTH, expand=True)
        self._win.update_idletasks()   # necessário para obter o HWND real

    def _stop_video(self) -> None:
        if self._vlc_player is not None:
            try:
                self._vlc_player.stop()
                self._vlc_player.release()
            except Exception:
                pass
            self._vlc_player = None
        self._ativar_canvas()

    # ── API pública ─────────────────────────────────────────────────────

    def show_letra(self, pagina: list, info: str, page_str: str) -> None:
        self._stop_video()
        self._modo    = "letra"
        self._payload = (pagina, info, page_str)
        self._redesenhar()

    def show_versiculo(self, text: str, reference: str) -> None:
        self._stop_video()
        self._verse_pages    = self._split_verse(text)
        self._verse_page_idx = 0
        self._verse_ref      = reference
        self._modo           = "versiculo"
        self._payload        = None
        self._redesenhar()

    def show_imagem(self, path: str) -> None:
        """Exibe imagem em tela cheia (cover-fit, sem distorção)."""
        self._stop_video()
        if not _HAS_PIL:
            return
        try:
            self._media_img_src = Image.open(path).convert("RGB")
            self._modo    = "imagem"
            self._payload = path
            self._redesenhar()
        except Exception:
            pass

    def show_video(self, path: str) -> None:
        """Reproduz vídeo com áudio via VLC. Requer VLC instalado na máquina."""
        self._stop_video()
        if not _HAS_VLC:
            return
        try:
            if self._vlc_instance is None:
                self._vlc_instance = _vlc.Instance(
                    "--no-xlib",
                    "--avcodec-hw=none",
                    "--no-video-title-show",
                    "--quiet",                  # suprime todos os logs do VLC no stderr
                )
            player = self._vlc_instance.media_player_new()
            # Desabilita captura de teclado/mouse pelo VLC para não conflitar com tkinter
            player.video_set_mouse_input(False)
            player.video_set_key_input(False)

            self._ativar_video_frame()
            hwnd = self._video_frame.winfo_id()
            player.set_hwnd(hwnd)

            media = self._vlc_instance.media_new(path)
            # Loop automático do vídeo
            media.add_option("input-repeat=65535")
            media.add_option(":avcodec-hw=none")   # garante sw decode mesmo após seek
            player.set_media(media)
            player.play()

            self._vlc_player = player
            self._modo    = "video"
            self._payload = path
        except Exception:
            self._stop_video()

    @staticmethod
    def video_disponivel() -> bool:
        """Retorna True se python-vlc e VLC estão disponíveis."""
        return _HAS_VLC

    def get_player(self):
        """Retorna o MediaPlayer VLC ativo se estiver em modo vídeo, senão None."""
        if self._modo == "video":
            return self._vlc_player
        return None

    def bind_nav(self, on_prev, on_next) -> None:
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
        self._stop_video()
        self._modo           = None
        self._payload        = None
        self._verse_pages    = []
        self._verse_page_idx = 0
        self._media_img_src  = None
        self._redesenhar()

    def show(self) -> None:
        if not self.exists():
            return
        self._win.deiconify()
        self._win.lift()
        self._win.focus_force()

    @property
    def is_fullscreen(self) -> bool:
        return self._fullscreen

    @property
    def current_monitor(self) -> int:
        return self._current_monitor

    def set_monitor(self, idx: int) -> None:
        self._current_monitor = idx

    def exists(self) -> bool:
        try:
            return bool(self._win.winfo_exists())
        except Exception:
            return False

    # ── Fullscreen / seleção de monitor ────────────────────────────────

    @staticmethod
    def get_monitors() -> list[dict]:
        """Retorna a lista de monitores disponíveis."""
        return enumerate_monitors()

    def set_fs_callback(self, cb) -> None:
        """Registra callback chamado quando o estado fullscreen muda: cb(is_fullscreen)."""
        self._fs_change_cb = cb

    def _notify_fs(self, is_fs: bool) -> None:
        if self._fs_change_cb:
            try:
                self._fs_change_cb(is_fs)
            except Exception:
                pass

    def go_fullscreen(self, monitor_idx: int = 0) -> None:
        """Tela cheia no monitor indicado.

        Usa overrideredirect + geometry explícita em vez de attributes(-fullscreen)
        porque o mecanismo nativo do Windows aplica fullscreen no monitor onde a
        janela *já está*, o que causa condição de corrida ao trocar de monitor.
        Com overrideredirect controlamos exatamente qual área cobrir.
        """
        monitors = enumerate_monitors()
        monitor_idx = max(0, min(monitor_idx, len(monitors) - 1))
        m = monitors[monitor_idx]
        self._current_monitor = monitor_idx

        # Salva geometria atual para poder restaurar ao sair
        if not self._fullscreen:
            try:
                self._pre_fs_geometry = self._win.geometry()
            except Exception:
                pass

        self._fullscreen = True

        # Garante que não há fullscreen nativo ativo
        self._win.attributes("-fullscreen", False)
        self._win.deiconify()
        self._win.update()

        # Janela sem bordas cobrindo exatamente o monitor alvo
        self._win.overrideredirect(True)
        self._win.geometry(f"{m['w']}x{m['h']}+{m['x']}+{m['y']}")
        self._win.update()
        self._win.lift()
        self._win.focus_force()

        # Força redesenho com as dimensões EXATAS do monitor alvo —
        # evita timing race onde winfo_width/height ainda retornam o valor antigo
        mw, mh = m["w"], m["h"]
        self._win.after(50, lambda: self._redesenhar(mw, mh))
        self._notify_fs(True)

    def move_to_monitor(self, monitor_idx: int) -> None:
        """Move a janela para o monitor indicado sem alterar o modo fullscreen."""
        monitors = enumerate_monitors()
        monitor_idx = max(0, min(monitor_idx, len(monitors) - 1))
        m = monitors[monitor_idx]
        self._current_monitor = monitor_idx
        self._win.deiconify()
        ww = self._win.winfo_width()  or 1280
        wh = self._win.winfo_height() or 720
        x = m["x"] + max(0, (m["w"] - ww) // 2)
        y = m["y"] + max(0, (m["h"] - wh) // 2)
        self._win.geometry(f"+{x}+{y}")
        self._win.update()
        self._win.lift()

    def cycle_monitor(self) -> None:
        """Alterna para o próximo monitor respeitando o modo atual."""
        monitors = enumerate_monitors()
        if len(monitors) <= 1:
            return
        next_idx = (self._current_monitor + 1) % len(monitors)
        if self._fullscreen:
            self.go_fullscreen(next_idx)
        else:
            self.move_to_monitor(next_idx)

    def _toggle_fullscreen(self, _=None) -> None:
        if self._fullscreen:
            self._exit_fullscreen()
        else:
            self.go_fullscreen(self._current_monitor)

    def _exit_fullscreen(self, _=None) -> None:
        if self._fullscreen:
            self._fullscreen = False
            self._win.overrideredirect(False)
            self._win.attributes("-fullscreen", False)
            self._win.geometry(self._pre_fs_geometry)
            self._win.update()
            self._notify_fs(False)

    def _on_close(self) -> None:
        self._stop_video()
        if self._fullscreen:
            self._fullscreen = False
            self._win.overrideredirect(False)
            self._win.attributes("-fullscreen", False)
        self._win.withdraw()
