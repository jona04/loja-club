# Fase 4 — Admin do SaaS (plataforma)

> Objetivo: a equipe Loja Club ganha um **admin da plataforma** (`frontend-admin` em `admin.${DOMAIN}` + módulo `platform_admin`) pra operar lojas/planos/usuários **e cadastrar/gerenciar os templates** (assets no CDN + preview navegável). Fase **enxuta e antes do lançamento** — só o essencial pra operar e pra alimentar a **configuração da loja ([Fase 5](./phase-5-store-configuration.md))**. Segurança/observabilidade, CI/CD e beta seguem na **[Fase 9](./phase-9-platform-ops-and-production.md)**.

> **Por que antes do lançamento:** o lojista precisa **escolher e personalizar templates** (Fase 5), e os templates precisam estar **cadastrados pela plataforma** — com assets no **CDN** e **preview navegável** publicado. Sem o admin, isso fica hardcoded (hoje os PNGs vêm do `public/` e as imagens dos templates apontam pra URLs temporárias). Doc [25](../25_platform_admin.md), [26](../26_template_system.md).

Docs de referência: [25](../25_platform_admin.md) (admin), [26](../26_template_system.md) (templates), [05](../05_frontend_architecture.md), [08](../08_modules_and_permissions.md), [06](../06_multitenancy_and_domains.md)/[12](../12_aws_infrastructure_and_deployment.md) (Traefik/host), [13](../13_performance_cache_and_cdn.md) (CDN), [09](../09_merchant_dashboard.md), [07](../07_database_strategy.md), [14](../14_security_strategy.md).

## Definition of Done da fase
- Admin em `admin.${DOMAIN}` (Traefik/host) com login e **papéis globais** (`platform.*`); o `is_superuser` do template é substituído.
- Admin **opera lojas** (listar/detalhe/bloquear/desbloquear, ver usuários/pedidos) e **planos**.
- Admin **cadastra/gerencia templates**: metadados, **upload de assets pro CDN** (thumb + imagens-default), **settings schema** (consumido na Fase 5) e **preview navegável** publicado.
- **Auditoria** mínima das ações sensíveis.

## Escopo (enxuto — antes do lançamento)

### `frontend-admin` + roteamento
- [ ] Projeto `frontend-admin/` (React/Vite, separado do dashboard) em `admin.${DOMAIN}`, com **indicação visual clara de ambiente interno**. Reusa cliente OpenAPI/componentes/padrões. Doc [05](../05_frontend_architecture.md)/[21](../21_design_system_todo.md).
- [ ] **Traefik:** reservar/rotear o host `admin.${DOMAIN}` (no dev local já há wildcard; o painel do lojista é `app.`, o admin é `admin.`). Doc [06](../06_multitenancy_and_domains.md)/[12](../12_aws_infrastructure_and_deployment.md).

### Módulo `platform_admin` + papéis globais
- [ ] Permissões `platform.*` + papéis globais (`platform_owner|platform_ops|platform_finance|platform_support|platform_catalog`). Doc [08](../08_modules_and_permissions.md).
- [ ] `platform_admin_roles` + **migração de `account_users.is_superuser`** (template/Fase 1) pro modelo de papéis globais. Doc [07](../07_database_strategy.md)/[08](../08_modules_and_permissions.md).

### Operação de lojas/planos/usuários
- [ ] Listar lojas; detalhe; **bloquear/desbloquear**; ver usuários; pedidos por loja; volume transacionado; webhooks com erro; comissões; auditoria. Doc [09](../09_merchant_dashboard.md)/[25](../25_platform_admin.md).
- [ ] **Gerenciar planos** (consome `billing` quando existir; na V1 pode ser seed/stub).
- [ ] **Suporte com impersonation** + auditoria obrigatória do acesso. Doc [08](../08_modules_and_permissions.md)/[14](../14_security_strategy.md).

### Cadastro/gestão de templates (alimenta a [Fase 5](./phase-5-store-configuration.md))
- [ ] **CRUD de templates** no admin: id, nome, descrição, status. Doc [26](../26_template_system.md).
- [ ] **Upload de assets pro CDN** (S3/CloudFront via `media`): **thumbnail** + **imagens-default** do template — substitui os PNGs hardcoded em `frontend-dashboard/public/templates/` e as URLs temporárias (uxpilot) dos templates. Doc [13](../13_performance_cache_and_cdn.md)/[26](../26_template_system.md).
- [ ] **Settings schema** do template (manifesto dos campos editáveis) — cadastrado/versionado aqui, **consumido na Fase 5**. Doc [26](../26_template_system.md).
- [ ] **Preview navegável**: publicar/registrar a URL do **preview navegável** do template (storefront + loja-demo) que o painel do lojista vai abrir. Doc [26](../26_template_system.md).

## Fora de escopo (fica para a [Fase 9](./phase-9-platform-ops-and-production.md))
- Segurança/observabilidade completas (audit hardening, Sentry, rate limit, URLs assinadas, backups, alertas).
- CI/CD e deploy automatizado; beta com lojas reais.
- **Integração da API de geração 3D** (config no admin) — depende da **[Fase 7](./phase-7-3d-products.md)**.

## Reconciliações
- O **admin** entra **antes do lançamento** (Fase 4) pra cadastrar templates que a **Fase 5** consome; a **Fase 9** cobre segurança/observabilidade, CI/CD e beta. Os papéis globais `platform.*` substituem o `is_superuser` (anotado desde a Fase 1).
- O **cadastro de templates** + **settings schema** + **CDN** + **preview navegável** vêm das decisões dos docs [25](../25_platform_admin.md)/[26](../26_template_system.md) (`P3-TPL-04`).
