"""
pages/whatsapp.py
=================
Tela de WhatsApp. Estilizada com:
  - card de conexão (verde/vermelho)
  - tabs entre Individual e Lote
  - formulários consistentes (field + text_input/textarea)

Aceita `prefill` dict gerado a partir de um evento, com:
  {"funcao_alvo": str|None, "titulo": str, "hora": str,
   "local": str, "dia": int, "mes": str}
"""

import tkinter as tk
from datetime import datetime
from ..ui import COLORS, SPACING, FONTS
from ..ui.components import (
    page_container, screen_header, tabs as build_tabs,
    connection_card, button, select, field, text_input, textarea,
    section_label,
)

_FUNCOES_OPTIONS = [
    "Todas", "Membro", "Pastor(a)", "Presbítero", "Diácono(a)",
    "Evangelista", "Líder de Célula", "Louvor", "Obreiro(a)",
    "Secretário(a)", "Tesoureiro(a)",
]


def _build_template(event: dict) -> str:
    """Gera template de lembrete baseado nos dados do evento."""
    now = datetime.now()
    hora_atual = now.hour
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


def render(parent, *, connected: bool = True, callbacks=None, prefill=None):
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
           icon="📷").pack(side=tk.LEFT, padx=(0, SPACING[2]))
    button(hdr["actions"], text="Verificar", kind="secondary",
           icon="↻").pack(side=tk.LEFT)

    # ─── Card de conexão ──────────────────────────────────────────
    connection_card(
        content,
        connected=connected,
        session_info="sessão ativa há 2h 14min",
        on_toggle=callbacks.get("toggle_connection"),
    ).pack(fill=tk.X, pady=(0, SPACING[6]))

    # ─── Tabs ─────────────────────────────────────────────────────
    tab_row = tk.Frame(content, bg=COLORS["bg_dark"])
    tab_row.pack(fill=tk.X, pady=(0, SPACING[4]))

    form_container = tk.Frame(content, bg=COLORS["bg_dark"])
    form_container.pack(fill=tk.BOTH, expand=True)

    # Se veio com prefill de evento, abre direto na aba Lote
    default_tab = "lote" if prefill else "individual"

    def _render_form(tab):
        for w in form_container.winfo_children():
            w.destroy()
        if tab == "individual":
            _render_individual(form_container, connected)
        else:
            _render_lote(form_container, connected, prefill=prefill)

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


def _render_individual(parent, connected):
    wrap, inner = _form_wrap(parent)
    wrap.pack(fill=tk.X)

    inner.columnconfigure(0, weight=1, uniform="f")
    inner.columnconfigure(1, weight=1, uniform="f")

    m_field = field(inner, label="Membro",
                    hint="opcional — preenche o telefone abaixo")
    m_field.grid(row=0, column=0, sticky="ew", padx=(0, SPACING[3]),
                 pady=(0, SPACING[3]))
    text_input(m_field, value="").pack(fill=tk.X)

    t_field = field(inner, label="Telefone")
    t_field.grid(row=0, column=1, sticky="ew", pady=(0, SPACING[3]))
    text_input(t_field, value="").pack(fill=tk.X)

    msg_field = field(inner, label="Mensagem", hint="0 / 1000 caracteres")
    msg_field.grid(row=1, column=0, columnspan=2, sticky="ew",
                   pady=(0, SPACING[3]))
    textarea(msg_field, lines=6,
             placeholder=("Olá {nome}! Lembrete: amanhã às 8h temos o "
                          "culto dos jovens. Conto com você!\n\nDeus abençoe!")).pack(fill=tk.X)

    footer = tk.Frame(inner, bg=COLORS["bg_card"])
    footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(SPACING[2], 0))
    hint_color = COLORS["text_muted"] if connected else COLORS["danger"]
    hint_text  = ("Pronto para enviar." if connected
                  else "⚠ Conexão inativa — conecte o WhatsApp antes de enviar.")
    tk.Label(footer, text=hint_text, font=FONTS["small"],
             bg=COLORS["bg_card"], fg=hint_color).pack(side=tk.LEFT)
    button(footer, text="Limpar", kind="ghost").pack(side=tk.RIGHT, padx=(SPACING[2], 0))
    button(footer, text="Enviar Mensagem", kind="whatsapp",
           icon="📤").pack(side=tk.RIGHT)


