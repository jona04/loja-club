---
id: P1-ACCT-01
title: Retrofit account_users — soft delete + updated_at (mixins)
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: ACCT
status: done
depends_on: []
blocks: [P1-PERM-01]
tests: [integration]
---

# P1-ACCT-01 — Retrofit `account_users`: soft delete + `updated_at` (mixins)

## Contexto
O `account_users` (criado no `P0-MOD-04` com migração mínima) **não usa os mixins**: define `id`/`created_at` na mão, **sem `updated_at` e sem soft delete**, e a rota de remoção faz **hard delete** (`session.delete`). Isso contraria **INV-D2** e o doc [07](../../07_database_strategy.md) ("não deve existir hard delete em registros de negócio"). Como `store_members` vai referenciar `account_users`, este é o momento de alinhar antes que mais modelos dependam disso.

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md) (soft delete; sem hard delete)
- [14 — Security Strategy](../../14_security_strategy.md)
- [Fundações INV-D2](../_foundations-and-bottlenecks.md)

## Escopo (o que ENTRA)
- `User` (`account_users`) passa a usar `TimestampMixin` (ganha `updated_at`) e `SoftDeleteMixin` (`deleted_at`/`deleted_by_user_id`/`delete_reason`), mantendo `created_at`.
- Migration: adiciona `updated_at`, `deleted_at`, `deleted_by_user_id`, `delete_reason` a `account_users`.
- Rotas de remoção (`delete_user`, `delete_user_me`) viram **soft delete** (marcam `deleted_at`/`deleted_by_user_id`) em vez de `session.delete`.
- Leituras de usuário (`get_user_by_email`, `authenticate`, `read_users`, `get_current_user`) passam a **excluir** registros soft-deletados.

## Fora de escopo (o que NÃO entra)
- Papéis globais de plataforma (`platform_admin_roles`/`platform.*`) → Fase 6.
- Tela de gestão de usuários (admin) → Fase 6 (`frontend-admin`).

## Arquivos a criar/alterar
- `backend/app/modules/accounts/models.py` (alterar) — `User` herda `TimestampMixin`/`SoftDeleteMixin`.
- `backend/app/modules/accounts/repositories.py` (alterar) — filtra soft-deletados.
- `backend/app/modules/accounts/services.py` (alterar) — `authenticate` ignora soft-deletados.
- `backend/app/modules/accounts/routes.py` (alterar) — delete vira soft.
- `backend/app/api/deps.py` (alterar) — `get_current_user` ignora soft-deletados.
- `backend/app/alembic/versions/xxxx_account_users_soft_delete.py` (criar).

## Passos
1. Aplicar os mixins ao `User`; gerar a migration de colunas.
2. Trocar os deletes por soft delete.
3. Ajustar leituras para excluir soft-deletados.
4. Rodar a suíte (login/recuperação/CRUD seguem verdes) + novos testes.

## Testes
> Fundações §10. Soft delete/queries são fronteiras reais → integração.

- **Níveis:** integração.
- **Quando escrever:** durante (manter login/recuperação verdes).
- **Cobrir:**
  - integração — `delete` marca `deleted_at` (não remove a linha); usuário soft-deletado **não** autentica nem aparece em `read_users`; `updated_at` muda no update.

## Definition of Done
- [x] `account_users` tem `updated_at` + colunas de soft delete (migration `a7b8c9d0e1f2` aplica em db do zero) — `created_at` agora NOT NULL.
- [x] Remoção é soft; usuário soft-deletado não autentica nem é listado *(tests verdes)*.
- [x] Suíte existente (login/recuperação/CRUD) segue verde *(76 testes; cobertura 91%)*.

## Notas / Reconciliações
- **Implementado:** `User` herda `UUIDMixin`/`TimestampMixin`/`SoftDeleteMixin`; `delete_user`/`delete_user_me` marcam `deleted_at`+`deleted_by_user_id` (sem `session.delete`); `get_user_by_email`, `read_users` e `get_current_user` filtram `deleted_at IS NULL`. Migration `a7b8c9d0e1f2` (`down_revision=b1c2d3e4f5a6`).
- **E-mail único + soft delete (decidido):** mantido o índice **único cheio** em `email`. Um e-mail de usuário soft-deletado **permanece reservado** (não recadastra com o mesmo e-mail). Escolha por simplicidade + identidade (sem migration de índice parcial); revisitar se o produto precisar liberar e-mails de contas removidas.
- **Escopo:** leituras por id de admin (`read_user_by_id`/`update_user` via `session.get`) **não** filtram soft-deletados — são operações de superuser por id; se virar problema, aplicar o mesmo guard.
- Testes de delete da Fase 0 ajustados (a linha permanece com `deleted_at` setado, em vez de sumir).
