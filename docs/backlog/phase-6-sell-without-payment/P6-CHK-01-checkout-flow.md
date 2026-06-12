---
id: P6-CHK-01
title: Checkout — sessão + fluxo (sem gateway)
phase: 6
etapa: "Etapa 5 — Módulo checkout"
area: CHK
status: done
depends_on: [P6-CUST-01, P6-CART-01, P6-SHIP-01, P6-ORD-01]
blocks: [P6-SF-01, P6-NOTIF-01]
tests: [integration]
---

# P6-CHK-01 — Checkout: sessão + fluxo

## Contexto
Orquestra a finalização: coleta contato/endereço/entrega, identifica o cliente (dedup), valida, e chama `create_order`. **Sem gateway** — para no pedido pendente + confirmação; pagamento combinado fora da plataforma.

## Docs de referência
- [11 — Fluxo de checkout / Venda sem gateway](../../concepts/11_checkout_payments_and_split.md)
- [23 — Identificação no checkout](../../concepts/23_customer_identity_and_guest_checkout.md)
- [10 — Checkout](../../concepts/10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- `checkout_sessions` (`store_id`, `cart_id`, `status`, `expires_at` ≈24h). Índices `store_id+cart_id+status`, `expires_at+status`.
- Fluxo: coletar cliente (nome/e-mail/telefone + **seletor de país**) sem senha → `create_or_update_customer` (`P6-CUST-01`) + endereço → escolher método de entrega (`P6-SHIP-01`, inclui `private_delivery` com aviso) → **exibir/linkar políticas da loja** (`checkout.policies.*`) → revisão (**validação composável**: estoque + valores; + sessão `approved` na Fase 7) → `create_order` (`P6-ORD-01`).
- **Sem gateway:** após criar o pedido, segue pra confirmação (sem webhook). **Interface de pagamento** stub (sem implementar) reservada pra Fase 8.

## Fora de escopo (o que NÃO entra)
- Telas da vitrine (single-page + confirmação): `P6-SF-01`.
- Gateway/split/webhook: **Fase 8**.
- Cupom no resumo: `P6-DISC-01`.

## Arquivos a criar/alterar
- `backend/app/modules/checkout/{models,enums,schemas,services,routes}.py` (criar).
- `backend/app/modules/payments/...` (criar) — **stub** da interface (sem implementar).
- migration alembic.

## Passos
1. `checkout_sessions` + migration.
2. Fluxo (coleta → dedup → entrega → políticas → validação composável → `create_order`).
3. Stub da interface de pagamento (ponto de extensão Fase 8).

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** compra sem login cria `pending_payment`; dedup acionado no checkout; estoque/valores validados (composável); `private_delivery` marca "combinada"; **pedido não vira pago sozinho**; isolamento por loja.

## Definition of Done
- [x] `checkout_sessions` + migration (`alembic check` vazio).
- [x] Fluxo completo sem login até `pending_payment` (dedup + endereço + entrega + políticas).
- [x] **Validação composável** (estoque/valores) + **interface de pagamento** stub.
- [x] **Modos de falha mapeados** (estoque some na revisão → 409 no `create_order`; loja sem método ativo → 404; telefone inválido → 422; sessão expirada → fluxo é single-call, abandono = follow-up de limpeza) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Adianta** o follow-up de **políticas da loja** (`checkout.policies.*`, Fase 1) — `return/exchange/privacy_policy` em `store_settings`, rota painel `GET/PATCH /stores/{id}/checkout/policies` (gated `checkout.view`/`checkout.policies.update`), e exposição em `StorefrontStore` (a vitrine mostra no checkout). Marcado `[x]` na origem.
- Congelamento por item + validação **composáveis** (costura pra Fase 7 plugar a personalização).
- **Implementação:** `checkout_sessions` (`active`→`completed`, expira 24h) + `submit_checkout` (`POST /storefront/checkout`, host+cookie guest): valida (lista composável `_CHECKOUT_CHECKS`) → `create_or_update_customer` (dedup/E.164) → resolve método ativo (404 se indisponível) → `create_order` → retorna `OrderPublic`. **Sem gateway:** `payments/gateway.py` (`PaymentGateway` Protocol + `NoOpGateway` + `get_gateway()`) é chamado como no-op (seam Fase 8). `OrderPublic`/`OrderItemPublic` + `order_to_public` adicionados em `orders`. Migration `9e95a44969bd`. 7 testes, módulos checkout+payments 100%.

## Follow-ups
- [ ] **Limpeza de `checkout_sessions` abandonadas** — sessões `active` que não viram `completed` ficam até `expires_at` sem worker que marque `expired` (mesma família do follow-up de guest sessions do `P6-CUST-01`). Origem: `P6-CHK-01`.
