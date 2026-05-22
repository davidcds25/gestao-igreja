import sys
import tkinter as tk
from pathlib import Path

from design.ui import COLORS, SPACING, FONTS
from design.ui.components import cross_icon


def _config_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "config.py"
    return Path(__file__).parent.parent / "config.py"


def _escape(s: str) -> str:
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return s


def _write_config(app_name: str, email: str, password: str, api_key: str):
    content = (
        f'APP_NAME         = "{_escape(app_name)}"\n'
        f'WHATSAPP_API_KEY = "{_escape(api_key)}"\n'
        f'ADMIN_EMAIL      = "{_escape(email)}"\n'
        f'ADMIN_PASSWORD   = "{_escape(password)}"\n'
    )
    _config_path().write_text(content, encoding="utf-8")


class SetupWizard:

    def __init__(self, root: tk.Tk, on_complete):
        self.root = root
        self.on_complete = on_complete
        self.root.title("Configuração Inicial")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.state("zoomed")
        self.root.minsize(960, 600)
        self._build()

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self):
        main = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=23, uniform="setup")
        main.columnconfigure(1, weight=20, uniform="setup")
        main.rowconfigure(0, weight=1)

        self._build_brand(main).grid(row=0, column=0, sticky="nsew")
        self._build_form(main).grid(row=0, column=1, sticky="nsew")

        self.root.bind("<Return>", lambda e: self._submit())

    def _build_brand(self, parent):
        bg = COLORS["sidebar_bg"]
        panel = tk.Frame(parent, bg=bg)

        sep = tk.Frame(panel, bg=COLORS["divider"], width=1)
        sep.place(relx=1.0, rely=0, relheight=1.0, x=-1, anchor="ne")

        inner = tk.Frame(panel, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True,
                   padx=SPACING[12] + SPACING[2],
                   pady=SPACING[10] + SPACING[2])

        # Logo
        logo_row = tk.Frame(inner, bg=bg)
        logo_row.pack(anchor=tk.W)

        logo_box = tk.Frame(logo_row, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["divider"],
                            highlightthickness=1,
                            width=44, height=44)
        logo_box.pack(side=tk.LEFT)
        logo_box.pack_propagate(False)
        ch = tk.Frame(logo_box, bg=COLORS["bg_card"])
        ch.place(relx=0.5, rely=0.5, anchor="center")
        cross_icon(ch, size=20, color=COLORS["accent"], bg=COLORS["bg_card"]).pack()

        brand_text = tk.Frame(logo_row, bg=bg)
        brand_text.pack(side=tk.LEFT, padx=(SPACING[3], 0))
        tk.Label(brand_text, text="Sistema de Gestão",
                 font=(FONTS["body"][0], 17, "bold"),
                 bg=bg, fg=COLORS["text"]).pack(anchor=tk.W)
        tk.Label(brand_text,
                 text="    ".join(list("CONFIGURAÇÃO INICIAL")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(2, 0))

        tk.Frame(inner, bg=bg).pack(fill=tk.BOTH, expand=True)

        # Headline
        msg = tk.Frame(inner, bg=bg)
        msg.pack(fill=tk.X, anchor=tk.W)

        tk.Label(msg, text="    ".join(list("BEM-VINDO")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)

        tk.Label(msg,
                 text="Configure seu\nsistema antes\nde começar.",
                 font=(FONTS["body"][0], 28, "bold"),
                 bg=bg, fg=COLORS["text"],
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(SPACING[3], SPACING[3]))

        tk.Label(msg,
                 text=("Preencha as informações da sua organização.\n"
                       "Esses dados criam o acesso inicial e definem\n"
                       "o nome exibido no sistema."),
                 font=FONTS["body"],
                 bg=bg, fg=COLORS["text_muted"],
                 justify=tk.LEFT).pack(anchor=tk.W)

        tk.Frame(inner, bg=bg).pack(fill=tk.BOTH, expand=True)

        # Footer
        footer = tk.Frame(inner, bg=bg)
        footer.pack(fill=tk.X)
        tk.Label(footer, text="Primeiro Acesso", font=FONTS["tiny"],
                 bg=bg, fg=COLORS["text_very_dim"]).pack(side=tk.LEFT)

        return panel

    def _build_form(self, parent):
        bg = COLORS["bg_dark"]
        panel = tk.Frame(parent, bg=bg)

        tk.Frame(panel, bg=bg).pack(fill=tk.Y, expand=True)

        form_wrap = tk.Frame(panel, bg=bg)
        form_wrap.pack(fill=tk.X)
        form_wrap.columnconfigure(0, weight=1)
        form_wrap.columnconfigure(1, weight=0, minsize=380)
        form_wrap.columnconfigure(2, weight=1)

        form = tk.Frame(form_wrap, bg=bg, width=380)
        form.grid(row=0, column=1, sticky="ew")

        tk.Label(form,
                 text="    ".join(list("CONFIGURAÇÃO INICIAL")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)
        tk.Label(form, text="Dados da organização",
                 font=(FONTS["body"][0], 22, "bold"),
                 bg=bg, fg=COLORS["text"]).pack(anchor=tk.W, pady=(SPACING[2], SPACING[1]))
        tk.Label(form,
                 text="Estas informações configuram o acesso inicial ao sistema.",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, SPACING[5]))

        # Campos
        self._name_var = tk.StringVar()
        self._build_field(
            form, "Nome da Igreja", self._name_var,
            "Ex: Igreja Comunidade Cristã", "🏛"
        ).pack(fill=tk.X, pady=(0, SPACING[3]))

        self._email_var = tk.StringVar()
        self._build_field(
            form, "E-mail do Administrador", self._email_var,
            "admin@suaigreja.com", "✉"
        ).pack(fill=tk.X, pady=(0, SPACING[3]))

        self._pass_var = tk.StringVar()
        self._build_field(
            form, "Senha do Administrador", self._pass_var,
            "Mínimo 6 caracteres", "🔒", show="•"
        ).pack(fill=tk.X, pady=(0, SPACING[3]))

        self._pass2_var = tk.StringVar()
        self._build_field(
            form, "Confirmar Senha", self._pass2_var,
            "Repita a senha", "🔒", show="•"
        ).pack(fill=tk.X, pady=(0, SPACING[2]))

        self._waha_var = tk.StringVar()
        self._build_field(
            form, "Chave WhatsApp — API Key (opcional)", self._waha_var,
            "Deixe em branco se não usar WhatsApp", "💬"
        ).pack(fill=tk.X, pady=(0, SPACING[1]))
        tk.Label(form, text="Pode ser configurado depois em config.py.",
                 font=FONTS["tiny"], bg=bg,
                 fg=COLORS["text_very_dim"]).pack(anchor=tk.W, pady=(0, SPACING[3]))

        # Erro
        self._error_var = tk.StringVar()
        tk.Label(form, textvariable=self._error_var,
                 font=FONTS["small"], bg=bg, fg=COLORS["danger"],
                 anchor=tk.W).pack(fill=tk.X, pady=(SPACING[2], 0))

        # Botão
        self._btn = tk.Button(
            form, text="SALVAR E CONTINUAR  →",
            font=(FONTS["body"][0], 11, "bold"),
            bg=COLORS["accent"], fg=COLORS["bg_dark"],
            activebackground=COLORS["accent"], activeforeground=COLORS["bg_dark"],
            relief=tk.FLAT, bd=0,
            padx=SPACING[5], pady=SPACING[3],
            cursor="hand2",
            command=self._submit,
        )
        self._btn.pack(fill=tk.X, pady=(SPACING[5], SPACING[5]))

        tk.Frame(form, bg=COLORS["divider_soft"], height=1).pack(
            fill=tk.X, pady=(0, SPACING[3]))
        tk.Label(form,
                 text="As configurações serão salvas em config.py ao lado do sistema.",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_muted"]).pack()

        tk.Frame(panel, bg=bg).pack(fill=tk.Y, expand=True)
        return panel

    def _build_field(self, parent, label, var, placeholder, icon=None, show=None):
        bg = COLORS["bg_dark"]
        wrap = tk.Frame(parent, bg=bg)

        head = tk.Frame(wrap, bg=bg)
        head.pack(fill=tk.X, pady=(0, SPACING[1] + 2))
        tk.Label(head, text=label, font=FONTS["body_strong"],
                 bg=bg, fg=COLORS["text"]).pack(side=tk.LEFT)

        box = tk.Frame(wrap, bg=COLORS["input_bg"],
                       highlightbackground=COLORS["divider"],
                       highlightcolor=COLORS["accent"],
                       highlightthickness=1, bd=0)
        box.pack(fill=tk.X, ipady=2)

        if icon:
            tk.Label(box, text=icon, font=(FONTS["body"][0], 12),
                     bg=COLORS["input_bg"], fg=COLORS["text_muted"],
                     padx=SPACING[3]).pack(side=tk.LEFT)

        entry = tk.Entry(box, textvariable=var, font=FONTS["body"],
                         bg=COLORS["input_bg"], fg=COLORS["text"],
                         insertbackground=COLORS["text"],
                         relief=tk.FLAT, bd=0, show=show or "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                   ipady=8, padx=(0 if icon else SPACING[3], SPACING[3]))

        if placeholder:
            entry.insert(0, placeholder)
            entry.configure(fg=COLORS["text_very_dim"], show="")

            def _fi(_e, en=entry, ph=placeholder, sh=show):
                if en.get() == ph:
                    en.delete(0, tk.END)
                    en.configure(fg=COLORS["text"])
                    if sh:
                        en.configure(show=sh)

            def _fo(_e, en=entry, ph=placeholder):
                if not en.get():
                    en.configure(show="")
                    en.insert(0, ph)
                    en.configure(fg=COLORS["text_very_dim"])

            entry.bind("<FocusIn>", _fi)
            entry.bind("<FocusOut>", _fo)

        return wrap

    # ── Submit ─────────────────────────────────────────────────────────

    _PLACEHOLDERS = {
        "_name_var":  "Ex: Igreja Comunidade Cristã",
        "_email_var": "admin@suaigreja.com",
        "_pass_var":  "Mínimo 6 caracteres",
        "_pass2_var": "Repita a senha",
        "_waha_var":  "Deixe em branco se não usar WhatsApp",
    }

    def _val(self, attr: str) -> str:
        raw = getattr(self, attr).get().strip()
        return "" if raw == self._PLACEHOLDERS[attr] else raw

    def _submit(self):
        name    = self._val("_name_var")
        email   = self._val("_email_var")
        pwd     = self._val("_pass_var")
        pwd2    = self._val("_pass2_var")
        api_key = self._val("_waha_var")

        if not name:
            self._error_var.set("✕   Informe o nome da organização.")
            return
        if not email or "@" not in email:
            self._error_var.set("✕   Informe um e-mail válido.")
            return
        if len(pwd) < 6:
            self._error_var.set("✕   A senha deve ter no mínimo 6 caracteres.")
            return
        if pwd != pwd2:
            self._error_var.set("✕   As senhas não conferem.")
            return

        self._btn.configure(text="SALVANDO…", state=tk.DISABLED,
                            bg=COLORS["divider"], fg=COLORS["text_muted"])
        self.root.update_idletasks()

        try:
            _write_config(name, email, pwd, api_key)
            self._error_var.set("")
            for w in self.root.winfo_children():
                w.destroy()
            self.root.unbind("<Return>")
            self.on_complete()
        except Exception as e:
            self._btn.configure(text="SALVAR E CONTINUAR  →", state=tk.NORMAL,
                                bg=COLORS["accent"], fg=COLORS["bg_dark"])
            self._error_var.set(f"✕   Erro ao salvar configuração: {e}")
