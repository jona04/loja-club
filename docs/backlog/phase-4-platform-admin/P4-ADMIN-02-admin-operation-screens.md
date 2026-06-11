---
id: P4-ADMIN-02
title: Telas de operação no admin — lojas, usuários, planos, suporte
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: ADMIN
status: done
depends_on: [P4-ADMIN-01, P4-STORE-01, P4-USER-01, P4-PLAN-01]
tests: [e2e]
---

# P4-ADMIN-02 — Telas de operação (frontend-admin)

## Contexto
As telas do `frontend-admin` que consomem os endpoints de operação (`P4-STORE-01`/`P4-USER-01`/`P4-PLAN-01`): a equipe opera lojas, usuários e planos, e usa o suporte (impersonation).

## Docs de referência
- [25 — Platform Admin](../../concepts/25_platform_admin.md)
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md)
- [05 — Frontend Architecture](../../concepts/05_frontend_architecture.md)

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
- [x] Telas de **lojas** (lista+busca+detalhe+bloquear/desbloquear), **usuários** (lista+busca+impersonation com confirmação auditada) e **planos** (CRUD) — consumindo `P4-STORE-01`/`USER-01`/`PLAN-01`.
- [x] Gates: `tsc`/`biome` + **e2e Playwright 6/6** (planos lista o seed; usuários pede confirmação de impersonation; lojas carrega).
- [x] **Modos de falha mapeados** (403 → `/login`; listas vazias; confirmação antes de impersonar) → tratados ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `frontend-admin/src/routes/_layout/{stores,users,plans}.tsx` + navegação no shell; tabelas/dialogs reaproveitando o padrão do dashboard (`useQuery`/`useMutation` + `Table` + `Dialog`). Specs `operations.spec.ts` (3) → gate **6/6**.

## Notas / Reconciliações
- Reaproveita componentes/padrões do `frontend-dashboard` (não recriar).

## Follow-ups
- [ ] **Atribuir plano a uma loja** (estava no escopo): depende de `billing_store_subscriptions` → **Fase 8** (`P4-PLAN-01` entregou só as definições). → README da fase.
- [ ] **Detalhe da loja: pedidos/volume** (Fase 6) + **webhooks/comissões** (Fase 8) — hoje o detalhe mostra settings + membros + status. → README da fase.
- [ ] **Handoff da impersonation:** a tela **gera** o token (auditado) + confirma; falta **abrir o painel agindo como o usuário** (handoff cross-origin do token app↔admin) → **Fase 9** (junto do hardening). → README da fase.
