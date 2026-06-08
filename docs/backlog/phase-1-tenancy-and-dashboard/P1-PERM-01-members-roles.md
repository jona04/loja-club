---
id: P1-PERM-01
title: store_members + store_roles (membership)
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: PERM
status: done
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
- Migration: cria as duas tabelas. **Seed dos 6 papéis via `init_db`** (idempotente, mesma estratégia do superuser — ver Notas).

## Fora de escopo (o que NÃO entra)
- Catálogo de permissões (`store_permissions`) + mapa papel→permissões → `P1-PERM-02`.
- `require_permission`/enforcement na rota → `P1-PERM-03`.
- Overrides de permissão por membro: doc [07](../../07_database_strategy.md) lista `store_member_permissions` como **opcional** ("se necessário") → **fora do MVP** (só papel→permissões em `P1-PERM-02`).
- Convite por e-mail (fluxo completo) → tela em `P1-DASH-03`; envio reaproveita `app/utils.py`.

## Arquivos a criar/alterar
- `backend/app/modules/stores/models.py` (alterar) — `StoreRole` (tabela) + `StoreMember`; `MembershipStatus` em `enums.py`.
- `backend/app/modules/stores/repositories.py` (criar) — `STORE_ROLES` + `seed_store_roles` (idempotente).
- `backend/app/core/db.py` (alterar) — `init_db` chama `seed_store_roles`.
- `backend/app/alembic/versions/067477c95fc2_create_store_members_and_roles.py` (criar) — só as tabelas.

## Passos
1. Modelar `StoreRole` (tabela, `key`/`name`) e `StoreMember` (FKs para `account_users`, `store_stores`, `store_roles`) com `status` e mixins.
2. Migration cria as tabelas; o **seed** dos papéis fica no `init_db` (idempotente, fonte única em `stores/repositories.py`).
3. Índice único `store_id + user_id` (parcial p/ ativos) + `store_id + status`.
4. Aplicar em db do zero e conferir.

## Testes
> Fundações §10. Constraints/FK/seed são fronteiras reais → integração.

- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — os 6 papéis existem em `store_roles` após a migration; não permite dois membros ativos com mesmo `store_id + user_id`; remover membro (soft) libera novo convite; FK para `account_users`/`store_roles`.

## Definition of Done
- [x] `store_roles` e `store_members` criadas via migration `067477c95fc2` (db do zero); 6 papéis seedados por `init_db` (idempotente) — verificado por teste *(84 testes; cobertura 91%)*.
- [x] Índice único **parcial** `(store_id, user_id) WHERE deleted_at IS NULL` verificado por teste (remover/soft-delete libera novo convite).
- [x] Um `account_user` é membro de 2 lojas com papéis diferentes (teste).

## Notas / Reconciliações
- **Seed via `init_db`, não na migration (reconciliação):** os testes criam o schema com `create_all` (não rodam migrations), então o seed na migration não chegaria neles. Seguindo o padrão do superuser, os papéis são seedados em `init_db` (idempotente), com fonte única `STORE_ROLES` em `stores/repositories.py`. A migration só cria as tabelas. Prod: `prestart`→`init_db` semeia (como o superuser).
- **`MembershipStatus`** (`invited|active|removed`) em `stores/enums.py`; **`StoreMember`** com mixins (soft delete) + FKs (`store_stores`/`account_users`/`store_roles`); **`StoreRole`** é lookup mínimo (`id`/`key`/`name`).
- **`store_roles` é global/seed** (os 6 papéis valem para todas as lojas; aplicam-se no contexto da loja via `store_members`). Doc [07](../../07_database_strategy.md) diz "papéis por loja" — interpretado como "no contexto da loja", não linhas por-loja. Se a implementação exigir papéis editáveis por loja, registrar e atualizar o doc.
- `account_users.is_superuser` ↔ admin de plataforma: superuser cobre acesso interno no MVP; `platform_admin_roles` na Fase 7 (herdado de `P0-MOD-04`).
