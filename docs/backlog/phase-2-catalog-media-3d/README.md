# Fase 2 — Catálogo, mídia e personalização 3D

> Roadmap: Etapas 5–6. Objetivo: lojista cadastra produtos reais com imagens (S3/CloudFront), marca produtos como `customizable_3d` e vincula modelos 3D da biblioteca da Loja Club; sessões de personalização funcionam via API.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [07](../../07_database_strategy.md), [09](../../09_merchant_dashboard.md), [12](../../12_aws_infrastructure_and_deployment.md), [13](../../13_performance_cache_and_cdn.md), [14](../../14_security_strategy.md), [22](../../22_product_customization_3d.md), [16](../../16_testing_strategy.md), [20](../../20_api_contracts_todo.md).

> Visão geral / trilha de alto nível: [`../phase-2-catalog-media-3d.md`](../phase-2-catalog-media-3d.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase

- CRUD de produtos (`simple` e `customizable_3d`) com imagens, categorias, variações e estoque, **isolado por loja**.
- Upload de imagem validado → **AWS S3**, servido por **CloudFront**; thumbnails gerados por **worker** (S3/CloudFront reais, inclusive do dev local).
- Biblioteca inicial de modelos 3D (caneca, squeeze, camisa) cadastrada; produto vinculável a um modelo.
- Sessões de personalização via API: criar, atualizar estado (autosave), upload de arte (privado/URL assinada), preview, **aprovar** (congela snapshot); lojista vê sessões da própria loja.
- Testes de isolamento e de regras (slug único por loja; arte privada; sessão só da loja) passando.

## Construído sobre as Fases 0–1 (não recriar)

- **Tenancy/autorização:** `require_permission("catalog.*"/"customization.*")`, `get_active_store`/`ActiveStore`, `get_store_scoped` (INV-T2) — o catálogo de permissões já está **seedado** (`P1-PERM-02`).
- **API:** `Page[T]`, `pagination_params`, `AppError`, envelope `{data,count}`/`{error}` (`P1-API-01`).
- **Infra:** fila `arq` + `enqueue()` (`P0-CFG-04`); cache Redis + chaves padronizadas (`P0-CFG-03`/doc 13); mixins (`StoreScopedMixin`/UUID/timestamps/soft delete, `P0-MOD-01`); `Money` (`P0-MOD-05`).
- **Testes:** fixtures multi-tenant (`two_stores`, `tests/utils/store.py`) + `moto[s3]` para mock de S3 (`P1-TEST-01`/`P0-TEST-01`).
- **Scaffolds vazios** de `catalog`/`media`/`product_customization` (enums/schemas) já existem.

## Pré-requisitos (o que ainda falta — "já temos tudo?")

**A construir no código (entra nas tasks):**
- `app/core/storage.py` — abstração S3 (boto3), INV-F2 → `P2-MEDIA-01`.
- **Pillow** (dep) para gerar thumbnails no worker → `P2-MEDIA-02` *(decisão registrada)*.
- Config `S3_BUCKET`/`S3_REGION`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`CDN_BASE_URL` em `config.py`/`.env` → `P2-MEDIA-01`.

**AWS dev — provisionada de forma guiada (não é "você se vira"):**
- ⚠️ Bucket **S3 dev** (privado) + **CloudFront/OAC** + **IAM least-privilege** (DEC-8, doc [12](../../12_aws_infrastructure_and_deployment.md)). A **`P2-MEDIA-01` provisiona isso COM você** (eu forneço passos/policy; você executa na sua conta e me passa os valores) e deixa **verificado por smoke real**. Detalhes na seção abaixo. **Prod = Fase 6.**

**Conteúdo (responsabilidade Loja Club):**
- ⚠️ **GLBs 3D** (caneca, squeeze, camisa) com áreas imprimíveis (doc [22](../../22_product_customization_3d.md)). Até existirem, `P2-CUST-01` faz **seed mínimo** (registros + placeholders) para destravar o resto.

## AWS dev — guiado + garantia de funcionamento

- **Região (1ª etapa):** **Ohio (`us-east-2`)** — S3 + CloudFront + IAM na mesma região.
- **Quem faz o quê:** eu forneço o passo a passo (console/CLI), a **policy IAM least-privilege** e a config de **OAC/CORS/lifecycle**; **você executa** na sua conta e me devolve `S3_REGION`/`S3_BUCKET`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`CDN_BASE_URL`. (Não acesso sua conta; quando for criar algo, te guio até concluir.)
- **Best practices (dev):** bucket **privado** (Block Public Access) → público via **CloudFront/OAC**; arte do cliente **privada** via **presigned**; IAM **mínimo**; lifecycle p/ temporários.
- **Garantia de que funciona (local/dev):** toda task que usa AWS tem **2 níveis de teste** — `moto` (CI, sem credencial) **e** **smoke real** env-gated (sobe/baixa de verdade no bucket dev + GET via CloudFront; pulado no CI sem secrets). É o que prova o provisionamento + credenciais.
- **Prod (2ª etapa, Fase 6):** bucket/distribuição de prod + **IAM role** (sem chave longa) + segredos via SSM.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P2-MEDIA-01](./P2-MEDIA-01-storage-abstraction.md) | Abstração de storage (S3/boto3) + config + setup AWS dev | todo | — |
| 2 | [P2-CAT-01](./P2-CAT-01-catalog-models.md) | Modelos do `catalog` (produtos/variações/imagens/categorias/estoque/coleções) | todo | — |
| 3 | [P2-MEDIA-02](./P2-MEDIA-02-media-pipeline.md) | `media_files` + pipeline de upload + worker de thumbnails | todo | P2-MEDIA-01 |
| 4 | [P2-CAT-02](./P2-CAT-02-catalog-service-routes.md) | `catalog`: serviço/rotas (CRUD/publicar/categorias/variações/estoque/imagens) | todo | P2-CAT-01, P2-MEDIA-02 |
| 5 | [P2-CUST-01](./P2-CUST-01-3d-library.md) | Biblioteca 3D global (`customization_3d_models` + versões) + seed + listagem | todo | — |
| 6 | [P2-CUST-02](./P2-CUST-02-customization-models.md) | Modelos por loja/produto (settings/sessions/uploads + cart/order item) | todo | P2-CAT-01, P2-CUST-01 |
| 7 | [P2-CUST-03](./P2-CUST-03-customization-service-routes.md) | `product_customization`: rotas (sessão/autosave/upload/aprovar/expirar/merchant) | todo | P2-CUST-02, P2-MEDIA-02 |
| 8 | [P2-FE-01](./P2-FE-01-products-screen.md) | Painel: tela de Produtos + componente de upload de imagem | todo | P2-CAT-02, P2-MEDIA-02 |
| 9 | [P2-FE-02](./P2-FE-02-customization-config.md) | Painel: config de personalização no produto + visão de sessões | todo | P2-CUST-03, P2-CAT-02, P2-FE-01 |

## Ordem sugerida de execução

```text
P2-MEDIA-01 → P2-CAT-01 → P2-MEDIA-02 → P2-CAT-02 → P2-CUST-01
→ P2-CUST-02 → P2-CUST-03 → P2-FE-01 → P2-FE-02
```

## Reconciliações da fase (registrar conforme surgirem)

- **Editor 3D do cliente é Fase 3** (storefront/Three.js). A Fase 2 entrega só o **backend** das sessões + o **painel do lojista** (configurar/visualizar) — doc [22](../../22_product_customization_3d.md).
- **`customization_cart_items`/`customization_order_items`:** o **modelo** é definido aqui (doc 07), mas só **consumido** na Fase 4 (carrinho/checkout).
- **Storage real (sem MinIO):** S3 + CloudFront de verdade desde o dev local (DEC-8, doc [12](../../12_aws_infrastructure_and_deployment.md)); testes usam `moto`.
- **Pillow** para thumbnails: decisão a registrar nas Fundações (lib de imagem) ao implementar `P2-MEDIA-02`.

## Follow-ups / débitos técnicos

> Mesma convenção da Fase 1: item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

- (preencher conforme as tasks forem implementadas)
