# Changelog

Todas as mudanças notáveis serão documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Nao lancado]
- Em desenvolvimento

---

## [1.2.0] — 26/05/2026

### Adicionado
- Modulo de Apresentacao com duas abas: "Som" (musicas) e "Versiculo ao Vivo"; acessivel a todos os niveis de acesso
- `design/pages/apresentacao.py`: pagina principal com controle do display e busca de versiculo
- `design/modals/apresentacao_display.py`: `DisplayWindow` — janela separada para projetor/TV com fundo tematico, outline de texto, font caching e navegacao por teclado
- `design/modals/musica.py`: modal de cadastro e edicao de musicas
- `core/musicas.py`: CRUD completo de musicas + `paginar_por_linhas()` e `paginar_letra()` para navegacao no display
- `core/assets.py`: carregamento centralizado de logos, icone da janela e fundos do display com graceful fallback quando `assets/` esta vazia
- `themes.py`: 6 paletas tematicas para fundo do projetor (dourado, navy, vinho, mata, roxo, petroleo)
- `assets/README.md`: documenta nomes de arquivo esperados em `assets/` para personalizacao da marca

### Alterado
- `core/verse.py`: migra de `bible-api.com` para `scripture.api.bible` (autenticado com `BIBLE_API_KEY`); adiciona `buscar_versiculo()`, `buscar_por_usfm()`, lista canonica dos 66 livros em USFM e preferencia de traducao salva em `user_prefs.json`
- `core/pdf_export.py`: corrige logo sobrepondo titulo no header do PDF (variavel `_name_x` calculada dinamicamente)
- `design/ui/components.py`: `header_bar` usa logo da marca quando disponivel, mantem icone de cruz como fallback
- `views/login.py`: logo centralizado na tela de login com suporte a imagem da marca; remove abertura automatica do display
- `config.example.py`: documenta `BIBLE_API_KEY` e `BIBLE_ID` com IDs de traducoes PT gratuitas
- `.gitignore`: ignora `assets/*.png`, `assets/*.jpg`, `assets/*.jpeg`, `assets/*.ico`, `assets/*.gif`, `assets/*.webp`

### Banco de Dados
- Migration `CREATE TABLE IF NOT EXISTS musicas` (titulo, artista, letra, criado_em, atualizado_em)

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
