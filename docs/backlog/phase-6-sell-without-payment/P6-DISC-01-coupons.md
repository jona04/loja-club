---
id: P6-DISC-01
title: Cupons (discount_coupons) — fast-follow
phase: 6
etapa: "Etapa 2 — Módulo discounts (cupons)"
area: DISC
status: todo
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
- [ ] `discount_coupons`/`redemptions` + índice + migration (`alembic check` vazio).
- [ ] CRUD gated + validação/aplicação no carrinho.
- [ ] **Modos de falha mapeados** (código inválido/expirado/sem usos/abaixo do mínimo; cupom de outra loja) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- (preencher ao implementar.)

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
