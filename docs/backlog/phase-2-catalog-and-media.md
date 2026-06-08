# Fase 2 — Catálogo e mídia

> Roadmap: Etapa 5. Objetivo: o lojista cadastra **produtos com imagem** (S3/CloudFront), com categorias, variações e estoque, isolado por loja. O **3D** é a [Fase 5 — Produtos 3D](./phase-5-3d-products.md).

Docs de referência: [07](../07_database_strategy.md), [09](../09_merchant_dashboard.md), [12](../12_aws_infrastructure_and_deployment.md), [13](../13_performance_cache_and_cdn.md), [14](../14_security_strategy.md), [16](../16_testing_strategy.md), [20](../20_api_contracts_todo.md).

> **Decomposta em tasks** — ver [`phase-2-catalog-and-media/`](./phase-2-catalog-and-media/README.md) (5 tasks: storage, modelos do catálogo, pipeline de mídia, rotas do catálogo, tela de produtos). O detalhe e o status oficial estão no README da pasta.

## Definition of Done da fase

- CRUD de **produtos com imagem**, categorias, variações e estoque, **isolado por loja**.
- Upload validado → **AWS S3** + **CloudFront**; thumbnails por **worker** (reais, inclusive do dev local).
- Tela de **Produtos** no painel + componente de upload de imagem.
- Testes de isolamento e regras (slug único por loja) passando.

## Fora desta fase

- **[Fase 5 — Produtos 3D](./phase-5-3d-products.md):** produto **3D / 3D-personalizável**, **geração de modelo via API** (Meshy/Tripo3D/Hyper3D), sessões de personalização e editor 3D do storefront — **o lojista gera os modelos**.
- **→ Fase 6:** planos + pagamentos.

## Construído sobre a Fase 1 (reusar, não recriar)

- **Autorização:** `require_permission("catalog.*")` — permissões `catalog.*` já seedadas (`P1-PERM-02`).
- **Tenancy:** rotas sob `/api/v1/stores/{store_id}/...`; recurso por `store_id + id` via `get_store_scoped` (INV-T2).
- **API:** `Page[T]` / `AppError` / `{data,count}` (`P1-API-01`).
- **Storage:** `app/core/storage.py` + AWS dev em us-east-2 (`P2-MEDIA-01`, feito).
- **Convenção de módulo** + `slug` **único por loja quando ativo** (índice parcial), como nas tabelas `store_*`.

## Reconciliações

- **3D — Fase 5:** o lojista gera o modelo via API 3rd-party; **não há biblioteca 3D da plataforma**. Ver [Fase 5](./phase-5-3d-products.md) e doc [22](../22_product_customization_3d.md).
