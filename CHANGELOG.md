# Changelog

Todas as mudanças notáveis serão documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Nao lancado]
- Em desenvolvimento

---

## [1.1.0] — 22/05/2026

### Adicionado
- Tela completa de gerenciamento de oracoes (pedidos, categorias, privacidade, status, testemunho)
- Setup wizard de primeiro acesso (`views/setup.py`): detecta ausencia de `config.py` e guia o usuario pela configuracao inicial sem necessidade de editar arquivos manualmente
- Crash logger automatico (`core/crash_logger.py`): instala `sys.excepthook` global que grava `crash.log` com timestamp, versao Python e traceback completo; exibe dialogo tkinter informando o caminho do arquivo
- Exibicao da versao atual (tag git) no rodape da tela de login, carregada em background thread
- Modal de perfil do usuario redesenhado com badges de grupo coloridos
- Paginacao na tela de oracoes e na tela de relatorios
- Aba de relatorios com ordenacao e filtros
- Modais redesenhados: reset de senha, confirmacao, usuario
- Exportacao de relatorios em PDF (`core/pdf_export.py`)
- Hooks Claude Code automaticos (`.claude/settings.json`):
  - `guard-sensitive-files`: bloqueia `git add` em `config.py`, `*.db`, `user_prefs.json`
  - `guard-main-push`: bloqueia push direto para main sem `--tags`
  - `remind-qa-after-edit`: lembra de rodar `/qa` ao editar `core/*.py`
- `CLAUDE.md` com documentacao completa do projeto para uso com Claude Code

### Corrigido
- Tabela de usuarios invísivel: substituicao de `pack_propagate` por `grid` com `minsize`
- Scroll desnecessario em telas com conteudo pequeno

### Dependencias
- `bcrypt` atualizado de 4.1.1 para 5.0.0

---

## [1.0.0] — 15/05/2026

### Adicionado
- Integracao WhatsApp via WAHA (substituindo Evolution API): popup QR Code com auto-refresh de 20s, botao Desconectar condicional ao status de conexao, sessao FAILED recriada automaticamente
- Botao de parabens por card de membro com envio WhatsApp
- Grupos: Casais, Jovens, Infantil adicionados ao cadastro de membros
- `config.py` gitignored com `config.example.py` como template seguro

### Corrigido
- Crash ao navegar durante callbacks de thread no WhatsApp (`winfo_exists`)
- Erro 422 na sessao FAILED ao tentar escanear QR Code
- Imports nao utilizados em `activities.py`

### Segurança
- Credenciais e chave de API movidas para `config.py` (gitignored)
- `.gitignore` cobre `*.db`, `config.py`, `venv/`, `dist/`, `build/`

---

## [0.4.0] — anterior

### Adicionado
- `config.py`, `.gitignore`, preparacao para open source

---

## [0.3.0] — anterior

### Adicionado
- Integracao WhatsApp (WAHA + popup QR + auto-refresh)

---

## [0.2.0] — anterior

### Adicionado
- Atividades, relatorios, versiculo do dia

---

## [0.1.0] — anterior

### Adicionado
- Primeira versao funcional: login + membros + SQLite
