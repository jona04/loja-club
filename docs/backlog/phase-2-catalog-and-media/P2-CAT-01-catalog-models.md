---
id: P2-CAT-01
title: Modelos do catálogo (produtos/variações/imagens/categorias/estoque/coleções)
phase: 2
etapa: "Etapa 5 — Módulo catalog"
area: CAT
status: done
depends_on: []
blocks: [P2-CAT-02]
tests: [integration]
---

# P2-CAT-01 — Modelos do `catalog`

## Contexto
Base de dados do catálogo, **isolada por loja** (`store_id` + soft delete), com os índices do doc [07](../../07_database_strategy.md). Só os modelos + migration aqui; rotas em `P2-CAT-02`.

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md) (tabelas `catalog_*` + índices)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (campos do produto)

## Escopo (o que ENTRA)
Modelos em `app/modules/catalog/models.py` (todos com `store_id` + mixins; enums em `enums.py`):
- `catalog_products`: `store_id`, `slug` (único por loja quando ativo), `name`, `description`, `status` (`draft|published|archived`), preço (`price_amount_minor` + `price_currency`, INV-G1/D4), `is_featured`. *(Produto com imagem; o campo `type` (3D) entra na Fase 7.)*
- `catalog_product_variants`: `store_id`, `product_id`, atributos (ex.: tamanho/cor), `price_override_amount_minor?`, `status`.
- `catalog_product_images`: `store_id`, `product_id`, `media_file_id`, `position`.
- `catalog_categories`: `store_id`, `slug` (único por loja quando ativo), `name`.
- `catalog_product_categories`: produto×categoria.
- `catalog_inventory_items`: `store_id`, `product_id`, `variant_id`, `quantity`.
- `catalog_collections`: vitrines/coleções (destaque da home).
- **Enums:** `ProductStatus`.
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

- **Cobrir:** `slug` único por loja quando ativo; mesmo slug em lojas diferentes ok; default de `status`; **FK de `store_id`** (StoreScopedMixin); cadeia produto→variante→estoque.

## Definition of Done
- [x] Tabelas `catalog_*` (7) com `store_id` + soft delete + índices do doc 07.
- [x] Migration aplicada; `alembic check` → "No new upgrade operations detected".
- [x] Testes de modelo verdes (7) — suíte 147 passed, cobertura 91%.
- [x] Itens adiados varridos → Follow-ups + README.

## Progresso
- ✅ **Modelos** (`catalog/models.py`): `Product`, `ProductVariant`, `ProductImage`, `Category`, `ProductCategory`, `InventoryItem`, `Collection` — via `StoreScopedMixin` (FK `store_stores.id`) + soft delete + índices do doc 07. Enums `ProductStatus`/`ProductVariantStatus`. Registrados no `models_registry`.
- ✅ **Migration** `db3416735b1e_create_catalog_tables` (autogenerate + revisão: ordem de FK, índices parciais de `slug`). `alembic check` vazio.
- ✅ **Testes** `tests/integration/test_catalog_models.py` (defaults, slug único por loja, cross-store, soft-delete, FK de `store_id`, variante/estoque).

## Notas / Reconciliações
- **Só imagem (sem 3D) nesta fase.** O `type` (`image` / `image_3d` / `image_3d_customizable`) e o vínculo a modelo 3D entram na **[Fase 7 — Produtos 3D](../phase-7-3d-products.md)** (lojista gera o 3D via API 3rd-party) — ver doc [22](../../22_product_customization_3d.md). Por enquanto a tabela não tem `type`.
- **`StoreScopedMixin` carrega a FK** (`foreign_key="store_stores.id"`) e o catálogo o usa. `store_settings`/`store_members`/`domain_hosts` mantêm FK explícita (uma é `unique`).
- **`catalog_product_images.media_file_id`** é coluna indexada **sem FK** aqui; a FK → `media_files` entra na `P2-MEDIA-02` (tabela criada lá).
- Preço como `Money` (amount_minor + currency, INV-G1) — moeda default herdada da loja na criação (decisão de `P2-CAT-02`).

## Follow-ups
- — nenhum. (FK de `media_file_id` → `media_files` é escopo da `P2-MEDIA-02`.)
