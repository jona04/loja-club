---
id: P4-PLAT-01
title: Módulo platform_admin — permissões platform.* + papéis globais
phase: 4
etapa: "Etapa 1 — frontend-admin + platform_admin + papéis globais"
area: PLAT
status: done
depends_on: []
blocks: [P4-ADMIN-01, P4-STORE-01, P4-USER-01, P4-PLAN-01, P4-TPL-01]
tests: [integration]
---

# P4-PLAT-01 — Módulo `platform_admin` + papéis globais

## Contexto
O admin da plataforma precisa de autorização **global** (não por loja). Substitui o `is_superuser` do template pelos papéis `platform.*` e entrega a **auditoria mínima** que as ações sensíveis do admin usam. Base de toda a Fase 4.

## Docs de referência
- [25 — Platform Admin](../../concepts/25_platform_admin.md)
- [08 — Modules and Permissions](../../concepts/08_modules_and_permissions.md) (§480-508: catálogo `platform.*` + papéis)
- [07 — Database Strategy](../../concepts/07_database_strategy.md) (`audit_logs`)
- [14 — Security](../../concepts/14_security_strategy.md) / [15 — Observability](../../concepts/15_observability_and_operations.md)

## Escopo (o que ENTRA)
- Módulo `app/modules/platform_admin/` (`models/enums/schemas/permissions/services/routes`).
- **Catálogo `platform.*` do doc [08](../../concepts/08_modules_and_permissions.md) §480-498** (seed em código, como `P1-PERM-02`): `platform.stores.view|block|unblock`, `platform.users.view`, `platform.plans.view|update`, `platform.webhooks.view`, `platform.audit.view`, `platform.support.impersonate`, `platform.3d_models.view|manage`, `platform.templates.view|manage`.
- **Papéis globais** `platform_owner|platform_ops|platform_finance|platform_support|platform_catalog` com o **mapa papel→permissão do doc [08](../../concepts/08_modules_and_permissions.md) §500-508** (seed). *(`platform.3d_models.*` é seedado aqui, mas só exercido na [Fase 7](../phase-7-3d-products.md).)*
- `platform_admin_roles` (`user_id` ↔ papel global; doc [07](../../concepts/07_database_strategy.md)/[25](../../concepts/25_platform_admin.md)) + dependência **`require_platform_permission`** (parente **global** de `require_permission`/`P1-PERM-03`, sem `store_id`).
- **Migrar `account_users.is_superuser`**: superuser → `platform_owner` (data migration) e remover `is_superuser` do código de autorização.
- **Auditoria mínima** — introduz a tabela **`audit_logs`** (doc [07](../../concepts/07_database_strategy.md)/[15](../../concepts/15_observability_and_operations.md)) + um helper pra registrar ação sensível (ator/ação/alvo), consumido pelas tasks de operação. É o **mínimo** da Fase 4; a [Fase 9](../phase-9-platform-ops-and-dev-deploy.md) **estende** (`account_login_events`, `audit_security_events`, retenção, hardening).

## Fora de escopo (o que NÃO entra)
- Telas (`frontend-admin`) → `P4-ADMIN-01`/`P4-ADMIN-02`.
- Operação de lojas/usuários/planos → `P4-STORE-01`/`P4-USER-01`/`P4-PLAN-01`.
- Auditoria completa + hardening (`account_login_events`, `audit_security_events`, retenção, Sentry, rate limit) → **Fase 9**.

## Arquivos a criar/alterar
- `app/modules/platform_admin/{models,enums,schemas,permissions,services,routes}.py` (criar).
- `app/alembic/versions/*` (criar) — `platform_admin_roles`, `audit_logs` (mínimo), seed de permissões/papéis, data migration do `is_superuser`.
- `app/models_registry.py`, `app/api/main.py` (alterar) — registrar modelos/rotas.
- Código que checa `is_superuser` (alterar) → `require_platform_permission`.

## Passos
1. Catálogo `platform.*` (doc 08) + papéis globais (seed idempotente).
2. `platform_admin_roles` + `require_platform_permission` (global, sem tenant).
3. `audit_logs` (mínimo) + helper de registro de ação.
4. Data migration `is_superuser=true` → `platform_owner`; trocar as checagens.
5. Migration autogenerate → revisar (FK ordenadas/nomeadas) → `alembic check` vazio.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração.
- **Cobrir:** papel global concede/nega `platform.*` (conforme o mapa do doc 08); usuário sem papel → 403; migração do superuser; ação sensível grava em `audit_logs`.

## Definition of Done
- [x] Catálogo `platform.*` + mapa papel→permissão (doc 08) **em código** (`permissions.py`) + `platform_admin_roles` + `require_platform_permission`; `get_current_active_superuser` migrado para checar `platform_owner` (não consulta mais `is_superuser`).
- [x] `audit_logs` (mínimo, no módulo `audit`) + helper `record_audit`; migration aplicada, **`alembic check` vazio**.
- [x] **Modos de falha / edge cases mapeados** → Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** módulo `app/modules/platform_admin/` (`enums`/`permissions`/`models`/`repositories`/`deps`) + `audit/models.py` (`audit_logs`) + `audit/services.py` (`record_audit`); seed do superuser→`platform_owner` (`core/db.py`); migration `727624122b41`. Gate: **203 testes** (10 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- Herdado de `P0-MOD-04`/`P1-*`: o MVP usava `is_superuser`; os papéis `platform.*` (doc 08) o substituem (anotado desde a Fase 1).
- **`audit_logs` nasce aqui** (mínimo, p/ as ações do admin); a [Fase 9](../phase-9-platform-ops-and-dev-deploy.md) acrescenta `account_login_events`/`audit_security_events` + retenção/hardening (doc [07](../../concepts/07_database_strategy.md)/[15](../../concepts/15_observability_and_operations.md)).
- `require_platform_permission` é o **parente global** de `require_permission` (`P1-PERM-03`) — mesmo padrão, sem `store_id`.
- **Storage leve (decisão de impl):** o doc [07](../../concepts/07_database_strategy.md) define só `platform_admin_roles` — então o **catálogo/mapa fica em código** (`permissions.py`), sem tabelas `platform_permissions`/`platform_role_permissions` (diferente da loja). `require_platform_permission` resolve os papéis no DB e checa o mapa em código.

## Follow-ups
- [ ] **Checks inline de `is_superuser` em `accounts/routes`** (`delete_user_me`, `read_user_by_id`): ainda usam o campo — migrar para papel/permissão na **`P4-USER-01`** (gestão de usuários do admin). → README da fase.
- [ ] **Remover o campo `is_superuser`** de `account_users` (legado): mantido por ora como dado; remoção depois que `accounts/routes` deixar de usá-lo. → README da fase.
- [x] **Comentário stale do `StoreStatus`** (`stores/enums.py`): dizia "(Fase 7)" para `suspended`/`blocked` → corrigido para **Fase 4** na `P4-STORE-01`.
