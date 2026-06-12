---
id: P6-SHIP-01
title: Frete — métodos MVP (retirada/combinada/fixo)
phase: 6
etapa: "Etapa 1 — Módulo shipping (frete)"
area: SHIP
status: done
depends_on: []
blocks: [P6-CHK-01]
tests: [integration]
---

# P6-SHIP-01 — Frete: métodos MVP

## Contexto
O checkout precisa de opções de entrega. **MVP fino:** retirada local, entrega combinada (`private_delivery`) e frete fixo — o suficiente pra vender. Zonas/tarifas por região = **Fase 8, Etapa 5** (saiu da Fase 6).

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
- **Zonas/tarifas/regras** (`shipping_zones`/`shipping_rates`/`shipping_method_rules`): **Fase 8, Etapa 5** (saiu da Fase 6).

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
- [x] `shipping_methods` + índice + migration (`alembic check` vazio).
- [x] CRUD gated + leitura pública (ativos) consumida pelo checkout.
- [x] `private_delivery` com aviso de "combinada após a compra".
- [x] **Modos de falha mapeados** (fixo sem preço → 422; método inexistente → 404; loja sem método ativo → o checkout exige um, em `P6-CHK-01`) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Zonas/tarifas movidas pra **Fase 8, Etapa 5** (MVP fino primeiro; saíram da Fase 6).
- **Implementação:** `shipping_methods` (soft delete) + enum `ShippingMethodType` + índice `store_id+type+is_active`. CRUD em `/stores/{id}/shipping/methods` gated `shipping.view/create/update/delete`; leitura pública em `GET /storefront/shipping-methods` (host-resolved, só ativos). Validação: `fixed_shipping` exige `price_amount_minor` (422). **Sem moeda por método** — os valores são na moeda da loja (single-currency, INV-G3), pareados com `store.currency` no checkout. A aplicação da regra "free acima do mínimo" + o aviso de `private_delivery` no checkout são do `P6-CHK-01`/`P6-SF-01`. Migration `50108c983547`. 5 testes, módulo 100%.

## Follow-ups
- [ ] **`shipping.private_delivery.update` órfã** — o CRUD usa `shipping.create/update/delete` (genérico, cobre `private_delivery`); a permissão `shipping.private_delivery.update` não é lida por nenhuma rota. Decidir se vira ação própria (config da entrega combinada / regras de região na **Fase 8, Etapa 5**) ou remover do catálogo. Origem: `P6-SHIP-01`.
