"""
core/pdf_export.py
==================
Geração de relatórios em PDF usando fpdf2.
Exporta a aba ativa da tela de Relatórios.
"""

import os
from datetime import datetime
from fpdf import FPDF

try:
    from config import APP_NAME
except ImportError:
    APP_NAME = "Sistema de Gestão"

_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_MESES_ABR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Paleta — legível em impressão
_NAV = (22, 30, 70)       # azul escuro
_ACE = (0, 140, 180)      # ciano
_WH  = (255, 255, 255)
_ALT = (243, 244, 249)    # cinza claro — linha alternada
_TXT = (30, 35, 60)
_MUT = (110, 115, 140)
_GRN = (34, 160, 90)
_ORG = (210, 130, 0)
_RED = (190, 45, 45)


def _s(v):
    """Converte para string segura para latin-1 (core fonts do fpdf2)."""
    if v is None:
        return ""
    s = str(v)
    # Substituições explícitas de caracteres fora do latin-1
    s = s.replace("—", "-").replace("–", "-")  # em dash / en dash
    s = s.replace("✓", "Sim").replace("✔", "Sim")  # check marks
    s = s.replace("✕", "Nao").replace("✖", "Nao")  # x marks
    s = s.replace("’", "'").replace("‘", "'")  # smart quotes
    s = s.replace("“", '"').replace("”", '"')
    return s.encode("latin-1", errors="replace").decode("latin-1")


# ══════════════════════════════════════════════════════════════════════
# Classe base do PDF
# ══════════════════════════════════════════════════════════════════════

class _PDF(FPDF):
    def __init__(self, tab_title: str, orientation: str = "P"):
        super().__init__(orientation=orientation, unit="mm", format="A4")
        self._tab_title = tab_title
        # largura utilizável (margens de 12mm cada lado)
        self._pw = self.w - 24
        self.set_margins(12, 12, 12)
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    # ── header / footer ──────────────────────────────────────────────

    def header(self):
        self.set_fill_color(*_NAV)
        self.rect(0, 0, self.w, 20, "F")

        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 180, 220)
        self.set_xy(12, 4)
        self.cell(self.w / 2, 6, _s(APP_NAME))

        self.set_font("Helvetica", "", 8)
        self.set_text_color(185, 195, 215)
        self.set_xy(12, 12)
        self.cell(self.w / 2, 5, _s(self._tab_title))

        self.set_font("Helvetica", "", 8)
        self.set_text_color(155, 165, 190)
        self.set_xy(12, 8)
        self.cell(self.w - 24, 5,
                  datetime.now().strftime("%d/%m/%Y  %H:%M"), align="R")

        self.set_xy(12, 22)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*_MUT)
        self.cell(0, 5, f"Página {self.page_no()}/{{nb}}", align="C")

    # ── compositing helpers ───────────────────────────────────────────

    def section(self, title: str):
        self.ln(5)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*_NAV)
        self.cell(0, 6, _s(title))
        self.ln(1)
        self.set_draw_color(*_ACE)
        self.set_line_width(0.4)
        x, y = self.get_x(), self.get_y()
        self.line(x, y, x + self._pw, y)
        self.ln(4)

    def kpis(self, items: list):
        """items: [(value, label, sub), ...]"""
        n  = len(items)
        bw = self._pw / n
        y0 = self.get_y()
        x0 = self.get_x()
        for i, (val, lbl, sub) in enumerate(items):
            x = x0 + i * bw
            self.set_fill_color(*_ALT)
            self.set_draw_color(208, 212, 228)
            self.set_line_width(0.3)
            self.rect(x, y0, bw - 2, 20, "FD")

            self.set_font("Helvetica", "B", 15)
            self.set_text_color(*_ACE)
            self.set_xy(x + 3, y0 + 2)
            self.cell(bw - 6, 8, _s(str(val)))

            self.set_font("Helvetica", "B", 7)
            self.set_text_color(*_TXT)
            self.set_xy(x + 3, y0 + 10)
            self.cell(bw - 6, 4, _s(lbl))

            self.set_font("Helvetica", "", 6)
            self.set_text_color(*_MUT)
            self.set_xy(x + 3, y0 + 14)
            self.cell(bw - 6, 5, _s(sub))

        self.set_xy(x0, y0 + 23)

    def thead(self, cols: list):
        """cols: [(label, width_mm), ...]"""
        self.set_fill_color(*_NAV)
        self.set_text_color(*_WH)
        self.set_font("Helvetica", "B", 7)
        for label, w in cols:
            self.cell(w, 6, _s(label.upper()), border=0, fill=True)
        self.ln()

    def trow(self, cols: list, values: list, alt: bool = False):
        self.set_fill_color(*(_ALT if alt else _WH))
        self.set_text_color(*_TXT)
        self.set_font("Helvetica", "", 8)
        for (_, w), val in zip(cols, values):
            self.cell(w, 5, _s(str(val))[:50], border=0, fill=True)
        self.ln()

    def bar_h(self, label: str, value: int, max_val: int,
              color: tuple = None, lbl_w: int = 65, bar_max: int = 100):
        color = color or _ACE
        x0, y0 = self.get_x(), self.get_y()

        self.set_font("Helvetica", "", 8)
        self.set_text_color(*_TXT)
        self.cell(lbl_w, 5, _s(str(label)[:30]))

        # trilho
        self.set_fill_color(218, 220, 235)
        self.rect(x0 + lbl_w, y0 + 1, bar_max, 3, "F")

        # preenchimento
        if max_val > 0 and value > 0:
            filled = max(2, int(bar_max * value / max_val))
            self.set_fill_color(*color)
            self.rect(x0 + lbl_w, y0 + 1, filled, 3, "F")

        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*_TXT)
        self.set_xy(x0 + lbl_w + bar_max, y0)
        self.cell(20, 5, _s(str(value)), align="R")
        self.ln(5)


