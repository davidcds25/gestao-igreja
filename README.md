# Sistema de Gestão para Igrejas

Aplicativo desktop para gestão de igrejas: membros, eventos, comunicação via WhatsApp e versículo diário. Desenvolvido em Python/tkinter com banco de dados local SQLite e design system próprio.

## Funcionalidades

- Login com autenticação segura (bcrypt), tela cheia automática e "lembrar este computador"
- Versículo do dia via API com fallback para base local (cache compartilhado entre login e home)
- Gerenciamento de usuários com níveis de acesso (somente Admin)
- Cadastro e gerenciamento completo de membros
- Controle de atividades e eventos com modais redesenhados
- Envio de mensagens WhatsApp individual e em lote (WAHA)
- Banco de dados local SQLite com migrações automáticas
- Interface dark theme com design system consistente

## Níveis de Acesso

| Nível | Permissões |
|---|---|
| **Admin** | Acesso total, gerenciar usuários, relatórios |
| **Coordenador** | Gerenciar atividades, visualizar relatórios |
| **Usuário** | Visualizar informações e membros |

## Estrutura do Projeto

```
Projeto/
├── main.py                      # Ponto de entrada
├── config.py                    # Configurações locais (não vai ao git)
├── config.example.py            # Modelo de configuração
├── docker-compose.yml           # WAHA (WhatsApp HTTP API)
├── requirements.txt
│
├── core/                        # Lógica de negócio
│   ├── auth.py                  # Autenticação e criptografia
│   ├── database.py              # Banco de dados e migrações
│   ├── users.py                 # CRUD de usuários
│   ├── members.py               # CRUD de membros
│   ├── activities.py            # CRUD de atividades/eventos
│   ├── verse.py                 # Versículo do dia (bible-api.com + fallback)
│   └── whatsapp.py              # Integração WAHA
│
├── design/                      # Design system
│   ├── ui/
│   │   ├── tokens.py            # COLORS, SPACING, FONTS — fonte única de verdade
│   │   ├── components.py        # Biblioteca de componentes reutilizáveis
│   │   └── helpers.py           # Utilitários (truncate, initials, hover, etc.)
│   ├── pages/                   # Renderers de cada tela
│   │   ├── home.py              # Dashboard (KPIs, eventos, aniversariantes)
│   │   ├── activities.py        # Atividades e eventos
│   │   ├── members.py           # Lista de membros
│   │   ├── whatsapp.py          # Envio de mensagens
│   │   ├── users.py             # Gerenciamento de usuários
│   │   └── reports.py           # Relatórios
│   ├── modals/                  # Modais com design system
│   │   ├── base.py              # StyledModal — base com header/body/footer
│   │   └── activity.py          # ActivityModal — Nova/Editar atividade
│   └── app_shell.py             # Shell (header + sidebar + área de conteúdo)
│
├── views/                       # Controladores de tela
│   ├── login.py                 # Shell principal, navegação, tela de login
│   └── dialogs.py               # Diálogos de CRUD (membros, usuários)
│
└── .claude/
    └── agents/                  # Agentes especializados do Claude Code
        ├── commit.md
        ├── code-review.md
        ├── design.md
        └── ...
```

## Banco de Dados

| Tabela | Descrição |
|---|---|
| `usuarios` | Usuários do sistema com credenciais |
| `niveis_acesso` | Roles e permissões |
| `logs` | Auditoria de ações |
| `atividades` | Eventos e atividades da igreja |
| `membros` | Membros com função, status e aniversário |

### Status de Membros
- **Ativo** — membro regular
- **Afastado** — membro temporariamente afastado
- **Visitante** — visitante cadastrado

### Funções disponíveis
Pastor(a), Presbítero, Diácono(a), Evangelista, Líder de Célula, Louvor, Obreiro(a), Secretário(a), Tesoureiro(a), Membro

## Instalação e Uso

### 1. Configurar o arquivo de configuração

```bash
cp config.example.py config.py
```

Edite o `config.py` com o nome da sua organização e a chave do WhatsApp:

```python
APP_NAME         = "Minha Igreja"
WHATSAPP_API_KEY = "sua-chave-aqui"
ADMIN_EMAIL      = "admin@sistema.com"
ADMIN_PASSWORD   = "admin123"
```

> O `config.py` está no `.gitignore` e nunca será enviado ao repositório.

### 2. Configurar Ambiente Python

```bash
python -m venv venv

# Windows:
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar Aplicação

```bash
python main.py
```

A janela abre automaticamente em tela cheia.

### 5. Credenciais padrão

Na primeira execução, um usuário administrador é criado automaticamente:

| Campo | Valor |
|---|---|
| **E-mail** | `admin@igreja.com` |
| **Senha** | `admin123` |

> Altere a senha após o primeiro acesso em **Gerenciar Usuários**.

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
cd /mnt/c/caminho/ate/o/projeto   # substitua pelo caminho onde você clonou o repositório
sudo docker compose up -d
```

### 4. Conectar o número

1. Abra o sistema → menu **WhatsApp**
2. Clique em **"Ver QR Code"**
3. Escaneie com o WhatsApp do celular
4. O status muda para Conectado ao escanear

### 5. Uso diário

```bash
sudo service docker start
cd /mnt/c/caminho/ate/o/projeto
sudo docker compose up -d   # iniciar
sudo docker compose down    # parar
```

A sessão é salva em volume persistente — não precisa escanear o QR novamente, desde que use `up -d` e não `down`.

## Segurança

- Senhas criptografadas com bcrypt (12 rounds)
- Verificação de usuários ativos no login
- Sistema de auditoria com logs por usuário
- `config.py`, `user_prefs.json` e `*.db` excluídos do repositório via `.gitignore`

## Compilar para Executável

```bash
pyinstaller --onefile --windowed --name "gestao-igreja" main.py
```

O executável será gerado em `dist/gestao-igreja.exe`.

## Processos para a próxima release

- Corrigir o layout da aba **Membros**.
- Ao criar ou editar um membro, adicionar a opção de grupo:
  - Homens
  - Mulheres
  - Casais
- Nas reuniões e eventos, permitir marcar se a reunião é direcionada para um desses grupos.
- Atualizar a aba de eventos para exibir claramente o público-alvo do encontro.
- Garantir que filtros e relatórios também considerem o grupo selecionado.

## CI simples sugerido

Para ter validação automática sem complicar muito, podemos usar um workflow leve de CI com estes passos:

1. `actions/setup-python` para configurar o Python.
2. `pip install -r requirements.txt` para instalar dependências.
3. Rodar um script de validação simples:
   - `python -m pytest` (se houver testes)
   - ou `python -m py_compile main.py` para checar se não há erros de sintaxe.
4. Opcional: adicionar um lint básico caso configure o `flake8` ou `ruff` no futuro.

Esse workflow ajuda a detectar regressões antes do merge e mantém o processo de release mais seguro.

---

Desenvolvido com Python 3 + tkinter + SQLite
