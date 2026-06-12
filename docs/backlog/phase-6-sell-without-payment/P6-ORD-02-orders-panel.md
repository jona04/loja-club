---
id: P6-ORD-02
title: Painel de pedidos (lista/detalhe/marcar-pago/cancelar)
phase: 6
etapa: "Etapa 6 — orders (painel)"
area: ORD
status: todo
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
- [ ] Rotas do painel gated `orders.*` (lista c/ nº + detalhe + status + nota).
- [ ] Marcar pago manual + cancelar (restock).
- [ ] Tela + menu (gated `orders.view`).
- [ ] **Modos de falha mapeados** (transição de status inválida; cancelar já entregue; pedido de outra loja) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- (preencher ao implementar.)

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