# ══════════════════════════════════════════════════════════════════════
# Exportadores por aba
# ══════════════════════════════════════════════════════════════════════

def _export_membros(data: dict, filepath: str):
    pdf = _PDF("Relatório de Membros")
    pdf.add_page()

    total      = data.get("total", 0)
    ativos     = data.get("ativos", 0)
    afastados  = data.get("afastados", 0)
    visitantes = data.get("visitantes", 0)

    pdf.section("Resumo geral")
    pdf.kpis([
        (total,      "Total de membros",  "Todos os cadastros"),
        (ativos,     "Membros ativos",    "Status Ativo"),
        (afastados,  "Afastados",         "Temporariamente afastados"),
        (visitantes, "Visitantes",        "Cadastrados como visitantes"),
    ])

    funcao = data.get("funcao_counts", {})
    if funcao:
        pdf.section("Distribuição por função")
        max_f = max(funcao.values(), default=1)
        colors = [_ACE, _GRN, _ORG, _RED, _NAV, (140, 70, 180)]
        for i, (f, c) in enumerate(
                sorted(funcao.items(), key=lambda x: -x[1])):
            pdf.bar_h(f, c, max_f, color=colors[i % len(colors)])

    grupos = data.get("grupo_counts", {})
    if grupos:
        pdf.section("Distribuição por grupo")
        max_g = max(grupos.values(), default=1)
        g_colors = [(140, 70, 180), _ORG, _GRN]
        for i, (g, c) in enumerate(
                sorted(grupos.items(), key=lambda x: -x[1])):
            pdf.bar_h(g, c, max_g, color=g_colors[i % len(g_colors)])

    pdf.output(filepath)


def _export_aniversariantes(mes_idx: int, filepath: str):
    from core.members import aniversariantes_do_mes
    mes_nome = _MESES[mes_idx]
    pdf = _PDF(f"Aniversariantes de {mes_nome}")
    pdf.add_page()

    raw = list(aniversariantes_do_mes(mes_idx + 1))

    pdf.section(f"Aniversariantes de {mes_nome} - {len(raw)} pessoa(s)")

    cols = [
        ("Dia",    18),
        ("Nome",   100),
        ("Função", 50),
        ("Contato", 18),
    ]
    pdf.thead(cols)

    for i, r in enumerate(raw):
        dia  = f"{r['aniversario_dia']:02d}/{mes_idx + 1:02d}" \
               if r["aniversario_dia"] else "--"
        tel  = "Sim" if r["telefone"] else "-"
        pdf.trow(cols,
                 [dia, r["nome"], r["funcao"] or "Membro", tel],
                 alt=(i % 2 == 1))

    if not raw:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*_MUT)
        pdf.cell(0, 8, f"Nenhum aniversariante em {mes_nome}.")
        pdf.ln()

    pdf.output(filepath)


