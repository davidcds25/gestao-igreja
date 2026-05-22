# CLAUDE.md — Gestão de Igreja

Sistema desktop de gestão para igrejas. Python + tkinter + SQLite, distribuído como `.exe` via PyInstaller.

---

## Stack

- **Python 3** + **tkinter** (GUI nativo, sem web)
- **SQLite** — banco local (`igreja.db`, gitignored)
- **bcrypt 4.1.1** — hashing de senhas (12 rounds)
- **fpdf2** — exportação de relatórios em PDF
- **Pillow** — processamento de imagens
- **tkcalendar** — widget de calendário
- **WAHA (WhatsApp HTTP API)** — mensagens via Docker/WSL2 na porta 3000
- **bible-api.com** — versículo diário (com fallback local em PT)

---

## Estrutura de diretórios

```
main.py                  # Entry point: init_database() → views.login.main()
config.py                # Config local (gitignored) — APP_NAME, WHATSAPP_API_KEY, ADMIN_*
config.example.py        # Template seguro para commitar
requirements.txt
start.bat                # Atalho Windows (ativa venv + executa main.py)
docker-compose.yml       # Serviço WAHA

core/                    # Lógica de negócio e acesso ao banco
  auth.py                # Autenticação, hashing
  database.py            # Inicialização SQLite + migrations automáticas
  users.py               # CRUD de usuários
  members.py             # CRUD de membros + constantes (FUNCOES, STATUS, GRUPOS)
  activities.py          # CRUD de atividades + tipos
  prayers.py             # Gestão de pedidos de oração
  reports.py             # Queries para estatísticas
  pdf_export.py          # Geração de PDF
  verse.py               # Versículo diário (thread em background)
  whatsapp.py            # Integração WAHA
  crash_logger.py        # Handler de exceções não tratadas → crash.log

design/                  # Camada de apresentação
  ui/
    tokens.py            # ÚNICA fonte de verdade: COLORS, SPACING, FONTS
    components.py        # ~40 componentes reutilizáveis
    helpers.py           # truncate, initials, hover effects, etc.
  pages/                 # Renderizadores de página (home, members, activities, users, reports, whatsapp, prayers)
  modals/                # Modais (base.py, member.py, activity.py, user.py, password_reset.py, confirm.py, prayer.py)
  app_shell.py           # Janela principal: header + sidebar + área de conteúdo
  perfil.py              # Perfil do usuário

views/
  login.py               # Shell principal, navegação, tela de login
  setup.py               # Wizard de primeiro acesso — gera config.py quando ausente
  dialogs.py             # Entry points dos modais (open_*_form())

scripts/
  pre-push.ps1           # Checklist PowerShell antes do push

.claude/
  CLAUDE.md              # Este arquivo — carregado automaticamente em toda conversa
  WORKFLOW.md            # Fluxo de branches e ordem dos agents
  settings.json          # Hooks automáticos (PreToolUse / PostToolUse)
  agents/                # Subagents: qa, code-review, peer-review, commit, merge-guard,
                         #            db-migration, design, branch-pr, release, deploy
  hooks/
    guard-sensitive-files.ps1  # Bloqueia git add com config.py / *.db / user_prefs.json
    guard-main-push.ps1        # Bloqueia git push origin main sem --tags
    remind-qa-after-edit.ps1   # Lembra de rodar qa ao editar core/*.py
```

---

## Banco de dados

Criado automaticamente na inicialização. Migrations via `ADD COLUMN + UPDATE` (idempotentes).

| Tabela | Propósito |
|---|---|
| `usuarios` | Usuários do sistema (nome, email, senha, nivel_acesso, ativo) |
| `niveis_acesso` | Definições de papéis (Admin / Coordenador / Usuário) |
| `membros` | Membros da igreja (funcao, status, grupo, grupo_casais, aniversario, telefone) |
| `atividades` | Eventos (tipo, data_inicio, data_fim, local, responsavel_id, status) |
| `oracoes` | Pedidos de oração (solicitante, categoria, privacidade, status, testemunho) |
| `logs` | Trilha de auditoria (usuario_id, acao, data_hora) |

**Valores de domínio importantes:**
- `status` membros: `Ativo` / `Afastado` / `Visitante`
- `funcao` membros: Membro, Pastor(a), Presbítero, Diácono(a), Evangelista, Líder de Célula, Louvor, Obreiro(a), Secretário(a), Tesoureiro(a)
- `grupo` membros: Grupo de Mulheres, Grupo dos Homens, Grupo de Jovens, Grupo Infantil
- `tipo` atividades: Culto, Reunião, Evento Social, Estudo Bíblico, Oração, Treinamento, Confraternização, Visita, Trabalho Voluntário, Outro

---

## Controle de acesso

```
Admin        → tudo (usuários, relatórios, atividades, membros, orações, WhatsApp)
Coordenador  → atividades, relatórios, visualizar membros, WhatsApp
Usuário      → visualizar membros, atividades, orações
```

Sidebar oculta itens sem permissão. Checar `nivel_acesso` antes de adicionar features protegidas.

---

## Convenções críticas de UI

- **Componentes nunca chamam `.pack()` ou `.grid()` em si mesmos** — o pai decide o layout.
- **Todos os tokens de design** (cores, espaçamento, fontes) estão em `design/ui/tokens.py`. Nunca hardcode valores visuais.
- **Status colors** são automáticos via `STATUS_COLORS` dict em `tokens.py`.
- **Paginação**: 6 membros/página, 7 atividades/página.
- **Mouse wheel** habilitado em todas as telas; nunca rola acima do título da seção.
- **Tema escuro** por padrão; variáveis `_DARK` nos tokens.

---

## Configuração local

`config.py` (gitignored) é obrigatório para rodar. Variáveis:
- `APP_NAME` — nome da organização exibido na UI
- `WHATSAPP_API_KEY` — chave de autenticação WAHA
- `ADMIN_EMAIL`, `ADMIN_PASSWORD` — credenciais do admin inicial

Copiar de `config.example.py` para configurar novo ambiente.

---

## Workflow de desenvolvimento

Ver `.claude/WORKFLOW.md` para o fluxo completo com branches e ordem dos agentes.

**Regra principal:** nunca trabalhar direto em `main` ou `release/*`. Toda alteração parte de uma feature branch criada a partir da `release/YYYY-MM-DD` atual.

**Agents disponíveis em `.claude/agents/`:** qa, code-review, peer-review, commit, merge-guard, db-migration, design, branch-pr, release, deploy.

---

## Hooks automáticos

Configurados em `.claude/settings.json`, executam via PowerShell antes/após tool calls:

| Hook | Evento | Ação |
|---|---|---|
| `guard-sensitive-files` | PreToolUse Bash | Bloqueia (exit 2) `git add` com `config.py`, `*.db`, `user_prefs.json`, `verse_cache.json` |
| `guard-main-push` | PreToolUse Bash | Bloqueia `git push origin main` sem `--tags` |
| `remind-qa-after-edit` | PostToolUse Write/Edit | Reminder ao editar `core/*.py` |

Hooks bloqueantes escrevem no stderr (`[Console]::Error.WriteLine`) — a mensagem aparece no output do tool call.

---

## Build

```powershell
pyinstaller --onefile --windowed --name "gestao-igreja" main.py
# Saída: dist/gestao-igreja.exe
```

Arquivos sensíveis gitignored: `igreja.db`, `config.py`, `user_prefs.json`, `verse_cache.json`, `venv/`, `dist/`, `*.spec`.
