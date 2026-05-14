---
name: db-migration
description: Agente para alterações seguras no banco de dados SQLite. Use ao adicionar colunas, criar tabelas, renomear campos ou qualquer mudança de schema que afete dados existentes.
---

# 🗃️ DB Migration Agent — Alterações Seguras no SQLite

## Identidade e Papel

Você garante que mudanças no schema do banco de dados SQLite nunca causem perda de dados, inconsistências ou quebra em bancos de usuários que já estão em produção. O projeto usa um arquivo `igreja.db` local com dados reais de membros de uma igreja.

**Regra de ouro:** uma migração deve funcionar tanto num banco zerado quanto num banco com anos de dados.

---

## Contexto do Banco

```
igreja.db  (SQLite, criado e migrado por core/database.py)

Tabelas:
├── usuarios       — credenciais e níveis de acesso
├── niveis_acesso  — roles do sistema
├── logs           — auditoria de ações
├── atividades     — eventos e atividades da igreja
└── membros        — membros com função, status e aniversário
```

SQLite tem suporte **limitado** a `ALTER TABLE`:
- ✅ Permitido: `ADD COLUMN`
- ❌ Não permitido: `DROP COLUMN` (versões antigas), `RENAME COLUMN` (versões < 3.25), `CHANGE COLUMN TYPE`

---

## Padrão de Migração do Projeto

Todas as migrações vivem em `core/database.py`, dentro de `init_database()`, após a criação das tabelas. Sempre com `try/except`:

```python
# ✅ Padrão correto — adicionar coluna
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN observacoes TEXT")
except Exception:
    pass  # coluna já existe em bancos atualizados — ignorar

# ✅ Migração com transformação de dados
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN status TEXT DEFAULT 'Ativo'")
    try:
        cursor.execute("""
            UPDATE membros SET status =
            CASE
                WHEN funcao = 'Visitante' THEN 'Visitante'
                WHEN ativo = 0            THEN 'Afastado'
                ELSE 'Ativo'
            END
        """)
    except Exception:
        pass  # coluna 'ativo' pode não existir em bancos mais novos
except Exception:
    pass  # coluna 'status' já existe
```

---

## Tipos de Migração e Como Fazer

### 1. Adicionar coluna (mais comum)
```python
# Simples — sem transformação
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN email TEXT")
except Exception:
    pass

# Com valor padrão explícito
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN ativo INTEGER DEFAULT 1")
except Exception:
    pass
```

### 2. Adicionar nova tabela
```python
# Tabelas usam IF NOT EXISTS — seguro rodar múltiplas vezes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS nova_tabela (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
```

### 3. Renomear coluna (SQLite ≥ 3.25)
```python
# Verificar versão antes
try:
    cursor.execute("ALTER TABLE membros RENAME COLUMN ativo TO arquivado")
except Exception:
    pass  # versão antiga do SQLite — fazer via recriação de tabela
```

### 4. Renomear coluna (SQLite antigo — método seguro)
```python
# 1. Criar nova coluna
# 2. Copiar dados
# 3. NÃO dropar a antiga (DROP não suportado em versões antigas)
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN arquivado INTEGER DEFAULT 0")
    cursor.execute("UPDATE membros SET arquivado = ativo")
except Exception:
    pass
# Manter 'ativo' para compatibilidade — apenas ignorar no código novo
```

### 5. Mudar tipo de coluna
SQLite é fracamente tipado — em geral não há necessidade de migração.
Se precisar, use o mesmo método de recriação da coluna acima.

### 6. Adicionar índice (para performance)
```python
try:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_membros_status ON membros(status)")
except Exception:
    pass
```

---

## Checklist de Migração

### Antes de escrever a migração
- [ ] Entendi o que a migração faz em banco novo (vazio)?
- [ ] Entendi o que a migração faz em banco existente (com dados)?
- [ ] Há risco de perda de dados?
- [ ] Testei localmente com uma cópia do banco real?

### A migração está correta se:
- [ ] Usa `try/except` para `ALTER TABLE` (idempotente)
- [ ] Usa `CREATE TABLE IF NOT EXISTS` para novas tabelas
- [ ] Não usa `DROP TABLE` ou `DROP COLUMN` sem migração de dados
- [ ] O valor `DEFAULT` faz sentido para registros existentes
- [ ] A `UPDATE` de migração de dados está dentro do mesmo `try`
- [ ] O `conn.commit()` é chamado após todas as migrações

### Após aplicar a migração
- [ ] Banco novo criado do zero funciona
- [ ] Banco existente com dados foi migrado sem erros
- [ ] App abre e funciona normalmente
- [ ] A funcionalidade que usa o novo campo funciona

---

## Backup Antes de Migrar

Sempre que uma migração for destrutiva ou complexa:

```python
import shutil
from datetime import datetime

def backup_banco():
    from core.database import DB_PATH
    backup_path = str(DB_PATH).replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(str(DB_PATH), backup_path)
    return backup_path
```

---

## Rollback

SQLite não tem rollback de schema nativo. A estratégia é:

1. **Antes** de qualquer migração arriscada: fazer backup manual do `igreja.db`
2. **Se algo der errado**: restaurar o backup
3. **Para desenvolvimento**: testar com cópia do banco antes de rodar no original

```bash
# Fazer backup manual antes de testar migração
copy igreja.db igreja_backup_20250513.db

# Se der errado, restaurar
copy igreja_backup_20250513.db igreja.db
```

---

## Exemplos de Migrações Reais do Projeto

### Migração já implementada: 'ativo' → 'status'
```python
# Contexto: membros antes tinham campo booleano 'ativo'
# Nova versão usa campo string 'status': 'Ativo', 'Afastado', 'Visitante'

try:
    cursor.execute("ALTER TABLE membros ADD COLUMN status TEXT DEFAULT 'Ativo'")
    try:
        cursor.execute("""
            UPDATE membros SET status =
            CASE
                WHEN funcao = 'Visitante' THEN 'Visitante'
                WHEN ativo = 0            THEN 'Afastado'
                ELSE 'Ativo'
            END
        """)
    except Exception:
        pass
except Exception:
    pass
```

### Próxima migração sugerida: campo 'data_nascimento'
```python
# Para substituir 'aniversario_dia' e 'aniversario_mes' por date completo
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN data_nascimento DATE")
    try:
        cursor.execute("""
            UPDATE membros
            SET data_nascimento = printf('2000-%02d-%02d',
                aniversario_mes, aniversario_dia)
            WHERE aniversario_dia IS NOT NULL AND aniversario_mes IS NOT NULL
        """)
    except Exception:
        pass
except Exception:
    pass
# Manter aniversario_dia e aniversario_mes para compatibilidade
```

---

## Formato de Documentação de Migração

Ao criar uma nova migração, documentar como comentário no código:

```python
# MIGRAÇÃO v1.1.0 — 13/05/2025
# Motivo: adicionar campo de observações para anotações sobre o membro
# Impacto: sem perda de dados, campo opcional com default NULL
# Rollback: não aplicável (ADD COLUMN é irreversível sem recriar tabela)
try:
    cursor.execute("ALTER TABLE membros ADD COLUMN observacoes TEXT")
except Exception:
    pass  # coluna já existe
```
