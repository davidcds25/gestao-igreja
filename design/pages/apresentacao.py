"""
pages/apresentacao.py
=====================
Painel de controle do Som e Letras.
Duas abas: Som (lista + slides) e Versículo (busca + display).
Exibe conteúdo em DisplayWindow separada (projetor/TV).
"""

import tkinter as tk
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import page_container, screen_header, button, empty_state

_PG_LINES = 4  # linhas por slide no display


def render(parent, *, callbacks=None, get_display=None):
    callbacks   = callbacks  or {}
    get_display = get_display or (lambda: None)

    from core.musicas import listar_musicas, paginar_por_linhas

    state = {
        "musicas":     [],
        "busca":       "",
        "selecionada": None,
        "paginas":     [],
        "pagina_idx":  0,
        "versiculo":   None,
        "livro_sel":   None,
        "cap_sel":     1,
        "ver_sel":     1,
        "midia_imagens":  [],    # [{"path": str, "nome": str}]
        "midia_videos":   [],    # [{"path": str, "nome": str}]
        "midia_tipo_sel": None,  # "imagem" | "video" | None
        "midia_idx_img":  0,
        "midia_idx_vid":  0,
        "_poll_id":       None,
    }

    # ── container principal ──────────────────────────────────────────
    outer = page_container(parent)
    outer.pack(fill=tk.BOTH, expand=True)

    hdr = screen_header(
        outer,
        icon="🎬",
        title="Apresentação",
        subtitle="Som, letras e versículos ao vivo",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[2]))

    # ── tema do fundo do display ─────────────────────────────────────
    from core.assets import temas_display_disponiveis as _temas_disp

    _available_temas  = _temas_disp()
    # inicia no primeiro tema disponível, ou None (preto puro)
    _tema_var         = [_available_temas[0] if _available_temas else None]
    _TEMA_NONE_LABEL  = "● nenhum"
    _tema_var_str     = tk.StringVar(
        value=_TEMA_NONE_LABEL if _tema_var[0] is None else _tema_var[0]
    )

    def _set_tema(t):
        _tema_var[0] = t
        _tema_var_str.set(_TEMA_NONE_LABEL if t is None else t)
        dw = get_display()
        if dw and dw.exists():
            dw.set_tema(t)

    def _abrir_display():
        dw = get_display()
        if dw:
            dw.set_tema(_tema_var[0])
            dw._current_monitor = _mon_idx[0]
            dw.show()

    def _limpar_display():
        dw = get_display()
        if dw and dw.exists():
            dw.limpar()

    # ── seletor de fundo ─────────────────────────────────────────────────
    tema_row = tk.Frame(hdr["actions"], bg=COLORS["bg_dark"])
    tema_row.pack(side=tk.LEFT, padx=(0, SPACING[4]))

    tk.Label(tema_row, text="Fundo",
             font=FONTS["tiny_bold"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(
                 side=tk.LEFT, padx=(0, SPACING[2]))

    def _rebuild_tema_menu():
        from core.assets import temas_display_disponiveis
        temas = temas_display_disponiveis()
        menu  = _tema_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label=_TEMA_NONE_LABEL, command=lambda: _set_tema(None))
        for _t in temas:
            menu.add_command(label=_t, command=lambda t=_t: _set_tema(t))

    _opts = [_TEMA_NONE_LABEL] + _available_temas
    _tema_menu = tk.OptionMenu(tema_row, _tema_var_str, *_opts)
    _tema_menu.configure(
        font=FONTS["tiny_bold"],
        bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        activebackground=COLORS["accent"],
        activeforeground=COLORS["bg_dark"],
        relief=tk.FLAT, bd=0,
        highlightthickness=0,
        cursor="hand2",
        anchor=tk.W,
        width=12,
    )
    _tema_menu["menu"].configure(
        font=FONTS["tiny_bold"],
        bg=COLORS["bg_card"], fg=COLORS["text"],
        activebackground=COLORS["accent"],
        activeforeground=COLORS["bg_dark"],
        relief=tk.FLAT, bd=0,
    )
    # substitui os comandos gerados pelo OptionMenu para usar _set_tema
    _rebuild_tema_menu()
    _tema_menu.pack(side=tk.LEFT)

    def _abrir_importacao():
        """Mostra popup de especificações e, ao confirmar, abre o seletor de arquivo."""

        _SPECS = [
            ("Formato",    "PNG ou JPG"),
            ("Resolução",  "1920 × 1080 px  (Full HD / 16:9)"),
            ("Fundo",      "Escuro — texto branco do app fica sobreposto"),
            ("Tamanho",    "Máx. 5 MB"),
            ("Arte / logo","Evite o centro — letras ficam sobrepostas ali"),
        ]

        spec_win = tk.Toplevel(outer)
        spec_win.title("Padrão para Temas Personalizados")
        spec_win.configure(bg=COLORS["bg_dark"])
        spec_win.resizable(False, False)
        spec_win.transient(outer)
        spec_win.grab_set()

        outer.update_idletasks()
        cx = outer.winfo_rootx() + outer.winfo_width()  // 2
        cy = outer.winfo_rooty() + outer.winfo_height() // 2
        spec_win.geometry(f"500x490+{cx - 250}+{cy - 245}")

        tk.Label(spec_win,
                 text="Padrão para Temas Personalizados",
                 font=FONTS["subtitle"],
                 bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(
                     anchor=tk.W, padx=24, pady=(20, 4))

        tk.Label(spec_win,
                 text="Siga estas especificações para garantir a melhor qualidade na apresentação:",
                 font=FONTS["body"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                 wraplength=452, justify=tk.LEFT).pack(
                     anchor=tk.W, padx=24, pady=(0, 12))

        tbl = tk.Frame(spec_win, bg=COLORS["bg_card"])
        tbl.pack(fill=tk.X, padx=24, pady=(0, 12))

        for i, (campo, valor) in enumerate(_SPECS):
            row_bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_dark"]
            row = tk.Frame(tbl, bg=row_bg)
            row.pack(fill=tk.X)
            tk.Label(row, text=campo,
                     font=FONTS["tiny_bold"],
                     bg=row_bg, fg=COLORS["text_muted"],
                     width=14, anchor=tk.W).pack(side=tk.LEFT, padx=(12, 0), pady=7)
            tk.Label(row, text=valor,
                     font=FONTS["tiny"],
                     bg=row_bg, fg=COLORS["text"],
                     anchor=tk.W).pack(side=tk.LEFT, padx=(8, 12), pady=7)

        # ── botão de template ──────────────────────────────────────────
        tmpl_row = tk.Frame(spec_win, bg=COLORS["bg_dark"])
        tmpl_row.pack(fill=tk.X, padx=24, pady=(0, 16))

        tk.Label(tmpl_row,
                 text="Nao tem uma imagem pronta? Gere um template guia para abrir no seu editor:",
                 font=FONTS["tiny"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                 wraplength=452, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 6))

        def _gerar_template():
            import os
            from tkinter import filedialog, messagebox
            from core.assets import gerar_template_tema

            path = filedialog.asksaveasfilename(
                title="Salvar template do tema",
                defaultextension=".png",
                initialfile="template_tema_1920x1080.png",
                filetypes=[("PNG", "*.png")],
                parent=spec_win,
            )
            if not path:
                return
            try:
                gerar_template_tema(path)
                os.startfile(path)
            except Exception as exc:
                messagebox.showerror("Erro ao gerar template", str(exc),
                                     parent=spec_win)

        button(tmpl_row, text="Gerar Template PNG", kind="ghost", icon="📐",
               command=_gerar_template).pack(anchor=tk.W)

        btn_row = tk.Frame(spec_win, bg=COLORS["bg_dark"])
        btn_row.pack(fill=tk.X, padx=24, pady=(0, 20))

        def _prosseguir():
            spec_win.destroy()
            _escolher_arquivo()

        button(btn_row, text="Cancelar", kind="ghost",
               command=spec_win.destroy).pack(side=tk.RIGHT, padx=(SPACING[2], 0))
        button(btn_row, text="Entendido — Escolher Imagem",
               kind="primary", icon="📂",
               command=_prosseguir).pack(side=tk.RIGHT)

    def _escolher_arquivo():
        from tkinter import filedialog, simpledialog, messagebox
        from core.assets import importar_tema_custom
        from pathlib import Path as _Path

        path = filedialog.askopenfilename(
            title="Selecionar imagem do tema personalizado",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("JPG", "*.jpg *.jpeg"),
            ],
            parent=outer,
        )
        if not path:
            return

        default_name = _Path(path).stem
        nome = simpledialog.askstring(
            "Nome do Tema",
            "Nome para este tema personalizado:",
            initialvalue=default_name,
            parent=outer,
        )
        if nome is None:
            return
        nome = nome.strip() or default_name

        try:
            slug = importar_tema_custom(path, nome)
        except Exception as exc:
            messagebox.showerror("Erro ao importar tema", str(exc), parent=outer)
            return

        _rebuild_tema_menu()
        _set_tema(slug)

    tk.Button(
        tema_row, text="+",
        font=FONTS["tiny_bold"],
        bg=COLORS["bg_card"], fg=COLORS["accent"],
        activebackground=COLORS["accent"],
        activeforeground=COLORS["bg_dark"],
        relief=tk.FLAT, bd=0,
        padx=SPACING[3], pady=SPACING[1],
        cursor="hand2",
        command=_abrir_importacao,
    ).pack(side=tk.LEFT, padx=(SPACING[2], 0))

    # marca o tema inicial como ativo
    _set_tema(_tema_var[0])

    button(hdr["actions"], text="Limpar", kind="ghost", icon="✕",
           command=_limpar_display).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(hdr["actions"], text="Abrir Display", kind="primary", icon="📺",
           command=_abrir_display).pack(side=tk.LEFT)

    # ── barra de seleção de monitor ──────────────────────────────────
    from ..modals.apresentacao_display import enumerate_monitors as _enum_monitors

    _mon_idx      = [0]     # índice do monitor selecionado
    _mon_var      = tk.StringVar(value="Monitor 1")
    _mon_list     = []      # cache da última enumeração
    _mon_init_ok  = [False] # True após a primeira auto-seleção do monitor

    monitor_bar = tk.Frame(outer, bg=COLORS["bg_card"],
                           highlightbackground=COLORS["divider"],
                           highlightthickness=1)
    monitor_bar.pack(fill=tk.X, pady=(0, SPACING[3]))

    tk.Label(monitor_bar, text="🖥  Monitor:",
             font=FONTS["small"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(
                 side=tk.LEFT, padx=(SPACING[3], SPACING[2]), pady=SPACING[2])

    _mon_menu = tk.OptionMenu(monitor_bar, _mon_var, "Monitor 1")
    _mon_menu.configure(
        font=FONTS["small"],
        bg=COLORS["input_bg"], fg=COLORS["text"],
        activebackground=COLORS["accent"],
        activeforeground=COLORS["bg_dark"],
        highlightthickness=0, relief=tk.FLAT,
        anchor=tk.W,
        padx=SPACING[2],
    )
    _mon_menu["menu"].configure(
        bg=COLORS["bg_card"], fg=COLORS["text"],
        activebackground=COLORS["accent"],
        activeforeground=COLORS["bg_dark"],
        font=FONTS["small"],
    )
    _mon_menu.pack(side=tk.LEFT, padx=(0, SPACING[3]), pady=SPACING[2])

    def _mon_short_label(i: int, m: dict) -> str:
        return f"Monitor {i + 1}  ({m['w']}×{m['h']})"

    def _refresh_monitors():
        _mon_list.clear()
        _mon_list.extend(_enum_monitors())
        menu = _mon_menu["menu"]
        menu.delete(0, "end")
        for i, m in enumerate(_mon_list):
            prim      = "  ★ principal" if m.get("primary") else ""
            full_lbl  = f"{_mon_short_label(i, m)}{prim}"
            short_lbl = _mon_short_label(i, m)
            menu.add_command(
                label=full_lbl,
                command=lambda s=short_lbl, i=i: (
                    _mon_var.set(s),
                    _mon_idx.__setitem__(0, i),
                ),
            )
        if _mon_list:
            # Na primeira carga: seleciona automaticamente o segundo monitor
            # se houver mais de um (padrão de uso projetor/TV)
            if not _mon_init_ok[0]:
                _mon_init_ok[0] = True
                if len(_mon_list) > 1:
                    _mon_idx[0] = 1
            i0 = min(_mon_idx[0], len(_mon_list) - 1)
            _mon_var.set(_mon_short_label(i0, _mon_list[i0]))
        multi = len(_mon_list) > 1
        _btn_trocar.configure(
            state=tk.NORMAL if multi else tk.DISABLED,
            fg=COLORS["text"] if multi else COLORS["text_muted"],
        )

    def _on_fs_change(is_fs: bool):
        """Callback chamado pelo DisplayWindow quando o estado fullscreen muda."""
        if is_fs:
            _btn_fs.configure(text="⬜  Modo Janela",
                              bg=COLORS["bg_card"], fg=COLORS["text"])
        else:
            _btn_fs.configure(text="⛶  Tela Cheia",
                              bg=COLORS["bg_card"], fg=COLORS["text"])

    def _register_fs_callback():
        dw = get_display()
        if dw and dw.exists():
            dw.set_fs_callback(_on_fs_change)

    def _tela_cheia_toggle():
        dw = get_display()
        # Se já está em fullscreen → sai
        if dw and dw.exists() and dw._fullscreen:
            dw._exit_fullscreen()
            return
        # Garante que o display existe
        if not dw or not dw.exists():
            _abrir_display()
            dw = get_display()
            if not dw:
                return
        _register_fs_callback()
        _refresh_monitors()
        # Só envia conteúdo da aba Mídia se ela estiver ativa.
        # Em Som ou Versículo, o display já tem o conteúdo correto.
        if _active_tab[0] == "midia" and state.get("midia_tipo_sel"):
            _exibir_midia()
        dw.go_fullscreen(_mon_idx[0])

    def _trocar_monitor():
        dw = get_display()
        if not dw or not dw.exists():
            return
        dw.cycle_monitor()
        _mon_idx[0] = dw._current_monitor
        _refresh_monitors()

    _btn_fs = button(monitor_bar, text="⛶  Tela Cheia", kind="ghost",
                     command=_tela_cheia_toggle)
    _btn_fs.pack(side=tk.LEFT, padx=(0, SPACING[2]), pady=SPACING[2])

    _btn_trocar = button(monitor_bar, text="Trocar Monitor", kind="ghost", icon="⇄",
                         command=_trocar_monitor)
    _btn_trocar.pack(side=tk.LEFT, pady=SPACING[2])

    tk.Label(monitor_bar,
             text="F11 = tela cheia  ·  Esc ou F11 novamente para sair",
             font=FONTS["tiny"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(
                 side=tk.RIGHT, padx=SPACING[3])

    _refresh_monitors()   # preenche a lista na abertura da página

    # ── tab bar ──────────────────────────────────────────────────────
    _active_tab = ["som"]

    tab_bar = tk.Frame(outer, bg=COLORS["bg_card"],
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
    tab_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    tab_som_frame   = tk.Frame(outer, bg=COLORS["bg_dark"])
    tab_verse_frame = tk.Frame(outer, bg=COLORS["bg_dark"])
    tab_midia_frame = tk.Frame(outer, bg=COLORS["bg_dark"])

    def _switch_tab(name):
        _active_tab[0] = name
        tab_som_frame.pack_forget()
        tab_verse_frame.pack_forget()
        tab_midia_frame.pack_forget()
        for btn in (_btn_som, _btn_verse, _btn_midia):
            btn.configure(bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        if name == "som":
            tab_som_frame.pack(fill=tk.BOTH, expand=True)
            _btn_som.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
        elif name == "versiculo":
            tab_verse_frame.pack(fill=tk.BOTH, expand=True)
            _btn_verse.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
        else:
            tab_midia_frame.pack(fill=tk.BOTH, expand=True)
            _btn_midia.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])

    def _tab_btn(text):
        return tk.Button(
            tab_bar, text=text,
            font=FONTS["body_strong"],
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg_dark"],
            relief=tk.FLAT, bd=0,
            padx=SPACING[5], pady=SPACING[3],
            cursor="hand2",
        )

    _btn_som   = _tab_btn("🎵  Som")
    _btn_verse = _tab_btn("📖  Versículo")
    _btn_midia = _tab_btn("📷  Mídia")
    _btn_som.configure(command=lambda: _switch_tab("som"))
    _btn_verse.configure(command=lambda: _switch_tab("versiculo"))
    _btn_midia.configure(command=lambda: _switch_tab("midia"))
    _btn_som.pack(side=tk.LEFT)
    _btn_verse.pack(side=tk.LEFT)
    _btn_midia.pack(side=tk.LEFT)

    # ════════════════════════════════════════════════════════════════
    # ABA SOM — lista de músicas + controle de slides
    # ════════════════════════════════════════════════════════════════
    tab_som_frame.columnconfigure(0, weight=2, minsize=280)
    tab_som_frame.columnconfigure(1, weight=0, minsize=1)
    tab_som_frame.columnconfigure(2, weight=3)
    tab_som_frame.rowconfigure(0, weight=1)

    left = tk.Frame(tab_som_frame, bg=COLORS["bg_dark"])
    left.grid(row=0, column=0, sticky="nsew")

    tk.Frame(tab_som_frame, bg=COLORS["divider"],
             width=1).grid(row=0, column=1, sticky="ns", padx=SPACING[4])

    right_som = tk.Frame(tab_som_frame, bg=COLORS["bg_dark"])
    right_som.grid(row=0, column=2, sticky="nsew")

    # — lista de músicas —
    def _reload_list(busca=""):
        state["musicas"] = listar_musicas(busca)
        _render_list()

    lhdr = tk.Frame(left, bg=COLORS["bg_dark"])
    lhdr.pack(fill=tk.X, pady=(0, SPACING[3]))

    tk.Label(lhdr, text="MÚSICAS",
             font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    button(lhdr, text="+ Nova", kind="primary",
           command=lambda: callbacks.get("new_music", lambda: None)()
           ).pack(side=tk.RIGHT)

    search_box = tk.Frame(left, bg=COLORS["input_bg"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    search_box.pack(fill=tk.X, pady=(0, SPACING[3]))

    tk.Label(search_box, text="🔍",
             font=(FONTS["body"][0], 11),
             bg=COLORS["input_bg"], fg=COLORS["text_muted"],
             padx=SPACING[2]).pack(side=tk.LEFT)

    _search_var = tk.StringVar()
    tk.Entry(search_box, textvariable=_search_var,
             font=FONTS["body"],
             bg=COLORS["input_bg"], fg=COLORS["text"],
             insertbackground=COLORS["text"],
             relief=tk.FLAT, bd=0,
             ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7,
                    padx=(0, SPACING[2]))

    def _on_search(*_):
        state["busca"] = _search_var.get()
        _reload_list(state["busca"])

    _search_var.trace_add("write", _on_search)

    list_outer = tk.Frame(left, bg=COLORS["bg_dark"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    list_outer.pack(fill=tk.BOTH, expand=True)

    _list_canvas = tk.Canvas(list_outer, bg=COLORS["bg_dark"],
                             highlightthickness=0, bd=0)
    _list_scroll = tk.Scrollbar(list_outer, orient=tk.VERTICAL,
                                command=_list_canvas.yview)
    _list_canvas.configure(yscrollcommand=_list_scroll.set)
    _list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    _list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    _list_frame  = tk.Frame(_list_canvas, bg=COLORS["bg_dark"])
    _list_window = _list_canvas.create_window((0, 0), window=_list_frame, anchor="nw")

    _list_frame.bind("<Configure>",
                     lambda _e: _list_canvas.configure(scrollregion=_list_canvas.bbox("all")))
    _list_canvas.bind("<Configure>",
                      lambda e: _list_canvas.itemconfigure(_list_window, width=e.width))
    _list_canvas.bind("<MouseWheel>",
                      lambda e: _list_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _render_list():
        for w in _list_frame.winfo_children():
            w.destroy()
        musicas = state["musicas"]
        if not musicas:
            empty_state(_list_frame,
                        icon="🎵",
                        title="Nenhuma música",
                        body="Clique em '+ Nova' para cadastrar.").pack(
                            fill=tk.BOTH, expand=True, pady=SPACING[8])
            return
        for m in musicas:
            _make_song_row(_list_frame, m)

    def _make_song_row(parent, m):
        ativa    = (state["selecionada"] and state["selecionada"]["id"] == m["id"])
        bg       = COLORS["sidebar_active"] if ativa else COLORS["bg_dark"]
        bg_hover = COLORS["sidebar_hover"]

        row = tk.Frame(parent, bg=bg, cursor="hand2")
        row.pack(fill=tk.X)

        tk.Frame(row, bg=COLORS["accent"] if ativa else bg,
                 width=3).pack(side=tk.LEFT, fill=tk.Y)

        inner = tk.Frame(row, bg=bg)
        inner.pack(side=tk.LEFT, fill=tk.X, expand=True,
                   padx=SPACING[3], pady=SPACING[2])

        tk.Label(inner, text=m["titulo"], font=FONTS["body_strong"],
                 bg=bg, fg=COLORS["text"], anchor=tk.W).pack(fill=tk.X)
        if m.get("artista"):
            tk.Label(inner, text=m["artista"], font=FONTS["small"],
                     bg=bg, fg=COLORS["text_muted"], anchor=tk.W).pack(fill=tk.X)

        tk.Frame(parent, bg=COLORS["divider_soft"], height=1).pack(fill=tk.X)

        def _select(_e=None, mid=m["id"]):
            _load_music(mid)

        def _enter(_e, r=row, a=ativa):
            if not a:
                _set_bg(r, bg_hover)

        def _leave(_e, r=row, a=ativa):
            if not a:
                _set_bg(r, bg)

        for w in [row, inner] + list(inner.winfo_children()):
            w.bind("<Button-1>", _select)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)

    def _set_bg(widget, color):
        try:
            widget.configure(bg=color)
        except Exception:
            pass
        for child in widget.winfo_children():
            _set_bg(child, color)

    # — controle de slides —
    slides_section = tk.Frame(right_som, bg=COLORS["bg_dark"])
    slides_section.pack(fill=tk.X, pady=(0, SPACING[5]))

    tk.Label(slides_section, text="SLIDE ATUAL",
             font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(
                 anchor=tk.W, pady=(0, SPACING[2]))

    _music_info_var = tk.StringVar(value="Nenhuma música selecionada")
    tk.Label(slides_section, textvariable=_music_info_var,
             font=FONTS["body_strong"],
             bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(anchor=tk.W)

    nav_row = tk.Frame(slides_section, bg=COLORS["bg_dark"])
    nav_row.pack(fill=tk.X, pady=(SPACING[3], SPACING[3]))

    _prev_btn = button(nav_row, text="← Anterior", kind="ghost",
                       command=lambda: _nav(-1))
    _prev_btn.pack(side=tk.LEFT, padx=(0, SPACING[2]))

    _page_var = tk.StringVar(value="—")
    tk.Label(nav_row, textvariable=_page_var,
             font=FONTS["body_strong"],
             bg=COLORS["bg_dark"], fg=COLORS["text"],
             width=12, anchor=tk.CENTER).pack(side=tk.LEFT)

    _next_btn = button(nav_row, text="Próximo →", kind="ghost",
                       command=lambda: _nav(+1))
    _next_btn.pack(side=tk.LEFT, padx=(SPACING[2], 0))

    _preview_frame = tk.Frame(slides_section, bg=COLORS["bg_card"],
                              highlightbackground=COLORS["divider"],
                              highlightthickness=1)
    _preview_frame.pack(fill=tk.X, pady=(0, SPACING[3]))

    _preview_text = tk.Text(
        _preview_frame,
        font=FONTS["body"],
        bg=COLORS["bg_card"], fg=COLORS["text"],
        relief=tk.FLAT, bd=0,
        wrap=tk.WORD, height=8,
        padx=SPACING[3], pady=SPACING[2],
        state=tk.DISABLED,
    )
    _preview_text.pack(fill=tk.X)

    action_row = tk.Frame(slides_section, bg=COLORS["bg_dark"])
    action_row.pack(fill=tk.X, pady=(0, SPACING[2]))

    _exibir_btn = button(action_row, text="Exibir Slide no Display",
                         kind="primary", icon="📺",
                         command=lambda: _exibir_slide())
    _exibir_btn.pack(side=tk.LEFT, padx=(0, SPACING[2]))

    _edit_btn = button(action_row, text="Editar", kind="ghost",
                       command=lambda: callbacks.get("edit_music", lambda _: None)(
                           state["selecionada"]["id"] if state["selecionada"] else None))
    _edit_btn.pack(side=tk.LEFT, padx=(0, SPACING[2]))

    _del_btn = button(action_row, text="Excluir", kind="ghost",
                      command=lambda: callbacks.get("delete_music", lambda _: None)(
                          state["selecionada"] if state["selecionada"] else None))
    _del_btn.pack(side=tk.LEFT)

    # — seletor de slides (pular para slide específico) —
    slides_sel_hdr = tk.Frame(right_som, bg=COLORS["bg_dark"])
    slides_sel_hdr.pack(fill=tk.X, pady=(SPACING[4], SPACING[2]))

    tk.Label(slides_sel_hdr, text="SLIDES",
             font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    tk.Label(slides_sel_hdr, text="clique para navegar  ·  duplo-clique para exibir",
             font=FONTS["tiny"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT,
                                                                   padx=(SPACING[3], 0))

    slides_lb_outer = tk.Frame(right_som, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["divider"],
                               highlightthickness=1)
    slides_lb_outer.pack(fill=tk.BOTH, expand=True)

    _slides_sb = tk.Scrollbar(slides_lb_outer, orient=tk.VERTICAL)
    _slides_lb = tk.Listbox(
        slides_lb_outer,
        font=FONTS["body"],
        bg=COLORS["bg_card"], fg=COLORS["text"],
        selectbackground=COLORS["accent"], selectforeground=COLORS["bg_dark"],
        activestyle="none",
        relief=tk.FLAT, bd=0,
        yscrollcommand=_slides_sb.set,
    )
    _slides_sb.configure(command=_slides_lb.yview)
    _slides_sb.pack(side=tk.RIGHT, fill=tk.Y)
    _slides_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=SPACING[1])

    def _render_slides_lb():
        _slides_lb.delete(0, tk.END)
        for i, page in enumerate(state["paginas"]):
            first = page[0] if page else ""
            _slides_lb.insert(tk.END, f"  {i + 1:>2}.  {first}")

    def _on_slide_lb_select(_e=None):
        sel = _slides_lb.curselection()
        if not sel:
            return
        state["pagina_idx"] = sel[0]
        _update_slide_view()

    def _on_slide_lb_doubleclick(_e=None):
        _on_slide_lb_select()
        _exibir_slide()

    _slides_lb.bind("<<ListboxSelect>>", _on_slide_lb_select)
    _slides_lb.bind("<Double-Button-1>", _on_slide_lb_doubleclick)
    _slides_lb.bind("<MouseWheel>",
                    lambda e: _slides_lb.yview_scroll(-1 * (e.delta // 120), "units"))

    # ════════════════════════════════════════════════════════════════
    # ABA VERSÍCULO — seletor (esq.) + resultado (dir.)
    # ════════════════════════════════════════════════════════════════
    from core.verse import (BIBLE_TRANSLATIONS, LIVROS_BIBLIA,
                            get_bible_id, set_bible_id)
    from ..ui.components import select as ui_select

    tab_verse_frame.columnconfigure(0, weight=2, minsize=320)
    tab_verse_frame.columnconfigure(1, weight=3)
    tab_verse_frame.rowconfigure(0, weight=1)

    v_left  = tk.Frame(tab_verse_frame, bg=COLORS["bg_dark"])
    v_left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING[6]))

    v_right = tk.Frame(tab_verse_frame, bg=COLORS["bg_dark"])
    v_right.grid(row=0, column=1, sticky="nsew")

    # cabeçalho da aba
    tk.Label(v_left, text="VERSÍCULO AO VIVO",
             font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(
                 anchor=tk.W, pady=(0, SPACING[4]))

    # tradução
    trans_row = tk.Frame(v_left, bg=COLORS["bg_dark"])
    trans_row.pack(fill=tk.X, pady=(0, SPACING[3]))

    tk.Label(trans_row, text="Tradução",
             font=FONTS["tiny_bold"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor=tk.W)

    _trans_options = {t["label"]: t["id"] for t in BIBLE_TRANSLATIONS}
    _cur_id        = get_bible_id()
    _cur_label     = next((t["label"] for t in BIBLE_TRANSLATIONS
                           if t["id"] == _cur_id), BIBLE_TRANSLATIONS[0]["label"])
    ui_select(trans_row,
              value=_cur_label,
              options=list(_trans_options.keys()),
              on_change=lambda lbl: set_bible_id(_trans_options[lbl]),
              ).pack(fill=tk.X, pady=(SPACING[1], 0))

    # campo livro com autocomplete
    livro_col = tk.Frame(v_left, bg=COLORS["bg_dark"])
    livro_col.pack(fill=tk.X, pady=(0, SPACING[2]))

    tk.Label(livro_col, text="Livro",
             font=FONTS["tiny_bold"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor=tk.W)

    livro_box = tk.Frame(livro_col, bg=COLORS["input_bg"],
                         highlightbackground=COLORS["divider"],
                         highlightcolor=COLORS["accent"],
                         highlightthickness=1)
    livro_box.pack(fill=tk.X)

    _livro_var   = tk.StringVar()
    _livro_entry = tk.Entry(
        livro_box, textvariable=_livro_var,
        font=FONTS["body"],
        bg=COLORS["input_bg"], fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief=tk.FLAT, bd=0,
    )
    _livro_entry.pack(fill=tk.X, expand=True, ipady=7, padx=SPACING[3])

    # dropdown flutuante — Toplevel sem decoração, flutua sobre tudo sem clipping
    _drop_top = tk.Toplevel(outer)
    _drop_top.overrideredirect(True)
    _drop_top.configure(bg=COLORS["accent"])   # 1 px de borda via padding
    _drop_top.withdraw()
    _drop_top.transient(outer.winfo_toplevel())
    # destrói o Toplevel apenas quando o próprio outer for destruído (não filhos)
    outer.bind("<Destroy>", lambda e: _drop_top.destroy()
               if e.widget is outer and _drop_top.winfo_exists() else None)

    _drop_inner = tk.Frame(_drop_top, bg=COLORS["bg_card"])
    _drop_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    _listbox = tk.Listbox(
        _drop_inner,
        font=FONTS["body"],
        bg=COLORS["bg_card"], fg=COLORS["text"],
        selectbackground=COLORS["accent"], selectforeground=COLORS["bg_dark"],
        activestyle="none",
        relief=tk.FLAT, bd=0,
        height=6,
    )
    _listbox.pack(fill=tk.BOTH, expand=True)
    _drop_visible = [False]

    def _nomes_livros():
        return [l["nome"] for l in LIVROS_BIBLIA]

    def _show_drop(nomes):
        _listbox.delete(0, tk.END)
        for n in nomes:
            _listbox.insert(tk.END, n)
        outer.update_idletasks()
        x = livro_box.winfo_rootx()
        y = livro_box.winfo_rooty() + livro_box.winfo_height()
        w = max(livro_box.winfo_width(), 1)
        # altura: até 6 itens, ~24px cada + 2px de borda
        h = min(len(nomes), 6) * 24 + 2
        _drop_top.geometry(f"{w}x{h}+{x}+{y}")
        _drop_top.deiconify()
        _drop_top.lift()
        _drop_visible[0] = True

    def _hide_drop():
        if _drop_visible[0]:
            _drop_top.withdraw()
            _drop_visible[0] = False

    def _filter_livros(*_):
        txt     = _livro_var.get().strip().lower()
        matches = [n for n in _nomes_livros() if txt in n.lower()]
        if matches:
            _show_drop(matches)
        else:
            _hide_drop()

    def _livro_focus_in(_e):
        if not _livro_var.get().strip():
            _show_drop(_nomes_livros())
        else:
            _filter_livros()

    def _select_livro(nome: str):
        _livro_var.set(nome)
        livro = next((l for l in LIVROS_BIBLIA if l["nome"] == nome), None)
        if livro:
            state["livro_sel"] = livro
            state["cap_sel"]   = 1
            state["ver_sel"]   = 1
            _cap_var.set("1")
            _ver_var.set("1")
            _cap_entry.configure(
                validate="key",
                validatecommand=(_cap_vcmd, "%P", str(livro["caps"])),
            )
        _hide_drop()
        _cap_entry.focus_set()

    def _on_listbox_select(_e=None):
        sel = _listbox.curselection()
        if sel:
            _select_livro(_listbox.get(sel[0]))

    _livro_var.trace_add("write", _filter_livros)
    _livro_entry.bind("<FocusIn>",  _livro_focus_in)
    _livro_entry.bind("<FocusOut>", lambda _e: outer.after(150, _hide_drop))
    _livro_entry.bind("<Down>",
                      lambda _e: _listbox.focus_set() or _listbox.selection_set(0))
    _listbox.bind("<<ListboxSelect>>", _on_listbox_select)
    _listbox.bind("<Return>",          _on_listbox_select)
    _listbox.bind("<FocusOut>",        lambda _e: outer.after(150, _hide_drop))

    # cap / ver / nav / buscar
    cv_row = tk.Frame(v_left, bg=COLORS["bg_dark"])
    cv_row.pack(fill=tk.X, pady=(0, SPACING[3]))

    def _entry_num(parent, var, w=5):
        box = tk.Frame(parent, bg=COLORS["input_bg"],
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
        ent = tk.Entry(box, textvariable=var,
                       font=FONTS["body"],
                       bg=COLORS["input_bg"], fg=COLORS["text"],
                       insertbackground=COLORS["text"],
                       relief=tk.FLAT, bd=0, width=w,
                       justify=tk.CENTER)
        ent.pack(ipady=7, padx=SPACING[2])
        return box, ent

    tk.Label(cv_row, text="Cap.",
             font=FONTS["tiny_bold"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    _cap_var = tk.StringVar(value="1")
    cap_box, _cap_entry = _entry_num(cv_row, _cap_var)
    cap_box.pack(side=tk.LEFT, padx=(SPACING[1], SPACING[2]))

    tk.Label(cv_row, text="Ver.",
             font=FONTS["tiny_bold"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    _ver_var = tk.StringVar(value="1")
    ver_box, _ver_entry = _entry_num(cv_row, _ver_var)
    ver_box.pack(side=tk.LEFT, padx=(SPACING[1], SPACING[3]))

    def _validate_cap(new_val, max_str):
        if new_val == "":
            return True
        try:
            v = int(new_val)
            return 1 <= v <= int(max_str)
        except ValueError:
            return False

    _cap_vcmd = v_left.register(_validate_cap)
    _cap_entry.configure(validate="key",
                         validatecommand=(_cap_vcmd, "%P", "150"))

    def _validate_ver(new_val):
        if new_val == "":
            return True
        try:
            return int(new_val) >= 1
        except ValueError:
            return False

    _ver_vcmd = v_left.register(_validate_ver)
    _ver_entry.configure(validate="key", validatecommand=(_ver_vcmd, "%P"))

    def _btn_nav(parent, txt, delta):
        return tk.Button(
            parent, text=txt,
            font=FONTS["body_strong"],
            bg=COLORS["input_bg"], fg=COLORS["text"],
            activebackground=COLORS["sidebar_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT, bd=0,
            padx=SPACING[3], pady=6,
            cursor="hand2",
            command=lambda: _nav_ver(delta),
        )

    _btn_nav(cv_row, "‹", -1).pack(side=tk.LEFT, padx=(0, 2))
    _btn_nav(cv_row, "›", +1).pack(side=tk.LEFT, padx=(0, SPACING[3]))

    button(cv_row, text="Buscar", kind="primary",
           command=lambda: _buscar_versiculo()).pack(side=tk.LEFT)

    _cap_entry.bind("<Return>", lambda _e: _ver_entry.focus_set())
    _ver_entry.bind("<Return>", lambda _e: _buscar_versiculo())

    # resultado (coluna direita da aba versículo)
    tk.Label(v_right, text="RESULTADO",
             font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(
                 anchor=tk.W, pady=(0, SPACING[3]))

    _verse_frame = tk.Frame(v_right, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["divider"],
                            highlightthickness=1)
    _verse_frame.pack(fill=tk.X, pady=(0, SPACING[2]))

    _verse_text_var = tk.StringVar(value="")
    _verse_ref_var  = tk.StringVar(value="")
    _verse_err_var  = tk.StringVar(value="")

    tk.Label(_verse_frame, textvariable=_verse_text_var,
             font=FONTS["body_italic"],
             bg=COLORS["bg_card"], fg=COLORS["text"],
             wraplength=500, justify=tk.LEFT, anchor=tk.W,
             ).pack(fill=tk.X, padx=SPACING[4], pady=(SPACING[3], SPACING[1]))

    tk.Label(_verse_frame, textvariable=_verse_ref_var,
             font=FONTS["small_bold"],
             bg=COLORS["bg_card"], fg=COLORS["verse_gold"],
             anchor=tk.E,
             ).pack(fill=tk.X, padx=SPACING[4], pady=(0, SPACING[3]))

    tk.Label(v_right, textvariable=_verse_err_var,
             font=FONTS["small"],
             bg=COLORS["bg_dark"], fg=COLORS["danger"],
             wraplength=500, justify=tk.LEFT,
             ).pack(anchor=tk.W, pady=(0, SPACING[3]))

    _exibir_verse_btn = button(v_right, text="Exibir Versículo no Display",
                               kind="primary", icon="📺",
                               command=lambda: _exibir_versiculo())
    _exibir_verse_btn.pack(anchor=tk.W)
    _exibir_verse_btn.configure(state=tk.DISABLED,
                                bg=COLORS["divider"], fg=COLORS["text_muted"])

    # ════════════════════════════════════════════════════════════════
    # ABA MÍDIA — imagens e vídeos locais
    # Layout: listas de imagens | vídeos lado a lado (cima)
    #         preview + controles abaixo (largura total)
    # ════════════════════════════════════════════════════════════════
    import os
    from tkinter import filedialog

    _EXTS_IMG = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.webp", "*.tiff")
    _EXTS_VID = ("*.mp4", "*.avi", "*.mov", "*.mkv", "*.wmv", "*.flv", "*.webm")
    try:
        import vlc as _vlc_check  # noqa: F401
        _VIDEO_OK = True
    except Exception:
        _VIDEO_OK = False

    # ── Grid: linha 0 = listas, linha 1 = preview+controles ────────────
    tab_midia_frame.rowconfigure(0, weight=1)
    tab_midia_frame.rowconfigure(1, weight=0)
    tab_midia_frame.columnconfigure(0, weight=1)

    lists_row = tk.Frame(tab_midia_frame, bg=COLORS["bg_dark"])
    lists_row.grid(row=0, column=0, sticky="nsew")
    lists_row.columnconfigure(0, weight=1)
    lists_row.columnconfigure(1, weight=0)
    lists_row.columnconfigure(2, weight=1)
    lists_row.rowconfigure(0, weight=1)

    # ── Coluna IMAGENS (esquerda) ────────────────────────────────────
    img_col = tk.Frame(lists_row, bg=COLORS["bg_dark"])
    img_col.grid(row=0, column=0, sticky="nsew")
    img_col.rowconfigure(1, weight=1)
    img_col.columnconfigure(0, weight=1)

    img_hdr = tk.Frame(img_col, bg=COLORS["bg_dark"])
    img_hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING[3]))

    tk.Label(img_hdr, text="IMAGENS", font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    def _adicionar_imagem():
        paths = filedialog.askopenfilenames(
            title="Selecionar imagens",
            filetypes=[("Imagens", " ".join(_EXTS_IMG)), ("Todos", "*.*")],
        )
        for p in paths:
            if p:
                state["midia_imagens"].append({"path": p, "nome": os.path.basename(p)})
        _render_img_lista()

    button(img_hdr, text="+ Imagem", kind="primary",
           command=_adicionar_imagem).pack(side=tk.RIGHT)

    img_list_outer = tk.Frame(img_col, bg=COLORS["bg_dark"],
                               highlightbackground=COLORS["divider"],
                               highlightthickness=1)
    img_list_outer.grid(row=1, column=0, sticky="nsew")

    _img_canvas = tk.Canvas(img_list_outer, bg=COLORS["bg_dark"],
                            highlightthickness=0, bd=0)
    _img_scroll = tk.Scrollbar(img_list_outer, orient=tk.VERTICAL,
                               command=_img_canvas.yview)
    _img_canvas.configure(yscrollcommand=_img_scroll.set)
    _img_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    _img_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    _img_frame  = tk.Frame(_img_canvas, bg=COLORS["bg_dark"])
    _img_wnd    = _img_canvas.create_window((0, 0), window=_img_frame, anchor="nw")
    _img_frame.bind("<Configure>",
                    lambda _e: _img_canvas.configure(scrollregion=_img_canvas.bbox("all")))
    _img_canvas.bind("<Configure>",
                     lambda e: _img_canvas.itemconfigure(_img_wnd, width=e.width))
    _img_canvas.bind("<MouseWheel>",
                     lambda e: _img_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    # ── Divider ──────────────────────────────────────────────────────
    tk.Frame(lists_row, bg=COLORS["divider"], width=1).grid(
        row=0, column=1, sticky="ns", padx=SPACING[3])

    # ── Coluna VÍDEOS (direita) ──────────────────────────────────────
    vid_col = tk.Frame(lists_row, bg=COLORS["bg_dark"])
    vid_col.grid(row=0, column=2, sticky="nsew")
    vid_col.rowconfigure(1, weight=1)
    vid_col.columnconfigure(0, weight=1)

    vid_hdr = tk.Frame(vid_col, bg=COLORS["bg_dark"])
    vid_hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING[3]))

    tk.Label(vid_hdr, text="VÍDEOS", font=FONTS["section"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

    def _adicionar_video():
        paths = filedialog.askopenfilenames(
            title="Selecionar vídeos",
            filetypes=[("Vídeos", " ".join(_EXTS_VID)), ("Todos", "*.*")],
        )
        for p in paths:
            if p:
                state["midia_videos"].append({"path": p, "nome": os.path.basename(p)})
        _render_vid_lista()

    if _VIDEO_OK:
        button(vid_hdr, text="+ Vídeo", kind="primary",
               command=_adicionar_video).pack(side=tk.RIGHT)
    else:
        tk.Button(vid_hdr, text="+ Vídeo", font=FONTS["body_strong"],
                  bg=COLORS["divider"], fg=COLORS["text_muted"],
                  relief=tk.FLAT, bd=0, state=tk.DISABLED,
                  padx=SPACING[3], pady=SPACING[1]).pack(side=tk.RIGHT)

    vid_list_outer = tk.Frame(vid_col, bg=COLORS["bg_dark"],
                               highlightbackground=COLORS["divider"],
                               highlightthickness=1)
    vid_list_outer.grid(row=1, column=0, sticky="nsew")

    _vid_canvas = tk.Canvas(vid_list_outer, bg=COLORS["bg_dark"],
                            highlightthickness=0, bd=0)
    _vid_scroll = tk.Scrollbar(vid_list_outer, orient=tk.VERTICAL,
                               command=_vid_canvas.yview)
    _vid_canvas.configure(yscrollcommand=_vid_scroll.set)
    _vid_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    _vid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    _vid_frame  = tk.Frame(_vid_canvas, bg=COLORS["bg_dark"])
    _vid_wnd    = _vid_canvas.create_window((0, 0), window=_vid_frame, anchor="nw")
    _vid_frame.bind("<Configure>",
                    lambda _e: _vid_canvas.configure(scrollregion=_vid_canvas.bbox("all")))
    _vid_canvas.bind("<Configure>",
                     lambda e: _vid_canvas.itemconfigure(_vid_wnd, width=e.width))
    _vid_canvas.bind("<MouseWheel>",
                     lambda e: _vid_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    # ── Linha inferior: preview 16:9 + controles ────────────────────
    bottom_row = tk.Frame(tab_midia_frame, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["divider"],
                          highlightthickness=1)
    bottom_row.grid(row=1, column=0, sticky="ew", pady=(SPACING[3], 0))

    _m_preview_canvas = tk.Canvas(
        bottom_row, bg="#0f0f0f",
        highlightbackground=COLORS["divider"], highlightthickness=1,
        width=284, height=160,
    )
    _m_preview_canvas.pack(side=tk.LEFT, padx=SPACING[3], pady=SPACING[3])
    _m_preview_ref = [None]

    ctrl_panel = tk.Frame(bottom_row, bg=COLORS["bg_card"])
    ctrl_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                    padx=(0, SPACING[3]), pady=SPACING[3])

    _m_info_var = tk.StringVar(value="Nenhum arquivo selecionado")
    tk.Label(ctrl_panel, textvariable=_m_info_var,
             font=FONTS["body_strong"],
             bg=COLORS["bg_card"], fg=COLORS["text"],
             anchor=tk.W).pack(fill=tk.X, pady=(0, SPACING[2]))

    # Navegação + Exibir
    nav_ctrl = tk.Frame(ctrl_panel, bg=COLORS["bg_card"])
    nav_ctrl.pack(fill=tk.X, pady=(0, SPACING[2]))

    _m_prev_btn = button(nav_ctrl, text="← Anterior", kind="ghost",
                          command=lambda: _nav_midia(-1))
    _m_prev_btn.pack(side=tk.LEFT, padx=(0, SPACING[2]))

    _m_page_var = tk.StringVar(value="—")
    tk.Label(nav_ctrl, textvariable=_m_page_var,
             font=FONTS["body_strong"],
             bg=COLORS["bg_card"], fg=COLORS["text"],
             width=8, anchor=tk.CENTER).pack(side=tk.LEFT)

    _m_next_btn = button(nav_ctrl, text="Próximo →", kind="ghost",
                          command=lambda: _nav_midia(+1))
    _m_next_btn.pack(side=tk.LEFT, padx=(SPACING[2], SPACING[4]))

    _m_exibir_btn = button(nav_ctrl, text="Exibir no Display",
                            kind="primary", icon="📺",
                            command=lambda: _exibir_midia())
    _m_exibir_btn.pack(side=tk.LEFT)

    # ── Controles de vídeo (oculto quando imagem está selecionada) ──
    _vid_ctrl_frame = tk.Frame(ctrl_panel, bg=COLORS["bg_card"])

    _seek_dragging = [False]
    _seek_var    = tk.IntVar(value=0)
    _time_var    = tk.StringVar(value="0:00 / 0:00")
    _vol_var     = tk.IntVar(value=100)
    _vol_pct_var = tk.StringVar(value="100%")

    # — play / parar —
    pb_row = tk.Frame(_vid_ctrl_frame, bg=COLORS["bg_card"])
    pb_row.pack(fill=tk.X, pady=(SPACING[2], 0))

    _play_btn = button(pb_row, text="▶  Reproduzir", kind="primary",
                       command=lambda: _toggle_play())
    _play_btn.pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(pb_row, text="⏹  Parar", kind="ghost",
           command=lambda: _stop_video_ctrl()).pack(side=tk.LEFT)

    # — seek —
    seek_row = tk.Frame(_vid_ctrl_frame, bg=COLORS["bg_card"])
    seek_row.pack(fill=tk.X, pady=(SPACING[2], 0))

    tk.Label(seek_row, text="⏱", font=FONTS["body"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(
                 side=tk.LEFT, padx=(0, SPACING[1]))

    _seek_slider = tk.Scale(
        seek_row, from_=0, to=1000, orient=tk.HORIZONTAL,
        variable=_seek_var, showvalue=0,
        bg=COLORS["bg_card"], fg=COLORS["text"],
        troughcolor=COLORS["divider"],
        activebackground=COLORS["accent"],
        highlightthickness=0, sliderlength=12, bd=0,
    )
    _seek_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

    tk.Label(seek_row, textvariable=_time_var,
             font=FONTS["small"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"],
             width=13, anchor=tk.W).pack(side=tk.LEFT, padx=(SPACING[2], 0))

    # — volume —
    vol_row = tk.Frame(_vid_ctrl_frame, bg=COLORS["bg_card"])
    vol_row.pack(fill=tk.X, pady=(SPACING[1], 0))

    tk.Label(vol_row, text="🔊", font=FONTS["body"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(
                 side=tk.LEFT, padx=(0, SPACING[1]))

    def _on_vol_change(val):
        v = int(val)
        _vol_pct_var.set(f"{v}%")
        dw = get_display()
        if not dw or not dw.exists():
            return
        player = dw.get_player()
        if player:
            player.audio_set_volume(v)

    _vol_slider = tk.Scale(
        vol_row, from_=0, to=100, orient=tk.HORIZONTAL,
        variable=_vol_var, showvalue=0, length=160,
        bg=COLORS["bg_card"], fg=COLORS["text"],
        troughcolor=COLORS["divider"],
        activebackground=COLORS["accent"],
        highlightthickness=0, sliderlength=12, bd=0,
        command=_on_vol_change,
    )
    _vol_slider.pack(side=tk.LEFT)

    tk.Label(vol_row, textvariable=_vol_pct_var,
             font=FONTS["small"],
             bg=COLORS["bg_card"], fg=COLORS["text_muted"],
             width=5, anchor=tk.W).pack(side=tk.LEFT, padx=(SPACING[2], 0))

    # Seek: clique direto OU arrastar → posição calculada pelas coordenadas do mouse.
    # tk.Scale move apenas 1 passo por clique no trough; contornamos capturando x.
    def _seek_pos_from_event(event) -> int:
        w    = _seek_slider.winfo_width()
        half = 6  # metade do sliderlength=12
        eff  = max(1, w - 2 * half)
        x    = max(0, min(event.x - half, eff))
        return int(x / eff * 1000)

    def _on_seek_press(event):
        _seek_dragging[0] = True
        _seek_var.set(_seek_pos_from_event(event))
        return "break"  # impede Scale de mover só 1 passo

    def _on_seek_motion(event):
        if _seek_dragging[0]:
            _seek_var.set(_seek_pos_from_event(event))

    def _on_seek_release(event=None):
        _seek_dragging[0] = False
        dw = get_display()
        if not dw or not dw.exists():
            return
        player = dw.get_player()
        if player and player.get_length() > 0:
            ms = int(_seek_var.get() / 1000 * player.get_length())
            player.set_time(ms)

    _seek_slider.bind("<ButtonPress-1>",   _on_seek_press)
    _seek_slider.bind("<B1-Motion>",       _on_seek_motion)
    _seek_slider.bind("<ButtonRelease-1>", _on_seek_release)

    if not _VIDEO_OK:
        tk.Label(ctrl_panel,
                 text="⚠️  Para vídeos: pip install python-vlc  (VLC obrigatório)",
                 font=FONTS["tiny"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(
                     anchor=tk.W, pady=(SPACING[2], 0))

    # ── Render das listas ────────────────────────────────────────────

    def _make_media_row(parent, idx, item, tipo, on_select, on_remove):
        img_ativa = (tipo == "imagem" and state["midia_tipo_sel"] == "imagem"
                     and state["midia_idx_img"] == idx)
        vid_ativa = (tipo == "video"  and state["midia_tipo_sel"] == "video"
                     and state["midia_idx_vid"] == idx)
        ativa    = img_ativa or vid_ativa
        bg       = COLORS["sidebar_active"] if ativa else COLORS["bg_dark"]
        bg_hover = COLORS["sidebar_hover"]
        icone    = "🖼" if tipo == "imagem" else "🎬"

        row = tk.Frame(parent, bg=bg, cursor="hand2")
        row.pack(fill=tk.X)
        tk.Frame(row, bg=COLORS["accent"] if ativa else bg,
                 width=3).pack(side=tk.LEFT, fill=tk.Y)
        inner = tk.Frame(row, bg=bg)
        inner.pack(side=tk.LEFT, fill=tk.X, expand=True,
                   padx=SPACING[2], pady=SPACING[2])
        tk.Label(inner, text=f"{icone}  {item['nome']}",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text"], anchor=tk.W).pack(fill=tk.X)

        tk.Button(row, text="✕", font=FONTS["tiny"],
                  bg=bg, fg=COLORS["text_muted"],
                  activebackground=COLORS["danger"],
                  activeforeground="#ffffff",
                  relief=tk.FLAT, bd=0, padx=SPACING[2],
                  cursor="hand2",
                  command=lambda i=idx: on_remove(i)).pack(
                      side=tk.RIGHT, padx=SPACING[1])

        tk.Frame(parent, bg=COLORS["divider_soft"], height=1).pack(fill=tk.X)

        def _sel(_e=None, i=idx):
            on_select(i)

        def _enter(_e, r=row, a=ativa):
            if not a:
                _set_bg(r, bg_hover)

        def _leave(_e, r=row, a=ativa):
            if not a:
                _set_bg(r, bg)

        for w in [row, inner] + list(inner.winfo_children()):
            w.bind("<Button-1>", _sel)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)

    def _render_img_lista():
        for w in _img_frame.winfo_children():
            w.destroy()
        imgs = state["midia_imagens"]
        if not imgs:
            empty_state(_img_frame, icon="🖼", title="Sem imagens",
                        body="Clique em '+ Imagem'.").pack(
                            fill=tk.BOTH, expand=True, pady=SPACING[6])
        else:
            for i, it in enumerate(imgs):
                _make_media_row(_img_frame, i, it, "imagem",
                                on_select=_sel_imagem, on_remove=_rem_imagem)
        _update_midia_controls()

    def _render_vid_lista():
        for w in _vid_frame.winfo_children():
            w.destroy()
        vids = state["midia_videos"]
        if not vids:
            body_txt = ("Instale python-vlc para suporte a vídeo."
                        if not _VIDEO_OK else "Clique em '+ Vídeo'.")
            empty_state(_vid_frame, icon="🎬", title="Sem vídeos",
                        body=body_txt).pack(
                            fill=tk.BOTH, expand=True, pady=SPACING[6])
        else:
            for i, it in enumerate(vids):
                _make_media_row(_vid_frame, i, it, "video",
                                on_select=_sel_video, on_remove=_rem_video)
        _update_midia_controls()

    def _sel_imagem(idx):
        state["midia_tipo_sel"] = "imagem"
        state["midia_idx_img"]  = idx
        _render_img_lista()
        _render_vid_lista()
        _vid_ctrl_frame.pack_forget()
        _update_midia_controls()

    def _sel_video(idx):
        state["midia_tipo_sel"] = "video"
        state["midia_idx_vid"]  = idx
        _render_img_lista()
        _render_vid_lista()
        _vid_ctrl_frame.pack(fill=tk.X, pady=(SPACING[2], 0))
        _update_midia_controls()

    def _rem_imagem(idx):
        lst = state["midia_imagens"]
        if 0 <= idx < len(lst):
            lst.pop(idx)
        if state["midia_tipo_sel"] == "imagem":
            state["midia_idx_img"] = max(0, min(state["midia_idx_img"], len(lst) - 1))
            if not lst:
                state["midia_tipo_sel"] = None
        _render_img_lista()

    def _rem_video(idx):
        lst = state["midia_videos"]
        if 0 <= idx < len(lst):
            lst.pop(idx)
        if state["midia_tipo_sel"] == "video":
            state["midia_idx_vid"] = max(0, min(state["midia_idx_vid"], len(lst) - 1))
            if not lst:
                state["midia_tipo_sel"] = None
                _vid_ctrl_frame.pack_forget()
        _render_vid_lista()

    # ── Preview ──────────────────────────────────────────────────────

    def _update_midia_preview():
        c  = _m_preview_canvas
        pw = c.winfo_width()  or 284
        ph = c.winfo_height() or 160
        c.delete("all")
        _m_preview_ref[0] = None
        tipo = state["midia_tipo_sel"]

        if tipo == "imagem":
            lst = state["midia_imagens"]
            idx = state["midia_idx_img"]
            if not lst or idx >= len(lst):
                return
            try:
                from PIL import Image, ImageTk as _ITk
                img = Image.open(lst[idx]["path"]).convert("RGB")
                img.thumbnail((pw, ph), Image.LANCZOS)
                tk_img = _ITk.PhotoImage(img)
                _m_preview_ref[0] = tk_img
                c.create_image((pw - img.width) // 2,
                               (ph - img.height) // 2,
                               anchor="nw", image=tk_img)
            except Exception:
                pass

        elif tipo == "video":
            lst = state["midia_videos"]
            idx = state["midia_idx_vid"]
            if not lst or idx >= len(lst):
                return
            # Placeholder — VLC não suporta snapshot sem janela visível
            c.create_rectangle(0, 0, pw, ph, fill="#0a0a0a", outline="")
            c.create_text(pw // 2, ph // 2 - 16,
                          text="▶", font=(FONTS["body"][0], 30),
                          fill=COLORS["text_muted"])
            c.create_text(pw // 2, ph // 2 + 20,
                          text=lst[idx]["nome"],
                          font=FONTS["tiny"],
                          fill=COLORS["text_muted"],
                          width=pw - 20)

    # ── Controles gerais ─────────────────────────────────────────────

    def _update_midia_controls():
        tipo = state["midia_tipo_sel"]
        if tipo == "imagem":
            lst, idx = state["midia_imagens"], state["midia_idx_img"]
        elif tipo == "video":
            lst, idx = state["midia_videos"],  state["midia_idx_vid"]
        else:
            lst, idx = [], 0

        tem   = bool(lst)
        s_on  = tk.NORMAL if tem else tk.DISABLED
        bg_on = COLORS["accent"]
        bg_off = COLORS["divider"]

        for btn in (_m_prev_btn, _m_next_btn):
            btn.configure(
                state=s_on,
                bg=COLORS["input_bg"] if tem else COLORS["divider"],
                fg=COLORS["text"]     if tem else COLORS["text_muted"])

        _m_exibir_btn.configure(
            state=s_on,
            bg=bg_on  if tem else bg_off,
            fg=COLORS["bg_dark"] if tem else COLORS["text_muted"])

        if tem:
            _m_page_var.set(f"{idx + 1}  /  {len(lst)}")
            _m_info_var.set(lst[idx]["nome"])
        else:
            _m_page_var.set("—")
            _m_info_var.set("Nenhum arquivo selecionado")

        _update_midia_preview()

    def _nav_midia(delta: int):
        tipo = state["midia_tipo_sel"]
        if tipo == "imagem":
            lst = state["midia_imagens"]
            state["midia_idx_img"] = max(0, min(state["midia_idx_img"] + delta, len(lst) - 1))
            _render_img_lista()
        elif tipo == "video":
            lst = state["midia_videos"]
            state["midia_idx_vid"] = max(0, min(state["midia_idx_vid"] + delta, len(lst) - 1))
            _render_vid_lista()
        _update_midia_controls()

    def _exibir_midia():
        dw = get_display()
        if not dw or not dw.exists():
            return
        tipo = state["midia_tipo_sel"]
        if tipo == "imagem":
            lst = state["midia_imagens"]
            idx = state["midia_idx_img"]
            if not lst or idx >= len(lst):
                return
            _stop_poll()
            dw.show_imagem(lst[idx]["path"])
            dw.bind_nav(
                on_prev=lambda: (_nav_midia(-1), _exibir_midia()),
                on_next=lambda: (_nav_midia(+1), _exibir_midia()),
            )
        elif tipo == "video":
            lst = state["midia_videos"]
            idx = state["midia_idx_vid"]
            if not lst or idx >= len(lst):
                return
            dw.show_video(lst[idx]["path"])
            dw.bind_nav(
                on_prev=lambda: (_nav_midia(-1), _exibir_midia()),
                on_next=lambda: (_nav_midia(+1), _exibir_midia()),
            )
            _start_poll()
        else:
            return
        dw.show()

    # ── Controles de vídeo ───────────────────────────────────────────

    def _toggle_play():
        dw = get_display()
        if not dw or not dw.exists():
            return
        player = dw.get_player()
        if player is None:
            _exibir_midia()   # inicia se ainda não está reproduzindo
            return
        if player.is_playing():
            player.pause()
        else:
            player.play()

    def _stop_video_ctrl():
        _stop_poll()
        dw = get_display()
        if dw and dw.exists():
            dw.limpar()
        _play_btn.configure(text="▶  Reproduzir",
                            bg=COLORS["accent"], fg=COLORS["bg_dark"])
        _time_var.set("0:00 / 0:00")
        _seek_var.set(0)

    def _start_poll():
        _stop_poll()
        _poll_video()

    def _stop_poll():
        pid = state.get("_poll_id")
        if pid:
            try:
                outer.after_cancel(pid)
            except Exception:
                pass
            state["_poll_id"] = None

    def _poll_video():
        if not outer.winfo_exists():
            return
        dw = get_display()
        if not dw or not dw.exists():
            return
        player = dw.get_player()
        if player is None:
            state["_poll_id"] = None
            return
        try:
            t_ms  = max(0, player.get_time())
            l_ms  = max(0, player.get_length())
            is_pl = bool(player.is_playing())
            _play_btn.configure(
                text="⏸  Pausar"       if is_pl else "▶  Reproduzir",
                bg=COLORS["divider"]   if not is_pl else COLORS["accent"],
                fg=COLORS["text"]      if not is_pl else COLORS["bg_dark"],
            )
            if l_ms > 0 and not _seek_dragging[0]:
                _seek_var.set(int(t_ms / l_ms * 1000))

            def _fmt(ms):
                s = ms // 1000
                return f"{s // 60}:{s % 60:02d}"
            _time_var.set(f"{_fmt(t_ms)} / {_fmt(l_ms)}")
        except Exception:
            pass
        state["_poll_id"] = outer.after(500, _poll_video)

    # Inicializa as duas listas vazias
    _render_img_lista()
    _render_vid_lista()

    # ════════════════════════════════════════════════════════════════
    # Lógica interna
    # ════════════════════════════════════════════════════════════════

    def _set_slides_state(enabled: bool):
        s = tk.NORMAL if enabled else tk.DISABLED
        for btn in (_prev_btn, _next_btn, _exibir_btn, _edit_btn, _del_btn):
            try:
                if not enabled:
                    btn.configure(state=s, bg=COLORS["divider"], fg=COLORS["text_muted"])
                else:
                    if btn is _exibir_btn:
                        btn.configure(state=s, bg=COLORS["accent"], fg=COLORS["bg_dark"])
                    else:
                        btn.configure(state=s, bg=COLORS["input_bg"], fg=COLORS["text"])
            except Exception:
                pass

    def _load_music(mid: int):
        from core.musicas import obter_musica
        m = obter_musica(mid)
        if not m:
            return
        state["selecionada"] = m
        state["paginas"]     = paginar_por_linhas(m["letra"], _PG_LINES)
        state["pagina_idx"]  = 0
        artista = m.get("artista") or ""
        info    = m["titulo"] + (f"  ·  {artista}" if artista else "")
        _music_info_var.set(info)
        _render_slides_lb()
        _update_slide_view()
        _set_slides_state(bool(state["paginas"]))
        _reload_list(state["busca"])

    def _update_slide_view():
        pages = state["paginas"]
        idx   = state["pagina_idx"]
        if not pages:
            _page_var.set("—")
            _set_preview("")
            return
        _page_var.set(f"Slide  {idx + 1}  /  {len(pages)}")
        _set_preview("\n".join(pages[idx]))
        _slides_lb.selection_clear(0, tk.END)
        _slides_lb.selection_set(idx)
        _slides_lb.see(idx)

    def _set_preview(text: str):
        _preview_text.configure(state=tk.NORMAL)
        _preview_text.delete("1.0", tk.END)
        _preview_text.insert("1.0", text)
        _preview_text.configure(state=tk.DISABLED)

    def _nav(delta: int):
        pages = state["paginas"]
        if not pages:
            return
        state["pagina_idx"] = max(0, min(state["pagina_idx"] + delta,
                                         len(pages) - 1))
        _update_slide_view()

    def _exibir_slide():
        dw = get_display()
        if not dw or not dw.exists():
            return
        pages = state["paginas"]
        idx   = state["pagina_idx"]
        m     = state["selecionada"]
        if not pages or not m:
            return
        artista  = m.get("artista") or ""
        info     = m["titulo"] + (f"  ·  {artista}" if artista else "")
        page_str = f"Slide {idx + 1} / {len(pages)}"
        dw.show_letra(pages[idx], info, page_str)
        dw.bind_nav(
            on_prev=lambda: _nav_and_display(-1),
            on_next=lambda: _nav_and_display(+1),
        )
        dw.show()

    def _nav_and_display(delta: int):
        _nav(delta)
        dw = get_display()
        if dw and dw.exists() and state["paginas"] and state["selecionada"]:
            pages    = state["paginas"]
            idx      = state["pagina_idx"]
            m        = state["selecionada"]
            artista  = m.get("artista") or ""
            info     = m["titulo"] + (f"  ·  {artista}" if artista else "")
            page_str = f"Slide {idx + 1} / {len(pages)}"
            dw.show_letra(pages[idx], info, page_str)

    def _nav_ver(delta: int):
        try:
            ver = int(_ver_var.get() or 1) + delta
            if ver < 1:
                ver = 1
            _ver_var.set(str(ver))
            state["ver_sel"] = ver
            _buscar_versiculo()
        except ValueError:
            pass

    def _buscar_versiculo(update_display: bool = False):
        livro = state.get("livro_sel")
        if not livro:
            _verse_err_var.set("Selecione um livro.")
            return
        try:
            cap = int(_cap_var.get() or 1)
            ver = int(_ver_var.get() or 1)
        except ValueError:
            _verse_err_var.set("Capítulo e versículo devem ser números.")
            return
        cap = max(1, cap)
        ver = max(1, ver)
        state["cap_sel"] = cap
        state["ver_sel"] = ver

        state["_req_seq"] = state.get("_req_seq", 0) + 1
        seq = state["_req_seq"]

        _verse_text_var.set("Buscando…")
        _verse_ref_var.set("")
        _verse_err_var.set("")
        _exibir_verse_btn.configure(state=tk.DISABLED,
                                    bg=COLORS["divider"], fg=COLORS["text_muted"])

        from core.verse import buscar_por_usfm

        def _on_result(v):
            def _update():
                if not v_right.winfo_exists():
                    return
                if state.get("_req_seq") != seq:
                    return  # resposta obsoleta — requisição mais recente já chegou
                if "error" in v:
                    _verse_text_var.set("")
                    _verse_ref_var.set("")
                    _verse_err_var.set(v["error"])
                    state["versiculo"] = None
                else:
                    _verse_text_var.set(f'"{v["text"]}"')
                    _verse_ref_var.set(f'— {v["reference"]}')
                    _verse_err_var.set("")
                    state["versiculo"] = v
                    _exibir_verse_btn.configure(
                        state=tk.NORMAL,
                        bg=COLORS["accent"],
                        fg=COLORS["bg_dark"],
                    )
                    if update_display:
                        dw = get_display()
                        if dw and dw.exists():
                            dw.show_versiculo(v["text"], v["reference"])
            v_right.after(0, _update)

        buscar_por_usfm(livro["usfm"], cap, ver, livro["nome"], _on_result)

    def _exibir_versiculo():
        dw = get_display()
        if not dw or not dw.exists():
            return
        v = state["versiculo"]
        if not v:
            return
        dw.show_versiculo(v["text"], v["reference"])
        dw.bind_nav(
            on_prev=lambda: _nav_ver_display(-1),
            on_next=lambda: _nav_ver_display(+1),
        )
        dw.show()

    def _nav_ver_display(delta: int):
        """Avança ou recua um versículo no display, depois re-busca e exibe."""
        try:
            ver = int(_ver_var.get() or 1) + delta
            if ver < 1:
                ver = 1
            _ver_var.set(str(ver))
            state["ver_sel"] = ver
        except ValueError:
            return
        _buscar_versiculo(update_display=True)

    # ── estado inicial ─────────────────────────────────────────────
    _set_slides_state(False)
    _switch_tab("som")

    # teclas de seta só navegam slides quando a aba Som está ativa,
    # outer está visível e o foco não está em um campo de texto (Entry)
    def _nav_key(delta):
        try:
            if not outer.winfo_exists() or not outer.winfo_ismapped():
                return
        except Exception:
            return
        if isinstance(outer.focus_get(), (tk.Entry, tk.Listbox, tk.Text)):
            return
        if _active_tab[0] == "som":
            _nav(delta)

    outer.bind_all("<Left>",  lambda _e: _nav_key(-1))
    outer.bind_all("<Right>", lambda _e: _nav_key(+1))

    # remove os bind_all globais quando a página for destruída
    def _cleanup_nav(e):
        if e.widget is outer:
            try:
                outer.unbind_all("<Left>")
                outer.unbind_all("<Right>")
            except Exception:
                pass
            try:
                _stop_poll()
            except Exception:
                pass

    outer.bind("<Destroy>", _cleanup_nav, add="+")

    _reload_list()

    return outer
