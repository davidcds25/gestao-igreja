"""
pages/whatsapp.py
=================
Tela de WhatsApp com funcionalidade real.

Aceita callbacks (do login.py):
  - qr_code:           abrir QR Code
  - verificar:         re-navegar para atualizar status
  - toggle_connection: conectar / desconectar

Aceita prefill dict de evento:
  {"funcao_alvo": str|None, "titulo": str, "hora": str,
   "local": str, "dia": int, "mes": str}
"""

import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, tabs as build_tabs,
    connection_card, button, select, field, text_input, textarea,
)

_FUNCOES_OPTIONS = [
    "Todas", "Membro", "Pastor(a)", "Presbítero", "Diácono(a)",
    "Evangelista", "Líder de Célula", "Louvor", "Obreiro(a)",
    "Secretário(a)", "Tesoureiro(a)",
]


def _build_template(event: dict) -> str:
    hora_atual = datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    titulo = event.get("titulo", "")
    hora   = event.get("hora", "")
    local  = event.get("local", "")
    dia    = event.get("dia", "")
    mes    = event.get("mes", "")

    hora_part  = f" às {hora}" if hora else ""
    local_part = f"\n📍 Local: {local}" if local else ""

    return (
        f"{saudacao}, a paz do Senhor! 🙏\n\n"
        f"Passando para lembrar que no dia {dia}/{mes}{hora_part} "
        f"teremos: *{titulo}*.{local_part}\n\n"
        f"Contamos com a sua presença!\n"
        f"Deus abençoe! ✨"
    )


