# Sistema de Gestão para Igrejas

Aplicativo desktop para gestão de igrejas: membros, eventos, comunicação via WhatsApp e versículo diário. Desenvolvido em Python/tkinter com banco de dados local SQLite e design system próprio.

## Funcionalidades

- **Assistente de primeiro acesso**: detecta ausência de `config.py` e exibe wizard de configuração antes do login — sem precisar editar arquivos manualmente
- Login com autenticação segura (bcrypt), tela cheia automática, "lembrar este computador" e exibição da versão atual (tag git)
- **Log de erros automático**: exceções não tratadas são gravadas em `crash.log` ao lado do executável com timestamp, traceback completo e informações do sistema
- Versículo do dia via API com fallback para base local (cache entre login e home)
- Gerenciamento de usuários com níveis de acesso (somente Admin)
  - Modal redesenhado com avatar, medidor de força de senha, confirmação de ativação/desativação e feedback de sucesso
  - Redefinição de senha com medidor visual de segurança e confirmação de correspondência em tempo real
  - Modal de confirmação reutilizável com variantes danger / warning / info
- Cadastro completo de membros com avatar, pills de status, grupo de gênero e grupos adicionais
- Filtros de membros por Status, Função e Grupo com paginação (6 por página)
- Controle de atividades e eventos com paginação (7 por página)
- Envio de mensagens WhatsApp individual e em lote via WAHA com modal QR Code automático
  - Botão "Parabenizar" no dashboard e em Relatórios > Aniversariantes (apenas no dia do aniversário), com mensagem pré-montada
- Banco de dados local SQLite com migrações automáticas
- Relatórios completos com exportação em PDF (fpdf2):
  - Membros: KPIs + distribuição por função e por grupo
  - Aniversariantes: lista do mês com botão de parabenizar via WhatsApp
  - Eventos: KPIs + distribuição por status
  - Crescimento: gráfico de barras mensal (membros, visitantes, afastados) com seletor de ano
- Página de Orações (em desenvolvimento)
- Interface dark theme com design system consistente (tokens, componentes, modais)
- Scroll com mouse wheel em todas as telas — nunca rola acima do título, só desce se houver conteúdo além da área visível, velocidade natural (~40 px por tick)

## Níveis de Acesso

| Nível | Permissões |
|---|---|
| **Admin** | Acesso total, gerenciar usuários, relatórios |
| **Coordenador** | Gerenciar atividades, visualizar relatórios |
| **Usuário** | Visualizar informações e membros |

## Menu Lateral

A ordem do menu é fixa, com itens ocultados de acordo com o nível do usuário:

1. Página Inicial — todos
2. Gerenciar Usuários — somente Admin
3. Membros — todos
4. Atividades e Eventos — todos
5. Orações — todos
6. Relatórios — somente Admin
7. WhatsApp — todos

## Estrutura do Projeto

```
Projeto/
├── main.py                      # Ponto de entrada
├── config.py                    # Configurações locais (não vai ao git)
├── config.example.py            # Modelo de configuração
├── docker-compose.yml           # WAHA (WhatsApp HTTP API)
├── requirements.txt
├── start.bat                    # Atalho Windows para iniciar o app
├── scripts/
│   └── pre-push.ps1             # Checklist guiado antes do push (PowerShell)
│
├── core/                        # Lógica de negócio
│   ├── auth.py                  # Autenticação e criptografia
│   ├── database.py              # Banco de dados e migrações automáticas
│   ├── users.py                 # CRUD de usuários
│   ├── members.py               # CRUD de membros + crescimento_mensal()
│   ├── activities.py            # CRUD de atividades/eventos
│   ├── verse.py                 # Versículo do dia (bible-api.com + fallback)
│   ├── whatsapp.py              # Integração WAHA
│   ├── pdf_export.py            # Geração de relatórios em PDF (fpdf2)
│   └── crash_logger.py          # Log automático de erros → crash.log
│
├── design/                      # Design system
│   ├── ui/
│   │   ├── tokens.py            # COLORS, SPACING, FONTS — fonte única de verdade
│   │   ├── components.py        # Biblioteca de componentes reutilizáveis
│   │   └── helpers.py           # Utilitários (truncate, initials, hover, etc.)
│   ├── pages/                   # Renderers de cada tela
│   │   ├── home.py              # Dashboard (KPIs, eventos, aniversariantes)
│   │   ├── activities.py        # Atividades e eventos
│   │   ├── members.py           # Lista de membros (filtros, paginação)
│   │   ├── whatsapp.py          # Envio de mensagens (individual e em lote)
│   │   ├── users.py             # Gerenciamento de usuários
│   │   ├── reports.py           # Relatórios (4 abas + exportação PDF)
│   │   └── prayers.py           # Orações (em desenvolvimento)
│   ├── modals/                  # Modais com design system
│   │   ├── base.py              # StyledModal (legado) + StyledDialog (novo)
│   │   ├── activity.py          # ActivityModal — Nova/Editar atividade
│   │   ├── member.py            # MemberModal — Novo/Editar membro
│   │   ├── user.py              # UserModal — Novo/Editar usuário (Admin)
│   │   ├── password_reset.py    # PasswordResetModal — Redefinir senha
│   │   └── confirm.py           # ConfirmModal + ask_confirm() helper
│   └── app_shell.py             # Shell (header + sidebar + área de conteúdo)
│
├── views/                       # Controladores
│   ├── login.py                 # Shell principal, navegação, tela de login
│   ├── setup.py                 # Wizard de configuração inicial (primeiro acesso)
│   └── dialogs.py               # Ponto de entrada para os modais de CRUD
│
└── .claude/
    ├── WORKFLOW.md              # Fluxo completo de desenvolvimento e agentes
    ├── settings.json            # Hooks automáticos do Claude Code
    ├── agents/                  # Agentes especializados do Claude Code
    │   ├── qa.md
    │   ├── commit.md
    │   ├── code-review.md
    │   ├── peer-review.md
    │   ├── branch-pr.md
    │   ├── merge-guard.md
    │   ├── release.md
    │   ├── deploy.md
    │   ├── db-migration.md
    │   └── design.md
    └── hooks/                   # Scripts PowerShell de proteção automática
        ├── guard-sensitive-files.ps1
        ├── guard-main-push.ps1
        └── remind-qa-after-edit.ps1
```

