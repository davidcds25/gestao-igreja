# tkinter_impl/ — implementação Python pronta para colar

Esta pasta é o **pacote real em Python/tkinter** que reproduz, na sua app,
o que está no mockup HTML. Cole-a dentro do seu projeto e importe as views
nos lugares onde hoje você tem `views/login.py`, `views/members.py`, etc.

## Estrutura

```
tkinter_impl/
├── ui/                       ← biblioteca de design (importe nas views)
│   ├── __init__.py
│   ├── tokens.py             ← COLORS, SPACING, FONTS, STATUS_COLORS
│   ├── helpers.py            ← truncate, rounded_rect_canvas, initials_of
│   └── components.py         ← TODOS os componentes reutilizáveis
│
├── pages/                    ← uma view por arquivo (substitui views/*.py)
│   ├── __init__.py
│   ├── home.py               ← Página Inicial
│   ├── members.py            ← Membros
│   ├── activities.py         ← Atividades e Eventos
│   ├── whatsapp.py           ← WhatsApp
│   ├── users.py              ← Gerenciar Usuários
│   └── reports.py            ← Relatórios
│
├── app_shell.py              ← janela root + header + sidebar + navegação
└── README.md                 ← este arquivo
```

## Como integrar com o que você já tem

Você **não precisa jogar fora** o que tem. Pode migrar em duas estratégias:

### Estratégia A — adoção total (recomendada)

1. Copie `tkinter_impl/` pra raiz do seu projeto.
2. Adapte o `app_shell.main()` para receber `current_user` do seu `LoginWindow`.
3. Substitua o `MainWindow` antigo por `AppShell`.
4. Cada `_page_*` antigo vira `pages/*.py:render(parent)`.

### Estratégia B — adoção gradual (componente por componente)

1. Copie só `tkinter_impl/ui/` pra raiz do projeto.
2. Onde você quiser refinar uma tela, importe os componentes:
   ```python
   from tkinter_impl.ui import COLORS, SPACING, FONTS
   from tkinter_impl.ui.components import (
       button, badge, mini_stat, empty_state, screen_header,
   )
   ```
3. Substitua trechos do seu código atual chamando esses helpers no lugar
   dos `tk.Label`/`tk.Button` crus.

## Catálogo de componentes (1:1 com o mockup HTML)

Cada componente abaixo está em `ui/components.py` — chame, posicione, pronto.
**Nenhum chama `.pack()` ou `.grid()`** internamente — quem decide o layout
é a página.

| Componente             | O que é                                          | Onde é usado                  |
| ---------------------- | ------------------------------------------------ | ----------------------------- |
| `cross_icon`           | Cruz cristã (Canvas)                             | Header, card de versículo     |
| `initials_badge`       | Avatar quadrado com 2 letras                     | Tabelas, cards, header        |
| `button`               | 5 kinds (primary/secondary/danger/ghost/whatsapp)| Todo lugar                    |
| `icon_button`          | Botão pequeno só com emoji/ícone                 | Ações inline em linhas        |
| `badge`                | Pílula UPPERCASE para status (Ativo, Planejado…) | Cards, tabelas                |
| `pill`                 | Indicador com bolinha colorida + texto           | Tabela de usuários            |
| `field` + `text_input` | Label + entry estilizado                         | Formulários                   |
| `textarea`             | Text multilinhas estilizado                      | Mensagens WhatsApp            |
| `select`               | Combobox estilizada                              | Filtros, dropdowns            |
| `tabs`                 | Controle segmentado                              | Atividades, WhatsApp, Reports |
| `empty_state`          | Estado vazio amigável com CTA                    | Listas sem dados              |
| `mini_stat`            | Card pequeno com valor + label                   | Filtros de Membros/Usuários   |
| `big_stat`             | KPI grande com sub + barra accent                | Relatórios                    |
| `bar_chart`            | Barras horizontais                               | Relatórios                    |
| `section_label`        | Eyebrow uppercase de seção                       | Toda página                   |
| `screen_header`        | Cabeçalho padrão de tela (ícone+título+ações)    | Toda view                     |
| `header_bar`           | Top bar do app (logo + user chip)                | `app_shell.py`                |
| `sidebar` + `_nav_item`| Sidebar com indicador triplo de ativo            | `app_shell.py`                |
| `event_card`           | Card de evento (data grande + meta)              | Dashboard, Atividades         |
| `activity_row`         | Idem, mas com ações inline (alias)               | Atividades                    |
| `member_card`          | Card de membro 2-col                             | Membros                       |
| `verse_card`           | Card do versículo com barra dourada              | Dashboard                     |
| `quick_action_card`    | Ação rápida (ícone colorido + label + hint)      | Dashboard                     |
| `connection_card`      | Status verde/vermelho                            | WhatsApp                      |
| `skeleton_card`        | Placeholder de loading                           | Antes de queries pesadas      |
| `page_container`       | Container externo com padding consistente        | Toda view                     |
| `card`                 | Frame estilizado com borda                       | Geral                         |
| `divider_line`         | Linha horizontal de 1px                          | Entre seções                  |

