---
id: P6-SHIP-01
title: Frete — métodos MVP (retirada/combinada/fixo)
phase: 6
etapa: "Etapa 1 — Módulo shipping (frete)"
area: SHIP
status: todo
depends_on: []
blocks: [P6-CHK-01]
tests: [integration]
---

# P6-SHIP-01 — Frete: métodos MVP

## Contexto
O checkout precisa de opções de entrega. **MVP fino:** retirada local, entrega combinada (`private_delivery`) e frete fixo — o suficiente pra vender. Zonas/tarifas por região = `P6-SHIP-02`.

## Docs de referência
- [11 — Entrega combinada](../../concepts/11_checkout_payments_and_split.md)
- [10 — Opções de entrega no produto](../../concepts/10_storefront_and_layouts.md)
- [09 — Frete](../../concepts/09_merchant_dashboard.md)
- [20 — API contracts](../../concepts/20_api_contracts_todo.md)

## Escopo (o que ENTRA)
- `shipping_methods` (com `store_id`, soft delete): `type` (`fixed_shipping|free_shipping|local_pickup|private_delivery`), `is_active`, nome, descrição exibida no checkout, valor (p/ `fixed_shipping`), mínimo (p/ `free_shipping`). Índice `store_id+type+is_active`.
- CRUD no painel (gated `shipping.*`) + **leitura pública** (checkout lista os métodos ativos da loja).
- `private_delivery`: sem cálculo automático; deixa claro no checkout/pedido que a entrega é **combinada após a compra**.

## Fora de escopo (o que NÃO entra)
- **Zonas/tarifas/regras** (`shipping_zones`/`shipping_rates`/`shipping_method_rules`): `P6-SHIP-02` (fast-follow).

## Arquivos a criar/alterar
- `backend/app/modules/shipping/{models,enums,schemas,services,repositories,routes}.py` (criar).
- migration alembic.

## Passos
1. `ShippingMethodType` + modelo + índice + migration.
2. CRUD painel (gated) + endpoint público dos métodos ativos da loja.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** CRUD gated `shipping.update` (viewer não escreve); leitura pública só dos **ativos**; `private_delivery` marca "combinada"; isolamento por loja.

## Definition of Done
- [ ] `shipping_methods` + índice + migration (`alembic check` vazio).
- [ ] CRUD gated + leitura pública (ativos) consumida pelo checkout.
- [ ] `private_delivery` com aviso de "combinada após a compra".
- [ ] **Modos de falha mapeados** (loja sem nenhum método ativo → checkout exige ao menos retirada/combinada) → tratado/Follow-up.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Zonas/tarifas movidas pra `P6-SHIP-02` (MVP fino primeiro).

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