## Banco de Dados

| Tabela | Colunas relevantes |
|---|---|
| `usuarios` | id, nome, email, senha_hash, nivel_acesso, ativo |
| `niveis_acesso` | id, nome |
| `logs` | id, usuario_id, acao, criado_em |
| `atividades` | id, titulo, descricao, data_inicio, data_fim, local, status, funcao_alvo, grupo_alvo |
| `membros` | id, nome, funcao, status, grupo, grupo_casais, aniversario_dia, aniversario_mes, telefone, email, observacoes, data_cadastro |

O banco é criado automaticamente na primeira execução. Migrações são aplicadas de forma incremental e segura a cada inicialização.

### Status de Membros

| Status | Descrição |
|---|---|
| **Ativo** | Membro regular participante |
| **Afastado** | Membro temporariamente afastado |
| **Visitante** | Visitante cadastrado |

### Funções disponíveis

`Pastor(a)` · `Presbítero` · `Diácono(a)` · `Evangelista` · `Líder de Célula` · `Louvor` · `Obreiro(a)` · `Secretário(a)` · `Tesoureiro(a)` · `Membro`

### Grupos

Os grupos são separados em dois tipos:

**Grupo principal** (seleção única — um membro pertence a apenas um):
- `Grupo dos Homens`
- `Grupo de Mulheres`
- `Grupo de Jovens`
- `Grupo Infantil`

**Grupo adicional** (pode combinar com qualquer grupo principal):
- `Grupo de Casais`

> Exemplos válidos: "Grupo dos Homens" + "Grupo de Casais", "Grupo de Mulheres" + "Grupo de Casais", "Grupo de Jovens" sozinho, "Grupo Infantil" sozinho.

## Instalação e Uso

### 1. Clonar e configurar

```bash
cp config.example.py config.py
```

Edite o `config.py` com as configurações da sua organização:

```python
APP_NAME         = "Minha Igreja"
WHATSAPP_API_KEY = "sua-chave-aqui"
ADMIN_EMAIL      = "admin@sistema.com"
ADMIN_PASSWORD   = "admin123"
```

> O `config.py` está no `.gitignore` e nunca será enviado ao repositório.

### 2. Criar ambiente Python

```bash
python -m venv venv

# Windows:
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar

```bash
python main.py
# ou dê duplo clique em start.bat
```

A janela abre automaticamente em tela cheia.

### 5. Credenciais padrão

Na primeira execução, um usuário administrador é criado automaticamente com as credenciais definidas em `config.py`. Se não configurado:

| Campo | Valor padrão |
|---|---|
| **E-mail** | `admin@sistema.com` |
| **Senha** | `admin123` |

> Altere a senha após o primeiro acesso em **Gerenciar Usuários**.

## Exportação de Relatórios em PDF

Na tela de Relatórios, o botão **Exportar PDF** gera um arquivo `.pdf` com os dados da aba ativa:

| Aba | Conteúdo do PDF |
|---|---|
| Membros | KPIs (total, ativos, afastados, visitantes) + barras por função e grupo |
| Aniversariantes | Lista do mês selecionado com dia, nome, função e contato |
| Eventos | KPIs + barras por status (planejados, realizados, cancelados) |
| Crescimento | KPIs anuais + tabela mensal + gráfico de barras (membros, visitantes, afastados) |

O PDF é aberto automaticamente após a geração.

## Configurar WhatsApp (WAHA)

O envio de mensagens usa o **WAHA** (WhatsApp HTTP API) rodando via Docker no WSL2.

### Pré-requisitos

- Windows 10/11 com WSL2 habilitado
- Ubuntu instalado no WSL2 (`wsl --install -d Ubuntu`)
- Docker Engine instalado dentro do Ubuntu

### 1. Instalar Docker Engine no WSL2

Abra o terminal do Ubuntu e rode:

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

### 2. Configurar portproxy (PowerShell como Administrador)

```powershell
# Descubra o IP do WSL2
wsl hostname -I

