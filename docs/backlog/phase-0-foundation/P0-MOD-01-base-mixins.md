---
id: P0-MOD-01
title: Mixins base + app/db
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: MOD
status: done
depends_on: []
blocks: [P0-MOD-02, P0-MOD-04]
tests: [unit, integration]
---

# P0-MOD-01 — Mixins base + `app/db`

## Contexto
Todo modelo de domínio vai compartilhar o mesmo padrão: PK UUID, timestamps, soft delete e (quando comercial) `store_id`. Centralizar isso em mixins evita repetição e garante consistência com os docs.

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md)
- [14 — Security Strategy](../../14_security_strategy.md) (soft delete)

## Escopo (o que ENTRA)
- `backend/app/db/base.py` com mixins SQLModel:
  - `UUIDMixin` — `id: uuid.UUID` PK (`default_factory=uuid4`).
  - `TimestampMixin` — `created_at`, `updated_at` (timezone-aware).
  - `SoftDeleteMixin` — `deleted_at`, `deleted_by_user_id`, `delete_reason`.
  - `StoreScopedMixin` — `store_id: uuid.UUID` (indexado).
- Centralizar `get_datetime_utc()` (hoje em `app/models.py`) em `app/db/base.py`.

## Fora de escopo (o que NÃO entra)
- Aplicar os mixins nos modelos de domínio — cada módulo faz isso na sua fase.
- Criar os módulos em si → `P0-MOD-02`.

## Arquivos a criar/alterar
- `backend/app/db/__init__.py` (criar).
- `backend/app/db/base.py` (criar) — mixins + `get_datetime_utc`.

## Passos
1. Criar `app/db/base.py` com os 4 mixins e o helper de datetime.
2. Garantir tipos corretos (`sa_type=DateTime(timezone=True)` como no template).
3. Escrever um modelo de teste descartável usando os mixins para validar as colunas (remover depois ou manter em teste).

## Testes
> Fundações §10.

- **Níveis:** unit + integração.
- **Quando:** durante.
- **Cobrir:**
  - unit — `get_datetime_utc()` retorna datetime UTC tz-aware.
  - integração — modelo de teste com os mixins gera as colunas esperadas (UUID PK, timestamps, soft delete, `store_id`).

## Definition of Done
- [x] Mixins importáveis de `app.db.base`.
- [x] Um modelo usando os 4 mixins gera as colunas esperadas. *(test_mixins_generate_expected_columns, via `__table__.columns`)*

## Notas / Reconciliações
- PK é **UUID** (padrão do template). Os ids inteiros nos exemplos dos docs são ilustrativos (decisão global do backlog).
- **Implementado:** `app/db/base.py` (4 mixins + `get_datetime_utc` centralizado, movido do `models.py`, que agora o importa). `updated_at` tem `onupdate`. Verificação das colunas via `__table__.columns` de um modelo-probe (equivalente ao objetivo da task). 69 testes passam; gate `app` verde.
