---
id: P2-CUST-02
title: Modelos por loja/produto (settings/sessions/uploads + cart/order item)
phase: 2
etapa: "Etapa 6 — Personalização 3D"
area: CUST
status: todo
depends_on: [P2-CAT-01, P2-CUST-01]
blocks: [P2-CUST-03]
tests: [integration]
---

# P2-CUST-02 — Modelos por loja/produto

## Contexto
Tabelas **por loja** da personalização (config por produto, sessões, uploads) + a **definição** dos itens de carrinho/pedido personalizados (consumidos na Fase 4). Campos exatos do doc [07](../../07_database_strategy.md).

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md) (campos + índices)
- [22 — Product Customization 3D](../../22_product_customization_3d.md) (sessão, status)

## Escopo (o que ENTRA)
- `customization_product_settings`: `store_id`, `product_id` (único), `model_id`, `allow_color?`, `production_notes`.
- `customization_sessions`: `store_id`, `product_id`, `guest_session_id`, `customer_id`, `cart_id`, `model_id`, `model_version_id`, `status`, `state_json`, `preview_url`, `approved_snapshot_url`, `expires_at`, `approved_at`.
- `customization_uploads`: `store_id`, `customization_session_id`, refs de arquivo (privado), `content_type`, `size`.
- **Definir (modelo só; consumo Fase 4):** `customization_cart_items` (`store_id`, `cart_item_id` único) e `customization_order_items` (`store_id`, `order_id`, `order_item_id` único — cópia congelada).
- **Enums:** `SessionStatus` (`draft|approved|added_to_cart|ordered|abandoned|expired`), `ArtStatus` (`received|reviewing|needs_contact|approved_for_production|in_production|production_done`).
- **Índices** (doc 07): sessions por `store_id+product_id+status`, `store_id+guest_session_id+status`, `store_id+customer_id+status`, `expires_at+status`; uploads `store_id+customization_session_id`; settings `store_id+product_id` único; cart/order items conforme doc 07.
- Migration + `models_registry`.

## Fora de escopo (o que NÃO entra)
- Rotas/lógica → `P2-CUST-03`. Carrinho/pedido (consumo dos cart/order items) → Fase 4.

## Arquivos a criar/alterar
- `backend/app/modules/product_customization/models.py` (tabelas por loja)/`enums.py` (preencher). Migration + `models_registry`.

## Passos
1. Modelos por loja + enums + cart/order item (definição) + índices.
2. Migration (autogenerate + limpeza) do zero; conferir autogenerate vazio.

## Testes
> Fundações §10. Constraints/índices são fronteira real → integração.

- **Cobrir:** `store_id+product_id` único em settings; defaults de status; índices de sessão; soft delete em sessão (expiração).

## Definition of Done
- [ ] Tabelas por loja + `customization_cart_items`/`customization_order_items` (modelo) + índices do doc 07.
- [ ] Migration aplica do zero; autogenerate vazio; testes de modelo.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- `customization_cart_items`/`customization_order_items` são **definidos aqui, consumidos na Fase 4** (carrinho/checkout).

## Follow-ups
- (preencher)
