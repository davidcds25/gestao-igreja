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

    _available_temas = _temas_disp()
    # inicia no primeiro tema disponível, ou None (preto puro)
    _tema_var  = [_available_temas[0] if _available_temas else None]
    _tema_btns = {}

    def _set_tema(t):
        _tema_var[0] = t
        for k, b in _tema_btns.items():
            if k == t:
                b.configure(bg=COLORS["accent"], fg=COLORS["bg_dark"])
            else:
                b.configure(bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        dw = get_display()
        if dw and dw.exists():
            dw.set_tema(t)

    def _abrir_display():
        dw = get_display()
        if dw:
            dw.set_tema(_tema_var[0])   # garante tema atual mesmo se display foi recriado
            dw.show()

    def _limpar_display():
        dw = get_display()
        if dw and dw.exists():
            dw.limpar()

    # seletor de fundo — só exibe se houver ao menos um tema disponível
    if _available_temas:
        tema_row = tk.Frame(hdr["actions"], bg=COLORS["bg_dark"])
        tema_row.pack(side=tk.LEFT, padx=(0, SPACING[4]))

        tk.Label(tema_row, text="Fundo",
                 font=FONTS["tiny_bold"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(
                     side=tk.LEFT, padx=(0, SPACING[2]))

        for _t in [None] + _available_temas:
            _lbl = "●" if _t is None else _t
            _b = tk.Button(
                tema_row, text=_lbl,
                font=FONTS["tiny_bold"],
                bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                activebackground=COLORS["accent"],
                activeforeground=COLORS["bg_dark"],
                relief=tk.FLAT, bd=0,
                padx=SPACING[3], pady=SPACING[1],
                cursor="hand2",
                command=lambda t=_t: _set_tema(t),
            )
            _b.pack(side=tk.LEFT, padx=1)
            _tema_btns[_t] = _b

        # marca o tema inicial como ativo
        _set_tema(_tema_var[0])

    button(hdr["actions"], text="Limpar", kind="ghost", icon="✕",
           command=_limpar_display).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(hdr["actions"], text="Abrir Display", kind="primary", icon="📺",
           command=_abrir_display).pack(side=tk.LEFT)

    # ── tab bar ──────────────────────────────────────────────────────
    _active_tab = ["som"]

    tab_bar = tk.Frame(outer, bg=COLORS["bg_card"],
                       highlightbackground=COLORS["divider"],
                       highlightthickness=1)
    tab_bar.pack(fill=tk.X, pady=(0, SPACING[4]))

    tab_som_frame   = tk.Frame(outer, bg=COLORS["bg_dark"])
    tab_verse_frame = tk.Frame(outer, bg=COLORS["bg_dark"])

    def _switch_tab(name):
        _active_tab[0] = name
        if name == "som":
            tab_verse_frame.pack_forget()
            tab_som_frame.pack(fill=tk.BOTH, expand=True)
            _btn_som.configure(bg=COLORS["accent"],   fg=COLORS["bg_dark"])
            _btn_verse.configure(bg=COLORS["bg_card"], fg=COLORS["text_muted"])
        else:
            tab_som_frame.pack_forget()
            tab_verse_frame.pack(fill=tk.BOTH, expand=True)
            _btn_verse.configure(bg=COLORS["accent"],  fg=COLORS["bg_dark"])
            _btn_som.configure(bg=COLORS["bg_card"],   fg=COLORS["text_muted"])

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
    _btn_som.configure(command=lambda: _switch_tab("som"))
    _btn_verse.configure(command=lambda: _switch_tab("versiculo"))
    _btn_som.pack(side=tk.LEFT)
    _btn_verse.pack(side=tk.LEFT)

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

    outer.bind("<Destroy>", _cleanup_nav, add="+")

    _reload_list()

    return outer
