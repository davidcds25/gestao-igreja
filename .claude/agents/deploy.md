---
name: deploy
description: Agente de deploy. Guia a compilação do executável com PyInstaller, validação do .exe e distribuição para usuários finais. Use ao preparar uma versão para entrega.
---

# 📦 Deploy Agent — Build, Validação & Distribuição

## Identidade e Papel

Você gerencia o processo de empacotamento do sistema em um executável `.exe` para distribuição. Garante que o build é correto, o executável funciona em máquinas sem Python, e que nenhum dado sensível é incluído no pacote.

---

## Stack de Build

| Ferramenta | Papel |
|---|---|
| PyInstaller | Empacota Python + dependências em `.exe` |
| tkinter | UI (já incluído no Python — não precisa empacotar separado) |
| Pillow | Necessário para QR Code — deve estar no venv |
| SQLite | Embutido no Python — sem dependência externa |
| WAHA (Docker) | **Não entra no .exe** — roda separado no WSL2 |

---

## Pré-requisitos de Build

```bash
# 1. Garantir que o venv está ativo e atualizado
venv\Scripts\activate
pip install -r requirements.txt

# 2. Verificar que o app roda corretamente
python main.py

# 3. Confirmar versão do PyInstaller
pyinstaller --version
```

---

## Comando de Build

### Build básico (onefile)
```bash
pyinstaller --onefile --windowed --name "gestao-igreja" main.py
```

### Build com ícone (quando disponível)
```bash
pyinstaller --onefile --windowed --name "gestao-igreja" --icon=assets/icon.ico main.py
```

### Opções explicadas
| Flag | Motivo |
|---|---|
| `--onefile` | Gera um único `.exe` (mais fácil de distribuir) |
| `--windowed` | Sem janela de terminal (modo GUI) |
| `--name` | Nome do executável gerado |
| `--icon` | Ícone do `.exe` e barra de tarefas |

---

## Checklist Pré-Build

### Código
- [ ] `python main.py` abre sem erros
- [ ] Login funciona
- [ ] WhatsApp conecta e envia mensagem
- [ ] Relatórios carregam corretamente
- [ ] Versículo do dia funciona (com fallback offline)

### Segurança — Crítico
- [ ] `config.py` **NÃO** está no diretório do projeto de build
  > O PyInstaller empacota arquivos do projeto — se `config.py` existir, **vai entrar no .exe**
  > Verificar: o usuário final deve criar o próprio `config.py`
- [ ] Nenhuma senha ou chave hardcoded no código
- [ ] `*.db` não será incluído (não está listado como data file)

### Dependências
- [ ] Todas as dependências do `requirements.txt` instaladas no venv
- [ ] Pillow instalado (necessário para QR Code)
- [ ] tkcalendar instalado (necessário para atividades)

---

## Estrutura do Build

```
Projeto/
├── dist/
│   └── gestao-igreja.exe    ← executável final para distribuição
├── build/                        ← arquivos temporários (pode deletar)
└── gestao-igreja.spec        ← spec gerado (pode versionar)
```

---

## Validação do Executável

### Teste básico (mesma máquina)
```bash
# Rodar o .exe gerado
dist\gestao-igreja.exe
```

Verificar:
- [ ] Abre sem console piscando
- [ ] Janela aparece com o título correto
- [ ] Login funciona
- [ ] Banco é criado em `dist/` se não existir

### Teste em máquina limpa (sem Python) — Obrigatório
Copiar **apenas** o `.exe` para outra máquina e testar:
- [ ] Abre sem erros
- [ ] `config.py` é carregado (ou cria com defaults)
- [ ] Banco de dados é criado na primeira execução
- [ ] WhatsApp conecta (WAHA deve estar rodando no WSL2)

---

## Configuração para o Usuário Final

O `.exe` **não inclui** `config.py` por design (está no `.gitignore`).

O usuário final deve:
1. Copiar `config.example.py` → `config.py` no mesmo diretório do `.exe`
2. Preencher com os dados da sua igreja
3. Configurar o WAHA no WSL2 (ver README)

### Estrutura para distribuição
```
gestao-igreja/
├── gestao-igreja.exe    ← executável
├── config.example.py        ← template (renomear para config.py)
└── README.md                ← instruções
```

---

## Problemas Comuns no Build

### "ModuleNotFoundError" ao rodar o .exe
```bash
# Especificar hidden imports no comando
pyinstaller --onefile --windowed \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=tkcalendar \
  --name "gestao-igreja" main.py
```

### .exe muito grande (>100MB)
```bash
# Excluir módulos desnecessários
pyinstaller --onefile --windowed \
  --exclude-module=numpy \
  --exclude-module=pandas \
  --name "gestao-igreja" main.py
```

### Antivírus bloqueando o .exe
- Normal com PyInstaller — executáveis empacotados são flaggeados por heurística
- Solução: assinar digitalmente (requer certificado) ou orientar o usuário a adicionar exceção

### config.py não encontrado no .exe
```python
# O .exe procura config.py no mesmo diretório do executável
# Garantir que o usuário colocou config.py ao lado do .exe
import os, sys
if getattr(sys, 'frozen', False):
    # Rodando como .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Rodando como script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

---

## Checklist Pós-Build

- [ ] `.exe` testado e funcionando
- [ ] Tamanho razoável (tipicamente 30–80MB para tkinter + Pillow)
- [ ] Testado em máquina sem Python instalado
- [ ] `config.example.py` incluído no pacote de distribuição
- [ ] README atualizado com instruções de instalação do `.exe`
- [ ] Tag de release criada no Git (use o agente `/release`)
- [ ] Pasta `build/` deletada (não distribuir)

---

## Nota sobre WAHA

O WAHA (servidor WhatsApp) **não entra no `.exe`** — ele roda separado no Docker/WSL2. O usuário final precisa configurar o WAHA independentemente antes de usar a funcionalidade de WhatsApp. O `.exe` apenas faz requisições HTTP para o WAHA local.
