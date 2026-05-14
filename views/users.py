"""
Tela de gerenciamento de usuários (somente Admin)
"""

import tkinter as tk
from tkinter import ttk, messagebox

from core.users import (
    listar_usuarios, criar_usuario, atualizar_usuario,
    redefinir_senha, alternar_ativo, deletar_usuario, NIVEIS_ACESSO,
)

BG_DARK    = "#0f0f23"
BG_CARD    = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#00d4ff"
BTN_COLOR  = "#667eea"
TEXT       = "#ffffff"
TEXT_MUTED = "#888888"
DIVIDER    = "#2d2d44"

_NIVEL_COLORS = {
    "Admin":    ("#ffd700", "#1a1a2e"),
    "Usuário":  ("#667eea", "#ffffff"),
}
_AVATAR_COLORS = ["#00d4ff", "#667eea", "#51cf66", "#ffa94d", "#e599f7", "#ff8787"]


class UsersWindow:
    def __init__(self, parent, root, current_user):
        self.parent       = parent
        self.root         = root
        self.current_user = current_user
        self._usuarios    = []

        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        outer = tk.Frame(self.parent, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=40, pady=24)

        self._build_header(outer)

        self._stats_frame = tk.Frame(outer, bg=BG_DARK)
        self._stats_frame.pack(fill=tk.X, pady=(0, 16))

        tk.Frame(outer, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0, 12))

        # Scrollable list
        wrapper = tk.Frame(outer, bg=BG_DARK)
        wrapper.pack(fill=tk.BOTH, expand=True)
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(wrapper, bg=BG_DARK, highlightthickness=0)
        self._sb     = tk.Scrollbar(wrapper, orient=tk.VERTICAL,
                                    command=self._canvas.yview)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        def _update_sb(lo, hi):
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                self._sb.grid_remove()
            else:
                self._sb.grid(row=0, column=1, sticky="ns")
            self._sb.set(lo, hi)

        self._canvas.configure(yscrollcommand=_update_sb)

        self._list_inner = tk.Frame(self._canvas, bg=BG_DARK)
        win_id = self._canvas.create_window((0, 0), window=self._list_inner, anchor="nw")

        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(win_id, width=e.width))
        self._list_inner.bind("<Configure>",
                              lambda e: self._canvas.configure(
                                  scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Enter>",
                          lambda e: self._canvas.bind_all(
                              "<MouseWheel>",
                              lambda ev: self._canvas.yview_scroll(-1 * (ev.delta // 120), "units")))
        self._canvas.bind("<Leave>",
                          lambda e: self._canvas.unbind_all("<MouseWheel>"))

        self._carregar_tabela()

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 12))

        left = tk.Frame(hdr, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Gerenciar Usuários",
                 font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG_DARK).pack(anchor=tk.W)
        self._subtitle_lbl = tk.Label(left, text="",
                                      font=("Segoe UI", 10),
                                      fg=TEXT_MUTED, bg=BG_DARK)
        self._subtitle_lbl.pack(anchor=tk.W)

        tk.Button(hdr, text="+ Novo Usuário",
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg=BG_DARK,
                  relief=tk.FLAT, cursor="hand2", padx=14, pady=7,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  command=self._form_novo).pack(side=tk.RIGHT)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def _carregar_tabela(self):
        self._usuarios = [dict(u) for u in listar_usuarios()]

        # Stats
        for w in self._stats_frame.winfo_children():
            w.destroy()

        total  = len(self._usuarios)
        ativos = sum(1 for u in self._usuarios if u["ativo"])
        admins = sum(1 for u in self._usuarios if u["nivel_acesso"] == "Admin")

        self._subtitle_lbl.configure(
            text=f"{total} usuário{'s' if total != 1 else ''} cadastrado{'s' if total != 1 else ''}")

        stats = [
            ("Total",          total,  TEXT_MUTED),
            ("Ativos",         ativos, "#51cf66"),
            ("Administradores",admins, "#ffd700"),
        ]
        for label, value, color in stats:
            card = tk.Frame(self._stats_frame, bg=BG_CARD)
            card.pack(side=tk.LEFT, padx=(0, 10))
            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(padx=16, pady=10)
            tk.Label(inner, text=str(value),
                     font=("Segoe UI", 18, "bold"),
                     fg=color, bg=BG_CARD).pack(anchor=tk.W)
            tk.Label(inner, text=label,
                     font=("Segoe UI", 9),
                     fg=TEXT_MUTED, bg=BG_CARD).pack(anchor=tk.W)
            tk.Frame(card, bg=color, height=2).pack(fill=tk.X, side=tk.BOTTOM)

        # List
        for w in self._list_inner.winfo_children():
            w.destroy()

        if not self._usuarios:
            tk.Label(self._list_inner,
                     text="Nenhum usuário cadastrado.",
                     font=("Segoe UI", 12), fg="#555577",
                     bg=BG_DARK).pack(pady=40)
            return

        # Column headers
        hdr = tk.Frame(self._list_inner, bg=BG_DARK)
        hdr.pack(fill=tk.X, pady=(0, 4))
        _h = dict(font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_DARK, anchor=tk.W)
        tk.Label(hdr, text="Usuário",   **_h).pack(side=tk.LEFT, padx=(56, 0), expand=True, fill=tk.X)
        tk.Label(hdr, text="Nível",     **_h, width=14).pack(side=tk.LEFT)
        tk.Label(hdr, text="Status",    **_h, width=10).pack(side=tk.LEFT)
        tk.Label(hdr, text="Ações",     **_h, width=18).pack(side=tk.LEFT, padx=(0, 4))

        for idx, u in enumerate(self._usuarios):
            self._build_row(u, idx)

    def _build_row(self, u, idx):
        is_me   = u["id"] == self.current_user["id"]
        av_col  = _AVATAR_COLORS[idx % len(_AVATAR_COLORS)]
        nome    = u["nome"] or ""
        inits   = "".join(p[0].upper() for p in nome.split()[:2]) if nome else "?"

        row = tk.Frame(self._list_inner, bg=BG_CARD, height=60)
        row.pack(fill=tk.X, pady=(0, 2))
        row.pack_propagate(False)

        inner = tk.Frame(row, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=0)

        # Avatar
        av = tk.Canvas(inner, width=34, height=34,
                       bg=BG_CARD, highlightthickness=0)
        av.pack(side=tk.LEFT, padx=(0, 10))
        av.create_oval(2, 2, 32, 32, fill=av_col, outline="")
        av.create_text(17, 17, text=inits,
                       font=("Segoe UI", 10, "bold"), fill=BG_DARK)

        # Name + email
        name_col = tk.Frame(inner, bg=BG_CARD)
        name_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        name_txt = nome + "  (você)" if is_me else nome
        tk.Label(name_col, text=name_txt,
                 font=("Segoe UI", 10, "bold"),
                 fg=ACCENT if is_me else TEXT,
                 bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W)
        tk.Label(name_col, text=u["email"] or "",
                 font=("Courier", 9),
                 fg=TEXT_MUTED, bg=BG_CARD, anchor=tk.W).pack(anchor=tk.W)

        # Level badge
        nb_bg, nb_fg = _NIVEL_COLORS.get(u["nivel_acesso"], (DIVIDER, TEXT))
        nivel_frame = tk.Frame(inner, bg=BG_CARD, width=110)
        nivel_frame.pack(side=tk.LEFT, padx=(0, 8))
        nivel_frame.pack_propagate(False)
        tk.Label(nivel_frame, text=f"  {u['nivel_acesso']}  ",
                 font=("Segoe UI", 8, "bold"),
                 bg=nb_bg, fg=nb_fg).pack(anchor=tk.W, pady=2)

        # Active pill
        ativo = bool(u["ativo"])
        st_bg  = "#1a3a1a" if ativo else "#3a1a1a"
        st_fg  = "#51cf66" if ativo else "#ff6b6b"
        st_txt = "● Ativo" if ativo else "○ Inativo"
        st_frame = tk.Frame(inner, bg=BG_CARD, width=80)
        st_frame.pack(side=tk.LEFT, padx=(0, 8))
        st_frame.pack_propagate(False)
        tk.Label(st_frame, text=st_txt,
                 font=("Segoe UI", 8, "bold"),
                 bg=st_bg, fg=st_fg,
                 padx=6, pady=2).pack(anchor=tk.W, pady=2)

        # Action buttons
        uid = u["id"]
        btn_frame = tk.Frame(inner, bg=BG_CARD, width=130)
        btn_frame.pack(side=tk.LEFT)
        btn_frame.pack_propagate(False)
        btn_inner = tk.Frame(btn_frame, bg=BG_CARD)
        btn_inner.pack(side=tk.RIGHT)

        _ib = dict(relief=tk.FLAT, cursor="hand2",
                   font=("Segoe UI", 9), padx=5, pady=2)

        tk.Button(btn_inner, text="✏",
                  bg=BG_CARD, fg=BTN_COLOR,
                  activebackground=DIVIDER, activeforeground=BTN_COLOR,
                  command=lambda uid=uid: self._form_editar(uid), **_ib
                  ).pack(side=tk.LEFT)

        tk.Button(btn_inner, text="🔑",
                  bg=BG_CARD, fg="#ffd700",
                  activebackground=DIVIDER, activeforeground="#ffd700",
                  command=lambda uid=uid: self._form_senha(uid), **_ib
                  ).pack(side=tk.LEFT)

        if not is_me:
            toggle_txt = "⏸" if ativo else "▶"
            toggle_fg  = "#ff6b6b" if ativo else "#51cf66"
            tk.Button(btn_inner, text=toggle_txt,
                      bg=BG_CARD, fg=toggle_fg,
                      activebackground=DIVIDER, activeforeground=toggle_fg,
                      command=lambda uid=uid: self._toggle_ativo(uid), **_ib
                      ).pack(side=tk.LEFT)

            tk.Button(btn_inner, text="🗑",
                      bg=BG_CARD, fg="#ff6b6b",
                      activebackground="#2d1e1e", activeforeground="#ff6b6b",
                      command=lambda uid=uid, u=u: self._excluir(uid, u), **_ib
                      ).pack(side=tk.LEFT)

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _toggle_ativo(self, uid):
        alternar_ativo(uid)
        self._carregar_tabela()

    def _excluir(self, uid, u):
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o usuário '{u['nome']}'?\nEsta ação não pode ser desfeita.",
            parent=self.root,
        ):
            return
        deletar_usuario(uid)
        self._carregar_tabela()

    # ── Formulários ───────────────────────────────────────────────────────────

    def _abrir_form(self, titulo, usuario=None):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.configure(bg=BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        w, h = (460, 480) if usuario else (460, 560)
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        card = tk.Frame(win, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        tk.Label(card, text=titulo, font=("Segoe UI", 14, "bold"),
                 fg=ACCENT, bg=BG_CARD).pack(anchor=tk.W, pady=(0, 18))

        entry_kw = dict(bg=DIVIDER, fg=TEXT, relief=tk.FLAT, bd=0,
                        font=("Segoe UI", 11), insertbackground=TEXT)

        def campo(label, show=None, valor=""):
            tk.Label(card, text=label, font=("Segoe UI", 10, "bold"),
                     fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(8, 2))
            kw = dict(entry_kw)
            if show:
                kw["show"] = show
            e = tk.Entry(card, **kw)
            e.pack(fill=tk.X, ipady=7)
            if valor:
                e.insert(0, valor)
            return e

        e_nome  = campo("Nome Completo", valor=usuario["nome"]  if usuario else "")
        e_email = campo("E-mail",        valor=usuario["email"] if usuario else "")

        e_senha = e_conf = None
        if not usuario:
            e_senha = campo("Senha",           show="•")
            e_conf  = campo("Confirmar Senha", show="•")

        tk.Label(card, text="Nível de Acesso", font=("Segoe UI", 10, "bold"),
                 fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(8, 2))
        nivel_var = tk.StringVar(value=usuario["nivel_acesso"] if usuario else "Usuário")
        ttk.Combobox(card, values=NIVEIS_ACESSO, textvariable=nivel_var,
                     state="readonly", font=("Segoe UI", 11)).pack(fill=tk.X, ipady=4)

        err_lbl = tk.Label(card, text="", font=("Segoe UI", 10),
                           fg="#ff6b6b", bg=BG_CARD)
        err_lbl.pack(anchor=tk.W, pady=(8, 0))

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=(16, 0))

        def _salvar():
            nome  = e_nome.get().strip()
            email = e_email.get().strip()
            nivel = nivel_var.get()

            if not nome or not email:
                err_lbl.configure(text="Nome e e-mail são obrigatórios.")
                return

            if usuario:
                err = atualizar_usuario(usuario["id"], nome, email, nivel)
                if err:
                    err_lbl.configure(text=err)
                    return
            else:
                senha   = e_senha.get()
                confirm = e_conf.get()
                if not senha:
                    err_lbl.configure(text="Informe uma senha.")
                    return
                if len(senha) < 6:
                    err_lbl.configure(text="Mínimo 6 caracteres.")
                    return
                if senha != confirm:
                    err_lbl.configure(text="As senhas não coincidem.")
                    return
                _, err = criar_usuario(nome, email, senha, nivel)
                if err:
                    err_lbl.configure(text=err)
                    return

            win.destroy()
            self._carregar_tabela()

        _b = dict(relief=tk.FLAT, cursor="hand2",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8)
        tk.Button(btn_row, text="Salvar",
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  command=_salvar, **_b).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="Cancelar",
                  bg=DIVIDER, fg="#aaaaaa",
                  activebackground="#3d3d54", activeforeground=TEXT,
                  command=win.destroy, **_b).pack(side=tk.LEFT)

    def _form_novo(self):
        self._abrir_form("Novo Usuário")

    def _form_editar(self, uid):
        from core.users import obter_usuario
        u = obter_usuario(uid)
        if u:
            self._abrir_form("Editar Usuário", usuario=u)

    # ── Redefinir senha ───────────────────────────────────────────────────────

    def _form_senha(self, uid):
        from core.users import obter_usuario
        u = obter_usuario(uid)
        if not u:
            return

        win = tk.Toplevel(self.root)
        win.title("Redefinir Senha")
        win.configure(bg=BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        w, h = 400, 300
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        card = tk.Frame(win, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        tk.Label(card, text=f"Redefinir senha de\n{u['nome']}",
                 font=("Segoe UI", 13, "bold"),
                 fg=ACCENT, bg=BG_CARD,
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 16))

        kw = dict(bg=DIVIDER, fg=TEXT, relief=tk.FLAT, bd=0,
                  font=("Segoe UI", 11), show="•", insertbackground=TEXT)

        tk.Label(card, text="Nova Senha", font=("Segoe UI", 10, "bold"),
                 fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(0, 2))
        e_nova = tk.Entry(card, **kw)
        e_nova.pack(fill=tk.X, ipady=7)

        tk.Label(card, text="Confirmar Senha", font=("Segoe UI", 10, "bold"),
                 fg="#aaaaaa", bg=BG_CARD).pack(anchor=tk.W, pady=(10, 2))
        e_conf = tk.Entry(card, **kw)
        e_conf.pack(fill=tk.X, ipady=7)

        err_lbl = tk.Label(card, text="", font=("Segoe UI", 10),
                           fg="#ff6b6b", bg=BG_CARD)
        err_lbl.pack(anchor=tk.W, pady=(6, 0))

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=(12, 0))

        def _salvar():
            nova    = e_nova.get()
            confirm = e_conf.get()
            if len(nova) < 6:
                err_lbl.configure(text="Mínimo 6 caracteres.")
                return
            if nova != confirm:
                err_lbl.configure(text="As senhas não coincidem.")
                return
            redefinir_senha(uid, nova)
            win.destroy()
            messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!",
                                parent=self.root)

        _b = dict(relief=tk.FLAT, cursor="hand2",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8)
        tk.Button(btn_row, text="Salvar",
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#00b8d9", activeforeground=BG_DARK,
                  command=_salvar, **_b).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="Cancelar",
                  bg=DIVIDER, fg="#aaaaaa",
                  activebackground="#3d3d54", activeforeground=TEXT,
                  command=win.destroy, **_b).pack(side=tk.LEFT)
