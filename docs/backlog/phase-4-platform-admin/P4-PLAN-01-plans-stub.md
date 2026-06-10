---
id: P4-PLAN-01
title: Planos (seed/stub) — definições billing_plans gerenciadas pelo admin
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: PLAN
status: todo
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
- [ ] `billing_plans` seedado (Free/Pro) + CRUD admin gated `platform.plans.*`; `alembic check` vazio. Sem assinatura/cobrança (stub).
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Usa a tabela **definida** `billing_plans` (doc [07](../../07_database_strategy.md)), não uma tabela nova. O **resto do `billing`** (assinatura/cobrança/comissão/enforcement) é a **Fase 8**; a Fase 4 introduz só as **definições** (consistente com doc [25](../../25_platform_admin.md): "consome billing quando existir; na V1 seed/stub").

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
