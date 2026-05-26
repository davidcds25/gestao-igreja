"""
app_shell.py
============
Casca do app: janela root + header + sidebar + content_frame.
Substitui o seu `_build_header` + `_build_sidebar` + `navigate` atual.

USO:
    from app_shell import AppShell
    from pages import home, members, activities, whatsapp, users, reports

    root = tk.Tk()
    shell = AppShell(root, current_user={"nome": "David", "nivel": "Admin"})
    shell.register("home",       lambda c: home.render(c))
    shell.register("membros",    lambda c: members.render(c))
    shell.register("atividades", lambda c: activities.render(c))
    shell.register("whatsapp",   lambda c: whatsapp.render(c))
    shell.register("usuarios",   lambda c: users.render(c))
    shell.register("relatorios", lambda c: reports.render(c))
    shell.navigate("home")
    root.mainloop()
"""

import tkinter as tk

from .ui import COLORS, SPACING
from .ui.components import header_bar, sidebar

try:
    from config import APP_NAME
except ImportError:
    APP_NAME = "Sistema de Gestão"


SIDEBAR_ITEMS = [
    {"key": "home",          "icon": "🏠", "label": "Página Inicial",       "niveis": None},
    {"key": "usuarios",      "icon": "👤", "label": "Gerenciar Usuários",   "niveis": {"Admin"}},
    {"key": "membros",       "icon": "👥", "label": "Membros",               "niveis": None},
    {"key": "atividades",    "icon": "📋", "label": "Atividades e Eventos", "niveis": None},
    {"key": "oracoes",       "icon": "🙏", "label": "Orações",               "niveis": None},
    {"key": "apresentacao",  "icon": "🎬", "label": "Apresentação",           "niveis": None},
    {"key": "relatorios",    "icon": "📊", "label": "Relatórios",            "niveis": {"Admin"}},
    {"key": "whatsapp",      "icon": "💬", "label": "WhatsApp",              "niveis": None},
]


class AppShell:
    def __init__(self, root, *, current_user: dict, on_logout=None,
                 on_profile=None, on_edit_profile=None):
        self.root = root
        self.current_user = current_user
        self.on_logout = on_logout or (lambda: root.quit())
        self.on_profile = on_profile
        self.on_edit_profile = on_edit_profile

        # filtra itens conforme nível do usuário (None = todos podem ver)
        nivel = current_user.get("nivel", "")
        self._items = [
            it for it in SIDEBAR_ITEMS
            if it["niveis"] is None or nivel in it["niveis"]
        ]

        # janela raiz
        root.title(APP_NAME)
        root.configure(bg=COLORS["bg_dark"])
        try:
            root.state("zoomed")  # Windows
        except Exception:
            root.geometry("1280x800")

        # registry de views
        self._renderers = {}
        self._current = None

        self._build()

    def _build(self):
        # Header
        header_bar(self.root,
                   user=self.current_user,
                   on_profile=self.on_profile,
                   on_edit_profile=self.on_edit_profile,
                   on_logout=self.on_logout).pack(fill=tk.X, side=tk.TOP)
        # divisor
        tk.Frame(self.root, bg=COLORS["divider"],
                 height=1).pack(fill=tk.X, side=tk.TOP)

        # Wrapper sidebar + content
        body = tk.Frame(self.root, bg=COLORS["bg_dark"])
        body.pack(fill=tk.BOTH, expand=True)

        self.sidebar_widget = sidebar(
            body,
            items=self._items,
            active_key="home",
            on_select=self.navigate,
            on_logout=self.on_logout,
        )
        self.sidebar_widget.pack(side=tk.LEFT, fill=tk.Y)

        # divisor vertical
        tk.Frame(body, bg=COLORS["divider"],
                 width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Content frame — onde cada página vai renderizar
        self.content_frame = tk.Frame(body, bg=COLORS["bg_dark"])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ── API pública ──
    def register(self, key: str, renderer):
        """`renderer(parent)` recebe o content_frame e desenha a página."""
        self._renderers[key] = renderer

    def navigate(self, key: str):
        if key not in self._renderers:
            return
        # limpa content
        for w in self.content_frame.winfo_children():
            w.destroy()
        # re-renderiza sidebar para atualizar ativo
        self._refresh_sidebar(key)
        self._renderers[key](self.content_frame)
        self._current = key

    def _refresh_sidebar(self, active_key):
        # recria sidebar com o novo item ativo
        parent = self.sidebar_widget.master
        self.sidebar_widget.destroy()
        self.sidebar_widget = sidebar(
            parent,
            items=self._items,
            active_key=active_key,
            on_select=self.navigate,
            on_logout=self.on_logout,
        )
        # insere antes do primeiro filho restante (o divisor vertical)
        remaining = parent.winfo_children()
        if remaining:
            self.sidebar_widget.pack(side=tk.LEFT, fill=tk.Y, before=remaining[0])
        else:
            self.sidebar_widget.pack(side=tk.LEFT, fill=tk.Y)


# ─── Entrypoint de exemplo ────────────────────────────────────────────
def main():
    """Roda o app standalone (sem o seu sistema de login)."""
    from pages import home, members, activities, whatsapp, users, reports

    root = tk.Tk()
    shell = AppShell(
        root,
        current_user={"nome": "Usuário", "nivel": "Admin"},
    )
    shell.register("home",       lambda c: home.render(c))
    shell.register("membros",    lambda c: members.render(c))
    shell.register("atividades", lambda c: activities.render(c))
    shell.register("whatsapp",   lambda c: whatsapp.render(c))
    shell.register("usuarios",   lambda c: users.render(c))
    shell.register("relatorios", lambda c: reports.render(c))
    shell.navigate("home")
    root.mainloop()


if __name__ == "__main__":
    main()
