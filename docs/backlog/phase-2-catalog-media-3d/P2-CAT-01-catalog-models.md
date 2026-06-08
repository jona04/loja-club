---
id: P2-CAT-01
title: Modelos do catálogo (produtos/variações/imagens/categorias/estoque/coleções)
phase: 2
etapa: "Etapa 5 — Módulo catalog"
area: CAT
status: todo
depends_on: []
blocks: [P2-CAT-02, P2-CUST-02]
tests: [integration]
---

# P2-CAT-01 — Modelos do `catalog`

## Contexto
Base de dados do catálogo, **isolada por loja** (`store_id` + soft delete), com os índices do doc [07](../../07_database_strategy.md). Só os modelos + migration aqui; rotas em `P2-CAT-02`.

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md) (tabelas `catalog_*` + índices)
- [22 — Product Customization 3D](../../22_product_customization_3d.md) (tipo `simple|customizable_3d`)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (campos do produto)

## Escopo (o que ENTRA)
Modelos em `app/modules/catalog/models.py` (todos com `store_id` + mixins; enums em `enums.py`):
- `catalog_products`: `store_id`, `slug` (único por loja quando ativo), `name`, `description`, `type` (`simple|customizable_3d`), `status` (`draft|published|archived`), preço (`price_amount_minor` + `price_currency`, INV-G1/D4), `is_featured`.
- `catalog_product_variants`: `store_id`, `product_id`, atributos (ex.: tamanho/cor), `price_override_amount_minor?`, `status`.
- `catalog_product_images`: `store_id`, `product_id`, `media_file_id`, `position`.
- `catalog_categories`: `store_id`, `slug` (único por loja quando ativo), `name`.
- `catalog_product_categories`: produto×categoria.
- `catalog_inventory_items`: `store_id`, `product_id`, `variant_id`, `quantity`.
- `catalog_collections`: vitrines/coleções (destaque da home).
- **Enums:** `ProductType`, `ProductStatus`.
- **Índices** (doc 07): `store_id+slug` único-quando-ativo (products/categories), `store_id+status`, `store_id+created_at`, `store_id+product_id+status` (variants), `store_id+product_id+position` (images), `store_id+product_id+variant_id` (inventory).
- Migration + registro em `models_registry`.

## Fora de escopo (o que NÃO entra)
- Rotas/serviço → `P2-CAT-02`. Pipeline de mídia → `P2-MEDIA-02` (aqui só o FK `media_file_id`).

## Arquivos a criar/alterar
- `backend/app/modules/catalog/models.py`, `enums.py` (preencher).
- `backend/app/models_registry.py` (alterar).
- Migration Alembic.

## Passos
1. Modelos + enums + índices do doc 07.
2. Migration (autogenerate + limpeza) aplicando em DB do zero; conferir autogenerate vazio depois.

## Testes
> Fundações §10. Constraints são fronteira real → integração.

- **Cobrir:** `slug` único por loja quando ativo; mesmo slug em lojas diferentes ok; defaults (`type`/`status`); FK de imagem→`media_files`.

## Definition of Done
- [ ] Tabelas `catalog_*` com `store_id` + soft delete + índices do doc 07.
- [ ] Migration aplica do zero; `alembic` autogenerate volta vazio.
- [ ] Testes de modelo verdes.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- Preço como `Money` (amount_minor + currency, INV-G1) — moeda default herdada da loja na criação (decisão de `P2-CAT-02`).

## Follow-ups
- (preencher)