def _render_lote(parent, connected, prefill=None):
    wrap, inner = _form_wrap(parent)
    wrap.pack(fill=tk.X)

    # Se veio de um evento, mostra banner explicativo
    if prefill:
        banner = tk.Frame(inner, bg=COLORS["accent2"],
                          highlightbackground=COLORS["accent2"],
                          highlightthickness=0)
        banner.pack(fill=tk.X, pady=(0, SPACING[4]))
        banner_inner = tk.Frame(banner, bg=COLORS["accent2"])
        banner_inner.pack(fill=tk.X, padx=SPACING[4], pady=SPACING[2])
        tk.Label(banner_inner,
                 text=f"💬  Lembrete para: {prefill.get('titulo', '')}",
                 font=FONTS["body_strong"],
                 bg=COLORS["accent2"], fg=COLORS["bg_dark"]).pack(side=tk.LEFT)

    # Filtros
    filters = tk.Frame(inner, bg=COLORS["bg_card"])
    filters.pack(fill=tk.X, pady=(0, SPACING[4]))
    for c in range(3):
        filters.columnconfigure(c, weight=1, uniform="f")

    # Função — pré-seleciona a funcao_alvo do evento
    funcao_inicial = "Todas"
    if prefill and prefill.get("funcao_alvo"):
        fa = prefill["funcao_alvo"]
        funcao_inicial = fa if fa in _FUNCOES_OPTIONS else "Todas"

    f1 = field(filters, label="Função")
    f1.grid(row=0, column=0, sticky="ew", padx=(0, SPACING[3]))
    select(f1, value=funcao_inicial, options=_FUNCOES_OPTIONS).pack(fill=tk.X)

    f2 = field(filters, label="Status")
    f2.grid(row=0, column=1, sticky="ew", padx=(0, SPACING[3]))
    select(f2, value="Ativo", options=["Todos", "Ativo", "Afastado", "Visitante"]).pack(fill=tk.X)

    f3 = field(filters, label="Aniversariantes do mês")
    f3.grid(row=0, column=2, sticky="ew", padx=(0, SPACING[3]))
    select(f3, value="Não", options=["Não", "Sim"]).pack(fill=tk.X)

    button(filters, text="Filtrar", kind="secondary",
           icon="🔍").grid(row=0, column=3, sticky="e")

    # Contador de destinatários
    rc = tk.Frame(inner, bg=COLORS["bg_dark"],
                  highlightbackground=COLORS["divider"], highlightthickness=1)
    rc.pack(fill=tk.X, pady=(0, SPACING[4]))
    rc_inner = tk.Frame(rc, bg=COLORS["bg_dark"])
    rc_inner.pack(fill=tk.X, padx=SPACING[5], pady=SPACING[3])
    tk.Label(rc_inner, text="—",
             font=FONTS["metric_large"],
             bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(side=tk.LEFT,
                                                              padx=(0, SPACING[3]))
    txt_col = tk.Frame(rc_inner, bg=COLORS["bg_dark"])
    txt_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
    filtro_desc = (f"Função={funcao_inicial} · Status=Ativo"
                   if prefill else "Função=Todas · Status=Ativo")
    tk.Label(txt_col, text="destinatários selecionados",
             font=FONTS["body_strong"],
             bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(anchor=tk.W)
    tk.Label(txt_col, text=f"com filtros: {filtro_desc}",
             font=FONTS["small"],
             bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor=tk.W)
    button(rc_inner, text="Ver lista", kind="ghost").pack(side=tk.RIGHT)

    # Mensagem — template pré-preenchido se veio de evento
    msg_inicial = _build_template(prefill) if prefill else (
        "Olá {nome}! Estamos passando para lembrar do culto "
        "deste domingo às 19h. Esperamos você!"
    )
    msg_field = field(inner, label="Mensagem",
                      hint="use {nome} para personalizar com o nome do membro")
    msg_field.pack(fill=tk.X, pady=(0, SPACING[3]))
    textarea(msg_field, lines=6, value=msg_inicial).pack(fill=tk.X)

    # Footer
    footer = tk.Frame(inner, bg=COLORS["bg_card"])
    footer.pack(fill=tk.X, pady=(SPACING[2], 0))
    tk.Label(footer,
             text=("Envio em lotes de 10 mensagens com intervalo de 3s."
                   if connected else "⚠ Desconectado — não é possível enviar."),
             font=FONTS["small"],
             bg=COLORS["bg_card"],
             fg=COLORS["text_muted"] if connected else COLORS["danger"]
             ).pack(side=tk.LEFT)
    button(footer, text="Enviar para todos", kind="whatsapp",
           icon="📤").pack(side=tk.RIGHT)
