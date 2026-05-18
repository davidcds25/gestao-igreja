"""
Interface gráfica de login e shell principal do aplicativo
"""

import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path

from design.app_shell import AppShell
from design.pages import home, members, activities, whatsapp, users, reports, prayers
from design.ui import COLORS, SPACING, FONTS
from design.ui.components import cross_icon

from core.auth import authenticate_user
from core.database import init_database
from core.verse import get_verse_of_day
from views.dialogs import (
    open_member_form, confirm_delete_member,
    open_activity_form, confirm_done_activity, confirm_cancel_activity,
    open_user_form, open_reset_password_form,
    toggle_user_active, confirm_delete_user,
    open_prayer_form, confirm_delete_prayer,
)

try:
    from config import APP_NAME
except ImportError:
    APP_NAME = "Sistema de Gestão"

_PREFS_FILE = Path(__file__).parent.parent / "user_prefs.json"

_MESES_SHORT = ["JAN","FEV","MAR","ABR","MAI","JUN",
                 "JUL","AGO","SET","OUT","NOV","DEZ"]

_FUNCAO_COLOR = {
    "Pastor(a)":       "#ffd700",
    "Presbítero":      "#9b59b6",
    "Diácono(a)":      "#667eea",
    "Evangelista":     "#ffa94d",
    "Líder de Célula": "#51cf66",
    "Louvor":          "#00d4ff",
}
_MEMBER_COLORS = [
    "#667eea", "#51cf66", "#9b59b6", "#00d4ff",
    "#ffa94d", "#ff6b6b", "#ffd700", "#74c0fc",
]
_USER_LEVEL_COLORS = {"Admin": "#00d4ff", "Coordenador": "#667eea"}
_STATUS_MAP = {
    "Concluído":    "Realizado",
    "Em Andamento": "Realizado",
    "Adiado":       "Cancelado",
}


def _load_prefs() -> dict:
    try:
        if _PREFS_FILE.exists():
            return json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_prefs(data: dict):
    try:
        _PREFS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