def open_qr_modal(root):
    """
    Abre janela modal com QR Code renderizado no tkinter,
    auto-atualizado a cada 20s com countdown visível.
    Fecha automaticamente ao detectar conexão ativa.
    """
    from core.whatsapp import obter_qrcode_base64, status_conexao

    win = tk.Toplevel(root)
    win.title("QR Code — WhatsApp")
    win.configure(bg=COLORS["bg_dark"])
    win.resizable(False, False)
    win.grab_set()

    win.update_idletasks()
    w, h = 420, 560
    x = root.winfo_x() + (root.winfo_width()  - w) // 2
    y = root.winfo_y() + (root.winfo_height() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(win, text="Escanear QR Code",
             font=FONTS["subtitle"], bg=COLORS["bg_dark"],
             fg=COLORS["text"]).pack(pady=(SPACING[5], SPACING[1]))
    tk.Label(win,
             text="WhatsApp → Dispositivos Conectados → Conectar dispositivo",
             font=FONTS["small"], bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
             wraplength=340, justify=tk.CENTER).pack(pady=(0, SPACING[4]))

    # Área do QR
    img_frame = tk.Frame(win, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["divider"], highlightthickness=1)
    img_frame.pack(padx=SPACING[5])
    img_lbl = tk.Label(img_frame, bg=COLORS["bg_card"],
                       text="Carregando...", fg=COLORS["text_muted"],
                       font=FONTS["body"])
    img_lbl.pack(padx=SPACING[3], pady=SPACING[3])

    status_lbl = tk.Label(win, text="Aguardando escaneamento...",
                          font=FONTS["small"], bg=COLORS["bg_dark"],
                          fg=COLORS["text_muted"])
    status_lbl.pack(pady=(SPACING[3], 0))

    countdown_lbl = tk.Label(win, text="",
                             font=FONTS["small"], bg=COLORS["bg_dark"],
                             fg=COLORS["text_very_dim"])
    countdown_lbl.pack()

    _state = {"job": None, "img_ref": None, "busy": False}

    def _cancel():
        if _state["job"]:
            try:
                win.after_cancel(_state["job"])
            except Exception:
                pass
            _state["job"] = None

    def _countdown(secs):
        if not win.winfo_exists():
            return
        if secs <= 0:
            _load()
            return
        countdown_lbl.config(text=f"Próximo refresh em {secs}s")
        _state["job"] = win.after(1000, lambda: _countdown(secs - 1))

    def _apply(status, b64=None, msg=None, color=None, next_secs=None):
        """Atualiza a UI (sempre no main thread via after)."""
        if not win.winfo_exists():
            return
        _cancel()
        _state["busy"] = False

        if b64:
            raw = b64.split(",", 1)[1] if "," in b64 else b64
            photo = tk.PhotoImage(data=raw)
            _state["img_ref"] = photo
            img_lbl.config(image=photo, text="", width=0, height=0)
        elif msg:
            img_lbl.config(image="", text=msg,
                           fg=color or COLORS["text_muted"])

        status_lbl.config(text=status,
                          fg=color if color and not b64 else COLORS["text_muted"])

        if next_secs is not None:
            _countdown(next_secs)

    def _load():
        if not win.winfo_exists() or _state["busy"]:
            return
        _cancel()
        _state["busy"] = True

        # Bloqueia no thread, nunca no main thread
        def _worker():
            try:
                st, err = status_conexao()
            except Exception as ex:
                st, err = None, str(ex)

            def _done():
                if not win.winfo_exists():
                    return

                # Servidor offline
                if st is None and err and (
                        "offline" in err.lower() or "inacess" in err.lower()):
                    _apply("Servidor WAHA offline — inicie o Docker no WSL2.",
                           msg="Docker não está rodando no WSL2.",
                           color=COLORS["danger"], next_secs=15)
                    return

                # Conectado
                if st == "open":
                    _apply("✅ WhatsApp conectado!",
                           msg="Conectado com sucesso!", color=COLORS["success"])
                    countdown_lbl.config(text="Pode fechar esta janela.")
                    return

                # Sessão inexistente ou parada — inicia em background
                if st in (None, "close"):
                    status_lbl.config(text="Iniciando sessão WAHA...",
                                      fg=COLORS["text_muted"])
                    img_lbl.config(image="", text="Aguarde...",
                                   fg=COLORS["text_muted"])
                    countdown_lbl.config(text="")
                    _state["busy"] = False

                    def _start_worker():
                        try:
                            from core.whatsapp import criar_instancia
                            criar_instancia()
                        except Exception:
                            pass
                        if win.winfo_exists():
                            win.after(3000, _load)

                    threading.Thread(target=_start_worker, daemon=True).start()
                    return

                # Sessão conectando (STARTING / SCAN_QR_CODE) — tenta QR
                try:
                    b64, qerr = obter_qrcode_base64()
                except Exception as ex:
                    b64, qerr = None, str(ex)

                if b64 and not qerr:
                    _apply("Aguardando escaneamento...", b64=b64, next_secs=20)
                else:
                    _apply("Aguardando QR Code...",
                           msg="Preparando...", next_secs=3)

            win.after(0, _done)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_close():
        _cancel()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", _on_close)

    button(win, text="Fechar", kind="ghost",
           command=_on_close).pack(pady=(SPACING[3], SPACING[5]))

    win.after(50, _load)   # pequeno delay para janela aparecer antes de carregar


def render(parent, *, connected: bool = False, callbacks=None, prefill=None):
    callbacks = callbacks or {}
    content = page_container(parent)

    # ─── Header ───────────────────────────────────────────────────
    hdr = screen_header(
        content,
        icon="💬",
        title="WhatsApp",
        subtitle="Envio de mensagens via WAHA",
    )
    hdr["frame"].pack(fill=tk.X, pady=(0, SPACING[5]))

    button(hdr["actions"], text="Ver QR Code", kind="ghost",
           icon="📷",
           command=callbacks.get("qr_code")).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(hdr["actions"], text="Verificar", kind="secondary",
           icon="↻",
           command=callbacks.get("verificar")).pack(side=tk.LEFT)

    # ─── Card de conexão ──────────────────────────────────────────
    connection_card(
        content,
        connected=connected,
        session_info="sessão ativa" if connected else "desconectado",
        on_toggle=callbacks.get("toggle_connection"),
    ).pack(fill=tk.X, pady=(0, SPACING[6]))

    # ─── Tabs ─────────────────────────────────────────────────────
    tab_row = tk.Frame(content, bg=COLORS["bg_dark"])
    tab_row.pack(fill=tk.X, pady=(0, SPACING[4]))

    form_container = tk.Frame(content, bg=COLORS["bg_dark"])
    form_container.pack(fill=tk.BOTH, expand=True)

    is_birthday = prefill and prefill.get("type") == "birthday"
    default_tab = "individual" if is_birthday else ("lote" if prefill else "individual")

    def _render_form(tab):
        for w in form_container.winfo_children():
            w.destroy()
        if tab == "individual":
            _render_individual(form_container, connected,
                               prefill=prefill if is_birthday else None)
        else:
            _render_lote(form_container, connected,
                         prefill=prefill if not is_birthday else None)

    tabs_widget = build_tabs(
        tab_row,
        options=[
            ("individual", "💬  Mensagem Individual", None),
            ("lote",       "👥  Mensagem em Lote",    None),
        ],
        value=default_tab,
        on_change=_render_form,
    )
    tabs_widget.pack(side=tk.LEFT)
    _render_form(default_tab)


def _form_wrap(parent):
    wrap = tk.Frame(parent, bg=COLORS["bg_card"],
                    highlightbackground=COLORS["divider"],
                    highlightthickness=1)
    inner = tk.Frame(wrap, bg=COLORS["bg_card"])
    inner.pack(fill=tk.BOTH, expand=True,
               padx=SPACING[5], pady=SPACING[5])
    return wrap, inner


def _root_of(widget):
    return widget.winfo_toplevel()


# ─── ABA: INDIVIDUAL ──────────────────────────────────────────────

def _render_individual(parent, connected, prefill=None):
    # Carrega membros ativos com telefone
    membros_com_tel = []
    try:
        from core.members import listar_membros
        membros_com_tel = [
            {"nome": r["nome"], "telefone": r["telefone"]}
            for r in listar_membros(status="Ativo")
            if r["telefone"]
        ]
    except Exception:
        pass

    wrap, inner = _form_wrap(parent)
    wrap.pack(fill=tk.X)

    inner.columnconfigure(0, weight=2, uniform="f")
    inner.columnconfigure(1, weight=1, uniform="f")

    # Membro — combobox com todos ativos com telefone
    m_field = field(inner, label="Membro",
                    hint="selecione para preencher o telefone")
    m_field.grid(row=0, column=0, sticky="ew", padx=(0, SPACING[3]),
                 pady=(0, SPACING[3]))
    nomes = ["(selecionar membro)"] + [m["nome"] for m in membros_com_tel]
    sel_membro = select(m_field, value="(selecionar membro)", options=nomes)
    sel_membro.pack(fill=tk.X)

    t_field = field(inner, label="Telefone")
    t_field.grid(row=0, column=1, sticky="ew", pady=(0, SPACING[3]))
    phone_entry = text_input(t_field, value="")
    phone_entry.pack(fill=tk.X)

    def _on_membro_sel(e=None):
        nome = sel_membro._var.get()
        m = next((m for m in membros_com_tel if m["nome"] == nome), None)
        if m:
            phone_entry.delete(0, tk.END)
            phone_entry.insert(0, m["telefone"])

    sel_membro.bind("<<ComboboxSelected>>", _on_membro_sel)

    if prefill and prefill.get("type") == "birthday":
        nome_aniv = prefill.get("nome", "")
        tel_aniv  = prefill.get("telefone", "")
        hora_atual = datetime.now().hour
        if hora_atual < 12:
            saudacao = "Bom dia"
        elif hora_atual < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"
        primeiro = nome_aniv.split()[0] if nome_aniv else "{nome}"
        msg_template = (
            f"{saudacao}, {primeiro}! 🎂\n\n"
            f"Hoje é um dia muito especial — seu aniversário!\n\n"
            f"Em nome de toda a nossa família de fé, queremos desejar a você "
            f"um feliz aniversário cheio de bênçãos, saúde e alegria.\n\n"
            f"Que Deus continue te abençoando e guardando! 🙏✨\n"
            f"Feliz aniversário!"
        )
        if nome_aniv in nomes:
            sel_membro._var.set(nome_aniv)
        if tel_aniv:
            phone_entry.delete(0, tk.END)
            phone_entry.insert(0, tel_aniv)
    else:
        msg_template = (
            "Olá {nome}! A paz do Senhor! 🙏\n\n"
            "Passando para lembrar você sobre as novidades da nossa comunidade.\n\n"
            "Contamos com sua presença!\n"
            "Deus abençoe! ✨"
        )
    msg_field = field(inner, label="Mensagem", hint="use {nome} para personalizar")
    msg_field.grid(row=1, column=0, columnspan=2, sticky="ew",
                   pady=(0, SPACING[3]))
    msg_area = textarea(msg_field, lines=5, value=msg_template)
    msg_area.pack(fill=tk.X)

    footer = tk.Frame(inner, bg=COLORS["bg_card"])
    footer.grid(row=2, column=0, columnspan=2, sticky="ew",
                pady=(SPACING[2], 0))

    hint_color = COLORS["text_muted"] if connected else COLORS["danger"]
    hint_text  = ("Pronto para enviar." if connected
                  else "⚠ Conexão inativa — conecte o WhatsApp antes de enviar.")
    tk.Label(footer, text=hint_text, font=FONTS["small"],
             bg=COLORS["bg_card"], fg=hint_color).pack(side=tk.LEFT)

    _sending = {"v": False}
    _birthday_nome = (prefill.get("nome", "") if prefill else "")
    _birthday_tel  = (prefill.get("telefone", "") if prefill else "")

    def _limpar():
        if _birthday_nome and _birthday_nome in nomes:
            sel_membro._var.set(_birthday_nome)
        else:
            sel_membro._var.set("(selecionar membro)")
        phone_entry.delete(0, tk.END)
        if _birthday_tel:
            phone_entry.insert(0, _birthday_tel)
        msg_area.delete("1.0", tk.END)
        msg_area.insert("1.0", msg_template)

    def _enviar():
        if _sending["v"]:
            return
        phone = phone_entry.get().strip()
        texto = msg_area.get("1.0", "end-1c").strip()
        root  = _root_of(parent)
        nome_sel = sel_membro._var.get()
        if nome_sel != "(selecionar membro)" and "{nome}" in texto:
            texto = texto.replace("{nome}", nome_sel.split()[0])
        if not phone:
            messagebox.showwarning("Campo obrigatório",
                                   "Selecione um membro ou informe o telefone.", parent=root)
            return
        if not texto:
            messagebox.showwarning("Campo obrigatório",
                                   "Escreva uma mensagem antes de enviar.", parent=root)
            return
        if not connected:
            messagebox.showerror("Desconectado",
                                 "Conecte o WhatsApp antes de enviar mensagens.",
                                 parent=root)
            return

        _sending["v"] = True
        send_btn.configure(state=tk.DISABLED)

        def _on_sucesso():
            messagebox.showinfo("Enviado!", "Mensagem enviada com sucesso.", parent=root)
            _limpar()

        def _run():
            try:
                from core.whatsapp import enviar_mensagem
                _, err = enviar_mensagem(phone, texto)
                if not parent.winfo_exists():
                    return
                if err:
                    parent.after(0, lambda: messagebox.showerror("Erro no envio", err, parent=root))
                else:
                    parent.after(0, _on_sucesso)
            except Exception as ex:
                msg = str(ex)
                if parent.winfo_exists():
                    parent.after(0, lambda m=msg: messagebox.showerror("Erro", m, parent=root))
            finally:
                _sending["v"] = False
                if parent.winfo_exists():
                    parent.after(0, lambda: send_btn.configure(state=tk.NORMAL))

        threading.Thread(target=_run, daemon=True).start()

    button(footer, text="Limpar", kind="ghost",
           command=_limpar).pack(side=tk.RIGHT, padx=(SPACING[2], 0))
    send_btn = button(footer, text="Enviar Mensagem", kind="whatsapp",
                      icon="📤", command=_enviar)
    send_btn.pack(side=tk.RIGHT)


# ─── ABA: LOTE ────────────────────────────────────────────────────

_TIPOS_FILTRO = ["Função", "Grupo", "Aniversariantes do mês"]


def _ver_lista_dialog(root, state, count_lbl, filtro_lbl):
    """Abre janela com checkboxes para incluir/excluir membros da lista de envio."""
    membros = state["membros"]
    if not membros:
        messagebox.showinfo("Lista vazia",
                            "Clique em Filtrar para buscar destinatários.", parent=root)
        return

    dlg = tk.Toplevel(root)
    dlg.title(f"Destinatários ({len(membros)})")
    dlg.configure(bg=COLORS["bg_dark"])
    dlg.grab_set()
    dlg.resizable(False, True)

    w, h = 460, 500
    x = root.winfo_x() + (root.winfo_width()  - w) // 2
    y = root.winfo_y() + (root.winfo_height() - h) // 2
    dlg.geometry(f"{w}x{h}+{x}+{y}")

    com_tel = sum(1 for m in membros if m.get("telefone"))
    sem_tel = len(membros) - com_tel

    hdr = tk.Frame(dlg, bg=COLORS["bg_dark"])
    hdr.pack(fill=tk.X, padx=SPACING[5], pady=(SPACING[4], SPACING[2]))
    tk.Label(hdr, text=f"{len(membros)} destinatários encontrados",
             font=FONTS["subtitle"], bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(anchor=tk.W)
    info = f"✅ {com_tel} com telefone"
    if sem_tel:
        info += f"   ⚠ {sem_tel} sem telefone (serão ignorados)"
    tk.Label(hdr, text=info, font=FONTS["small"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor=tk.W)

    # Lista com scroll
    list_frame = tk.Frame(dlg, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["divider"], highlightthickness=1)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING[5], pady=SPACING[3])

    canvas = tk.Canvas(list_frame, bg=COLORS["bg_card"], highlightthickness=0)
    sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
    inner_list = tk.Frame(canvas, bg=COLORS["bg_card"])

    inner_list.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner_list, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    def _scroll(e):
        canvas.yview_scroll(-1 * (e.delta // 120), "units")

    canvas.bind("<MouseWheel>", _scroll)
    inner_list.bind("<MouseWheel>", _scroll)
    dlg.bind("<MouseWheel>", _scroll)

    vars_list = []
    for m in membros:
        has_phone = bool(m.get("telefone"))
        var = tk.BooleanVar(value=has_phone)
        vars_list.append(var)

        row = tk.Frame(inner_list, bg=COLORS["bg_card"])
        row.pack(fill=tk.X, padx=SPACING[4], pady=2)
        row.bind("<MouseWheel>", _scroll)

        cb = tk.Checkbutton(
            row, text=m["nome"], variable=var,
            bg=COLORS["bg_card"], fg=COLORS["text"],
            selectcolor=COLORS["accent"], activebackground=COLORS["bg_card"],
            font=FONTS["body"], anchor=tk.W,
            state=tk.NORMAL if has_phone else tk.DISABLED,
        )
        cb.pack(side=tk.LEFT)
        cb.bind("<MouseWheel>", _scroll)

        tel_text = m.get("telefone") or "sem telefone"
        tel_color = COLORS["text_muted"] if has_phone else COLORS["danger"]
        lbl = tk.Label(row, text=f"— {tel_text}", font=FONTS["small"],
                       bg=COLORS["bg_card"], fg=tel_color)
        lbl.pack(side=tk.LEFT, padx=(SPACING[1], 0))
        lbl.bind("<MouseWheel>", _scroll)

    # Footer do dialog
    footer_dlg = tk.Frame(dlg, bg=COLORS["bg_dark"])
    footer_dlg.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[4])

    def _sel_todos():
        for var, m in zip(vars_list, membros):
            if m.get("telefone"):
                var.set(True)

    def _desel_todos():
        for var in vars_list:
            var.set(False)

    def _confirmar():
        selecionados = [m for m, v in zip(membros, vars_list) if v.get()]
        state["membros"] = selecionados
        count_lbl.config(text=str(len(selecionados)))
        filtro_lbl.config(text=f"{len(selecionados)} selecionados de {len(membros)}")
        dlg.destroy()

    button(footer_dlg, text="Marcar todos", kind="ghost",
           command=_sel_todos).pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(footer_dlg, text="Desmarcar todos", kind="ghost",
           command=_desel_todos).pack(side=tk.LEFT)
    button(footer_dlg, text="Confirmar seleção", kind="primary",
           command=_confirmar).pack(side=tk.RIGHT)


def _render_lote(parent, connected, prefill=None):
    try:
        from core.members import GRUPOS as _base_grupos
        _GRUPOS_LOTE = list(_base_grupos) + ["Grupo de Casais"]
    except Exception:
        _GRUPOS_LOTE = ["Grupo de Mulheres", "Grupo dos Homens",
                        "Grupo de Jovens", "Grupo Infantil", "Grupo de Casais"]

    wrap, inner = _form_wrap(parent)
    wrap.pack(fill=tk.X)

    if prefill:
        banner = tk.Frame(inner, bg=COLORS["accent2"])
        banner.pack(fill=tk.X, pady=(0, SPACING[3]))
        banner_inner = tk.Frame(banner, bg=COLORS["accent2"])
        banner_inner.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[2])
        tk.Label(banner_inner,
                 text=f"💬  Lembrete para: {prefill.get('titulo', '')}",
                 font=FONTS["body_strong"],
                 bg=COLORS["accent2"], fg=COLORS["bg_dark"]).pack(side=tk.LEFT)

    # ── Filtros: UM critério por vez ──────────────────────────────
    filters = tk.Frame(inner, bg=COLORS["bg_card"])
    filters.pack(fill=tk.X, pady=(0, SPACING[3]))

    row1 = tk.Frame(filters, bg=COLORS["bg_card"])
    row1.pack(fill=tk.X)

    # Tipo do filtro
    f_tipo = field(row1, label="Filtrar por")
    f_tipo.pack(side=tk.LEFT, padx=(0, SPACING[3]))

    tipo_inicial = "Função"
    if prefill and prefill.get("grupo_alvo"):
        tipo_inicial = "Grupo"
    elif prefill and prefill.get("funcao_alvo"):
        tipo_inicial = "Função"

    sel_tipo = select(f_tipo, value=tipo_inicial, options=_TIPOS_FILTRO)
    sel_tipo.pack()

    # Frame dinâmico para o valor do filtro
    val_frame = tk.Frame(row1, bg=COLORS["bg_card"])
    val_frame.pack(side=tk.LEFT, padx=(0, SPACING[3]))
    _val_widget = {"w": None}

    def _rebuild_val(tipo=None):
        tipo = tipo or sel_tipo._var.get()
        for w in val_frame.winfo_children():
            w.destroy()
        _val_widget["w"] = None

        if tipo == "Função":
            fi = "Todas"
            if prefill and prefill.get("funcao_alvo"):
                fa = prefill["funcao_alvo"]
                fi = fa if fa in _FUNCOES_OPTIONS else "Todas"
            f = field(val_frame, label="Função")
            f.pack()
            cb = select(f, value=fi, options=_FUNCOES_OPTIONS)
            cb.pack()
            _val_widget["w"] = cb

        elif tipo == "Grupo":
            gi = _GRUPOS_LOTE[0] if _GRUPOS_LOTE else ""
            if prefill and prefill.get("grupo_alvo"):
                g = prefill["grupo_alvo"]
                gi = g if g in _GRUPOS_LOTE else gi
            f = field(val_frame, label="Grupo")
            f.pack()
            cb = select(f, value=gi, options=list(_GRUPOS_LOTE))
            cb.pack()
            _val_widget["w"] = cb

        else:  # Aniversariantes
            f = field(val_frame, label="Mês")
            f.pack()
            _MES_NAMES = ["Jan","Fev","Mar","Abr","Mai","Jun",
                          "Jul","Ago","Set","Out","Nov","Dez"]
            mes_lbl = tk.Label(f, text=_MES_NAMES[datetime.now().month - 1],
                               font=FONTS["body"],
                               bg=COLORS["bg_card"], fg=COLORS["accent"])
            mes_lbl.pack(anchor=tk.W, pady=(SPACING[1], 0))
            _val_widget["mes_lbl"] = mes_lbl

    sel_tipo.bind("<<ComboboxSelected>>",
                  lambda e: _rebuild_val(sel_tipo._var.get()))
    _rebuild_val(tipo_inicial)

    state = {"membros": []}

    def _filtrar():
        tipo = sel_tipo._var.get()
        root = _root_of(parent)
        try:
            from core.members import listar_membros, aniversariantes_do_mes

            if tipo == "Função":
                val = _val_widget["w"]._var.get() if _val_widget["w"] else "Todas"
                rows = listar_membros(
                    status="Ativo",
                    funcao=None if val == "Todas" else val,
                )
                membros = [{k: r[k] for k in r.keys()} for r in rows]
                desc = f"Função: {val}"

            elif tipo == "Grupo":
                val = _val_widget["w"]._var.get() if _val_widget["w"] else ""
                if val == "Grupo de Casais":
                    rows = listar_membros(status="Ativo", grupo_casais=True)
                else:
                    rows = listar_membros(status="Ativo", grupo=val)
                membros = [{k: r[k] for k in r.keys()} for r in rows]
                desc = f"Grupo: {val}"

            else:  # Aniversariantes
                mes = datetime.now().month
                _MES_NAMES = ["Jan","Fev","Mar","Abr","Mai","Jun",
                              "Jul","Ago","Set","Out","Nov","Dez"]
                mes_nome = _MES_NAMES[mes - 1]
                rows = list(aniversariantes_do_mes(mes))
                membros = [{k: r[k] for k in r.keys()} for r in rows]
                # Atualiza label do mês (pode ter mudado se o sistema ficou aberto)
                lbl = _val_widget.get("mes_lbl")
                if lbl and lbl.winfo_exists():
                    lbl.config(text=mes_nome)
                desc = f"Aniversariantes de {mes_nome}"

            state["membros"] = membros
            count_lbl.config(text=str(len(membros)))
            filtro_lbl.config(text=desc)

        except Exception as ex:
            messagebox.showerror("Erro ao filtrar", str(ex), parent=root)

    button(row1, text="Filtrar", kind="secondary",
           icon="🔍", command=_filtrar).pack(side=tk.LEFT, anchor="s",
                                              pady=(SPACING[4], 0))

    # ── Contador de destinatários ──────────────────────────────────
    rc = tk.Frame(inner, bg=COLORS["bg_dark"],
                  highlightbackground=COLORS["divider"], highlightthickness=1)
    rc.pack(fill=tk.X, pady=(0, SPACING[3]))
    rc_inner = tk.Frame(rc, bg=COLORS["bg_dark"])
    rc_inner.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[3])

    count_lbl = tk.Label(rc_inner, text="—",
                         font=FONTS["metric_large"],
                         bg=COLORS["bg_dark"], fg=COLORS["accent"])
    count_lbl.pack(side=tk.LEFT, padx=(0, SPACING[3]))

    txt_col = tk.Frame(rc_inner, bg=COLORS["bg_dark"])
    txt_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Label(txt_col, text="destinatários",
             font=FONTS["body_strong"],
             bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(anchor=tk.W)
    filtro_lbl = tk.Label(txt_col, text="clique em Filtrar para buscar",
                          font=FONTS["small"],
                          bg=COLORS["bg_dark"], fg=COLORS["text_muted"])
    filtro_lbl.pack(anchor=tk.W)

    def _ver_lista():
        root = _root_of(parent)
        _ver_lista_dialog(root, state, count_lbl, filtro_lbl)

    button(rc_inner, text="Ver lista", kind="ghost",
           command=_ver_lista).pack(side=tk.RIGHT)

    # ── Mensagem ───────────────────────────────────────────────────
    msg_inicial = _build_template(prefill) if prefill else (
        "Olá {nome}! A paz do Senhor! 🙏\n\n"
        "Passando para lembrar você sobre as atividades da nossa comunidade.\n\n"
        "Contamos com sua presença!\n"
        "Deus abençoe! ✨"
    )
    msg_field = field(inner, label="Mensagem",
                      hint="use {nome} para personalizar — cada membro recebe com seu nome")
    msg_field.pack(fill=tk.X, pady=(0, SPACING[2]))
    msg_area = textarea(msg_field, lines=4, value=msg_inicial)
    msg_area.pack(fill=tk.X)

    # ── Footer ─────────────────────────────────────────────────────
    footer = tk.Frame(inner, bg=COLORS["bg_card"])
    footer.pack(fill=tk.X, pady=(SPACING[2], 0))
    tk.Label(footer,
             text=("Intervalo de 6s entre mensagens para maior segurança."
                   if connected else "⚠ Desconectado — não é possível enviar."),
             font=FONTS["small"],
             bg=COLORS["bg_card"],
             fg=COLORS["text_muted"] if connected else COLORS["danger"],
             ).pack(side=tk.LEFT)

    def _enviar_lote():
        membros  = state["membros"]
        root     = _root_of(parent)
        com_tel  = [m for m in membros if m.get("telefone")]
        sem_tel  = [m for m in membros if not m.get("telefone")]
        texto_raw = msg_area.get("1.0", "end-1c").strip()

        if not membros:
            messagebox.showwarning("Sem destinatários",
                                   "Filtre os destinatários antes de enviar.", parent=root)
            return
        if not texto_raw:
            messagebox.showwarning("Mensagem vazia",
                                   "Escreva a mensagem antes de enviar.", parent=root)
            return
        if not connected:
            messagebox.showerror("Desconectado",
                                 "Conecte o WhatsApp antes de enviar.", parent=root)
            return
        if not com_tel:
            messagebox.showwarning("Sem telefones",
                                   "Nenhum destinatário tem telefone cadastrado.", parent=root)
            return

        aviso = f"Enviar para {len(com_tel)} destinatário(s) com 6s de intervalo."
        if sem_tel:
            aviso += f"\n({len(sem_tel)} sem telefone serão ignorados.)"
        aviso += "\n\nConfirmar?"
        if not messagebox.askyesno("Confirmar envio", aviso, parent=root):
            return

        # Janela de progresso
        prog = tk.Toplevel(root)
        prog.title("Enviando...")
        prog.configure(bg=COLORS["bg_dark"])
        prog.geometry("380x180")
        prog.grab_set()
        prog.protocol("WM_DELETE_WINDOW", lambda: None)  # bloqueia X durante envio
        px = root.winfo_x() + (root.winfo_width()  - 380) // 2
        py = root.winfo_y() + (root.winfo_height() - 180) // 2
        prog.geometry(f"380x180+{px}+{py}")

        prog_nome = tk.Label(prog, text="Iniciando...",
                             font=FONTS["body"], bg=COLORS["bg_dark"], fg=COLORS["text"])
        prog_nome.pack(pady=(SPACING[5], SPACING[2]))
        prog_count = tk.Label(prog, text=f"0 / {len(com_tel)}",
                              font=FONTS["metric_large"],
                              bg=COLORS["bg_dark"], fg=COLORS["accent"])
        prog_count.pack()

        def _run():
            import time
            from core.whatsapp import enviar_mensagem
            resultados = []
            for i, membro in enumerate(com_tel):
                nome  = membro["nome"]
                tel   = membro["telefone"]
                # Personaliza com o primeiro nome
                texto = texto_raw.replace("{nome}", nome.split()[0])

                if prog.winfo_exists():
                    prog.after(0, lambda n=nome, idx=i: (
                        prog_nome.config(text=f"Enviando para {n}..."),
                        prog_count.config(text=f"{idx + 1} / {len(com_tel)}"),
                    ))
                _, err = enviar_mensagem(tel, texto)
                resultados.append((nome, err is None, err or "Enviado"))
                if i < len(com_tel) - 1:
                    time.sleep(6)

            enviados = sum(1 for _, ok, _ in resultados if ok)
            falhas   = len(resultados) - enviados
            res = f"✅ {enviados} mensagem(ns) enviada(s)"
            if falhas:
                res += f"\n❌ {falhas} falha(s)"

            def _done():
                if prog.winfo_exists():
                    prog.destroy()
                messagebox.showinfo("Envio concluído", res, parent=root)

            root.after(0, _done)

        threading.Thread(target=_run, daemon=True).start()

    button(footer, text="Enviar para todos", kind="whatsapp",
           icon="📤", command=_enviar_lote).pack(side=tk.RIGHT)
