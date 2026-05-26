"""Modal de cadastro e edição de músicas."""

import tkinter as tk
from .base import StyledDialog, modal_field, modal_input, modal_button
from ..ui import COLORS, SPACING, FONTS


class MusicaModal(StyledDialog):

    def __init__(self, parent, *, mode: str = "new", initial: dict = None,
                 on_save=None, on_delete=None):
        self._mode      = mode
        self._initial   = initial or {}
        self._on_save   = on_save
        self._on_delete = on_delete

        subtitle = "Editar letra e informações" if mode == "edit" else "Nova música no repertório"
        super().__init__(
            parent,
            eyebrow="Músicas",
            icon="🎵",
            title="Editar Música" if mode == "edit" else "Nova Música",
            subtitle=subtitle,
            width=720,
            height=680,
        )

    def _build_body(self, parent):
        bg = COLORS["bg_card"]

        # Título
        titulo_wrap = modal_field(parent, label="Título", required=True)
        titulo_wrap.pack(fill=tk.X, pady=(0, SPACING[3]))
        self._titulo_var = tk.StringVar(value=self._initial.get("titulo", ""))
        modal_input(titulo_wrap, var=self._titulo_var,
                    placeholder="Nome da música",
                    icon="🎵").pack(fill=tk.X)

        # Artista
        artista_wrap = modal_field(parent, label="Artista / Ministério",
                                   hint="Opcional")
        artista_wrap.pack(fill=tk.X, pady=(0, SPACING[3]))
        self._artista_var = tk.StringVar(value=self._initial.get("artista", ""))
        modal_input(artista_wrap, var=self._artista_var,
                    placeholder="Ex: Hillsong, Fernandinho…",
                    icon="🎤").pack(fill=tk.X)

        # Letra
        letra_wrap = modal_field(
            parent, label="Letra",
            required=True,
            hint="Cole a letra completa — estrofes separadas por linha em branco",
        )
        letra_wrap.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        text_box = tk.Frame(letra_wrap, bg=COLORS["input_bg"],
                            highlightbackground=COLORS["divider"],
                            highlightcolor=COLORS["accent"],
                            highlightthickness=1)
        text_box.pack(fill=tk.BOTH, expand=True)

        self._letra_text = tk.Text(
            text_box,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD,
            padx=SPACING[3],
            pady=SPACING[2],
        )
        scroll = tk.Scrollbar(text_box, orient=tk.VERTICAL,
                              command=self._letra_text.yview)
        self._letra_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._letra_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if self._initial.get("letra"):
            self._letra_text.insert("1.0", self._initial["letra"])

        self._error_var = tk.StringVar()
        tk.Label(parent, textvariable=self._error_var,
                 font=FONTS["small"],
                 bg=bg, fg=COLORS["danger"],
                 anchor=tk.W).pack(fill=tk.X, pady=(SPACING[2], 0))

    def _build_footer(self, left, right):
        if self._mode == "edit" and self._on_delete:
            modal_button(left, text="Excluir", kind="danger",
                         icon="🗑", command=self._delete).pack(side=tk.LEFT)

        modal_button(right, text="Cancelar", kind="ghost",
                     command=self.cancel).pack(side=tk.LEFT, padx=(0, SPACING[2]))
        modal_button(right, text="Salvar", kind="primary",
                     icon="✓", command=self._save).pack(side=tk.LEFT)

    def _save(self):
        titulo = self._titulo_var.get().strip()
        artista = self._artista_var.get().strip()
        letra = self._letra_text.get("1.0", tk.END).strip()

        if not titulo:
            self._error_var.set("✕  O título é obrigatório.")
            return
        if not letra:
            self._error_var.set("✕  Cole a letra da música antes de salvar.")
            return

        if self._on_save:
            err = self._on_save({"titulo": titulo, "artista": artista, "letra": letra})
            if err:
                self._error_var.set(f"✕  {err}")
                return

        self.close_with({"titulo": titulo})

    def _delete(self):
        if self._on_delete:
            self._on_delete()
        self.close_with({"_deleted": True})
