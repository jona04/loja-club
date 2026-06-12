# Fase 2 — Catálogo e mídia

> Objetivo: o lojista cadastra **produtos com imagem** (S3/CloudFront), com categorias, variações e estoque, isolado por loja. O **3D** é a [Fase 7 — Produtos 3D](./phase-7-3d-products.md).

Docs de referência: [07](../concepts/07_database_strategy.md), [09](../concepts/09_merchant_dashboard.md), [12](../concepts/12_aws_infrastructure_and_deployment.md), [13](../concepts/13_performance_cache_and_cdn.md), [14](../concepts/14_security_strategy.md), [16](../concepts/16_testing_strategy.md), [20](../concepts/20_api_contracts_todo.md).

> **Decomposta em tasks** — ver [`phase-2-catalog-and-media/`](./phase-2-catalog-and-media/README.md) (5 tasks: storage, modelos do catálogo, pipeline de mídia, rotas do catálogo, tela de produtos). O detalhe e o status oficial estão no README da pasta.

## Definition of Done da fase

- CRUD de **produtos com imagem**, categorias, variações e estoque, **isolado por loja**.
- Upload validado → **AWS S3** + **CloudFront**; thumbnails por **worker** (reais, inclusive do dev local).
- Tela de **Produtos** no painel + componente de upload de imagem.
- Testes de isolamento e regras (slug único por loja) passando.

---

## Etapa 1 — Mídia: storage + pipeline (S3/CloudFront)

### Storage + pipeline (doc [12](../concepts/12_aws_infrastructure_and_deployment.md)/[13](../concepts/13_performance_cache_and_cdn.md))
- [ ] Abstração fina de storage (`app/core/storage.py`; o domínio não conhece boto3) + AWS dev real (us-east-2). (`P2-MEDIA-01`.)
- [ ] `media_files` + upload validado → **S3**; **worker** gera thumbnails (Pillow); servir por **CloudFront**. (`P2-MEDIA-02`.)

---

## Etapa 2 — Catálogo: modelos + rotas

### Modelos (com `store_id`) (doc [07](../concepts/07_database_strategy.md))
- [ ] `catalog_products` (só imagem; `type` 3D = [Fase 7](./phase-7-3d-products.md)), `catalog_categories`, variações, estoque, status publicado/rascunho; `slug` **único por loja** (índice parcial). (`P2-CAT-01`.)

### Rotas/serviço (doc [20](../concepts/20_api_contracts_todo.md))
- [ ] CRUD + publish/archive sob `/api/v1/stores/{id}/...`, gating `catalog.*`, `Page[T]`. (`P2-CAT-02`.)

---

## Etapa 3 — Frontend (painel)
- [ ] Tela de **Produtos** + componente de **upload de imagem** (`ProductImageUpload`). Doc [09](../concepts/09_merchant_dashboard.md). (`P2-FE-01`.)

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] Isolamento multi-tenant (produto/categoria por loja); `slug` único por loja; upload → S3 + thumbnail por worker.

---

## Fora desta fase

- **[Fase 7 — Produtos 3D](./phase-7-3d-products.md):** produto **3D / 3D-personalizável**, **geração de modelo via API** (Meshy/Tripo3D/Hyper3D), sessões de personalização e editor 3D do storefront — **o lojista gera os modelos**.
- **→ Fase 8:** planos + pagamentos.

## Construído sobre a Fase 1 (reusar, não recriar)

- **Autorização:** `require_permission("catalog.*")` — permissões `catalog.*` já seedadas (`P1-PERM-02`).
- **Tenancy:** rotas sob `/api/v1/stores/{store_id}/...`; recurso por `store_id + id` via `get_store_scoped` (INV-T2).
- **API:** `Page[T]` / `AppError` / `{data,count}` (`P1-API-01`).
- **Storage:** `app/core/storage.py` + AWS dev em us-east-2 (`P2-MEDIA-01`, feito).
- **Convenção de módulo** + `slug` **único por loja quando ativo** (índice parcial), como nas tabelas `store_*`.

## Reconciliações

- **3D — Fase 7:** os modelos vêm do **catálogo da plataforma** (via seed; o lojista escolhe); a **geração pelo lojista** (GLB via API) é a [Fase 12](./phase-12-merchant-3d-generation.md). Ver [Fase 7](./phase-7-3d-products.md) e doc [22](../concepts/22_product_customization_3d.md).
