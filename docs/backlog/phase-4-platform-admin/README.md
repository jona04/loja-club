# Fase 4 — Admin do SaaS

> Objetivo: a equipe Loja Club ganha o **admin da plataforma** (`frontend-admin` em `admin.${DOMAIN}` + módulo `platform_admin`) pra operar lojas/planos/usuários **e cadastrar templates** (registro + thumbnail no CDN + schema). **Antes do lançamento** — alimenta a **[Fase 5](../phase-5-store-configuration.md)**.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [25](../../concepts/25_platform_admin.md), [26](../../concepts/26_template_system.md), [05](../../concepts/05_frontend_architecture.md), [08](../../concepts/08_modules_and_permissions.md), [06](../../concepts/06_multitenancy_and_domains.md)/[12](../../concepts/12_aws_infrastructure_and_deployment.md), [13](../../concepts/13_performance_cache_and_cdn.md), [07](../../concepts/07_database_strategy.md), [14](../../concepts/14_security_strategy.md), [16](../../concepts/16_testing_strategy.md).

> Visão geral / trilha de alto nível: [`../phase-4-platform-admin.md`](../phase-4-platform-admin.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase
- Admin em `admin.${DOMAIN}` (Traefik/host) com login + **papéis globais** (`platform.*`); o `is_superuser` é substituído.
- Admin **opera lojas** (listar/detalhe/**bloquear**), **usuários** e **planos** (stub); **suporte com impersonation** auditado.
- Admin **registra/gerencia templates**: metadados + **thumbnail no CDN** + **schema** (vindo do código). *(Import de imagens, loja-demo por template e preview navegável = [Fase 5](../phase-5-store-configuration.md).)*
- Toda ação sensível **auditada** (mínimo).

> **Fora desta fase:** segurança/observabilidade plenas, CI/CD e beta = **[Fase 9](../phase-9-platform-ops-and-production.md)**; **billing real** dos planos = **[Fase 8](../phase-8-customer-account-and-payments.md)**; integração da **API 3D** no admin = **[Fase 7](../phase-7-3d-products.md)**.

## Construído sobre as Fases 0–3 (não recriar)
- **Permissões/papéis em banco** (`P1-PERM-01/02`): `platform.*` segue o mesmo padrão de seed (porém **global**, sem `store_id`).
- **`accounts`/`account_users`** (`P0-MOD-04`/`P1-ACCT-01`): `platform_admin_roles` referencia `account_users`.
- **`content_theme_templates`** (`P3-CONTENT-01`): o registro de templates **estende** essa tabela (`settings_schema`/status).
- **`media`/`storage`** (`P2-MEDIA-01/02`): o thumbnail de template reusa S3/CloudFront.
- **`frontend-dashboard`** (`P1-DASH-*`/`P3`): o `frontend-admin` reusa o cliente OpenAPI + componentes/padrões.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P4-PLAT-01](./P4-PLAT-01-platform-admin-module-roles.md) | Módulo `platform_admin` + papéis globais `platform.*` + migrar `is_superuser` + audit mínimo | ✅ done | — |
| 2 | [P4-ADMIN-01](./P4-ADMIN-01-frontend-admin-scaffold.md) | `frontend-admin` scaffold + Traefik `admin.` + login/shell (e2e 3/3) | ✅ done | P4-PLAT-01 |
| 3 | [P4-STORE-01](./P4-STORE-01-admin-store-operations.md) | Operação de lojas (listar/detalhe/**bloquear**) | ✅ done | P4-PLAT-01 |
| 4 | [P4-USER-01](./P4-USER-01-admin-users-support.md) | Usuários + suporte (impersonation auditada) + guard soft-delete | ✅ done | P4-PLAT-01 |
| 5 | [P4-PLAN-01](./P4-PLAN-01-plans-stub.md) | Planos (seed/stub; billing = Fase 8) | ✅ done | P4-PLAT-01 |
| 6 | [P4-ADMIN-02](./P4-ADMIN-02-admin-operation-screens.md) | Telas de operação (lojas/usuários/planos/suporte) — e2e 6/6 | ✅ done | P4-ADMIN-01, P4-STORE-01, P4-USER-01, P4-PLAN-01 |
| 7 | [P4-TPL-01](./P4-TPL-01-template-registry.md) | Registro de templates (CRUD + `settings_schema` do código) | ✅ done | P4-PLAT-01 |
| 8 | [P4-TPL-02](./P4-TPL-02-template-cdn-assets.md) | Thumbnail de template no **CDN** (imagens chrome/demo = Fase 5) | ✅ done | P4-TPL-01 |
| 9 | [P4-ADMIN-03](./P4-ADMIN-03-admin-template-screens.md) | Telas de templates (CRUD + thumbnail + schema read-only) — e2e 8/8 | ✅ done | P4-ADMIN-01, P4-TPL-01, P4-TPL-02 |

## Ordem sugerida de execução

```text
P4-PLAT-01 → P4-ADMIN-01
          ├→ P4-STORE-01 ┐
          ├→ P4-USER-01  ┼→ P4-ADMIN-02
          ├→ P4-PLAN-01  ┘
          └→ P4-TPL-01 → P4-TPL-02 → P4-ADMIN-03
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

**Esta fase fecha follow-ups de fases anteriores** (marcar `[x]` na **origem** ao concluir a task):
- [x] **Guard de soft-delete em leitura por id** (Fase 1, `P1-ACCT-01`) → `P4-USER-01` ✅.
- [x] **Admin pra cadastrar templates** (Fase 3, `P3-TPL-03`) → `P4-ADMIN-03`/`P4-TPL-01` ✅.
- [x] **Previews no CloudFront** (Fase 3, `P3-TPL-03`) → `P4-TPL-02` ✅ (thumbnail no CDN).
- [x] **Preview ao vivo / preview visual** (Fase 3, `P3-TPL-03`/`P3-FE-02`) → **Fase 5** ✅ `P5-PREV-01` (preview navegável = loja-demo por template, aberta na vitrine).

**Da própria fase:**
- [ ] **Checks inline de `is_superuser`** em `accounts/routes` (`delete_user_me`/`read_user_by_id`) → **não** migrados (layering: `accounts` não importa `platform_admin`); ficam até remover o campo `is_superuser`. Origem: `P4-PLAT-01`.
- [ ] **Remover o campo `is_superuser`** (legado) quando `accounts/routes` não o usar mais. Origem: `P4-PLAT-01`.
- [x] **Comentário stale do `StoreStatus`** (`stores/enums.py`, "(Fase 7)" → Fase 4) → corrigido na `P4-STORE-01`. Origem: `P4-PLAT-01`.
- [ ] **Detalhe da loja: pedidos/volume** (Fase 6) e **webhooks/comissões** (Fase 8) — agregar quando esses módulos existirem. Origem: `P4-STORE-01`.
- [ ] **`suspended` como ação distinta** (hoje só `blocked`/`active`) — se um estado intermediário for necessário. Origem: `P4-STORE-01`.
- [ ] **Hardening da impersonation** (→ Fase 9): token emitido = login normal do alvo (sem marca de impersonation); só o **acesso** é auditado em `audit_logs`, **não as ações** da sessão (aparecem como do próprio usuário); faltam tag de impersonation no token + auditoria das ações + expiração curta / "parar de impersonar". Origem: `P4-USER-01`.
- [x] **Empacotar os `settings-schema.json` no deploy do backend:** o seed lê de `frontend-storefront/templates/<id>/settings-schema.json`; na imagem Docker do backend esse dir não existe → o build precisa copiar os JSONs, senão o schema fica `null` em deploy. ✅ `P5-CFG-01`: `backend/Dockerfile` faz `COPY ./frontend-storefront/templates /app/frontend-storefront/templates`. Origem: `P4-TPL-01`.
- [ ] **Imagens-default no CDN** (Fase 5, quando houver campos `image`; guardar **separado** do `settings_schema` p/ o seed não sobrescrever) + **limpeza de asset antigo** no re-upload. *(Os **PNGs de `public/` já foram removidos** e o `import_assets`→CDN existe — `P5-DEMO-01`/`P5-TPL-01`; falta a limpeza de asset órfão no re-upload + o caso de campos `image`.)* Origem: `P4-TPL-02`.
- [x] **`frontend-admin`: smoke (docker) + `bun.lock` + e2e Playwright 3/3** — validado. Resta o **gate de CI** (e2e de **todos** os frontends → deploy) na **Fase 9** (regra em `P3-SF-03`). Origem: `P4-ADMIN-01`.
- [ ] **Telas admin (ADMIN-02):** atribuir plano à loja (Fase 8); detalhe da loja com pedidos/volume (Fase 6) + webhooks/comissões (Fase 8); **handoff da impersonation** (abrir o painel como o usuário) → Fase 9. Origem: `P4-ADMIN-02`.
- [x] **Telas de templates (ADMIN-03):** thumb seedado é caminho relativo (quebra na lista até subir um thumbnail/CDN — resolve com o `import_assets` da Fase 5); botão "abrir preview" entra na Fase 5. ✅ `P5-TPL-01` (thumb absoluto no CDN: lista/detalhe/editar) + `P5-PREV-01` (preview navegável). Origem: `P4-ADMIN-03`.
- [x] **e2e polui o db de dev** ✅ resolvido na **`P5-TEST-01`** (Fase 5): e2e roda contra `db-test` (tmpfs) via `backend-e2e`; db de dev provado intacto (1→1). Origem: e2e da Fase 4.
- [ ] **`pre-commit` não roda local:** os hooks locais usam `language: unsupported` (válido só p/ o pre-commit.ci-lite pular; **inválido** no `pre-commit` instalado) → o dev não reproduz o job de pre-commit antes do CI (foi por isso que o eof-fixer/trailing-whitespace de `frontend-admin/src/client` passou batido). Tornar runnable local (`ci: skip` + `language: system`, ou um alvo `make`). Origem: CI da Fase 4.
