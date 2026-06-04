---
id: P1-STORE-01
title: Módulo stores — modelos store_stores + store_settings
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: STORE
status: done
depends_on: []
blocks: [P1-PERM-01, P1-DOM-01, P1-TEN-01, P1-STORE-02, P1-TEST-01]
tests: [integration]
---

# P1-STORE-01 — Módulo `stores`: modelos `store_stores` + `store_settings`

## Contexto
A loja é o **tenant** central (doc [06](../../06_multitenancy_and_domains.md)/[08](../../08_modules_and_permissions.md)). Esta task cria o módulo `stores` e seus modelos base, sobre os quais membership, domínios, tenancy e todo o comércio se apoiam. Usa os mixins da Fase 0 (`P0-MOD-01`).

## Docs de referência
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (estados da loja, configurações)
- [07 — Database Strategy](../../07_database_strategy.md)
- [Fundações INV-G3/INV-T1/INV-D1..D5](../_foundations-and-bottlenecks.md)

## Escopo (o que ENTRA)
- `store_stores` (`__tablename__="store_stores"`): `id` (UUID), `name`, `slug` (único **quando ativo**), `status` (`draft|active|paused|suspended|blocked|archived`), **`currency` (ISO 4217)** e **`locale`** próprios da loja (INV-G3; default vem de `P0-CFG-02`), timestamps, soft delete. Mixins: `UUIDMixin`/`TimestampMixin`/`SoftDeleteMixin`.
- `store_settings` (`__tablename__="store_settings"`): `store_id` (único, 1:1), nome público, descrição, `logo_url`, e-mail/telefone de contato, endereço, redes sociais, `whatsapp_number`, flag publicada. Doc [09](../../09_merchant_dashboard.md).
- Migration Alembic; índices: `store_stores.slug` único (parcial p/ não-arquivadas), `store_settings.store_id` único.
- Registrar os modelos em `app/models_registry.py`.

## Fora de escopo (o que NÃO entra)
- Serviço/rotas (criar/listar/publicar) → `P1-STORE-02`.
- `store_members`/papéis → `P1-PERM-01`; `domain_hosts` → `P1-DOM-01`.
- `currency`/`locale` do **cliente** → Fase 4.

## Arquivos a criar/alterar
- `backend/app/modules/stores/models.py` (criar) — `Store`/`StoreSettings` + schemas públicos.
- `backend/app/modules/stores/__init__.py` — já existe (skeleton do `P0-MOD-02`); só popular o módulo.
- `backend/app/alembic/versions/xxxx_create_store_tables.py` (criar).
- `backend/app/models_registry.py` (alterar) — importar os modelos.

## Passos
1. Modelar `Store` (com `status` como enum, `currency`/`locale`) e `StoreSettings` (1:1) usando os mixins.
2. Definir o enum de status conforme doc [09](../../09_merchant_dashboard.md).
3. Gerar e aplicar a migration; conferir índices/constraints em db do zero.
4. Registrar no `models_registry`.

## Testes
> Fundações §10.

- **Níveis:** integração (constraints/migration são fronteiras reais).
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — migration aplica limpa; `slug` único quando ativo; `store_settings.store_id` 1:1; soft delete preenche `deleted_at`.

## Definition of Done
- [x] `store_stores` e `store_settings` criadas via migration `516224031edd` (aplica em db do zero).
- [x] `Store` carrega `currency`/`locale` próprios; `status` (enum `storestatus`) com os 6 estados do doc [09](../../09_merchant_dashboard.md).
- [x] Índices/constraints (slug único quando não-deletado; `store_settings.store_id` 1:1) verificados por integração *(80 testes; cobertura 91%)*.

## Notas / Reconciliações
- IDs ilustrativos inteiros nos docs (`id: 123`) são ilustrativos — usamos UUID (INV-D1).
- **Implementado:** `Store`/`StoreSettings` herdam `UUIDMixin`/`TimestampMixin`/`SoftDeleteMixin`; `status` = enum nativo Postgres (`storestatus`); `currency`/`locale` **obrigatórios** (preenchidos a partir do default da plataforma em `P1-STORE-02`); `social_links` = coluna JSON. Schemas `StorePublic`/`StoreSettingsPublic` prontos.
- **Slug "quando ativo" = `deleted_at IS NULL`** (índice único parcial). Loja `archived` tem `deleted_at` setado → slug liberado para reuso. O índice fica em `__table_args__` (para o `create_all` dos testes enforçar) **e** na migration.
- **Migration via autogenerate**, limpa de dois ruídos não-relacionados que **foram resolvidos na sequência** (mini-limpeza, mesma PR): o probe `_MixinProbe` (`tests/integration/test_base_mixins.py`) passou a usar um `MetaData()` próprio (não registra mais no `SQLModel.metadata`), e o índice foi renomeado `ix_user_email`→`ix_account_users_email` pela migration `c2d3e4f5a6b7`. **Verificado:** autogenerate agora vem **vazio** (sem ruído recorrente).
- **Layout do módulo (convenção):** `models.py` = só tabelas + `*Base`; `StoreStatus` foi para `enums.py` e `StorePublic`/`StoreSettingsPublic` para `schemas.py` (mesmo split aplicado ao `accounts`). Convenção atualizada no doc [04](../../04_fastapi_template_adaptation.md) + README do backlog (#4).

## Follow-ups
- [x] **Limpeza do ruído de `alembic autogenerate`** (`_MixinProbe` isolado em `MetaData()` próprio + rename `ix_user_email`→`ix_account_users_email`, migration `c2d3e4f5a6b7`) — *resolvido nesta task.* → README da fase.