class LoginWindow:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.state("zoomed")
        self.current_user = None
        self.setup_login_screen()

    # ── TELA DE LOGIN ──────────────────────────────────────────────

    def setup_login_screen(self):
        self.root.unbind("<Return>")
        self._clear_root()
        self.root.minsize(960, 600)
        self.root.configure(bg=COLORS["bg_dark"])

        main = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=23, uniform="login")
        main.columnconfigure(1, weight=20, uniform="login")
        main.rowconfigure(0, weight=1)

        self._build_login_brand(main).grid(row=0, column=0, sticky="nsew")
        self._build_login_form(main).grid(row=0, column=1, sticky="nsew")

        self.root.bind("<Return>", lambda e: self._login_submit())

    def _build_login_brand(self, parent):
        bg = COLORS["sidebar_bg"]
        panel = tk.Frame(parent, bg=bg)

        sep = tk.Frame(panel, bg=COLORS["divider"], width=1)
        sep.place(relx=1.0, rely=0, relheight=1.0, x=-1, anchor="ne")

        inner = tk.Frame(panel, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True,
                   padx=SPACING[12] + SPACING[2],
                   pady=SPACING[10] + SPACING[2])

        # ── Logo ──────────────────────────────────────────────────
        logo_row = tk.Frame(inner, bg=bg)
        logo_row.pack(anchor=tk.W)

        logo_box = tk.Frame(logo_row, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["divider"],
                            highlightthickness=1,
                            width=44, height=44)
        logo_box.pack(side=tk.LEFT)
        logo_box.pack_propagate(False)
        cross_holder = tk.Frame(logo_box, bg=COLORS["bg_card"])
        cross_holder.place(relx=0.5, rely=0.5, anchor="center")
        cross_icon(cross_holder, size=20,
                   color=COLORS["accent"], bg=COLORS["bg_card"]).pack()

        brand_text = tk.Frame(logo_row, bg=bg)
        brand_text.pack(side=tk.LEFT, padx=(SPACING[3], 0))
        tk.Label(brand_text, text=APP_NAME,
                 font=(FONTS["body"][0], 17, "bold"),
                 bg=bg, fg=COLORS["text"]).pack(anchor=tk.W)
        tk.Label(brand_text,
                 text="    ".join(list("SISTEMA DE GESTÃO")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(2, 0))

        tk.Frame(inner, bg=bg).pack(fill=tk.BOTH, expand=True)

        # ── Headline ──────────────────────────────────────────────
        msg = tk.Frame(inner, bg=bg)
        msg.pack(fill=tk.X, anchor=tk.W)

        tk.Label(msg, text="    ".join(list("BEM-VINDO DE VOLTA")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)

        tk.Label(msg,
                 text="Cuide de cada nome\nda sua igreja\ncom clareza.",
                 font=(FONTS["body"][0], 28, "bold"),
                 bg=bg, fg=COLORS["text"],
                 justify=tk.LEFT).pack(anchor=tk.W,
                                       pady=(SPACING[3], SPACING[3]))

        tk.Label(msg,
                 text=("Entre na sua conta para acessar membros, atividades,\n"
                       "mensagens em lote pelo WhatsApp e relatórios do mês."),
                 font=FONTS["body"],
                 bg=bg, fg=COLORS["text_muted"],
                 justify=tk.LEFT).pack(anchor=tk.W)

        # ── Verse card (atualizado via StringVar após API/cache) ──
        verse_wrap = tk.Frame(inner, bg=bg)
        verse_wrap.pack(fill=tk.X, pady=(SPACING[6], SPACING[6]))

        vc = tk.Frame(verse_wrap, bg=COLORS["bg_card"],
                      highlightbackground=COLORS["divider"],
                      highlightthickness=1)
        vc.pack(fill=tk.X)
        tk.Frame(vc, bg=COLORS["verse_gold"], width=4).pack(side=tk.LEFT, fill=tk.Y)

        verse_body = tk.Frame(vc, bg=COLORS["bg_card"])
        verse_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                        padx=SPACING[4], pady=SPACING[3])

        verse_head = tk.Frame(verse_body, bg=COLORS["bg_card"])
        verse_head.pack(anchor=tk.W, fill=tk.X)
        cross_icon(verse_head, size=11,
                   color=COLORS["verse_gold"], bg=COLORS["bg_card"]).pack(side=tk.LEFT)
        tk.Label(verse_head,
                 text="    ".join(list("VERSÍCULO DO DIA")),
                 font=FONTS["section"],
                 bg=COLORS["bg_card"], fg=COLORS["verse_gold"]).pack(
                     side=tk.LEFT, padx=(SPACING[2], 0))

        verse_text_var = tk.StringVar(value="")
        verse_ref_var  = tk.StringVar(value="")

        tk.Label(verse_body,
                 textvariable=verse_text_var,
                 font=FONTS["body_italic"],
                 bg=COLORS["bg_card"], fg=COLORS["text"],
                 wraplength=380, justify=tk.LEFT).pack(
                     anchor=tk.W, pady=(SPACING[2], SPACING[1]))

        tk.Label(verse_body,
                 textvariable=verse_ref_var,
                 font=FONTS["small_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["verse_gold"]).pack(anchor=tk.E)

        def _on_verse(v):
            def _update():
                if panel.winfo_exists():
                    verse_text_var.set(f'"{v["text"]}"')
                    verse_ref_var.set(f'— {v["reference"]}')
            self.root.after(0, _update)

        get_verse_of_day(_on_verse)

        # ── Footer ────────────────────────────────────────────────
        footer = tk.Frame(inner, bg=bg)
        footer.pack(fill=tk.X, anchor=tk.W)
        tk.Label(footer, text="banco local", font=FONTS["tiny"],
                 bg=bg, fg=COLORS["text_very_dim"]).pack(side=tk.LEFT)

        return panel

    def _build_login_form(self, parent):
        bg = COLORS["bg_dark"]
        panel = tk.Frame(parent, bg=bg)

        # status top-right
        status_row = tk.Frame(panel, bg=bg)
        status_row.pack(anchor=tk.NE, padx=SPACING[6], pady=SPACING[5])
        tk.Frame(status_row, bg=COLORS["success"],
                 width=7, height=7).pack(side=tk.LEFT, pady=(4, 0))
        tk.Label(status_row, text="  Banco conectado · igreja.db",
                 font=FONTS["tiny"],
                 bg=bg, fg=COLORS["text_muted"]).pack(side=tk.LEFT)

        tk.Frame(panel, bg=bg).pack(fill=tk.Y, expand=True)

        form_wrap = tk.Frame(panel, bg=bg)
        form_wrap.pack(fill=tk.X)
        form_wrap.columnconfigure(0, weight=1)
        form_wrap.columnconfigure(1, weight=0, minsize=380)
        form_wrap.columnconfigure(2, weight=1)

        form = tk.Frame(form_wrap, bg=bg, width=380)
        form.grid(row=0, column=1, sticky="ew")

        # ── Form header ───────────────────────────────────────────
        tk.Label(form,
                 text="    ".join(list("ACESSO AO SISTEMA")),
                 font=FONTS["section"],
                 bg=bg, fg=COLORS["text_muted"]).pack(anchor=tk.W)
        tk.Label(form, text="Entrar na sua conta",
                 font=(FONTS["body"][0], 22, "bold"),
                 bg=bg, fg=COLORS["text"]).pack(
                     anchor=tk.W, pady=(SPACING[2], SPACING[1]))
        tk.Label(form,
                 text="Use o e-mail e senha cadastrados pelo administrador.",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack(
                     anchor=tk.W, pady=(0, SPACING[5]))

        # ── E-mail (pré-preenchido se "lembrar" estava marcado) ──
        prefs = _load_prefs()
        saved_email = prefs.get("email", "")

        self._email_var = tk.StringVar(value="")
        self._login_build_field(
            form,
            label="E-mail",
            var=self._email_var,
            placeholder="seu.email@igreja.com",
            icon="✉",
            prefill=saved_email,
        ).pack(fill=tk.X, pady=(0, SPACING[3]))

        # ── Senha ─────────────────────────────────────────────────
        self._password_var = tk.StringVar(value="")
        self._login_build_field(
            form,
            label="Senha",
            var=self._password_var,
            placeholder="••••••••",
            icon="🔒",
            show="•",
        ).pack(fill=tk.X, pady=(0, SPACING[3]))

        # ── Lembrar deste computador ──────────────────────────────
        self._remember_var = tk.BooleanVar(value=bool(saved_email))
        remember_row = tk.Frame(form, bg=bg)
        remember_row.pack(anchor=tk.W, pady=(SPACING[1], 0))
        tk.Checkbutton(remember_row,
                       variable=self._remember_var,
                       text="Lembrar deste computador",
                       font=FONTS["body"],
                       bg=bg,
                       fg=COLORS["text_dim"],
                       activebackground=bg,
                       activeforeground=COLORS["text"],
                       selectcolor=COLORS["input_bg"],
                       relief=tk.FLAT, bd=0,
                       cursor="hand2").pack(anchor=tk.W)

        # ── Error label ───────────────────────────────────────────
        self._login_error_var = tk.StringVar(value="")
        tk.Label(form,
                 textvariable=self._login_error_var,
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["danger"],
                 anchor=tk.W).pack(fill=tk.X, pady=(SPACING[3], 0))

        # ── Enter button ──────────────────────────────────────────
        self._login_btn = tk.Button(
            form,
            text="ENTRAR NO SISTEMA  →",
            font=(FONTS["body"][0], 11, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["bg_dark"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg_dark"],
            relief=tk.FLAT, bd=0,
            padx=SPACING[5],
            pady=SPACING[3],
            cursor="hand2",
            command=self._login_submit,
        )
        self._login_btn.pack(fill=tk.X, pady=(SPACING[5], SPACING[5]))

        tk.Frame(form, bg=COLORS["divider_soft"], height=1).pack(
            fill=tk.X, pady=(0, SPACING[3]))
        tk.Label(form,
                 text="Sem acesso? Fale com o administrador da igreja.",
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["text_muted"]).pack()

        tk.Frame(panel, bg=bg).pack(fill=tk.Y, expand=True)

        return panel

    def _login_build_field(self, parent, *, label, var, placeholder,
                            icon=None, show=None, prefill=""):
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
            tk.Label(box, text=icon,
                     font=(FONTS["body"][0], 12),
                     bg=COLORS["input_bg"], fg=COLORS["text_muted"],
                     padx=SPACING[3]).pack(side=tk.LEFT)

        entry = tk.Entry(box,
                         textvariable=var,
                         font=FONTS["body"],
                         bg=COLORS["input_bg"],
                         fg=COLORS["text"],
                         insertbackground=COLORS["text"],
                         relief=tk.FLAT, bd=0,
                         show=show or "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                   ipady=8,
                   padx=(0 if icon else SPACING[3], SPACING[3]))

        # If we have a saved email, pre-fill it (no placeholder behavior)
        if prefill:
            entry.insert(0, prefill)
            entry.configure(fg=COLORS["text"])
            if show:
                entry.configure(show=show)
            return wrap

        # Placeholder behavior (only when no prefill)
        if placeholder and not var.get():
            entry.insert(0, placeholder)
            entry.configure(fg=COLORS["text_very_dim"], show="")

            def _focus_in(_e, en=entry, ph=placeholder, sh=show):
                if en.get() == ph:
                    en.delete(0, tk.END)
                    en.configure(fg=COLORS["text"])
                    if sh:
                        en.configure(show=sh)

            def _focus_out(_e, en=entry, ph=placeholder):
                if not en.get():
                    en.configure(show="")
                    en.insert(0, ph)
                    en.configure(fg=COLORS["text_very_dim"])

            entry.bind("<FocusIn>", _focus_in)
            entry.bind("<FocusOut>", _focus_out)

        return wrap

    def _login_submit(self):
        email = self._email_var.get().strip()
        senha = self._password_var.get().strip()

        if email in ("", "seu.email@igreja.com") or "@" not in email:
            self._login_error_var.set("✕   Informe um e-mail válido.")
            return
        if senha in ("", "••••••••"):
            self._login_error_var.set("✕   Informe sua senha.")
            return

        self._login_btn.configure(text="ENTRANDO…", state=tk.DISABLED,
                                   bg=COLORS["divider"], fg=COLORS["text_muted"])
        self.root.update_idletasks()

        user = authenticate_user(email, senha)

        if user:
            # Salva ou apaga o e-mail conforme a preferência
            if self._remember_var.get():
                _save_prefs({"email": email})
            else:
                _save_prefs({})
            self._login_error_var.set("")
            self.current_user = user
            self.show_main_menu()
        else:
            self._login_btn.configure(text="ENTRAR NO SISTEMA  →",
                                       state=tk.NORMAL,
                                       bg=COLORS["accent"],
                                       fg=COLORS["bg_dark"])
            self._login_error_var.set("✕   E-mail ou senha inválidos. Tente novamente.")

    # ── SHELL PRINCIPAL ────────────────────────────────────────────

    def show_main_menu(self):
        self._clear_root()
        self.root.unbind("<Return>")

        try:
            self.root.state("zoomed")
        except Exception:
            self.root.geometry("1280x800")

        shell_user = {
            "nome":  self.current_user["nome"],
            "nivel": self.current_user["nivel_acesso"],
            "email": self.current_user["email"],
        }

        root = self.root
        uid  = self.current_user["id"]
        refresh_shell = lambda: self.show_main_menu()

        shell = AppShell(
            self.root,
            current_user=shell_user,
            on_logout=self.logout,
            on_profile=self.show_profile,
            on_edit_profile=lambda: open_user_form(root, uid=uid, on_save=refresh_shell,
                                                    current_user_id=uid),
        )
        self._current_shell = shell

        shell.register("home",       lambda c: self._render_home(c, shell))
        shell.register("usuarios",   lambda c: self._render_users(c, shell))
        shell.register("membros",    lambda c: self._render_members(c, shell))
        shell.register("atividades", lambda c: self._render_activities(c, shell))
        shell.register("oracoes",    lambda c: self._render_prayers(c, shell))
        shell.register("relatorios", lambda c: self._render_reports(c))
        shell.register("whatsapp",   lambda c: self._render_whatsapp(c, shell))

        shell.navigate("home")

    # ── RENDERERS ──────────────────────────────────────────────────

    def _render_home(self, parent, shell):
        from core.members import contar_membros, contar_visitantes_mes, aniversariantes_do_mes
        from core.activities import listar_proximas_atividades

        now = datetime.now()
        try:
            ativos, _afastados, _vis = contar_membros()
            vis_mes = contar_visitantes_mes()
            aniv    = list(aniversariantes_do_mes(now.month))
            raw_ev  = list(listar_proximas_atividades(7))
        except Exception:
            ativos, vis_mes, aniv, raw_ev = 0, 0, [], []

        # Versículo — usa cache do disco (já populado na tela de login)
        verse_result = [None]
        get_verse_of_day(lambda v: verse_result.__setitem__(0, v))
        verse = ({"text": verse_result[0]["text"],
                  "ref":  verse_result[0]["reference"]}
                 if verse_result[0] else None)

        mapped_events = []
        for a in raw_ev:
            dt = None
            try:
                dt = datetime.strptime(a["data_inicio"][:10], "%Y-%m-%d")
            except Exception:
                pass
            di = a["data_inicio"] or ""
            df = a["data_fim"] or ""
            hora_str = ""
            if len(di) > 10:
                hi = di[11:16]
                hf = df[11:16] if len(df) > 10 else ""
                hora_str = f"{hi} → {hf}" if hf else hi
            status = _STATUS_MAP.get(a["status"], a["status"])
            mapped_events.append({
                "id":          a["id"],
                "dia":         dt.day if dt else 1,
                "mes":         _MESES_SHORT[dt.month - 1] if dt else "---",
                "hora":        hora_str,
                "titulo":      a["titulo"],
                "local":       a["local"] or "",
                "resp":        a["nome_responsavel"] or "—",
                "status":      status,
                "funcao_alvo": a["funcao_alvo"] if "funcao_alvo" in a.keys() else None,
                "grupo_alvo":  a["grupo_alvo"]  if "grupo_alvo"  in a.keys() else None,
            })

        mapped_bdays = []
        for i, m in enumerate(aniv):
            funcao = m["funcao"] or "Membro"
            mes_idx = (m["aniversario_mes"] or now.month) - 1
            mapped_bdays.append({
                "nome":     m["nome"],
                "funcao":   funcao,
                "dia":      m["aniversario_dia"] or 0,
                "mes":      _MESES_SHORT[mes_idx],
                "color":    _FUNCAO_COLOR.get(funcao, _MEMBER_COLORS[i % len(_MEMBER_COLORS)]),
                "telefone": m["telefone"] or "",
            })

        shell_user = {
            "nome":  self.current_user["nome"],
            "nivel": self.current_user["nivel_acesso"],
        }
        root = self.root
        uid  = self.current_user["id"]

        home.render(
            parent,
            user=shell_user,
            totals={
                "ativos":          ativos,
                "aniversariantes": len(aniv),
                "eventos":         len(raw_ev),
                "visitantes":      vis_mes,
            },
            events=mapped_events,
            birthdays=mapped_bdays,
            verse=verse,
            callbacks={
                "new_member":      lambda: open_member_form(
                    root, on_save=lambda: shell.navigate("membros")),
                "new_activity":    lambda: open_activity_form(
                    root, current_user_id=uid, on_save=lambda: shell.navigate("atividades")),
                "send_whatsapp":   lambda: shell.navigate("whatsapp"),
                "open_reports":    lambda: shell.navigate("relatorios"),
                "view_activities": lambda: shell.navigate("atividades"),
                "send_birthday":   lambda b: self._open_whatsapp_for_birthday(b, shell),
            },
        )

    def _render_members(self, parent, shell):
        from core.members import listar_membros
        raw = listar_membros()
        mapped = []
        for i, m in enumerate(raw):
            funcao = m["funcao"] or "Membro"
            color  = _FUNCAO_COLOR.get(funcao, _MEMBER_COLORS[i % len(_MEMBER_COLORS)])
            mapped.append({
                "id":        m["id"],
                "nome":      m["nome"],
                "funcao":    funcao,
                "status":    m["status"],
                "tel":       m["telefone"] or "",
                "email":     m["email"] or "",
                "niver_dia": m["aniversario_dia"],
                "niver_mes": str(m["aniversario_mes"]) if m["aniversario_mes"] else None,
                "color":        color,
                "grupo":        m["grupo"] if m["grupo"] else None,
                "grupo_casais": bool(m["grupo_casais"]),
            })
        root = self.root
        refresh = lambda: shell.navigate("membros")
        members.render(parent, members=mapped, callbacks={
            "new_member":      lambda: open_member_form(root, on_save=refresh),
            "edit_member":     lambda mid: open_member_form(root, member_id=mid, on_save=refresh),
            "delete_member":   lambda m: confirm_delete_member(root, membro=m, on_confirm=refresh),
            "whatsapp_member": lambda _: shell.navigate("whatsapp"),
        })

    def _render_activities(self, parent, shell):
        from core.activities import listar_atividades
        raw = listar_atividades()
        mapped = []
        for a in raw:
            dt = None
            try:
                dt = datetime.strptime(a["data_inicio"][:10], "%Y-%m-%d")
            except Exception:
                pass
            di = a["data_inicio"] or ""
            df = a["data_fim"]    or ""
            hora_str = ""
            if len(di) > 10:
                hi = di[11:16]
                hf = df[11:16] if len(df) > 10 else ""
                hora_str = f"{hi} → {hf}" if hf else hi
            status = _STATUS_MAP.get(a["status"], a["status"])
            try:
                fa = a["funcao_alvo"]
            except (IndexError, KeyError):
                fa = None
            try:
                ga = a["grupo_alvo"]
            except (IndexError, KeyError):
                ga = None
            mapped.append({
                "id":          a["id"],
                "dia":         dt.day if dt else 1,
                "mes":         _MESES_SHORT[dt.month - 1] if dt else "---",
                "mes_num":     dt.month if dt else 0,
                "ano":         dt.year if dt else 0,
                "data_iso":    dt.strftime("%Y-%m-%d") if dt else "0000-00-00",
                "hora":        hora_str,
                "titulo":      a["titulo"],
                "local":       a["local"] or "",
                "resp":        a["nome_responsavel"] or "—",
                "status":      status,
                "funcao_alvo": fa,
                "grupo_alvo":  ga,
            })
        root    = self.root
        uid     = self.current_user["id"]
        refresh = lambda: shell.navigate("atividades")
        activities.render(parent, activities=mapped, callbacks={
            "new_activity":      lambda: open_activity_form(
                root, current_user_id=uid, on_save=refresh),
            "edit_activity":     lambda aid: open_activity_form(
                root, activity_id=aid, current_user_id=uid, on_save=refresh),
            "done_activity":     lambda aid: confirm_done_activity(
                root, activity_id=aid, current_user_id=uid, on_confirm=refresh),
            "cancel_activity":   lambda aid: confirm_cancel_activity(
                root, activity_id=aid, current_user_id=uid, on_confirm=refresh),
            "whatsapp_activity": lambda ev: self._open_whatsapp_for_event(ev, shell),
        })

    def _render_prayers(self, parent, shell):
        from core.prayers import obter_oracao
        root = self.root
        _content_ref = [None]

        def _smart_refresh():
            c = _content_ref[0]
            if c and c.winfo_exists() and hasattr(c, "_refresh"):
                c._refresh()
            else:
                shell.navigate("oracoes")

        def _delete_prayer(oid):
            row = obter_oracao(oid)
            solicitante = row["solicitante_nome"] if row else str(oid)
            confirm_delete_prayer(root, oracao_id=oid,
                                  solicitante=solicitante,
                                  on_confirm=_smart_refresh)

        _content_ref[0] = prayers.render(parent, callbacks={
            "new_prayer":    lambda: open_prayer_form(root, on_save=_smart_refresh),
            "edit_prayer":   lambda oid: open_prayer_form(
                root, oracao_id=oid, on_save=_smart_refresh),
            "delete_prayer": _delete_prayer,
        })

    def _open_whatsapp_for_event(self, event, shell):
        self._whatsapp_prefill = event
        shell.navigate("whatsapp")

    def _open_whatsapp_for_birthday(self, bday, shell):
        self._whatsapp_prefill = {
            "type":     "birthday",
            "nome":     bday["nome"],
            "telefone": bday.get("telefone", ""),
            "dia":      bday["dia"],
            "mes":      bday["mes"],
        }
        shell.navigate("whatsapp")

    def _render_whatsapp(self, parent, shell):
        connected = False
        try:
            from core.whatsapp import status_conexao
            st, _ = status_conexao()
            connected = (st == "open")
        except Exception:
            pass

        prefill = getattr(self, "_whatsapp_prefill", None)
        self._whatsapp_prefill = None

        root = self.root

        def _qr_code():
            from design.pages.whatsapp import open_qr_modal
            open_qr_modal(root)

        def _verificar():
            shell.navigate("whatsapp")

        def _toggle():
            try:
                from core.whatsapp import criar_instancia, desconectar_sessao
                if connected:
                    desconectar_sessao()
                else:
                    criar_instancia()
            except Exception as ex:
                from tkinter import messagebox
                messagebox.showerror("Erro", str(ex), parent=root)
            shell.navigate("whatsapp")

        callbacks = {
            "qr_code":          _qr_code,
            "verificar":        _verificar,
            "toggle_connection": _toggle,
        }

        whatsapp.render(parent, connected=connected,
                        callbacks=callbacks, prefill=prefill)

    def _render_users(self, parent, shell):
        from core.users import listar_usuarios
        raw = listar_usuarios()
        current_id = self.current_user["id"]
        mapped = []
        for i, u in enumerate(raw):
            nivel = u["nivel_acesso"]
            mapped.append({
                "id":    u["id"],
                "nome":  u["nome"],
                "email": u["email"],
                "nivel": nivel,
                "ativo": bool(u["ativo"]),
                "voce":  (u["id"] == current_id),
                "color": _USER_LEVEL_COLORS.get(nivel, _MEMBER_COLORS[i % len(_MEMBER_COLORS)]),
            })
        root    = self.root
        refresh = lambda: shell.navigate("usuarios")
        users.render(parent, users=mapped, callbacks={
            "new_user":       lambda: open_user_form(root, on_save=refresh),
            "edit_user":      lambda uid: open_user_form(root, uid=uid, on_save=refresh,
                                                         current_user_id=self.current_user["id"]),
            "reset_password": lambda uid, name: open_reset_password_form(
                root, uid=uid, username=name, on_save=refresh),
            "toggle_active":  lambda uid: toggle_user_active(uid=uid, root=root, on_done=refresh),
            "delete_user":    lambda u: confirm_delete_user(root, usuario=u, on_confirm=refresh),
        })

    def _render_reports(self, parent):
        from core.members import contar_membros, listar_membros
        from core.activities import listar_atividades
        data = {}
        try:
            ativos, afastados, visitantes = contar_membros()
            data["total"]      = ativos + afastados + visitantes
            data["ativos"]     = ativos
            data["afastados"]  = afastados
            data["visitantes"] = visitantes

            funcao_counts = {}
            grupo_counts  = {}
            for m in listar_membros():
                f = m["funcao"] or "Membro"
                funcao_counts[f] = funcao_counts.get(f, 0) + 1
                g = m["grupo"]
                if g:
                    grupo_counts[g] = grupo_counts.get(g, 0) + 1
                if m["grupo_casais"]:
                    grupo_counts["Grupo de Casais"] = grupo_counts.get("Grupo de Casais", 0) + 1
            data["funcao_counts"] = funcao_counts
            data["grupo_counts"]  = grupo_counts

            raw_at = listar_atividades()
            data["total_events"] = len(raw_at)
            data["planejadas"]   = sum(1 for a in raw_at if a["status"] == "Planejado")
            data["realizadas"]   = sum(1 for a in raw_at if a["status"] == "Concluído")
            data["canceladas"]   = sum(1 for a in raw_at if a["status"] == "Cancelado")
        except Exception as e:
            data.setdefault("_error", str(e))

        # Recupera o shell atual para poder navegar ao WhatsApp
        shell = getattr(self, "_current_shell", None)
        callbacks = {}
        if shell:
            callbacks["send_birthday"] = lambda b: self._open_whatsapp_for_birthday(b, shell)

        reports.render(parent, data=data, callbacks=callbacks)

    # ── AUXILIARES ─────────────────────────────────────────────────

    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_profile(self):
        messagebox.showinfo(
            "Meu Perfil",
            f"Nome:  {self.current_user['nome']}\n"
            f"Email: {self.current_user['email']}\n"
            f"Nível: {self.current_user['nivel_acesso']}",
        )

    def logout(self):
        self.current_user = None
        self.root.after(10, self.setup_login_screen)


def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    init_database()
    main()
