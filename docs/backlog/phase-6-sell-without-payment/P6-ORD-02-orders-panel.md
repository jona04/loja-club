---
id: P6-ORD-02
title: Painel de pedidos (lista/detalhe/marcar-pago/cancelar)
phase: 6
etapa: "Etapa 6 — orders (painel)"
area: ORD
status: done
depends_on: [P6-ORD-01]
blocks: []
tests: [integration, e2e]
---

# P6-ORD-02 — Painel de pedidos

## Contexto
O lojista precisa ver e operar os pedidos: lista, detalhe, **marcar pago manualmente** (sem gateway), **cancelar** (devolve estoque), status e notas.

## Docs de referência
- [09 — Pedidos](../../concepts/09_merchant_dashboard.md)
- [11 — Status do pedido / Venda sem gateway](../../concepts/11_checkout_payments_and_split.md)

## Escopo (o que ENTRA)
- Rotas/serviço (painel, gated `orders.*`): listar (filtro status/data, com **número do pedido**), detalhe (cliente, itens, endereço, histórico), nota interna, alterar status operacional.
- **Marcar pagamento recebido manualmente** (`pending_payment → paid`).
- **Cancelar** quando permitido (chama `cancel_order` → **devolve estoque**).
- Detalhe mostra o **handoff de WhatsApp** pra falar com o cliente.
- Tela no `frontend-dashboard` (`/_layout/orders`) + entrada no menu (gated `orders.view`).

## Fora de escopo (o que NÃO entra)
- Reembolso real: **Fase 8**.
- E-mails de pedido: `P6-NOTIF-01`.

## Arquivos a criar/alterar
- `backend/app/modules/orders/routes.py` (criar/alterar) — rotas do painel.
- `frontend-dashboard/src/routes/_layout/orders.tsx` (criar) + `src/lib/menu.ts` (alterar).
- client OpenAPI regenerado.

## Passos
1. Rotas do painel (gated) + serviço (lista/detalhe/marcar-pago/cancelar/status/nota).
2. Tela de pedidos + menu.

## Testes
- **Níveis:** integração (rotas gated) + e2e (painel).
- **Cobrir:** integração — gating `orders.*`, marcar-pago, cancelar devolve estoque, isolamento. e2e — lojista vê o pedido e marca pago.

## Definition of Done
- [x] Rotas do painel gated `orders.*` (lista c/ nº + detalhe + status + nota).
- [x] Marcar pago manual + cancelar (restock).
- [x] Tela + menu (gated `orders.view`).
- [x] **Modos de falha mapeados** (transição de status inválida → 409; cancelar já entregue → 409 `cannot_cancel`; pedido de outra loja → 404) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Backend:** rotas `/stores/{id}/orders` (`orders/routes.py`) — `GET` lista `Page[OrderSummary]` (filtro `?status=`, nº/cliente/total/itens/data, newest-first) gated `orders.view`; `GET /{id}` detalhe `OrderDetail` (cliente + endereço + itens + histórico + notas); `PATCH /{id}/status` (transição **um passo** pelo chain `_FORWARD`; "marcar pago" = `→paid`) gated `orders.update_status`; `POST /{id}/cancel` → `cancel_order` (**restock**) gated `orders.cancel`; `POST /{id}/notes` gated `orders.add_note` (autor = usuário atual). Serviços novos em `orders/services.py` (`list_orders`/`get_order`/`get_order_detail`/`set_status`/`add_note`); schemas novos. Permissões já existiam no catálogo (doc 08) — sem mudança de seed.
- **Status:** mantido o **forward de 1 passo** (`pending_payment→paid→processing→shipped→delivered`); cancelar é rota própria (não entra no `set_status`). Transição inválida = **409 `invalid_transition`**.
- **Frontend:** `routes/_layout/orders.tsx` (lista + filtro + diálogo de detalhe com ações de status/cancelar/nota + **handoff de WhatsApp** via `phone_e164`) + entrada "Pedidos" no `menu.ts` (gated `orders.view`). Client OpenAPI regenerado (`OrdersService`). Teste de componente `orders.test.tsx` (lista + gating do "Marcar pago").
- **Pré-existente corrigido:** `store-layout.test.tsx` checava `name: "Salvar"` mas o botão virou "Salvar template e aparência" (refactor de UX anterior) — asserção atualizada (não é desta task, mas estava vermelha).

## Follow-ups
- [ ] **e2e Playwright do painel de pedidos** — o fluxo (lojista vê o pedido → marca pago) está coberto por integração (backend) + teste de componente (vitest), **não** por Playwright; falta seedar um pedido no e2e e cobrir ao vivo. Origem: `P6-ORD-02`.
- [ ] **Exportar pedidos (`orders.export`)** — permissão existe no catálogo, sem rota/botão ainda. Origem: `P6-ORD-02`.
- [ ] **Paginação do detalhe (histórico/notas longos)** — detalhe carrega histórico/notas inteiros; ok no MVP, paginar se crescer. Origem: `P6-ORD-02`.
