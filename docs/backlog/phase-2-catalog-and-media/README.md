# Fase 2 — Catálogo e mídia

> O **3D/personalização** é a [Fase 5 — Produtos 3D](../phase-5-3d-products.md) (lojista gera os modelos via API de terceiros). Esta fase entrega só imagem.

> Roadmap: Etapa 5. Objetivo: o lojista cadastra **produtos com imagem** (S3/CloudFront), com categorias, variações e estoque, isolado por loja.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [07](../../07_database_strategy.md), [09](../../09_merchant_dashboard.md), [12](../../12_aws_infrastructure_and_deployment.md), [13](../../13_performance_cache_and_cdn.md), [14](../../14_security_strategy.md), [16](../../16_testing_strategy.md), [20](../../20_api_contracts_todo.md).

> Visão geral / trilha de alto nível: [`../phase-2-catalog-and-media.md`](../phase-2-catalog-and-media.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase

- CRUD de **produtos com imagem**, categorias, variações e estoque, **isolado por loja**.
- Upload de imagem validado → **AWS S3**, servido por **CloudFront**; thumbnails gerados por **worker** (S3/CloudFront reais, inclusive do dev local).
- Tela de **Produtos** no painel (listar/criar/editar/arquivar/publicar + upload de imagem).
- Testes de isolamento e de regras (slug único por loja; arte/upload válidos) passando.

> **Fora desta fase:** o **3D** (produto `image_3d`/`image_3d_customizable`, geração de modelo via API, sessões de personalização e o editor 3D do storefront) é a **[Fase 5 — Produtos 3D](../phase-5-3d-products.md)**; **planos + pagamentos** são a **Fase 6**.

## Construído sobre as Fases 0–1 (não recriar)

- **Tenancy/autorização:** `require_permission("catalog.*")`, `get_active_store`/`ActiveStore`, `get_store_scoped` (INV-T2) — catálogo de permissões já **seedado** (`P1-PERM-02`).
- **API:** `Page[T]`, `pagination_params`, `AppError`, envelope `{data,count}`/`{error}` (`P1-API-01`).
- **Infra:** fila `arq` + `enqueue()` (`P0-CFG-04`); cache Redis (`P0-CFG-03`/doc 13); mixins (UUID/timestamps/soft delete + `store_id` FK, `P0-MOD-01`); `Money` (`P0-MOD-05`); **storage S3** (`P2-MEDIA-01`, feito).
- **Testes:** fixtures multi-tenant (`two_stores`, `tests/utils/store.py`) + `moto[s3]` (`P1-TEST-01`/`P0-TEST-01`).

## Pré-requisitos (o que ainda falta)

**A construir no código (entra nas tasks):**
- **Pillow** (dep) para gerar thumbnails no worker → `P2-MEDIA-02` *(decisão registrada)*.

**AWS dev:** ✅ provisionada e verificada na `P2-MEDIA-01` (bucket privado + CloudFront/OAC + IAM, **us-east-2**), com smoke real verde.

## AWS dev — guiado + garantia de funcionamento

- **Região (1ª etapa):** **Ohio (`us-east-2`)** — S3 + CloudFront + IAM na mesma região.
- **Best practices (dev):** bucket **privado** (Block Public Access) → público via **CloudFront/OAC**; arquivos privados via **presigned**; IAM **mínimo**; lifecycle p/ temporários.
- **Garantia de que funciona:** toda task que usa AWS tem **2 níveis de teste** — `moto` (CI, sem credencial) **e** **smoke real** env-gated (sobe/baixa de verdade no bucket dev; pulado no CI sem secrets).
- **Prod (Fase 7):** bucket/distribuição de prod + **IAM role** (sem chave longa) + segredos via SSM.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P2-MEDIA-01](./P2-MEDIA-01-storage-abstraction.md) | Abstração de storage (S3/boto3) + config + setup AWS dev | **done** | — |
| 2 | [P2-CAT-01](./P2-CAT-01-catalog-models.md) | Modelos do `catalog` (produtos/variações/imagens/categorias/estoque/coleções) | **done** | — |
| 3 | [P2-MEDIA-02](./P2-MEDIA-02-media-pipeline.md) | `media_files` + pipeline de upload + worker de thumbnails | **done** | P2-MEDIA-01 |
| 4 | [P2-CAT-02](./P2-CAT-02-catalog-service-routes.md) | `catalog`: serviço/rotas (CRUD/publicar/categorias/variações/estoque/imagens) | **done** | P2-CAT-01, P2-MEDIA-02 |
| 5 | [P2-FE-01](./P2-FE-01-products-screen.md) | Painel: tela de Produtos + componente de upload de imagem | **done** | P2-CAT-02, P2-MEDIA-02 |

> ✅ **Fase 2 completa** — as 5 tasks estão `done`.

## Ordem sugerida de execução

```text
P2-MEDIA-01 (done) → P2-CAT-01 (done) → P2-MEDIA-02 (done) → P2-CAT-02 (done) → P2-FE-01 (done)
```

## Reconciliações da fase (registrar conforme surgirem)

- **3D é a [Fase 5 — Produtos 3D](../phase-5-3d-products.md).** O **lojista gera o modelo via API 3rd-party** (Meshy/Tripo3D/Hyper3D); não há catálogo 3D da plataforma. Decompõe em tasks quando chegar a fase.
- **Produto = imagem.** O campo `type` (`image`/`image_3d`/`image_3d_customizable`) entra na **Fase 5** (migration no `catalog_products`).
- **Storage real (sem MinIO):** S3 + CloudFront de verdade desde o dev local (DEC-8); testes com `moto` + smoke real (`P2-MEDIA-01`).
- **Pillow** para thumbnails: registrar a decisão de lib nas Fundações ao implementar `P2-MEDIA-02`.

## Follow-ups / débitos técnicos

> Mesma convenção da Fase 1: item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

- [ ] **`enqueue` falho após original no S3** → `media_files` preso em `processing` (sem reconciliação de órfãos). Origem: `P2-MEDIA-02`.
- [ ] **Worker falho** (`generate_variants`) não marca `status=failed` + sem retry. Origem: `P2-MEDIA-02`.
- [ ] **Tamanho do upload validado após `file.read()`** (risco de memória) — checar antes via `Content-Length`/streaming. Origem: `P2-MEDIA-02`.
- [ ] **Race no slug** → `IntegrityError` vira 500 em vez de 409 (tratar no service). Origem: `P2-CAT-02`.
- [ ] **Estoque sem índice único** `(store_id, product_id, variant_id)` → upsert pode duplicar linha. Origem: `P2-CAT-02`.
- [ ] **Archive de produto não cascateia** para variações/imagens/estoque (órfãos ativos). Origem: `P2-CAT-02`.
- [ ] **Lazy-init de client sem lock** (`storage._s3_client`, `queue._get_pool`, INV-F6): 1ª chamada concorrente pode criar 2 clients/pools (um descartado) — **benigno**; `close_pool` engole `RuntimeError` cross-loop **só em teste**. Origem: refactor INV-F6 (`P2-MEDIA-01`/`P0-CFG-04`).
- [ ] **Preço com expoente da moeda** (INV-G1) — a tela assume 2 casas. Origem: `P2-FE-01`.
- [ ] **UI de variações/categorias** (backend já suporta). Origem: `P2-FE-01`.
- [ ] **E2E ao vivo** (Playwright) da tela de Produtos. Origem: `P2-FE-01`.