# Redirecione a porta (substitua <IP_WSL2>)
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=127.0.0.1 connectport=3000 connectaddress=<IP_WSL2>
```

> O IP do WSL2 pode mudar ao reiniciar. Refaça este passo se o WhatsApp parar de funcionar.

### 3. Subir o servidor WAHA

```bash
sudo service docker start
cd /mnt/c/caminho/ate/o/projeto
sudo docker compose up -d
```

### 4. Conectar o número

1. Abra o sistema → menu **WhatsApp**
2. Clique em **"Ver QR Code"** — o modal abre e inicia a sessão automaticamente
3. Escaneie com o WhatsApp do celular (dispositivos conectados → conectar dispositivo)
4. O modal fecha e o status muda para Conectado

O QR Code é atualizado automaticamente a cada 20 segundos com countdown visível.

### 5. Uso diário

```bash
sudo service docker start
cd /mnt/c/caminho/ate/o/projeto
sudo docker compose up -d   # iniciar
sudo docker compose down    # parar
```

A sessão é salva em volume persistente — não precisa escanear o QR novamente, desde que use `up -d` e não `down`.

### Envio de mensagens

**Individual:** selecione um membro ativo com telefone cadastrado → o número é preenchido automaticamente → edite a mensagem → Enviar.

**Em lote:** escolha um filtro (Função / Grupo / Aniversariantes do mês) → clique Filtrar → revise a lista em "Ver lista" (pode desmarcar destinatários) → Enviar para todos. Intervalo de 6 segundos entre mensagens. A mensagem suporta `{nome}` que é substituído pelo primeiro nome de cada destinatário.

**Parabenizar aniversariante:** disponível no Dashboard e em Relatórios > Aniversariantes, visível apenas no dia do aniversário. Abre o WhatsApp com mensagem pré-montada e número preenchido automaticamente.

## Segurança

- Senhas criptografadas com bcrypt (12 rounds)
- Verificação de usuário ativo a cada login
- Sistema de auditoria com logs por usuário
- `config.py`, `user_prefs.json` e `*.db` excluídos do repositório via `.gitignore`

## Fluxo de Desenvolvimento

Todo trabalho novo parte de uma **feature branch** criada a partir da release ativa. Nunca commite direto na `release/*` nem na `main`.

```
main
 └── release/YYYY-MM-DD        ← branch de integração da versão atual
      └── feat/nome-da-feature ← onde você desenvolve
```

### Passo a passo

```powershell
# 1. Criar feature branch a partir da release
git checkout release/YYYY-MM-DD
git checkout -b feat/nome-da-feature

# 2. Desenvolver e commitar (use o agente /commit no Claude Code)

# 3. Rodar o checklist antes do push
.\scripts\pre-push.ps1

# 4. Seguir os agentes na ordem indicada pelo checklist
# /qa → /code-review → /peer-review → /commit → /merge-guard

# 5. Push e merge na release (após aprovação)
git push -u origin feat/nome-da-feature
git checkout release/YYYY-MM-DD
git merge --no-ff feat/nome-da-feature
git branch -d feat/nome-da-feature
git push origin release/YYYY-MM-DD
git push origin --delete feat/nome-da-feature
```

### Agentes do Claude Code

| # | Agente | Quando usar |
|---|---|---|
| 1 | `/qa` | Revisão de qualidade antes de qualquer commit |
| 2 | `/code-review` | Análise técnica profunda |
| 3 | `/peer-review` | Perspectiva crítica de colega |
| 4 | `/commit` | Gerar mensagem semântica e commitar |
| 5 | `/merge-guard` | Validar segurança do merge na release |
| 6 | `/release` | Versão + release notes + nova release branch (só no deploy) |
| 7 | `/deploy` | Build do .exe via PyInstaller (só no deploy) |

> Consulte `.claude/WORKFLOW.md` para o diagrama completo e regras de branch.

### Hooks automáticos

O Claude Code executa automaticamente hooks de proteção a cada operação:

| Hook | Proteção |
|---|---|
| `guard-sensitive-files` | Bloqueia `git add` com arquivos sensíveis (`config.py`, `*.db`, `user_prefs.json`) |
| `guard-main-push` | Bloqueia push direto para `main` sem passar pelo fluxo de release |
| `remind-qa-after-edit` | Lembra de rodar `/qa` após editar arquivos em `core/` |

## Compilar para Executável

```bash
pyinstaller --onefile --windowed --name "gestao-igreja" main.py
```

O executável será gerado em `dist/gestao-igreja.exe`.

---

Desenvolvido com Python 3 · tkinter · SQLite · fpdf2
