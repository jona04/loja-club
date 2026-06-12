---
id: P6-ORD-01
title: Pedidos — módulo + criação (congela/estoque/número)
phase: 6
etapa: "Etapa 6 — Módulo orders (pedidos)"
area: ORD
status: done
depends_on: [P6-CART-01]
blocks: [P6-CHK-01, P6-ORD-02, P6-NOTIF-01]
tests: [integration]
---

# P6-ORD-01 — Pedidos: módulo + criação

## Contexto
O coração da fase: transformar um carrinho num **pedido `pending_payment`** com preço/variação congelados, **estoque decrementado** e **número sequencial por loja**. Sem gateway — o pedido para em pendente.

## Docs de referência
- [11 — Pedido pendente / Venda sem gateway / Status do pedido](../../concepts/11_checkout_payments_and_split.md)
- [07 — Database (pedidos)](../../concepts/07_database_strategy.md)
- [09 — Pedidos](../../concepts/09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- Modelos (com `store_id`, soft delete): `order_orders` (**`order_number` sequencial por loja**, status, total, frete, desconto, método de entrega, `customer_id`, `guest_session_id`), `order_items` (congela **preço + `variant_id`**), `order_addresses`, `order_status_history`, `order_notes`, `order_fulfillments` (básico), `order_refunds` (stub).
- **Enum de status enxuto** (Fase 6, todos lidos): `pending_payment → paid → processing → shipped → delivered`, `canceled`. (Os de pagamento — `payment_failed|refunded|chargeback` — entram na **Fase 8**.)
- Índices: `store_id+order_number` único, `store_id+created_at`, `store_id+status`, `store_id+customer_id`, `order_items.store_id+order_id`, `order_status_history.store_id+order_id+created_at`.
- Serviço `create_order(...)`: **pipeline por item extensível** (congela preço/variação agora; **hook** para personalização na Fase 7), **decrementa estoque**, gera `order_number`, grava `pending_payment` + histórico.
- `cancel_order`: **devolve o estoque**.

## Fora de escopo (o que NÃO entra)
- A orquestração do checkout (coleta de dados/sessão): `P6-CHK-01` (chama `create_order`).
- Painel de pedidos (UI): `P6-ORD-02`.
- `customization_order_items` (congelar personalização): **Fase 7** (hook reservado).

## Arquivos a criar/alterar
- `backend/app/modules/orders/{models,enums,schemas,services,repositories}.py` (criar).
- migration alembic.

## Passos
1. Modelos + enum enxuto + índices + migration.
2. `create_order` (pipeline por item; congela; decrementa estoque; `order_number`).
3. `cancel_order` (restock) + transições de status.

## Testes
- **Níveis:** integração.
- **Quando escrever:** antes (regra de congelamento/estoque clara — TDD).
- **Cobrir:** cria `pending_payment`; **preço/variação congelados** (mudar o produto depois não altera o pedido); **estoque decrementa** e **cancelar devolve**; `order_number` **sequencial e único** por loja (isolado entre lojas).

## Definition of Done
- [x] Tabelas de pedido + enum enxuto + índices (`order_number` único) + migration (`alembic check` vazio).
- [x] `create_order` congela preço/variação, decrementa estoque e gera `order_number` (pipeline por item **extensível**).
- [x] `cancel_order` devolve estoque.
- [x] **Modos de falha mapeados** (estoque some entre validação e criação → 409; cancelar já enviado/entregue → 409; carrinho vazio → 422; corrida de `order_number` → unicidade + follow-up de retry) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Adianta** o follow-up `P2-CAT-02` (índice único de estoque `store_id+product_id+variant_id`, com `nulls_not_distinct` p/ a linha product-level com `variant_id` NULL) — marcado `[x]` na origem.
- Enum de status enxuto vs doc 11 (a tabela completa lá inclui os de pagamento da Fase 8).
- **Implementação:** `order_orders` (`order_number` único+sequencial, status, total/frete/desconto, método snapshot, customer/guest) + `order_items` (congela nome/preço/`variant_id`) + `order_addresses` (snapshot) + `order_status_history` + `order_notes`. `create_order` re-valida+decrementa estoque, congela por item (`_freeze_item` = hook da Fase 7), gera `order_number` (`max+1`), grava histórico e marca o carrinho `converted`; preço congelado = o do carrinho (o que o cliente viu). `cancel_order` faz restock (status permitidos: pending_payment/paid/processing). **Sem rotas** (CHK-01 chama; ORD-02 expõe). Migration `33517f4ccbc8` (enums reusados via `postgresql.ENUM(create_type=False)`). 9 testes, módulo 100%.

## Follow-ups
- [ ] **Corrida de `order_number`** — `max+1` + índice único garante que não duplica, mas concorrência alta gera `IntegrityError` (500) sem retry. Adicionar retry/lock por loja. Origem: `P6-ORD-01`.
- [ ] **`order_fulfillments` + `order_refunds` adiados** — não criados (sem consumidor: o status do pedido cobre o envio no MVP; reembolso é Fase 8). Criar quando forem consumidos. Origem: `P6-ORD-01`.
