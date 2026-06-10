# Fase 4 — Admin do SaaS

> Objetivo: a equipe Loja Club ganha o **admin da plataforma** (`frontend-admin` em `admin.${DOMAIN}` + módulo `platform_admin`) pra operar lojas/planos/usuários **e cadastrar templates** (assets no CDN + preview navegável). **Antes do lançamento** — alimenta a **[Fase 5](../phase-5-store-configuration.md)**.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [25](../../25_platform_admin.md), [26](../../26_template_system.md), [05](../../05_frontend_architecture.md), [08](../../08_modules_and_permissions.md), [06](../../06_multitenancy_and_domains.md)/[12](../../12_aws_infrastructure_and_deployment.md), [13](../../13_performance_cache_and_cdn.md), [07](../../07_database_strategy.md), [14](../../14_security_strategy.md), [16](../../16_testing_strategy.md).

> Visão geral / trilha de alto nível: [`../phase-4-platform-admin.md`](../phase-4-platform-admin.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase
- Admin em `admin.${DOMAIN}` (Traefik/host) com login + **papéis globais** (`platform.*`); o `is_superuser` é substituído.
- Admin **opera lojas** (listar/detalhe/**bloquear**), **usuários** e **planos** (stub); **suporte com impersonation** auditado.
- Admin **cadastra/gerencia templates**: metadados + **assets no CDN** + **schema** (vindo do código) + **preview navegável** publicado.
- Toda ação sensível **auditada** (mínimo).

> **Fora desta fase:** segurança/observabilidade plenas, CI/CD e beta = **[Fase 9](../phase-9-platform-ops-and-production.md)**; **billing real** dos planos = **[Fase 8](../phase-8-customer-account-and-payments.md)**; integração da **API 3D** no admin = **[Fase 7](../phase-7-3d-products.md)**.

## Construído sobre as Fases 0–3 (não recriar)
- **Permissões/papéis em banco** (`P1-PERM-01/02`): `platform.*` segue o mesmo padrão de seed (porém **global**, sem `store_id`).
- **`accounts`/`account_users`** (`P0-MOD-04`/`P1-ACCT-01`): `platform_admin_roles` referencia `account_users`.
- **`content_theme_templates`** (`P3-CONTENT-01`): o registro de templates **estende** essa tabela (`settings_schema`/status).
- **`media`/`storage`** (`P2-MEDIA-01/02`): os assets de template reusam S3/CloudFront.
- **`storefront`** (`P3-SF-*`): o preview navegável reusa a vitrine real.
- **`frontend-dashboard`** (`P1-DASH-*`/`P3`): o `frontend-admin` reusa o cliente OpenAPI + componentes/padrões.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P4-PLAT-01](./P4-PLAT-01-platform-admin-module-roles.md) | Módulo `platform_admin` + papéis globais `platform.*` + migrar `is_superuser` + audit mínimo | todo | — |
| 2 | [P4-ADMIN-01](./P4-ADMIN-01-frontend-admin-scaffold.md) | `frontend-admin` scaffold + Traefik `admin.` + login/shell | todo | P4-PLAT-01 |
| 3 | [P4-STORE-01](./P4-STORE-01-admin-store-operations.md) | Operação de lojas (listar/detalhe/**bloquear**) | todo | P4-PLAT-01 |
| 4 | [P4-USER-01](./P4-USER-01-admin-users-support.md) | Usuários + suporte (impersonation auditada) + guard soft-delete | todo | P4-PLAT-01 |
| 5 | [P4-PLAN-01](./P4-PLAN-01-plans-stub.md) | Planos (seed/stub; billing = Fase 8) | todo | P4-PLAT-01 |
| 6 | [P4-ADMIN-02](./P4-ADMIN-02-admin-operation-screens.md) | Telas de operação (lojas/usuários/planos/suporte) | todo | P4-ADMIN-01, P4-STORE-01, P4-USER-01, P4-PLAN-01 |
| 7 | [P4-TPL-01](./P4-TPL-01-template-registry.md) | Registro de templates (CRUD + `settings_schema` do código) | todo | P4-PLAT-01 |
| 8 | [P4-TPL-02](./P4-TPL-02-template-cdn-assets.md) | Assets de template no **CDN** (thumb + imagens-default) | todo | P4-TPL-01 |
| 9 | [P4-TPL-03](./P4-TPL-03-navigable-preview.md) | **Preview navegável** (loja-demo + host de preview) | todo | P4-TPL-01 |
| 10 | [P4-ADMIN-03](./P4-ADMIN-03-admin-template-screens.md) | Telas de templates (CRUD + assets + publicar preview) | todo | P4-ADMIN-01, P4-TPL-01, P4-TPL-02, P4-TPL-03 |

## Ordem sugerida de execução

```text
P4-PLAT-01 → P4-ADMIN-01
          ├→ P4-STORE-01 ┐
          ├→ P4-USER-01  ┼→ P4-ADMIN-02
          ├→ P4-PLAN-01  ┘
          └→ P4-TPL-01 → P4-TPL-02 ┐
                       → P4-TPL-03 ┴→ P4-ADMIN-03
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

**Esta fase fecha follow-ups de fases anteriores** (marcar `[x]` na **origem** ao concluir a task):
- [ ] **Guard de soft-delete em leitura por id** (Fase 1, `P1-ACCT-01`) → `P4-USER-01`.
- [ ] **Admin pra cadastrar templates** (Fase 3, `P3-TPL-03`) → `P4-ADMIN-03`/`P4-TPL-01`.
- [ ] **Previews no CloudFront** (Fase 3, `P3-TPL-03`) → `P4-TPL-02`.
- [ ] **Preview ao vivo / preview visual** (Fase 3, `P3-TPL-03`/`P3-FE-02`) → `P4-TPL-03`.

**Da própria fase:** _(preencher conforme as tasks forem implementadas)._
