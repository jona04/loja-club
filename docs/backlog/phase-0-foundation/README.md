# Fase 0 — Fundação (dev local)

> Roadmap: Etapas 1–2. Objetivo: projeto com a cara da Loja Club, com Redis, esqueleto modular e o exemplo `items` removido, pronto para construir os domínios reais.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [03](../../03_system_architecture.md), [04](../../04_fastapi_template_adaptation.md), [07](../../07_database_strategy.md), [16](../../16_testing_strategy.md).

## Definition of Done da fase

- `docker compose watch` sobe backend, frontend, db, **redis**, traefik com branding Loja Club.
- `app/modules/` existe com mixins base e convenção de módulos.
- Base **global** pronta: tipo `Money` (valor + moeda ISO 4217), UTC; **nada assume Brasil**.
- `Item` removido; `User` migrado para o módulo `accounts` como tabela `account_users`.
- Login/recuperação de senha continuam funcionando após o refactor.
- **Fundação de testes** pronta (unit/integração isolados + `vitest` no front), seguindo Fundações §10.
- CI verde (lint + type check + testes).

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P0-CFG-01](./P0-CFG-01-branding.md) | Branding Loja Club | done | — |
| 2 | [P0-TEST-01](./P0-TEST-01-testing-foundation.md) | Fundação de testes (layout, isolamento, mocks, vitest) | done | — |
| 3 | [P0-CFG-02](./P0-CFG-02-env-config.md) | Variáveis de ambiente e domínio de dev | done | — |
| 4 | [P0-CFG-03](./P0-CFG-03-redis.md) | Redis (cache/locks/fila leve) | done | P0-CFG-02 |
| 5 | [P0-CFG-04](./P0-CFG-04-queue-worker.md) | Fila/worker (base) | todo | P0-CFG-03 |
| 6 | [P0-MOD-01](./P0-MOD-01-base-mixins.md) | Mixins base + `app/db` | todo | — |
| 7 | [P0-MOD-02](./P0-MOD-02-module-skeleton.md) | Esqueleto de módulos | todo | P0-MOD-01 |
| 8 | [P0-MOD-05](./P0-MOD-05-shared-money-locale.md) | Tipos globais: Money/Currency, locale, UTC | todo | P0-MOD-01 |
| 9 | [P0-MOD-03](./P0-MOD-03-remove-items.md) | Remover exemplo `items` | todo | P0-MOD-02 |
| 10 | [P0-MOD-04](./P0-MOD-04-accounts-user.md) | Mover `User` → `accounts` (`account_users`) | todo | P0-MOD-01, P0-MOD-02 |
| 11 | [P0-CI-01](./P0-CI-01-ci-lint-tests.md) | CI, lint, testes e client OpenAPI | todo | P0-MOD-03, P0-MOD-04 |

## Ordem sugerida de execução

```text
P0-CFG-01 → P0-TEST-01 → P0-CFG-02 → P0-CFG-03 → P0-CFG-04 → P0-MOD-01 → P0-MOD-02 → P0-MOD-05 → P0-MOD-03 → P0-MOD-04 → P0-CI-01
```

## Reconciliações da fase

- `account_users.is_superuser` (template) ↔ admin de plataforma: no MVP o superuser cobre o acesso interno; o modelo `platform_admin_roles`/`platform.*` entra na Fase 6 (`P6-ADMIN-*`). Registrado em P0-MOD-04.
- **Global desde a base** (`P0-MOD-05`): dinheiro é sempre `(valor + moeda ISO 4217)`; telefone/endereço/locale globais. Telefone normalizado por lib (`phonenumbers`) para qualquer país — convenção já no [doc 23](../../23_customer_identity_and_guest_checkout.md); endereço país-aware (ISO 3166) vem na Fase 4.
- **Testes** (`P0-TEST-01` + Fundações §10): unit p/ lógica pura, integração no seam, E2E p/ jornadas; isolamento por teste (rollback), S3 mockado (`moto`), `vitest`+RTL no front. Fixtures/factories multi-tenant ficam para a Fase 1.
