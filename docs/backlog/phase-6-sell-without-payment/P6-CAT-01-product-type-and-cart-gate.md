---
id: P6-CAT-01
title: Tipo de produto (type) + portão do add-to-cart
phase: 6
etapa: "Etapa 0 — Catálogo: tipo de produto + portão do add-to-cart"
area: CAT
status: done
depends_on: []
blocks: [P6-CART-01]
tests: [integration]
---

# P6-CAT-01 — Tipo de produto + portão do add-to-cart

## Contexto
Costura para a [Fase 7](../phase-7-3d-products.md): o add-to-cart precisa saber se o produto vai direto ao carrinho ou exige personalização. Adiantar o campo `type` pra cá (default `image`) faz a Fase 7 só **ativar** os tipos 3D — sem migration nem retrofit do serviço de carrinho.

## Docs de referência
- [22 — Tipo de produto](../../concepts/22_product_customization_3d.md)
- [07 — Database](../../concepts/07_database_strategy.md)
- [11 — Checkout (portão do add-to-cart)](../../concepts/11_checkout_payments_and_split.md)

## Escopo (o que ENTRA)
- Enum `ProductType` (`image|image_3d|image_3d_customizable`) + campo `type` em `catalog_products` (default `image`), via migration.
- **Portão do add-to-cart** type-aware (helper/serviço reutilizável): `image`/`image_3d` → direto; `image_3d_customizable` → exige sessão `approved`. Na Fase 6 todo produto é `image`; o ramo customizável **levanta erro claro** (não há sessão de personalização nesta fase).
- Expor `type` no `ProductPublic` (painel) e no `StorefrontProduct` (vitrine).

## Fora de escopo (o que NÃO entra)
- Geração de modelo 3D, editor e sessões de personalização: **Fase 7**.
- O carrinho em si (que consome o portão): `P6-CART-01`.

## Arquivos a criar/alterar
- `backend/app/modules/catalog/enums.py` (alterar) — `ProductType`.
- `backend/app/modules/catalog/models.py` (alterar) — `Product.type`.
- `backend/app/modules/catalog/schemas.py` (alterar) — expor `type`.
- `backend/app/modules/catalog/services.py` (alterar) — helper `assert_addable(...)` do portão (ou em `cart/services` no `P6-CART-01`).
- migration alembic (autogenerate → revisar → `alembic check` vazio).

## Passos
1. Enum + campo `type` (default `image`) + migration.
2. Helper do portão (Fase 6: bloqueia `image_3d_customizable` por falta de sessão).
3. Expor `type` nos schemas público/vitrine.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — produto novo nasce `image`; `type` aparece no público/vitrine; portão deixa `image`/`image_3d` passar e **barra** `image_3d_customizable`.

## Definition of Done
- [x] `type` em `catalog_products` (default `image`) + migration (`alembic check` vazio).
- [x] Portão do add-to-cart type-aware (no-op p/ `image`).
- [x] `type` no `ProductPublic`/`StorefrontProduct`.
- [x] **Modos de falha mapeados** (produto legado sem `type` → default `image`; customizável sem sessão → erro) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reconcilia o doc 22 (era `simple`/`customizable_3d`) para `image|image_3d|image_3d_customizable`; o `type` **nasce aqui** (Fase 7 Etapa 2 reconciliada — passa a só **ativar** os tipos 3D).
- **Implementação:** `ProductType` em `catalog/enums.py`; `type` em `ProductBase` (→ herda no `Product` [coluna] e no `ProductPublic`/`StorefrontProduct` [leitura]; **não** entra em `ProductCreate`/`Update`, então na Fase 6 é sempre `image`). Portão = `catalog.services.assert_addable_to_cart(product, *, has_approved_customization=False)` → **422 `customization_required`** para `image_3d_customizable` sem sessão (o kwarg é a costura que o carrinho da Fase 7 usa).
- **Migration `6d906257c2c5`:** cria o enum, adiciona a coluna com `server_default='image'` (backfill das linhas existentes — 29 no dev), depois **dropa** o server default (casa com o model; `alembic check` vazio). Downgrade dropa coluna + enum.

## Follow-ups
- [ ] — nenhum.
