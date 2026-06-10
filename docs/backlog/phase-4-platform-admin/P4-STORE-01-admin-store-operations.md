---
id: P4-STORE-01
title: Operação de lojas no admin — listar/detalhe/bloquear
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: STORE
status: todo
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02]
tests: [integration]
---

# P4-STORE-01 — Operação de lojas (backend)

## Contexto
A equipe precisa **operar todas as lojas** (visão cross-store, fora do tenant): listar, ver detalhe e **bloquear/desbloquear** uma loja. O guard do painel (`P1-TEN-01`) já barra `suspended`/`blocked`; aqui entram os endpoints que setam esse estado.

## Docs de referência
- [25 — Platform Admin](../../25_platform_admin.md)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md)

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
- [ ] Listar/detalhe/bloquear lojas (cross-store, gated `platform.stores.*`, auditado); loja bloqueada barra no painel.
- [ ] Soft-delete respeitado nas leituras de admin.
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O guard `get_active_membership` (`P1-TEN-01`) já barra `suspended`/`blocked` (403 `store_unavailable`) — esta task entrega quem **seta** esse estado.

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
