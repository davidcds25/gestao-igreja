# Workflow de Agents — Ciclo completo antes do push

---

## Estrutura de branches

```
main                        ← histórico permanente (só recebe release)
 └── release/2026-05-14     ← base de integração (recriada a cada deploy)
      ├── feat/algo          ← criada a partir da release
      ├── fix/outro-bug      ← criada a partir da release
      └── refactor/limpeza
```

Nunca trabalhe direto na `main`. Nunca crie feature branch a partir da `main`.
**Toda branch parte da `release/YYYY-MM-DD` atual.**

---

## Ordem dos agents — Desenvolvimento de feature

```
INÍCIO: checkout na release/YYYY-MM-DD atual
        │
        ▼
  1. branch-pr        ← cria a feature branch (feat/, fix/, refactor/...)
        │               a partir da release — ANTES de qualquer alteração
        ▼
  [fazer as alterações no código]
        │
        ▼
  2. qa               ← revisão de qualidade geral
        │ corrige problemas encontrados
        ▼
  3. code-review      ← análise técnica profunda
        │ corrige problemas encontrados
        ▼
  4. peer-review      ← perspectiva crítica de colega
        │ corrige problemas encontrados
        ▼
  5. commit           ← commit semântico (na feature branch, não na release)
        │
        ▼
  6. merge-guard      ← valida segurança antes de mergear na release
        │
        ▼
  git merge na release/YYYY-MM-DD → deletar feature branch
```

---

## Agents especiais (quando aplicável)

| Agent | Quando invocar |
|---|---|
| `db-migration` | Sempre que alterar schema do SQLite (antes do commit) |
| `design` | Ao criar/modificar componentes visuais (antes do commit) |

---

## Ordem dos agents — Deploy para produção

Quando a `release/YYYY-MM-DD` está pronta com todas as features:

```
  7. release          ← versão semântica + release notes
        │               + merge release → main + tag
        │               + apaga release antiga + cria release/nova-data
        ▼
  8. deploy           ← build do .exe via PyInstaller
        │
        ▼
  git push origin main --tags
```

---

## Fluxo completo em um único visual

```
release/YYYY-MM-DD
      │
      ├── branch-pr → feat/algo
      │                   │
      │                  qa → code-review → peer-review → commit → merge-guard
      │                   │
      │               merge na release → deleta feat/algo
      │
      ├── branch-pr → fix/bug
      │                   │
      │                  qa → commit → merge na release → deleta fix/bug
      │
      ▼
  (pronto para produção)
  release → deploy → push main --tags
  apaga release/old → cria release/nova-data
```

---

## Script de pré-push

Para verificar o estado do git e receber o checklist em qualquer momento:

```powershell
.\scripts\pre-push.ps1
```
