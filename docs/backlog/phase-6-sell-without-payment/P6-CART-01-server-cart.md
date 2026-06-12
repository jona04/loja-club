---
id: P6-CART-01
title: Carrinho de servidor (cart_carts/cart_items)
phase: 6
etapa: "Etapa 4 — Módulo cart (carrinho)"
area: CART
status: todo
depends_on: [P6-CAT-01]
blocks: [P6-ORD-01, P6-CHK-01, P6-SF-01]
tests: [integration]
---

# P6-CART-01 — Carrinho de servidor

## Contexto
A vitrine tem um carrinho **client** (localStorage, placeholder da Fase 3). Esta task cria o carrinho de **servidor** (`cart_carts`, chaveado pelo cookie `guest_session_id`) — drawer e checkout passam a ler a **mesma** fonte.

## Docs de referência
- [10 — Carrinho](../../concepts/10_storefront_and_layouts.md)
- [11 — Fluxo de checkout](../../concepts/11_checkout_payments_and_split.md)
- [07 — Database](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- Modelos (com `store_id`, soft delete): `cart_carts` (`guest_session_id`|`customer_id`, `status`), `cart_items` (produto, **`variant_id`** quando houver, quantidade, preço unitário). Índices `store_id+guest_session_id+status`, `store_id+customer_id+status`, `cart_items.store_id+cart_id`.
- Serviço/rotas (público, por cookie guest): criar/recuperar carrinho ativo; **adicionar item** (via **portão** do `P6-CAT-01`); alterar quantidade; remover; **resumo** (subtotal); **validar estoque** (`catalog_inventory_items`).
- **Token seguro** para continuar a compra (aleatório, expira, escopado à loja).

## Fora de escopo (o que NÃO entra)
- **Aplicar cupom:** `P6-DISC-01` (o ponto fica reservado no resumo).
- **Congelar personalização** no item (`customization_cart_items`): **Fase 7**.
- UI (drawer/checkout): `P6-SF-01`.

## Arquivos a criar/alterar
- `backend/app/modules/cart/{models,enums,schemas,services,repositories,routes}.py` (criar).
- migration alembic.

## Passos
1. Modelos + índices + migration.
2. Add/update/remove/summary (subtotal) + validar estoque; `add` usa o portão de `P6-CAT-01`.
3. Token seguro de continuação.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** add/update/remove; subtotal; **estoque insuficiente barra**; `variant_id` capturado; recuperar por cookie; **isolamento por loja**; portão barra `image_3d_customizable`.

## Definition of Done
- [ ] `cart_carts`/`cart_items` (+ `variant_id`) + índices + migration (`alembic check` vazio).
- [ ] Add/update/remove/summary + validação de estoque (público, por cookie guest).
- [ ] `add` passa pelo **portão** de `P6-CAT-01`.
- [ ] **Modos de falha mapeados** (estoque insuficiente; produto/variação inexistente ou despublicado; carrinho de outra loja; quantidade ≤ 0) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Substitui o carrinho client (localStorage) da Fase 3 — fecha o follow-up "carrinho real" (P3); a UI vem em `P6-SF-01`.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