def _export_eventos(data: dict, filepath: str):
    pdf = _PDF("Relatório de Eventos")
    pdf.add_page()

    total      = data.get("total_events", 0)
    realizadas = data.get("realizadas", 0)
    planejadas = data.get("planejadas", 0)
    canceladas = data.get("canceladas", 0)

    pdf.section("Resumo de eventos")
    pdf.kpis([
        (total,      "Total de eventos",  "Registros no sistema"),
        (realizadas, "Realizados",        "Concluídos com sucesso"),
        (planejadas, "Planejados",        "Agenda futura"),
        (canceladas, "Cancelados",        "Não realizados"),
    ])

    pdf.section("Distribuição por status")
    max_ev = max(realizadas, planejadas, canceladas, 1)
    pdf.bar_h("Planejados", planejadas, max_ev, color=_ACE)
    pdf.bar_h("Realizados", realizadas, max_ev, color=_GRN)
    pdf.bar_h("Cancelados", canceladas, max_ev, color=_RED)

    pdf.output(filepath)


def _export_crescimento(ano: int, filepath: str):
    from core.members import crescimento_mensal
    d = crescimento_mensal(ano)
    membros    = d["membros"]
    visitantes = d["visitantes"]
    afastados  = d["afastados"]

    total_m = sum(membros)
    total_v = sum(visitantes)
    total_a = sum(afastados)
    total   = total_m + total_v + total_a

    combined = [membros[i] + visitantes[i] for i in range(12)]
    mes_pico_idx = combined.index(max(combined)) if any(combined) else -1
    mes_pico = _MESES[mes_pico_idx] if mes_pico_idx >= 0 and max(combined) > 0 else "-"

    pdf = _PDF(f"Crescimento {ano}", orientation="L")
    pdf.add_page()

    pdf.section(f"Resumo do ano {ano}")
    pdf.kpis([
        (total,    "Total cadastrado",   f"no ano de {ano}"),
        (total_m,  "Membros ativos",     "adicionados no período"),
        (total_v,  "Visitantes",         "cadastrados no período"),
        (total_a,  "Afastados",          "registrados no período"),
        (mes_pico, "Mês de pico",        "maior número de entradas"),
    ])

    pdf.section("Detalhamento mensal")

    cols = [
        ("Mês",        28),
        ("Membros",    32),
        ("Visitantes", 32),
        ("Afastados",  32),
        ("Total",      32),
    ]
    pdf.thead(cols)

    for i in range(12):
        tot = membros[i] + visitantes[i] + afastados[i]
        pdf.trow(
            cols,
            [_MESES[i], membros[i], visitantes[i], afastados[i], tot],
            alt=(i % 2 == 1),
        )

    # Linha de totais
    pdf.set_fill_color(*_NAV)
    pdf.set_text_color(*_WH)
    pdf.set_font("Helvetica", "B", 8)
    for label, w in cols:
        cell_val = {
            "Mês": "TOTAL",
            "Membros": str(total_m),
            "Visitantes": str(total_v),
            "Afastados": str(total_a),
            "Total": str(total),
        }[label]
        pdf.cell(w, 6, cell_val, border=0, fill=True)
    pdf.ln()

    # Gráfico de barras horizontais por mês
    pdf.section("Distribuicao mensal - Membros e Visitantes")
    max_bar = max(max(combined), 1)
    for i in range(12):
        if membros[i] or visitantes[i]:
            pdf.bar_h(
                _MESES_ABR[i],
                membros[i] + visitantes[i],
                max_bar,
                color=_ACE,
                lbl_w=20,
                bar_max=220,
            )

    pdf.output(filepath)


# ══════════════════════════════════════════════════════════════════════
# Ponto de entrada público
# ══════════════════════════════════════════════════════════════════════

def export_tab(*, tab: str, data: dict, aniv_mes: int = None,
               cresc_ano: int = None, filepath: str):
    if tab == "membros":
        _export_membros(data, filepath)
    elif tab == "aniversariantes":
        _export_aniversariantes(
            aniv_mes if aniv_mes is not None else datetime.now().month - 1,
            filepath,
        )
    elif tab == "eventos":
        _export_eventos(data, filepath)
    elif tab == "crescimento":
        _export_crescimento(
            cresc_ano if cresc_ano is not None else datetime.now().year,
            filepath,
        )
    else:
        raise ValueError(f"Aba desconhecida: {tab!r}")
