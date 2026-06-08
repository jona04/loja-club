# Fase 0 — Fundação (dev local)

> Roadmap: Etapas 1–2. Objetivo: projeto com a cara da Loja Club (branding, config, domínio de dev, Redis e fila), refatorado para a **convenção modular** (`app/modules/*` com mixins base e tipo `Money` global), com o exemplo `items` removido e o `User` migrado para o módulo `accounts` — pronto para construir os domínios reais.

Docs de referência: [Fundações & Gargalos](./_foundations-and-bottlenecks.md), [03](../03_system_architecture.md), [04](../04_fastapi_template_adaptation.md), [07](../07_database_strategy.md), [16](../16_testing_strategy.md).

> **Esta fase já está decomposta em tasks** — ver [`phase-0-foundation/`](./phase-0-foundation/README.md) (uma task por arquivo, com escopo, dependências e DoD; status no frontmatter). Este arquivo é a **visão geral (consulta)**: a trilha de alto nível que levou às tasks. **Fase concluída** (11/11 tasks `done`).

## Definition of Done da fase

- [x] `docker compose watch` sobe backend, frontend, db, **redis**, traefik com branding Loja Club.
- [x] `app/modules/` existe com mixins base e convenção de módulos.
- [x] Base **global** pronta: tipo `Money` (valor + moeda ISO 4217), UTC; **nada assume Brasil**.
- [x] `Item` removido; `User` migrado para o módulo `accounts` como tabela `account_users`.
- [x] Login/recuperação de senha continuam funcionando após o refactor.
- [x] **Fundação de testes** pronta (unit/integração isolados + `vitest` no front), seguindo Fundações §10.
- [x] CI verde (lint + type check + testes).

---

## Etapa 1 — Fundação do projeto

### Branding e identidade ([P0-CFG-01](./phase-0-foundation/P0-CFG-01-branding.md))
- [x] `PROJECT_NAME`/`STACK_NAME` e branding do frontend para Loja Club (sai o "Full Stack FastAPI Project").

### Variáveis de ambiente e domínio de dev ([P0-CFG-02](./phase-0-foundation/P0-CFG-02-env-config.md))
- [x] `.env` com segredos fortes, `DOMAIN=loja.localhost`, `PLATFORM_DEFAULT_CURRENCY`/`PLATFORM_DEFAULT_LOCALE`, CORS para `app.`/`admin.`.
- [x] Portas de dev **não-padrão** no `compose.override.yml` (db 5442, redis 6399, backend 8800, frontend 5180, etc.) para não conflitar com serviços locais. Doc [06](../06_multitenancy_and_domains.md).

### Redis — cache/locks/fila leve ([P0-CFG-03](./phase-0-foundation/P0-CFG-03-redis.md))
- [x] Serviço `redis` no compose; cliente em `app/core/cache.py` (`get_redis`, `cache_set`/`cache_get`); health check `/health/redis`. Doc [13](../13_performance_cache_and_cdn.md).

### Fila/worker (base) ([P0-CFG-04](./phase-0-foundation/P0-CFG-04-queue-worker.md))
- [x] **arq** (DEC-3): `enqueue()` como única interface, `dummy_task`, `WorkerSettings`; serviço `worker` no compose. Doc [18](../18_open_decisions.md).

---

## Etapa 2 — Refatoração modular

### Mixins base + `app/db` ([P0-MOD-01](./phase-0-foundation/P0-MOD-01-base-mixins.md))
- [x] `UUIDMixin`, `TimestampMixin` (`created_at`/`updated_at`, UTC), `SoftDeleteMixin` (`deleted_at`/`deleted_by_user_id`/`delete_reason`), `StoreScopedMixin` (`store_id`). Doc [07](../07_database_strategy.md)/[14](../14_security_strategy.md).

### Esqueleto de módulos ([P0-MOD-02](./phase-0-foundation/P0-MOD-02-module-skeleton.md))
- [x] `app/modules/<nome>/` com a convenção de arquivos (models/schemas/routes/services/repositories/permissions/exceptions, criados conforme a necessidade). Doc [04](../04_fastapi_template_adaptation.md)/[08](../08_modules_and_permissions.md).

### Tipos globais: Money/Currency, locale, UTC ([P0-MOD-05](./phase-0-foundation/P0-MOD-05-shared-money-locale.md))
- [x] `Money` = `(valor em unidades menores + moeda ISO 4217)` com aritmética/`apply_rate`/`format` (babel); UTC; base global (telefone/endereço país-aware vêm depois). Fundações DEC-1.

### Remover exemplo `items` ([P0-MOD-03](./phase-0-foundation/P0-MOD-03-remove-items.md))
- [x] Remover modelo/rotas/crud/testes/UI do `Item` (exemplo do template); migration de drop.

### Mover `User` → `accounts` (`account_users`) ([P0-MOD-04](./phase-0-foundation/P0-MOD-04-accounts-user.md))
- [x] Módulo `accounts` (`models`/`repositories`/`services`/`auth`/`routes`); tabela `account_users` via `__tablename__`; migrations de rename; login/recuperação mantidos. Doc [07](../07_database_strategy.md)/[08](../08_modules_and_permissions.md).

### Fundação de testes ([P0-TEST-01](./phase-0-foundation/P0-TEST-01-testing-foundation.md))
- [x] `tests/unit` (sem DB) + `tests/integration` (DB com **rollback transacional** por teste); S3 mockado (`moto`); `vitest`+RTL no front. Fundações §10. Doc [16](../16_testing_strategy.md).

### CI, lint, testes e client OpenAPI ([P0-CI-01](./phase-0-foundation/P0-CI-01-ci-lint-tests.md))
- [x] Ruff `D`/pydocstyle (Google), mypy/ty, pytest + cobertura (gate 90%); client OpenAPI regenerado (sem `Item*`); workflows de CI ajustados (push em `development`; limpeza da automação do template). Fundações DEC-13.

---

## Reconciliações

- `account_users.is_superuser` (template) ↔ admin de plataforma: no MVP o superuser cobre o acesso interno; `platform_admin_roles`/`platform.*` entram na Fase 7. Registrado em [P0-MOD-04](./phase-0-foundation/P0-MOD-04-accounts-user.md).
- **Global desde a base** ([P0-MOD-05](./phase-0-foundation/P0-MOD-05-shared-money-locale.md)): dinheiro `(valor + ISO 4217)`; telefone/endereço/locale globais (telefone normalizado por `phonenumbers`; endereço país-aware na Fase 4 — doc [23](../23_customer_identity_and_guest_checkout.md)).
- **Testes** ([P0-TEST-01](./phase-0-foundation/P0-TEST-01-testing-foundation.md) + Fundações §10): unit p/ lógica pura, integração no seam, isolamento por rollback, S3 mockado, `vitest`+RTL. Fixtures multi-tenant ficam para a Fase 1.
- **CI/portas/lockfile** ([P0-CI-01](./phase-0-foundation/P0-CI-01-ci-lint-tests.md)): CI roda no host nas portas publicadas (5442/6399); `bun.lock` único na raiz do workspace (regenerar ao mudar `frontend/package.json`); automação do template (board/labels/release-notes) removida.

> **Detalhe e status oficial por task:** [`phase-0-foundation/README.md`](./phase-0-foundation/README.md).