## Catálogo de tokens

Use **apenas** valores de `tokens.py`. Nunca digite hex/pixels soltos.

```python
from ui import COLORS, SPACING, FONTS, STATUS_COLORS

# Cores
COLORS["bg_dark"], COLORS["accent"], COLORS["success"], ...

# Espaçamento (escala de 4)
SPACING[1]=4  SPACING[2]=8  SPACING[3]=12  SPACING[4]=16
SPACING[5]=20 SPACING[6]=24 SPACING[8]=32  SPACING[10]=40 SPACING[12]=48

# Fontes (todas em Segoe UI com fallback Arial automático)
FONTS["display"]  → (Segoe UI, 26, bold)   saudações
FONTS["title"]    → (Segoe UI, 20, bold)   título de tela
FONTS["subtitle"] → (Segoe UI, 14, bold)   título de card
FONTS["section"]  → (Segoe UI, 10, bold)   eyebrow uppercase
FONTS["body"]     → (Segoe UI, 12)         corpo
FONTS["small"]    → (Segoe UI, 11)         auxiliar
FONTS["badge"]    → (Segoe UI,  9, bold)   dentro de badge
FONTS["btn"]      → (Segoe UI, 10, bold)   botões
FONTS["mono"]     → (Consolas, 11)         emails, IDs

# Status → cor automática
bg, fg = STATUS_COLORS["Ativo"]  # → ("#51cf66", "#0f0f23")
```

## Pain points resolvidos

| Pain point original                            | Onde foi resolvido                                    |
| ---------------------------------------------- | ----------------------------------------------------- |
| Inconsistência de espaçamento entre telas      | `tokens.SPACING` + `page_container` (padding único)   |
| Sem estado vazio amigável nas listas           | `empty_state()` — chamado em members/activities       |
| Sidebar sem indicador claro do item ativo      | `_nav_item()` com barra accent 3px + bg + bold        |
| Sem feedback de loading                        | `skeleton_card()`                                     |
| Modais de cadastro genéricos                   | (próxima entrega — pasta `modals/`)                   |
| Textos longos quebrando cards de membro        | `truncate()` em `helpers.py` + altura fixa nos cards  |

## Como testar isolado

```bash
cd tkinter_impl
python app_shell.py
```

Abre a janela com sidebar funcional e todas as 6 views renderizadas com
dados de exemplo. Quando ligar nos seus `core/*.py`, é só substituir as
listas `_*_SAMPLE` por chamadas reais.

## O que NÃO mudou no seu projeto

- `core/` (sua lógica de banco, WhatsApp, relatórios) fica intacto
- `views/login.py` continua sendo seu ponto de entrada — só troca o `MainWindow` no final
- O `igreja.db` e tudo mais permanece igual

## Próxima entrega: modais

Os modais (cadastro/edição de Membro, Atividade, Usuário, etc) virão como
`tkinter_impl/modals/`. Mesma filosofia: classe base `StyledModal` +
campos via `field()` + `text_input()`/`textarea()` + footer com `button()`.
