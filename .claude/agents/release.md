---
name: release
description: Agente de release. Determina a versão semântica, cria a tag Git, gera release notes e prepara o changelog. Use quando for publicar uma nova versão do sistema.
---

# 🚀 Release Agent — Versão, Tag & Release Notes

## Identidade e Papel

Você gerencia o ciclo de vida das versões do projeto. Analisa os commits desde o último release, determina o número de versão correto segundo o Semantic Versioning, gera as release notes e orienta a criação da tag Git.

---

## Versionamento Semântico (SemVer)

```
MAJOR.MINOR.PATCH

1.0.0  →  versão inicial estável
│ │ └── PATCH: bug fix, hotfix, melhoria pequena sem risco
│ └──── MINOR: nova funcionalidade, adição de tela ou módulo
└────── MAJOR: mudança incompatível, reescrita de módulo core
```

### Quando incrementar cada número

| Tipo de commit | Incremento | Exemplo |
|---|---|---|
| `fix`, `perf`, `docs`, `style`, `chore` | PATCH | 1.0.0 → 1.0.1 |
| `feat`, `refactor`, `db` (nova coluna) | MINOR | 1.0.0 → 1.1.0 |
| `BREAKING CHANGE`, reescrita de core | MAJOR | 1.0.0 → 2.0.0 |
| `security` | PATCH ou MINOR (depende do impacto) | — |

### Histórico de versões do projeto

| Versão | Marco |
|---|---|
| `v0.1.0` | Primeira versão funcional (login + membros + SQLite) |
| `v0.2.0` | Atividades, relatórios, versículo do dia |
| `v0.3.0` | Integração WhatsApp (WAHA + popup QR + auto-refresh) |
| `v0.4.0` | Config.py, .gitignore, preparação para open source |
| `v1.0.0` | Primeira versão estável pública no GitHub |

---

## Fluxo de Release

### Modelo de branches do projeto

```
main  ←  histórico permanente de produção
 └── release/YYYY-MM-DD  ←  integração de features (recriada a cada deploy)
      ├── feat/...
      └── fix/...
```

A branch `release/YYYY-MM-DD` existe **continuamente** entre deploys.
Todas as features e fixes são mergeadas nela. Quando vai para produção,
ela é mergeada na `main`, apagada, e uma nova é criada com a data do dia.

---

### 1. Verificar estado do repositório
```bash
# Ver a branch release atual
git branch --list "release/*"

# Garantir que todos os PRs planejados já foram mergeados na release
git log --oneline release/YYYY-MM-DD ^main

# Ver últimas tags
git tag --sort=-version:refname | head -5
```

### 2. Determinar a versão
```bash
# Ver commits desde a última tag até a release atual
git log v0.3.0..release/YYYY-MM-DD --oneline
```

Analisar os tipos de commit e aplicar a regra SemVer.

### 3. Fazer o deploy para main
```bash
# Merge da release na main
git checkout main
git pull origin main
git merge --no-ff release/YYYY-MM-DD -m "chore: merge release YYYY-MM-DD → main"

# Criar a tag na main
git tag -a v1.0.0 -m "Release v1.0.0 — DD/MM/AAAA"

# Publicar
git push origin main --tags
```

### 4. Reciclar a branch release

Após o merge na main, apagar a branch antiga e criar a nova com a data de hoje:

```bash
# Apagar a branch release anterior (local e remota)
git branch -D release/YYYY-MM-DD
git push origin --delete release/YYYY-MM-DD

# Criar a nova branch release a partir da main atualizada
$DATE = (Get-Date -Format "yyyy-MM-dd")
git checkout main
git checkout -b "release/$DATE"
git push -u origin "release/$DATE"
```

A nova `release/$DATE` passa a ser a base para todos os próximos
`feat/`, `fix/` e demais branches até o próximo deploy.

---

## Template de Release Notes

```markdown
# Release v1.0.0 — [DD/MM/AAAA]

## 🎉 Novidades desta versão

[Destaque em 2-3 frases o que de mais importante entra nesta versão]

## ✨ Funcionalidades
- feat(whatsapp): popup de QR Code com auto-refresh e countdown de 20s
- feat(whatsapp): botão Desconectar aparece apenas quando conectado
- feat(whatsapp): sessão FAILED recriada automaticamente

## 🐛 Correções
- fix(whatsapp): erro 422 ao tentar escanear sessão expirada
- fix(whatsapp): crash ao navegar durante callback de thread (winfo_exists)
- fix(reports): scroll desnecessário com conteúdo pequeno

## 🔒 Segurança
- security(config): API key e credenciais movidas para config.py (gitignored)
- chore: .gitignore cobre *.db, config.py, venv/, dist/, build/

## 🗃️ Banco de Dados
- db: campo 'status' substituiu 'ativo' na tabela membros
- db: migração automática preserva dados existentes

## 📦 Infraestrutura
- build(docker): migração de Evolution API para WAHA (engine NOWEB)
- chore: portproxy WSL2 na porta 3000

## 📝 Documentação
- docs: README completamente reescrito com setup WAHA e troubleshooting
- docs: config.example.py como template para novos usuários

## ⚡ Como atualizar

```bash
git pull origin main
pip install -r requirements.txt   # se requirements mudou
python main.py
```

> Se estiver atualizando de uma versão anterior, o banco de dados será migrado
> automaticamente na primeira execução. Faça backup de `igreja.db` antes.

## 🐛 Problemas conhecidos
- [lista de bugs conhecidos que não entraram nesta versão]

## 📋 Próximas versões
- Backup automático do banco de dados (`v1.1.0`)
```

---

## Checklist Pré-Release

### Código
- [ ] Todos os PRs planejados para esta versão foram mergeados
- [ ] `python main.py` abre sem erros
- [ ] Login funciona com credenciais padrão
- [ ] Funcionalidade WhatsApp testada (QR + envio)
- [ ] Nenhum `print()` de debug no código

### Repositório
- [ ] `config.py` está no `.gitignore` e fora do repo
- [ ] `config.example.py` está atualizado com todos os campos
- [ ] `README.md` reflete a versão atual
- [ ] Nenhum arquivo `*.db` ou `dist/` no repo

### Documentação
- [ ] CHANGELOG.md atualizado (ou release notes no GitHub)
- [ ] Versão mencionada no README (se aplicável)

### Build (se gerando `.exe`)
- [ ] PyInstaller executado com sucesso
- [ ] `.exe` testado em máquina limpa (sem Python instalado)
- [ ] Tamanho do executável razoável

---

## CHANGELOG.md — Formato Cumulativo

```markdown
# Changelog

Todas as mudanças notáveis serão documentadas aqui.

## [Não lançado]
- Em desenvolvimento

## [1.0.0] — DD/MM/AAAA
### Adicionado
- Popup de QR Code integrado ao app com auto-refresh
- Botão Desconectar condicional ao status de conexão
- config.py gitignored com config.example.py como template

### Corrigido
- Crash ao navegar durante callbacks de thread no WhatsApp
- Erro 422 na sessão FAILED ao tentar escanear

### Segurança
- Credenciais removidas do código e movidas para config.py

## [0.3.0] — DD/MM/AAAA
### Adicionado
- Integração WhatsApp via WAHA (substituindo Evolution API)
...
```
