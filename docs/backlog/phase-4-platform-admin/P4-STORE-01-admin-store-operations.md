---
id: P4-STORE-01
title: Operação de lojas no admin — listar/detalhe/bloquear
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: STORE
status: done
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02]
tests: [integration]
---

# P4-STORE-01 — Operação de lojas (backend)

## Contexto
A equipe precisa **operar todas as lojas** (visão cross-store, fora do tenant): listar, ver detalhe e **bloquear/desbloquear** uma loja. O guard do painel (`P1-TEN-01`) já barra `suspended`/`blocked`; aqui entram os endpoints que setam esse estado.

## Docs de referência
- [25 — Platform Admin](../../concepts/25_platform_admin.md)
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md)
- [08 — Modules and Permissions](../../concepts/08_modules_and_permissions.md)

## Escopo (o que ENTRA)
- Rotas `platform_admin` (gated `platform.stores.view|block|unblock`, **sem** `store_id` no path): listar lojas (paginado, busca), detalhe (settings, membros, nº de pedidos, volume transacionado, webhooks com erro, comissões).
- **Bloquear/desbloquear** loja (`status` `suspended`/`blocked` ↔ `active`), **auditado** (`record_platform_action`).
- Leituras cross-store **ignoram** o guard de tenant, mas respeitam `deleted_at` (não vazar loja excluída).

## Fora de escopo (o que NÃO entra)
- Telas → `P4-ADMIN-02`.
- Usuários/impersonation → `P4-USER-01`. Planos → `P4-PLAN-01`.
- Métricas avançadas/observabilidade → **Fase 9**.

## Arquivos a criar/alterar
- `app/modules/platform_admin/{services,routes,schemas}.py` (alterar) — operação de lojas.
- (Reusa `stores`/`orders` para leitura agregada.)

## Passos
1. Query cross-store paginada (lojas ativas + soft-delete fora).
2. Detalhe agregando settings/membros/pedidos/volume/webhooks/comissões.
3. Bloquear/desbloquear → set `status` + `record_platform_action`.
4. Validar que o guard do painel (`P1-TEN-01`) barra a loja bloqueada (403).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração.
- **Cobrir:** listagem cross-store sem vazar soft-deletada; bloquear → painel 403; ação auditada; gating `platform.*`.

## Definition of Done
- [x] Listar/detalhe/bloquear lojas (cross-store, gated `platform.stores.view|block|unblock`, auditado em `audit_logs`); loja bloqueada barra no painel (guard `P1-TEN-01`).
- [x] Soft-delete respeitado nas leituras de admin.
- [x] **Modos de falha / edge cases mapeados** → Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `platform_admin/{schemas,services,routes}.py` (rotas `/platform/stores*`) registradas em `app/api/router.py`; detalhe = **identidade + settings + membros** (pedidos/volume/webhooks/comissões dependem de Fase 6/8 → Follow-ups). Gate: **211 testes** (8 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- O guard `get_active_membership` (`P1-TEN-01`) já barra `suspended`/`blocked` (403 `store_unavailable`) — esta task entrega quem **seta** esse estado (`block` → `blocked`, `unblock` → `active`), auditado.
- **Escopo do detalhe (decisão):** só **settings + membros + status** — `orders`/`billing` não existem (Fase 6/8), então pedidos/volume/webhooks/comissões ficam de fora **sem inventar** (Follow-ups).

## Follow-ups
- [ ] **Detalhe: pedidos + volume transacionado** — agregar quando o módulo `orders` existir (**Fase 6**). → README da fase.
- [ ] **Detalhe: webhooks com erro + comissões** — quando billing/webhooks existirem (**Fase 8**). → README da fase.
- [ ] **`suspended` como ação distinta** (hoje só `blocked`/`active`): adicionar se um estado intermediário for necessário. → README da fase.
