# Fase 4 — Admin do SaaS (dev local)

> Objetivo: a equipe Loja Club ganha o **admin da plataforma** (`frontend-admin` em `admin.${DOMAIN}` + módulo `platform_admin`) pra operar lojas/planos/usuários **e cadastrar templates** (registro + thumbnail no CDN + schema). Fase **enxuta, antes do lançamento** — só o essencial pra operar e pra alimentar a **[Fase 5](./phase-5-store-configuration.md)**. Segurança/observabilidade plenas, CI/CD e beta são a **[Fase 9](./phase-9-platform-ops-and-production.md)**.

Docs de referência: [25](../25_platform_admin.md) (admin), [26](../26_template_system.md) (templates), [05](../05_frontend_architecture.md), [08](../08_modules_and_permissions.md), [06](../06_multitenancy_and_domains.md)/[12](../12_aws_infrastructure_and_deployment.md) (Traefik/host), [13](../13_performance_cache_and_cdn.md) (CDN), [09](../09_merchant_dashboard.md), [07](../07_database_strategy.md), [14](../14_security_strategy.md), [15](../15_observability_and_operations.md).

> **Decomposta em tasks** — ver [`phase-4-platform-admin/`](./phase-4-platform-admin/README.md) (**9 tasks**, 3 etapas). O detalhe e o status oficial estão no README da pasta.

> **Nota:** o admin **opera** a plataforma; **segurança/observabilidade plenas, CI/CD e beta** ficam na [Fase 9](./phase-9-platform-ops-and-production.md). O **billing real** dos planos é a [Fase 8](./phase-8-customer-account-and-payments.md) — aqui planos são **seed/stub**. A integração da **API de geração 3D** no admin depende da [Fase 7](./phase-7-3d-products.md).

## Definition of Done da fase
- Admin em `admin.${DOMAIN}` (Traefik/host) com login + **papéis globais** (`platform.*`); o `is_superuser` é substituído.
- Admin **opera lojas** (listar/detalhe/**bloquear**), **usuários** e **planos** (stub); **suporte com impersonation** auditado.
- Admin **registra/gerencia templates**: metadados + **thumbnail no CDN** + **schema** (vindo do código). *(Import de imagens, loja-demo por template e preview navegável = [Fase 5](./phase-5-store-configuration.md).)*
- Toda ação sensível **auditada** (mínimo).

---

## Etapa 1 — `frontend-admin` + `platform_admin` + papéis globais

### Projeto + roteamento (doc [05](../05_frontend_architecture.md)/[06](../06_multitenancy_and_domains.md)/[12](../12_aws_infrastructure_and_deployment.md))
- [ ] Projeto `frontend-admin/` (React/Vite, **separado** do `frontend-dashboard`) em `admin.${DOMAIN}`, com **indicação visual clara de ambiente interno**. Reusa cliente OpenAPI/componentes/padrões.
- [ ] **Traefik:** rotear o host `admin.${DOMAIN}` (`app.` = painel do lojista; `admin.` = admin; `api.` = backend; `*.` = vitrines).

### Módulo `platform_admin` + papéis globais (doc [08](../08_modules_and_permissions.md)/[07](../07_database_strategy.md))
- [ ] Permissões `platform.*` + papéis globais (`platform_owner|platform_ops|platform_finance|platform_support|platform_catalog`).
- [ ] `platform_admin_roles` + **migrar `account_users.is_superuser`** (template/Fase 1) pro modelo de papéis globais. *(funde os follow-ups de papéis globais das Fases 0/1)*

---

## Etapa 2 — Operação: lojas, usuários, planos, suporte

### Lojas / pedidos (doc [09](../09_merchant_dashboard.md)/[25](../25_platform_admin.md))
- [ ] Listar lojas; detalhe; **bloquear/desbloquear** (estados `suspended`/`blocked` que o guard do painel já barra — `P1-TEN-01`); ver usuários e pedidos por loja, volume transacionado, webhooks com erro, comissões.

### Usuários (doc [08](../08_modules_and_permissions.md)/[14](../14_security_strategy.md))
- [ ] Listar/ver usuários (gestão de `account_users` é do admin, não do painel do lojista).
- [ ] **Guard de soft-delete em leitura por id** (`read_user_by_id`/`update_user` via `session.get` não devem retornar soft-deletados). *(funde follow-up da Fase 1)*
- [ ] **Suporte com impersonation** + **auditoria obrigatória** do acesso.

### Planos (stub) (doc [02](../02_business_model_and_rules.md)/[08](../08_modules_and_permissions.md))
- [ ] **Gerenciar planos** (definições) — consome `billing` quando existir; na V1 = **seed/stub** (billing real = [Fase 8](./phase-8-customer-account-and-payments.md)).

---

## Etapa 3 — Cadastro/gestão de templates (alimenta a [Fase 5](./phase-5-store-configuration.md))

> O **`settings_schema`** de um template **vem do código** (manifesto exportado pelo template React, seedado no DB ao fazer deploy) — doc [26](../26_template_system.md). O admin **não edita os campos**: ele sobe **o thumbnail**, ajusta **metadados** e **ativa**.

### CRUD + thumbnail + schema (doc [26](../26_template_system.md)/[13](../13_performance_cache_and_cdn.md))
- [ ] **CRUD de templates** no admin: id, nome, descrição, **status** (ativo/inativo).
- [ ] **Upload do thumbnail pro CDN** (S3/CloudFront via `storage`) — substitui o PNG hardcoded de `frontend-dashboard/public/templates/`. *(funde "previews no CloudFront" da Fase 3; as **imagens de chrome/demo** entram via **import → Fase 5**)*
- [ ] **Schema do código → DB:** seed/registro do `settings_schema` (manifesto) por template em `content_theme_templates.settings_schema` — **consumido na [Fase 5](./phase-5-store-configuration.md)**.

> **Loja-demo por template, import das imagens (chrome/demo) pro CDN e preview navegável** são a **[Fase 5](./phase-5-store-configuration.md)** — ver doc [26](../26_template_system.md)/[27](../27_template_authoring_guide.md).

---

## Testes (doc [16](../16_testing_strategy.md))
- [ ] Papéis globais respeitados; **impersonation gera auditoria**; admin **não vaza** dados entre escopos.
- [ ] Bloquear loja → guard do painel barra (403).
- [ ] Upload de **thumbnail** de template → vai pro CDN.
- [ ] `read_user_by_id`/`update_user` **não** retornam usuário soft-deletado.

---

## Reconciliações
- O **admin** entra **antes do lançamento** (Fase 4) pra cadastrar templates que a **Fase 5** consome; a **Fase 9** cobre segurança/observabilidade, CI/CD e beta. Os papéis globais `platform.*` substituem o `is_superuser` (anotado desde a Fase 1).
- **Schema vem do código** (manifesto), não é autorado no admin — evita divergência schema↔código (doc [26](../26_template_system.md)). O admin sobe assets + ativa.
- **Assets no CDN** acabam com o hardcoded de `public/` e as URLs temporárias (decisões docs [25](../25_platform_admin.md)/[26](../26_template_system.md)).
