---
id: P6-DISC-01
title: Cupons (discount_coupons) — fast-follow
phase: 6
etapa: "Etapa 2 — Módulo discounts (cupons)"
area: DISC
status: done
depends_on: [P6-CART-01]
blocks: []
tests: [integration]
---

# P6-DISC-01 — Cupons (fast-follow)

## Contexto
**Fast-follow:** não bloqueia o núcleo vendável. Entra depois que cart→checkout→pedido fecha. O carrinho já reserva o ponto de "aplicar cupom".

## Docs de referência
- [07 — Database](../../concepts/07_database_strategy.md)
- [09 — Cupons](../../concepts/09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- `discount_coupons` (`store_id`, `code` único quando ativo, `type` `percentual|fixo`, validade, limite de uso, pedido mínimo, status) + `discount_coupon_redemptions`. Índice `store_id+code` único quando ativo.
- CRUD no painel (gated `discounts.*`) + serviço de **validação/aplicação** consumido pelo carrinho.

## Fora de escopo (o que NÃO entra)
- Promoções automáticas / regras complexas: pós-V1.

## Arquivos a criar/alterar
- `backend/app/modules/discounts/{models,enums,schemas,services,routes}.py` (criar).
- `backend/app/modules/cart/services.py` (alterar) — aplicar cupom no resumo.
- migration alembic.

## Passos
1. Modelos + índice + migration.
2. CRUD gated + validação/aplicação (consumida pelo carrinho).

## Testes
- **Níveis:** integração.
- **Cobrir:** CRUD gated; cupom inválido/expirado/limite estourado/abaixo do mínimo recusado; aplica desconto no subtotal; isolamento por loja.

## Definition of Done
- [x] `discount_coupons`/`redemptions` + índice parcial único + migration (`alembic check` vazio; downgrade/upgrade round-trip ok).
- [x] CRUD gated `discounts.*` + validação/aplicação no carrinho (e no checkout).
- [x] **Modos de falha mapeados** (inválido `invalid_coupon`/expirado `coupon_expired`/não-iniciado `coupon_not_active`/limite `coupon_usage_exceeded`/abaixo do mínimo `coupon_below_minimum` — todos 422; código duplicado ativo 409; cupom de outra loja → `invalid_coupon`) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Backend-only** (conforme Arquivos/testes da task): módulo `discounts` (`enums`/`models`/`schemas`/`services`/`routes`). `CouponType` `percentage|fixed`; `value` = percent (1..100) ou valor em menor unidade; `min_subtotal_amount_minor`, `max_redemptions`, `valid_from`/`valid_until`, `is_active`. Índice **parcial único** `(store_id, code)` quando `is_active AND deleted_at IS NULL` (código normalizado upper-case). `discount_coupon_redemptions` (coupon/order/customer) conta o uso.
- **Serviços:** `validate_coupon` (raising — 422 por motivo) + `compute_discount` (percent→`subtotal*value//100`; fixed→`min(value, subtotal)`; nunca > subtotal) + `quote_discount` (non-raising → `(coupon, discount)` ou `(None, 0)`, usado pelo render do carrinho) + CRUD + `record_redemption`/`redemptions_count`.
- **Carrinho:** `CartCart.coupon_code` (migration); `POST/DELETE /storefront/cart/coupon`; `CartPublic` ganhou `coupon_code`/`discount_amount_minor`/`total_amount_minor` (desconto re-derivado no `to_public` — código inválido some do payload sem quebrar).
- **Checkout:** `submit_checkout` re-cota o desconto do `cart.coupon_code` → passa `discount_amount_minor` ao `create_order` → grava `redemption`. Cupom inválido no checkout = ignorado (desconto 0; não bloqueia a venda).
- **Permissões** `discounts.view/create/update/delete` já existiam no catálogo (doc 08) — sem mudança de seed.

## Follow-ups
- [ ] **Tela de cupons no painel** — só a API existe; falta o CRUD no `frontend-dashboard` (`/_layout/...`) + menu (gated `discounts.view`). Origem: `P6-DISC-01`.
- [ ] **Campo de cupom na vitrine** — religar o input dos 3 checkouts (`P6-SF-01`) aos endpoints `POST/DELETE /storefront/cart/coupon` (já prontos). Origem: `P6-DISC-01` (desbloqueia o follow-up de cupom do `P6-SF-01`).
- [ ] **Corrida no limite de uso** — `redemptions_count < max_redemptions` + gravação não são atômicos; checkouts concorrentes podem estourar o limite (mesma família da corrida de `order_number`). Adicionar lock/constraint. Origem: `P6-DISC-01`.
- [ ] **Limite por cliente** — só há `max_redemptions` global; "1 por cliente" precisa checar `redemptions` por `customer_id`. Origem: `P6-DISC-01`.
