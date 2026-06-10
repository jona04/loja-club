---
id: P4-ADMIN-02
title: Telas de operação no admin — lojas, usuários, planos, suporte
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: ADMIN
status: todo
depends_on: [P4-ADMIN-01, P4-STORE-01, P4-USER-01, P4-PLAN-01]
tests: [e2e]
---

# P4-ADMIN-02 — Telas de operação (frontend-admin)

## Contexto
As telas do `frontend-admin` que consomem os endpoints de operação (`P4-STORE-01`/`P4-USER-01`/`P4-PLAN-01`): a equipe opera lojas, usuários e planos, e usa o suporte (impersonation).

## Docs de referência
- [25 — Platform Admin](../../25_platform_admin.md)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)
- [05 — Frontend Architecture](../../05_frontend_architecture.md)

## Escopo (o que ENTRA)
- **Lojas:** lista (busca/paginação) + detalhe (settings/membros/pedidos/volume/webhooks/comissões) + **bloquear/desbloquear**.
- **Usuários:** lista/ver + **impersonation** (com aviso claro de que a ação é auditada).
- **Planos:** CRUD das definições + atribuir plano a uma loja.

## Fora de escopo (o que NÃO entra)
- Endpoints/backend → `P4-STORE-01`/`P4-USER-01`/`P4-PLAN-01`.
- Telas de templates → `P4-ADMIN-03`.

## Arquivos a criar/alterar
- `frontend-admin/src/routes/...` (criar) — telas de lojas/usuários/planos.
- `frontend-admin/src/components/...` (criar) — tabelas/dialogs reaproveitando padrões do dashboard.

## Passos
1. Tela de lojas (lista + detalhe + ação bloquear/desbloquear).
2. Tela de usuários (lista/ver + impersonation com confirmação).
3. Tela de planos (CRUD + atribuição).
4. Validar via Traefik (`admin.localhost`).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** e2e (smoke) + `tsc`/`biome`.
- **Cobrir:** bloquear loja na UI reflete no backend; impersonation pede confirmação; telas gated por `platform.*`.

## Definition of Done
- [ ] Telas de lojas/usuários/planos operacionais (consumindo `P4-STORE-01`/`USER-01`/`PLAN-01`); impersonation com confirmação.
- [ ] Gates (`tsc`/`biome`) + smoke.
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reaproveita componentes/padrões do `frontend-dashboard` (não recriar).

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
