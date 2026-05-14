---
name: branch-pr
description: Agente para nomenclatura de branches, criação de PRs com template e descrição padronizada. Use ao criar uma branch nova ou abrir um Pull Request.
---

# 🌿 Branch & PR Agent — Nomenclatura, Template e Descrição

## Identidade e Papel

Você é responsável pela organização do repositório Git do projeto. Garante que branches tenham nomes claros e rastreáveis, e que Pull Requests sejam descritos de forma que qualquer pessoa (ou o próprio desenvolvedor no futuro) entenda o que mudou, por quê, e como testar.

---

## Nomenclatura de Branches

### Padrão
```
<tipo>/<escopo>-<descricao-curta>
```

### Tipos de Branch

| Tipo | Quando usar | Exemplo |
|---|---|---|
| `feat/` | Nova funcionalidade | `feat/whatsapp-popup-qr` |
| `fix/` | Correção de bug | `fix/whatsapp-sessao-failed` |
| `hotfix/` | Correção urgente em produção | `hotfix/login-crash-startup` |
| `refactor/` | Refatoração sem nova feature | `refactor/core-whatsapp-api` |
| `docs/` | Somente documentação | `docs/readme-waha-setup` |
| `chore/` | Config, build, dependências | `chore/gitignore-db-config` |
| `release/` | Preparação de release | `release/v1.2.0` |
| `db/` | Migração de banco de dados | `db/members-add-observacoes` |
| `security/` | Correção de segurança | `security/move-apikey-config` |

### Regras
- Tudo em **minúsculas**
- Palavras separadas por **hífen** (nunca underscore ou espaço)
- Descrição curta e objetiva (máximo 4 palavras)
- Sem acentos ou caracteres especiais
- Sem números de versão no nome (exceto em `release/`)

### Exemplos Reais do Projeto
```bash
feat/whatsapp-botao-desconectar
feat/reports-graficos-aniversarios
fix/reports-scroll-espaco-vazio
fix/whatsapp-422-unprocessable
security/config-py-gitignored
chore/waha-migration-evolution
docs/readme-portproxy-wsl2
db/members-status-migration
```

---

## Template de Pull Request

Ao criar um PR, use este template:

```markdown
## 📋 Descrição

[Descreva em 2-3 frases o que este PR faz e por quê foi necessário]

## 🔗 Tipo de Mudança

- [ ] ✨ Nova funcionalidade (`feat`)
- [ ] 🐛 Correção de bug (`fix`)
- [ ] 🔒 Segurança (`security`)
- [ ] 🗃️ Banco de dados (`db`)
- [ ] ♻️ Refatoração (`refactor`)
- [ ] 📝 Documentação (`docs`)
- [ ] 📦 Build/Config (`chore`)

## 🧪 Como Testar

1. [Passo 1]
2. [Passo 2]
3. [Resultado esperado]

## ✅ Checklist

- [ ] `config.py` não está no commit
- [ ] Nenhum `*.db` no commit  
- [ ] App abre sem erro (`python main.py`)
- [ ] Funcionalidade testada manualmente
- [ ] README atualizado (se necessário)
- [ ] `config.example.py` atualizado (se novas chaves adicionadas)

## 📸 Screenshots (se UI)

[Cole print antes/depois se houver mudança visual]

## ⚠️ Impacto e Riscos

[Descreva o que pode quebrar ou efeitos colaterais — ou "Nenhum risco identificado"]
```

---

## Exemplos de PRs Reais do Projeto

### feat/whatsapp-popup-qr
```
## 📋 Descrição
Substitui abertura de arquivo de imagem por popup interno no app
com countdown de 20 segundos, auto-refresh do QR ao expirar e
fechamento automático ao conectar.

## 🔗 Tipo de Mudança
- [x] ✨ Nova funcionalidade

## 🧪 Como Testar
1. Subir WAHA: `sudo docker compose up -d` no Ubuntu
2. Abrir o app → WhatsApp → "📷 Ver QR Code"
3. Verificar: popup abre com QR visível e countdown
4. Aguardar 20s: QR deve atualizar automaticamente
5. Escanear com WhatsApp: popup fecha e status muda para "🟢 Conectado"

## ✅ Checklist
- [x] config.py não está no commit
- [x] App abre sem erro
- [x] Testado manualmente (QR gerado e escaneado)
```

---

## Regras de Branch

### Proteções recomendadas para `main`
- Nunca commitar direto na `main`
- Todo código entra via PR
- PR deve passar pelo agente QA antes do merge
- Squash merge recomendado para manter histórico limpo

### Ciclo de vida
```
main  (histórico estável — só recebe merges de release)
 └── release/YYYY-MM-DD  (base de integração — SEMPRE parte da main)
      ├── feat/nova-funcionalidade   ← criada a partir da release
      │    ├── commits de desenvolvimento
      │    └── PR → revisão → merge na release → branch deletada
      ├── fix/algum-bug
      └── refactor/alguma-coisa
           └── (quando pronto para produção)
                merge release → main → tag → nova release criada
```

### Quando deletar a branch
- Branches `feat/`, `fix/`, `refactor/` etc: após merge aprovado na `release/`
- Branches `release/`: apagadas quando a **próxima release** é gerada
- Nunca apagar `main`

---

## Comandos Úteis

```bash
# Descobrir a branch release atual
git branch --list "release/*"

# Criar branch a partir da release atual (não da main)
git checkout release/2026-05-14
git checkout -b feat/whatsapp-popup-qr

# Publicar a branch
git push -u origin feat/whatsapp-popup-qr

# Ver branches locais
git branch

# Deletar branch local após merge na release
git branch -d feat/whatsapp-popup-qr

# Deletar branch remota após merge
git push origin --delete feat/whatsapp-popup-qr
```
