---
id: P7-ORD-01
title: Carrinho/pedido — congelar a personalização aprovada
phase: 7
etapa: "Etapa 6 — Carrinho/pedido: congelar personalização"
area: ORD
status: todo
depends_on: [P7-SESS-01, P7-EDITOR-02]
blocks: []
tests: [integration]
---

# P7-ORD-01 — Congelar a personalização no pedido (INV-P5)

## Contexto
A personalização **aprovada** vira item de carrinho e é **congelada** no pedido — cópia própria (`state_json` + `version_id` + snapshot), independente da sessão viva. Fecha o gate que a Fase 6 deixou pronto.

## Docs de referência
- [30 — §7 Versionamento e congelamento](../../concepts/30_3d_customization_technical_design.md)
- [07 — `customization_cart_items`/`order_items`](../../concepts/07_database_strategy.md)
- [11 — Checkout](../../concepts/11_checkout_payments_and_split.md)

## Escopo (o que ENTRA)
- `customization_cart_items` (sessão aprovada ↔ `cart_item`) + `customization_order_items` (cópia congelada). Índices do doc 07. Migration.
- **Add-to-cart de `image_3d_customizable`:** só com sessão `approved` → o carrinho passa `has_approved_customization=True` ao gate [`assert_addable_to_cart`](../../../backend/app/modules/catalog/services.py) (Fase 6).
- **Criar pedido:** copiar `state_json` + `version_id` + **snapshot** (copiado pra `private/<store_id>/orders/<order_id>/...`) pro `customization_order_items`. Não depende da sessão viva.

## Fora de escopo (o que NÃO entra)
- Editor/sessões: `P7-EDITOR-*`/`P7-SESS-01`.
- Operar/baixar arte no painel: `P7-OPS-01`.

## Arquivos a criar/alterar
- `backend/app/modules/customization/{models,services}.py` (alterar) — cart/order items + congelamento.
- `backend/app/modules/cart/services.py` (alterar) — passar `has_approved_customization`.
- `backend/app/modules/orders/services.py` (alterar) — copiar a personalização ao criar o pedido.
- migration alembic.

## Passos
1. Tabelas cart/order items + migration.
2. Carrinho: vincular sessão aprovada + acionar o gate corretamente.
3. Pedido: congelar (copiar estado + versão + snapshot pra chave do pedido).

## Testes
- **Níveis:** integração.
- **Quando escrever:** antes (contrato claro) / durante.
- **Cobrir:** integração — `image_3d_customizable` **só** entra com `approved`; criar pedido copia estado/versão/snapshot; **alterar a sessão depois não muda o pedido**; isolamento por loja.

## Definition of Done
- [ ] Item customizável só entra com sessão aprovada; pedido **congela** estado+versão+snapshot (chave do pedido).
- [ ] **Modos de falha mapeados** — add sem `approved` → 422 `customization_required`; cópia do snapshot falha → pedido não confirma; editar área/versão depois não afeta o congelado. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reusa o seam da Fase 6 (`assert_addable_to_cart(has_approved_customization=...)`).

## Follow-ups
- [ ] **Limpeza de uploads órfãos** de sessões que não viraram pedido (mantendo o que é do pedido) — *Quando:* retenção (cruza com `P7-SESS-01`). → README da fase.
