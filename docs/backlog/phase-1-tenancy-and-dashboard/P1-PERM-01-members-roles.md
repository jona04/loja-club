---
id: P1-PERM-01
title: store_members + store_roles (membership)
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: PERM
status: todo
depends_on: [P1-ACCT-01, P1-STORE-01]
blocks: [P1-PERM-02, P1-TEN-01, P1-STORE-02, P1-TEST-01]
tests: [integration]
---

# P1-PERM-01 — `store_members` + `store_roles` (membership)

## Contexto
Liga `account_users` (Fase 0) às lojas: um usuário pode ser membro de várias lojas com **papel diferente em cada uma** (doc [08](../../08_modules_and_permissions.md)/[06](../../06_multitenancy_and_domains.md)). Esta task cria a tabela de membership e a tabela de papéis (seed); o catálogo de permissões e o enforcement vêm depois.

## Docs de referência
- [08 — Modules and Permissions](../../08_modules_and_permissions.md)
- [07 — Database Strategy](../../07_database_strategy.md) (lista `store_members` e `store_roles` como **tabelas**; índices)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)

## Escopo (o que ENTRA)
- `store_roles` (`__tablename__="store_roles"`): tabela **seedada** com os 6 papéis do doc [08](../../08_modules_and_permissions.md) — `owner|admin|manager|support|catalog|marketing` (`key` único + `name`). Doc [07](../../07_database_strategy.md) lista `store_roles` como tabela.
- `store_members` (`__tablename__="store_members"`): `store_id`, `user_id` (→ `account_users.id`), `role` (→ `store_roles`), `status` (`active|invited|removed`), `invited_at`, `removed_at`, timestamps, soft delete (mixins). Índice **único `store_id + user_id` quando ativo**; índice `store_id + status` (doc [07](../../07_database_strategy.md)).
- Migration: cria as duas tabelas + **seed** dos 6 papéis em `store_roles`.

## Fora de escopo (o que NÃO entra)
- Catálogo de permissões (`store_permissions`) + mapa papel→permissões → `P1-PERM-02`.
- `require_permission`/enforcement na rota → `P1-PERM-03`.
- Overrides de permissão por membro: doc [07](../../07_database_strategy.md) lista `store_member_permissions` como **opcional** ("se necessário") → **fora do MVP** (só papel→permissões em `P1-PERM-02`).
- Convite por e-mail (fluxo completo) → tela em `P1-DASH-03`; envio reaproveita `app/utils.py`.

## Arquivos a criar/alterar
- `backend/app/modules/stores/models.py` (alterar) — `StoreRole` (tabela) + `StoreMember` + schemas.
- `backend/app/alembic/versions/xxxx_create_store_members_roles.py` (criar) — tabelas + seed dos papéis.
- `backend/app/models_registry.py` (alterar).

## Passos
1. Modelar `StoreRole` (tabela, `key`/`name`) e `StoreMember` (FKs para `account_users`, `store_stores`, `store_roles`) com `status` e mixins.
2. Migration cria as tabelas e **seed** dos 6 papéis.
3. Índice único `store_id + user_id` (parcial p/ ativos) + `store_id + status`.
4. Aplicar em db do zero e conferir.

## Testes
> Fundações §10. Constraints/FK/seed são fronteiras reais → integração.

- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — os 6 papéis existem em `store_roles` após a migration; não permite dois membros ativos com mesmo `store_id + user_id`; remover membro (soft) libera novo convite; FK para `account_users`/`store_roles`.

## Definition of Done
- [ ] `store_roles` (seedada com 6 papéis) e `store_members` criadas via migration (db do zero).
- [ ] Índice único `store_id + user_id` (ativo) verificado por teste.
- [ ] Um `account_user` é membro de 2 lojas com papéis diferentes (teste).

## Notas / Reconciliações
- **`store_roles` é global/seed** (os 6 papéis valem para todas as lojas; aplicam-se no contexto da loja via `store_members`). Doc [07](../../07_database_strategy.md) diz "papéis por loja" — interpretado como "no contexto da loja", não linhas por-loja. Se a implementação exigir papéis editáveis por loja, registrar e atualizar o doc.
- `account_users.is_superuser` ↔ admin de plataforma: superuser cobre acesso interno no MVP; `platform_admin_roles` na Fase 6 (herdado de `P0-MOD-04`).
