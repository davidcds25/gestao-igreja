"""
Tela de integração com WhatsApp via WAHA
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from core.members import listar_membros, FUNCOES, STATUS

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#00d4ff"
BTN_COLOR  = "#667eea"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"
DIVIDER    = "#2d2d44"
GREEN_WPP  = "#25D366"


class WhatsAppWindow:
    def __init__(self, parent, root, current_user):
        self.parent       = parent
        self.root         = root
        self.current_user = current_user
        self._modo        = tk.StringVar(value="individual")
        self._outer       = None
        self._build()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def _alive(self):
        try:
            return bool(self._outer and self._outer.winfo_exists())
        except Exception:
            return False

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        outer = tk.Frame(self.parent, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=40, pady=24)
        self._outer = outer

        self._build_header(outer)
        self._build_status_card(outer)

        tk.Frame(outer, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(16, 0))

        self._build_mode_tabs(outer)

        self._modo_frame = tk.Frame(outer, bg=BG_DARK)
        self._modo_frame.pack(fill=tk.BOTH, expand=True)

        self._trocar_modo()
        self._verificar_status()

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 16))

        left = tk.Frame(hdr, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="WhatsApp",
                 font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W)
        tk.Label(left, text="Integração com WhatsApp via WAHA",
                 font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(anchor=tk.W)

        _btn = dict(relief=tk.FLAT, cursor="hand2",
                    font=("Segoe UI", 10, "bold"), padx=14, pady=7)

        tk.Button(hdr, text="🔄 Verificar",
                  command=self._verificar_status,
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  **_btn).pack(side=tk.RIGHT, padx=(6, 0))

        tk.Button(hdr, text="📷 Ver QR Code",
                  command=self._abrir_qr,
                  bg=DIVIDER, fg=TEXT,
                  activebackground="#3d3d54", activeforeground=TEXT,
                  **_btn).pack(side=tk.RIGHT)

    def _build_status_card(self, parent):
        card = tk.Frame(parent, bg=BG_CARD)
        card.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=20, pady=16)

        left = tk.Frame(inner, bg=BG_CARD)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(left, text="Status da Conexão",
                 font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=BG_CARD).pack(anchor=tk.W)

        self._status_lbl = tk.Label(
            left, text="Verificando…",
            font=("Segoe UI", 10), fg=TEXT_MUTED, bg=BG_CARD)
        self._status_lbl.pack(anchor=tk.W, pady=(4, 0))

        right = tk.Frame(inner, bg=BG_CARD)
        right.pack(side=tk.RIGHT)

        self._btn_desconectar = tk.Label(
            right, text="Desconectar",
            font=("Segoe UI", 9, "underline"),
            fg="#ff6b6b", bg=BG_CARD, cursor="hand2")
        self._btn_desconectar.bind("<Button-1>", lambda _e: self._desconectar())
        # Hidden by default — only shown when connected

    # ── Mode tabs ────────────────────────────────────────────────────────────

    def _build_mode_tabs(self, parent):
        tab_row = tk.Frame(parent, bg=BG_DARK)
        tab_row.pack(fill=tk.X, pady=(0, 0))

        self._tab_refs = {}
        tabs = [
            ("individual", "Mensagem Individual"),
            ("lote",       "Mensagem em Lote"),
        ]
        for key, label in tabs:
            col = tk.Frame(tab_row, bg=BG_DARK)
            col.pack(side=tk.LEFT, padx=(0, 2))

            btn = tk.Label(col, text=label,
                           font=("Segoe UI", 10, "bold"),
                           fg=TEXT_MUTED, bg=BG_DARK,
                           padx=16, pady=10,
                           cursor="hand2")
            btn.pack()

            rail = tk.Frame(col, bg=BG_DARK, height=2)
            rail.pack(fill=tk.X)

            k = key
            btn.bind("<Button-1>", lambda _e, k=k: self._switch_tab(k))
            self._tab_refs[key] = {"btn": btn, "rail": rail}

        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X)
        self._render_tabs()

    def _switch_tab(self, key):
        self._modo.set(key)
        self._render_tabs()
        self._trocar_modo()

    def _render_tabs(self):
        key = self._modo.get()
        for k, refs in self._tab_refs.items():
            active = (k == key)
            refs["btn"].configure(
                fg=TEXT if active else TEXT_MUTED,
                font=("Segoe UI", 10, "bold") if active else ("Segoe UI", 10),
            )
            refs["rail"].configure(bg=ACCENT if active else BG_DARK)

    # ── Status / conexão ─────────────────────────────────────────────────────

    def _verificar_status(self):
        self._status_lbl.configure(text="Verificando…", fg=TEXT_MUTED)

        def _worker():
            from core.whatsapp import status_conexao
            state, err = status_conexao()
            self.root.after(0, lambda: self._atualizar_status(state, err))

        threading.Thread(target=_worker, daemon=True).start()

    def _desconectar(self):
        if not messagebox.askyesno(
            "Desconectar",
            "Deseja desconectar o número vinculado?\n\n"
            "O WhatsApp será desvinculado e você precisará\n"
            "escanear o QR Code novamente para reconectar.",
            parent=self.root,
        ):
            return

        self._btn_desconectar.configure(text="Aguarde…", fg=TEXT_MUTED)

        def _worker():
            from core.whatsapp import desconectar_sessao
            desconectar_sessao()
            self.root.after(0, _pos)

        def _pos():
            if not self._alive():
                return
            self._btn_desconectar.configure(text="Desconectar", fg="#ff6b6b")
            self._atualizar_status("close", None)

        threading.Thread(target=_worker, daemon=True).start()

    def _atualizar_status(self, state, err):
        if not self._alive():
            return
        if err and state is None:
            self._status_lbl.configure(text=f"⚠  {err}", fg="#ff6b6b")
            self._btn_desconectar.pack_forget()
            return

        configs = {
            "open":       ("🟢  Conectado",    "#51cf66"),
            "connecting": ("🟡  Conectando…",  "#ffd700"),
            "close":      ("🔴  Desconectado", "#ff6b6b"),
        }
        text, color = configs.get(state, (f"⚪  {state}", TEXT_MUTED))
        self._status_lbl.configure(text=text, fg=color)

        if state == "open":
            self._btn_desconectar.pack(side=tk.RIGHT, padx=(0, 0))
        else:
            self._btn_desconectar.pack_forget()

    # ── QR Code ───────────────────────────────────────────────────────────────

    def _abrir_qr(self):
        self._qr_ativo = True

        win = tk.Toplevel(self.root)
        win.title("QR Code — WhatsApp")
        win.configure(bg=BG_DARK)
        win.resizable(False, False)
        win.grab_set()
        self._qr_win = win

        tk.Label(win, text="Escaneie com o WhatsApp do celular",
                 font=("Segoe UI", 12, "bold"), fg=TEXT, bg=BG_DARK
                 ).pack(pady=(20, 4))

        self._qr_img_lbl = tk.Label(win, bg=BG_DARK,
                                    text="Carregando…", fg=TEXT_MUTED,
                                    font=("Segoe UI", 10))
        self._qr_img_lbl.pack(padx=30, pady=4)

        self._qr_timer_lbl = tk.Label(win, text="", font=("Segoe UI", 9),
                                      fg=TEXT_MUTED, bg=BG_DARK)
        self._qr_timer_lbl.pack()

        self._qr_status_lbl = tk.Label(win, text="Aguardando scan…",
                                       font=("Segoe UI", 10), fg=ACCENT,
                                       bg=BG_DARK)
        self._qr_status_lbl.pack(pady=(4, 20))

        def _on_close():
            self._qr_ativo = False
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)

        def _iniciar():
            import time
            from core.whatsapp import criar_instancia, status_conexao

            def _set_status(txt, cor=TEXT_MUTED):
                self.root.after(0, lambda: self._qr_status_lbl.configure(text=txt, fg=cor))

            _set_status("Iniciando sessão…")
            data, err = criar_instancia()
            if err and "already" not in str(err).lower() and "HTTP 422" not in str(err):
                _set_status(f"Erro ao iniciar: {err}", "#ff6b6b")
                return

            _set_status("Aguardando QR Code…")
            for _ in range(20):
                time.sleep(1)
                state, _ = status_conexao()
                if state == "connecting":
                    break
                if state == "open":
                    _set_status("✅ Já conectado!", "#51cf66")
                    self.root.after(0, lambda: self._atualizar_status("open", None))
                    self.root.after(1500, lambda: _fechar_win())
                    return
            else:
                _set_status("Tempo esgotado. Reinicie o WAHA e tente novamente.", "#ff6b6b")
                return

            self.root.after(0, _carregar_qr)

        def _carregar_qr():
            if not self._qr_ativo:
                return
            threading.Thread(target=_fetch_qr, daemon=True).start()

        def _fetch_qr():
            import io, base64 as b64lib
            from PIL import Image, ImageTk
            from core.whatsapp import obter_qrcode_base64
            b64, err = obter_qrcode_base64()
            if not self._qr_ativo:
                return
            if err or not b64:
                self.root.after(0, lambda: self._qr_status_lbl.configure(
                    text=f"Erro: {err or 'QR indisponível'}", fg="#ff6b6b"))
                return
            raw = b64.split(",", 1)[1] if "," in b64 else b64
            img = Image.open(io.BytesIO(b64lib.b64decode(raw))).resize((280, 280), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.root.after(0, lambda: _exibir_qr(photo))

        def _exibir_qr(photo):
            if not self._qr_ativo:
                return
            self._qr_img_lbl.configure(image=photo, text="")
            self._qr_img_lbl.image = photo
            _iniciar_countdown(20)
            _poll_status()

        _countdown_id = [None]

        def _iniciar_countdown(segundos):
            if _countdown_id[0]:
                self.root.after_cancel(_countdown_id[0])

            def _tick(n):
                if not self._qr_ativo:
                    return
                self._qr_timer_lbl.configure(text=f"QR expira em {n}s")
                if n > 0:
                    _countdown_id[0] = self.root.after(1000, lambda: _tick(n - 1))
                else:
                    self._qr_timer_lbl.configure(text="Atualizando QR…")
                    threading.Thread(target=_fetch_qr, daemon=True).start()

            _tick(segundos)

        def _poll_status():
            if not self._qr_ativo:
                return
            def _check():
                from core.whatsapp import status_conexao
                state, _ = status_conexao()
                self.root.after(0, lambda: _reagir_status(state))
            threading.Thread(target=_check, daemon=True).start()

        def _reagir_status(state):
            if not self._qr_ativo:
                return
            if state == "open":
                self._qr_status_lbl.configure(text="✅ Conectado!", fg="#51cf66")
                self._qr_timer_lbl.configure(text="")
                self._atualizar_status("open", None)
                self.root.after(1500, lambda: _fechar_win())
            else:
                self.root.after(3000, _poll_status)

        def _fechar_win():
            self._qr_ativo = False
            if win.winfo_exists():
                win.destroy()

        threading.Thread(target=_iniciar, daemon=True).start()

    # ── Troca de modo ─────────────────────────────────────────────────────────

    def _trocar_modo(self):
        for w in self._modo_frame.winfo_children():
            w.destroy()
        if self._modo.get() == "individual":
            self._build_individual()
        else:
            self._build_lote()

    # ── INDIVIDUAL ────────────────────────────────────────────────────────────

    def _build_individual(self):
        frame = tk.Frame(self._modo_frame, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        card = tk.Frame(frame, bg=BG_CARD)
        card.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=24, pady=20)

        def _field_lbl(text):
            tk.Label(inner, text=text, font=("Segoe UI", 10, "bold"),
                     fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(0, 4))

        _field_lbl("Membro")
        membros = listar_membros()
        self._membros_ind = {f"{m['nome']} ({m['telefone'] or 'sem tel.'})": m
                             for m in membros}
        nomes = list(self._membros_ind.keys())
        self._cb_membro = ttk.Combobox(inner, values=nomes, state="readonly",
                                       font=("Segoe UI", 11), width=50)
        self._cb_membro.pack(fill=tk.X, pady=(0, 4))
        self._cb_membro.bind("<<ComboboxSelected>>", self._preencher_tel)

        _field_lbl("Telefone")
        self._tel_var = tk.StringVar()
        tk.Entry(inner, textvariable=self._tel_var,
                 font=("Segoe UI", 11), bg=DIVIDER, fg=TEXT,
                 relief=tk.FLAT, bd=0,
                 insertbackground=TEXT).pack(fill=tk.X, ipady=7, pady=(0, 4))

        _field_lbl("Mensagem")
        self._txt_ind = tk.Text(inner, height=6, font=("Segoe UI", 11),
                                bg=DIVIDER, fg=TEXT,
                                relief=tk.FLAT, bd=0, wrap=tk.WORD,
                                insertbackground=TEXT)
        self._txt_ind.pack(fill=tk.X, pady=(0, 16))

        btn_row = tk.Frame(inner, bg=BG_CARD)
        btn_row.pack(anchor=tk.W)

        tk.Button(btn_row, text="Limpar",
                  font=("Segoe UI", 10, "bold"),
                  bg=DIVIDER, fg=TEXT,
                  relief=tk.FLAT, cursor="hand2", padx=14, pady=7,
                  activebackground="#3d3d54", activeforeground=TEXT,
                  command=self._limpar_individual).pack(side=tk.LEFT, padx=(0, 8))

        self._btn_ind = tk.Button(
            btn_row, text="Enviar Mensagem",
            font=("Segoe UI", 10, "bold"),
            bg=GREEN_WPP, fg=TEXT,
            relief=tk.FLAT, cursor="hand2", padx=14, pady=7,
            activebackground="#1da851", activeforeground=TEXT,
            command=self._enviar_individual,
        )
        self._btn_ind.pack(side=tk.LEFT)

        self._result_ind = tk.Label(inner, text="", font=("Segoe UI", 10),
                                    fg="#51cf66", bg=BG_CARD)
        self._result_ind.pack(anchor=tk.W, pady=(10, 0))

    def _limpar_individual(self):
        self._cb_membro.set("")
        self._tel_var.set("")
        self._txt_ind.delete("1.0", tk.END)
        self._result_ind.configure(text="")

    def _preencher_tel(self, _ev=None):
        sel = self._cb_membro.get()
        m   = self._membros_ind.get(sel)
        if m:
            self._tel_var.set(m["telefone"] or "")

    def _enviar_individual(self):
        tel   = self._tel_var.get().strip()
        texto = self._txt_ind.get("1.0", tk.END).strip()

        if not tel:
            messagebox.showwarning("Aviso", "Selecione um membro ou informe o telefone.",
                                   parent=self.root)
            return
        if not texto:
            messagebox.showwarning("Aviso", "Digite a mensagem antes de enviar.",
                                   parent=self.root)
            return

        self._btn_ind.configure(state=tk.DISABLED, text="Enviando…")
        self._result_ind.configure(text="")

        def _worker():
            from core.whatsapp import enviar_mensagem
            _, err = enviar_mensagem(tel, texto)
            self.root.after(0, lambda: self._pos_individual(err))

        threading.Thread(target=_worker, daemon=True).start()

    def _pos_individual(self, err):
        if not self._alive():
            return
        self._btn_ind.configure(state=tk.NORMAL, text="Enviar Mensagem")
        if err:
            self._result_ind.configure(text=f"⚠ Erro: {err}", fg="#ff6b6b")
        else:
            self._result_ind.configure(text="✓ Mensagem enviada!", fg="#51cf66")

    # ── LOTE ──────────────────────────────────────────────────────────────────

    def _build_lote(self):
        frame = tk.Frame(self._modo_frame, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        card = tk.Frame(frame, bg=BG_CARD)
        card.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=24, pady=20)

        def _field_lbl(text):
            tk.Label(inner, text=text, font=("Segoe UI", 10, "bold"),
                     fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(0, 4))

        # Filtros
        _field_lbl("Filtrar destinatários")
        filtros = tk.Frame(inner, bg=BG_CARD)
        filtros.pack(fill=tk.X, pady=(0, 8))

        tk.Label(filtros, text="Função:", font=("Segoe UI", 10),
                 fg=TEXT, bg=BG_CARD).pack(side=tk.LEFT)
        self._cb_funcao = ttk.Combobox(filtros, values=["Todas"] + FUNCOES,
                                       state="readonly", font=("Segoe UI", 10), width=18)
        self._cb_funcao.set("Todas")
        self._cb_funcao.pack(side=tk.LEFT, padx=(6, 20))

        tk.Label(filtros, text="Status:", font=("Segoe UI", 10),
                 fg=TEXT, bg=BG_CARD).pack(side=tk.LEFT)
        self._cb_status = ttk.Combobox(filtros, values=["Todos"] + STATUS,
                                       state="readonly", font=("Segoe UI", 10), width=14)
        self._cb_status.set("Todos")
        self._cb_status.pack(side=tk.LEFT, padx=(6, 20))

        tk.Button(filtros, text="🔍 Buscar",
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  command=self._buscar_membros).pack(side=tk.LEFT)

        self._lbl_encontrados = tk.Label(inner, text="",
                                         font=("Segoe UI", 10), fg=TEXT_MUTED,
                                         bg=BG_CARD)
        self._lbl_encontrados.pack(anchor=tk.W, pady=(0, 10))

        _field_lbl("Mensagem")
        self._txt_lote = tk.Text(inner, height=6, font=("Segoe UI", 11),
                                 bg=DIVIDER, fg=TEXT,
                                 relief=tk.FLAT, bd=0, wrap=tk.WORD,
                                 insertbackground=TEXT)
        self._txt_lote.pack(fill=tk.X, pady=(0, 12))

        delay_row = tk.Frame(inner, bg=BG_CARD)
        delay_row.pack(anchor=tk.W, pady=(0, 16))
        tk.Label(delay_row, text="Intervalo entre mensagens:",
                 font=("Segoe UI", 10), fg=TEXT, bg=BG_CARD).pack(side=tk.LEFT)
        self._delay_var = tk.IntVar(value=3)
        tk.Spinbox(delay_row, from_=1, to=30, textvariable=self._delay_var,
                   width=4, font=("Segoe UI", 10),
                   bg=DIVIDER, fg=TEXT, relief=tk.FLAT,
                   buttonbackground=DIVIDER).pack(side=tk.LEFT, padx=(8, 4))
        tk.Label(delay_row, text="segundos", font=("Segoe UI", 10),
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)

        self._btn_lote = tk.Button(
            inner, text="Enviar para todos",
            font=("Segoe UI", 10, "bold"),
            bg=GREEN_WPP, fg=TEXT,
            relief=tk.FLAT, cursor="hand2", padx=14, pady=7,
            activebackground="#1da851", activeforeground=TEXT,
            command=self._enviar_lote,
            state=tk.DISABLED,
        )
        self._btn_lote.pack(anchor=tk.W)

        self._prog_frame = tk.Frame(inner, bg=BG_CARD)
        self._prog_frame.pack(fill=tk.X, pady=(12, 0))

        self._prog_bar = ttk.Progressbar(self._prog_frame, mode="determinate", length=400)
        self._lbl_prog = tk.Label(self._prog_frame, text="",
                                  font=("Segoe UI", 10), fg=TEXT_MUTED,
                                  bg=BG_CARD)

        self._log_frame = tk.Frame(inner, bg=BG_CARD)
        self._log_frame.pack(fill=tk.X, pady=(12, 0))

        self._membros_lote = []

    def _buscar_membros(self):
        funcao = self._cb_funcao.get()
        status = self._cb_status.get()
        self._membros_lote = listar_membros(
            funcao=None if funcao == "Todas" else funcao,
            status=None if status == "Todos" else status,
        )
        total   = len(self._membros_lote)
        com_tel = sum(1 for m in self._membros_lote if m["telefone"])

        self._lbl_encontrados.configure(
            text=f"{total} membro(s) encontrado(s) — {com_tel} com telefone cadastrado",
            fg=ACCENT if total > 0 else TEXT_MUTED)

        self._btn_lote.configure(
            state=tk.NORMAL if com_tel > 0 else tk.DISABLED,
            text=f"Enviar para {com_tel} membro(s)",
        )

    def _enviar_lote(self):
        texto = self._txt_lote.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Digite a mensagem antes de enviar.",
                                   parent=self.root)
            return
        if not self._membros_lote:
            messagebox.showwarning("Aviso", "Faça uma busca de membros primeiro.",
                                   parent=self.root)
            return

        com_tel = [m for m in self._membros_lote if m["telefone"]]
        total   = len(com_tel)

        if not messagebox.askyesno(
            "Confirmar envio",
            f"Enviar mensagem para {total} membro(s)?\n\n"
            f"Intervalo: {self._delay_var.get()}s entre cada envio.",
            parent=self.root,
        ):
            return

        self._btn_lote.configure(state=tk.DISABLED, text="Enviando…")

        self._prog_bar.configure(maximum=total, value=0)
        self._prog_bar.pack(fill=tk.X, pady=(0, 4))
        self._lbl_prog.configure(text="0 / " + str(total))
        self._lbl_prog.pack(anchor=tk.W)

        for w in self._log_frame.winfo_children():
            w.destroy()
        self._log_txt = scrolledtext.ScrolledText(
            self._log_frame, height=8, font=("Courier", 9),
            bg="#0d0d1a", fg=TEXT, relief=tk.FLAT, state=tk.DISABLED)
        self._log_txt.pack(fill=tk.X)

        delay = self._delay_var.get()

        def _progress(enviados, total, nome):
            self.root.after(0, lambda: self._atualizar_prog(enviados, total, nome))

        def _worker():
            from core.whatsapp import enviar_em_lote
            membros_dict = [dict(m) for m in com_tel]
            resultados   = enviar_em_lote(membros_dict, texto, delay=delay,
                                          progress_cb=_progress)
            self.root.after(0, lambda: self._pos_lote(resultados))

        threading.Thread(target=_worker, daemon=True).start()

    def _atualizar_prog(self, enviados, total, nome):
        if not self._alive():
            return
        self._prog_bar.configure(value=enviados)
        self._lbl_prog.configure(text=f"{enviados} / {total}  —  {nome}")

    def _pos_lote(self, resultados):
        if not self._alive():
            return
        self._btn_lote.configure(state=tk.NORMAL)
        self._btn_lote.configure(
            text=f"Enviar para {len(resultados)} membro(s)")

        self._log_txt.configure(state=tk.NORMAL)
        ok  = sum(1 for _, s, _ in resultados if s)
        err = len(resultados) - ok
        self._log_txt.insert(tk.END,
            f"{'─'*50}\nConcluído: {ok} enviados, {err} falhas\n{'─'*50}\n")
        for nome, sucesso, detalhe in resultados:
            icone = "✓" if sucesso else "✗"
            self._log_txt.insert(tk.END, f"{icone}  {nome}: {detalhe}\n")
        self._log_txt.configure(state=tk.DISABLED)
        self._log_txt.see(tk.END)
