---
id: P4-PLAN-01
title: Planos (seed/stub) — definições billing_plans gerenciadas pelo admin
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: PLAN
status: done
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02]
tests: [integration]
---

# P4-PLAN-01 — Planos (seed/stub)

## Contexto
O admin gerencia as **definições** de planos — a tabela **`billing_plans`** do módulo `billing` (doc [07](../../07_database_strategy.md)). O **billing real** (assinatura, cobrança, comissão, enforcement) é a **[Fase 8](../phase-8-customer-account-and-payments.md)** — aqui só as **definições** (seed/stub): existem e são editáveis; nada é cobrado/forçado e a loja ainda **não** assina.

## Docs de referência
- [02 — Business Model and Rules](../../02_business_model_and_rules.md) (planos Free/Pro)
- [07 — Database Strategy](../../07_database_strategy.md) (`billing_plans`, `billing_*`)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (`platform.plans.view|update`)
- [25 — Platform Admin](../../25_platform_admin.md)

## Escopo (o que ENTRA)
- **`billing_plans`** (definições: nome, mensalidade, comissão %, observação) — **seed** dos planos do doc [02](../../02_business_model_and_rules.md) (**Free** R$0/5%, **Pro** R$99,90/1,5%).
- Rotas `platform_admin` (gated `platform.plans.view|update`): **CRUD das definições** de plano.

## Fora de escopo (o que NÃO entra)
- **Assinatura da loja** (`billing_store_subscriptions`), cobrança (`billing_subscription_invoices`), comissão (`billing_platform_commissions`), gateway → **[Fase 8](../phase-8-customer-account-and-payments.md)**.
- **Enforcement por plano** (bloquear recurso) → **Fase 8** (o gancho já existe em `require_permission`, Fase 1; doc [02](../../02_business_model_and_rules.md) §"plano + permissão").
- Telas → `P4-ADMIN-02`.

## Arquivos a criar/alterar
- `app/modules/billing/{models,services,routes,schemas}.py` (criar — só `billing_plans` nesta fase).
- `app/modules/platform_admin/routes.py` (alterar) — expor o CRUD de planos no admin.
- `app/alembic/versions/*` (criar) — `billing_plans` + seed Free/Pro.

## Passos
1. `billing_plans` (definições) + seed Free/Pro (doc 02), idempotente.
2. CRUD das definições, gated `platform.plans.view|update` (doc 08).
3. Migration → `alembic check` vazio.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração.
- **Cobrir:** seed cria Free/Pro; CRUD gated `platform.plans.*`; **nenhuma loja assina / nada é cobrado** (subscription/cobrança são Fase 8).

## Definition of Done
- [x] `billing_plans` seedado (Free R$0/5% · Pro R$99,90/1,5%) + CRUD admin (`/platform/plans`) gated `platform.plans.view`/`update`; `alembic check` vazio. Sem assinatura/cobrança (stub).
- [x] **Modos de falha mapeados** → tratados (chave duplicada → 409, não-encontrado → 404, soft-delete) ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** módulo `app/modules/billing/` (`models`/`schemas`/`repositories`/`services`) com `billing_plans` + seed + CRUD em `platform_admin/routes`; migration `9486ba430691`. Gate: **227 testes** (8 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- Usa a tabela **definida** `billing_plans` (doc [07](../../07_database_strategy.md)), não uma tabela nova. O **resto do `billing`** (assinatura/cobrança/comissão/enforcement) é a **Fase 8**; a Fase 4 introduz só as **definições** (consistente com doc [25](../../25_platform_admin.md): "consome billing quando existir; na V1 seed/stub").
- **Decisões de impl:** mensalidade como `*_amount_minor` (int) + `*_currency` (padrão do projeto); **comissão em basis points** (int, `500` = 5%) — exata, sem float; **`key` única parcial** (entre não-deletados, padrão do `store_stores.slug`) — chave de plano deletado pode ser reusada.

## Follow-ups
- [ ] — nenhum próprio (assinatura loja↔plano, cobrança e enforcement por plano são **Fase 8**, já em Fora de escopo).
