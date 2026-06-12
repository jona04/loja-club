# 25 — Admin do SaaS (plataforma)

> Como a equipe **Kriar** opera a plataforma. Complementa o doc [08](./08_modules_and_permissions.md) (permissões) e [09](./09_merchant_dashboard.md) (painel do lojista). O backlog é a **[Fase 4](../backlog/phase-4-platform-admin.md)** (admin, antes do lançamento) + o que sobra nas **Fases 9–11** (deploy/ops na [9](../backlog/phase-9-platform-ops-and-dev-deploy.md), segurança geral na [10](../backlog/phase-10-followups-and-hardening.md), beta na [11](../backlog/phase-11-production.md)).

## Por que existe (e por que antes do lançamento)

O admin é a ferramenta interna da plataforma — separada do painel do lojista. Foi **puxado pra antes do lançamento** porque o lojista precisa **escolher e personalizar templates** ([Fase 5](../backlog/phase-5-store-configuration.md)), e os templates precisam estar **registrados pela plataforma** (thumbnail no CDN + settings schema; o **import das imagens**, a **loja-demo** e o **preview navegável** são a [Fase 5](../backlog/phase-5-store-configuration.md)). Sem o admin, isso fica hardcoded. As demais funções de operação seguem depois: deploy/CI-CD/ops na **Fase 9**, segurança geral na **Fase 10**, beta na **Fase 11**.

## `frontend-admin` (projeto separado)

- Projeto próprio (React/Vite), **separado** do `frontend-dashboard`, em **`admin.${DOMAIN}`**. Reusa cliente OpenAPI/componentes/padrões, mas com build/rotas/deploy/permissões próprios e **indicação visual clara de ambiente interno**. Doc [05](./05_frontend_architecture.md).
- **Roteamento (Traefik):** `app.` = painel do lojista; `admin.` = admin da plataforma; `api.` = backend; `*.` = vitrines. Doc [06](./06_multitenancy_and_domains.md)/[12](./12_aws_infrastructure_and_deployment.md).

## Permissões globais (`platform.*`)

- Papéis **globais** (não por loja): `platform_owner | platform_ops | platform_finance | platform_support | platform_catalog`. Doc [08](./08_modules_and_permissions.md).
- `platform_admin_roles` no banco; o `is_superuser` do template (Fase 1) é **substituído** por esse modelo. Doc [07](./07_database_strategy.md).
- Toda ação sensível do admin é **auditada** (mínimo na Fase 4; módulo `audit` + hardening na Fase 10). Doc [14](./14_security_strategy.md)/[15](./15_observability_and_operations.md).
- O `frontend-admin` descobre o usuário logado + se é admin via **`GET /platform/me`** (devolve o usuário + `platform_roles`; vazio = não-admin → acesso negado).

## Escopo antes do lançamento (Fase 4)

- **Operar lojas:** listar/detalhe, **bloquear/desbloquear**, ver usuários e pedidos por loja, volume, webhooks com erro, comissões, auditoria.
- **Planos:** gerenciar (consome `billing` quando existir; na V1 pode ser seed/stub).
- **Suporte com impersonation** + auditoria obrigatória do acesso.
- **Cadastro/gestão de templates** (alimenta a Fase 5) — ver doc [26](./26_template_system.md): metadados (id/nome/status), **thumbnail no CDN** e **registro do settings schema** (vindo do código). O **import das imagens (chrome/demo) pro CDN**, a **loja-demo por template** e o **preview navegável** são a Fase 5.

### Cadastro "inteligente" de templates — abordagem

Um template tem **código** (componentes React + os **manifestos** `settings-schema.json` e `demo.json` no `frontend-storefront`) **e dados** (metadados, assets, conteúdo demo, valores por loja). O **schema vem do código** (seedado no deploy) — o admin **não autora os campos**, o que evita divergência schema↔código. O admin gerencia a parte **operável**: **registrar**, subir o **thumbnail**, **disparar o import** das imagens pro CDN, montar a **loja-demo** e **ativar/desativar**. Um template **genuinamente novo** exige deploy do storefront (código + manifestos) — o passo-a-passo está no doc [27](./27_template_authoring_guide.md). *(Import/demo/preview são entregues na [Fase 5](../backlog/phase-5-store-configuration.md).)*

## Fora do escopo da Fase 4 (fica para as Fases 9–12)

- **Deploy dev na AWS + CI/CD + ops mínimo** → [Fase 9](../backlog/phase-9-platform-ops-and-dev-deploy.md).
- **Segurança/observabilidade completas** (audit, hardening, retenção, restore) → [Fase 10](../backlog/phase-10-followups-and-hardening.md).
- **Beta com lojas reais** + produção → [Fase 11](../backlog/phase-11-production.md).
- **Habilitar/desabilitar modelos do catálogo 3D** (admin) → [Fase 7](../backlog/phase-7-3d-products.md); **config da API de geração 3D** → [Fase 12](../backlog/phase-12-merchant-3d-generation.md).

## Telas (referência)

Listagem/detalhe de lojas; usuários; pedidos por loja; planos; templates (CRUD + thumbnail + schema; import/demo/preview = Fase 5); auditoria; suporte/impersonation. Contratos em [20](./20_api_contracts_todo.md); checklist de operação em [09](./09_merchant_dashboard.md).
