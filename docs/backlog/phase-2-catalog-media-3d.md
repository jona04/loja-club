# Fase 2 — Catálogo, mídia e personalização 3D

> Roadmap: Etapas 5–6. Objetivo: lojista cadastra produtos reais com imagens; marca produtos como `customizable_3d` e vincula modelos 3D da biblioteca da Loja Club; sessões de personalização funcionam via API.

Docs de referência: [07](../07_database_strategy.md), [09](../09_merchant_dashboard.md), [12](../12_aws_infrastructure_and_deployment.md), [13](../13_performance_cache_and_cdn.md), [14](../14_security_strategy.md), [22](../22_product_customization_3d.md), [16](../16_testing_strategy.md).

> **Esta fase já está decomposta em tasks** — ver [`phase-2-catalog-media-3d/`](./phase-2-catalog-media-3d/README.md) (9 tasks, com escopo, dependências, DoD e pré-requisitos). Este arquivo é a **visão geral (consulta)**: a trilha de alto nível. O detalhe e o status oficial estão no README da pasta.

## Definition of Done da fase

- CRUD de produtos (simple e customizable_3d) com imagens, categorias, variações e estoque, isolado por loja.
- Upload de imagem validado, indo para **AWS S3** e servido por **CloudFront**; thumbnails gerados por worker. (S3/CloudFront reais, usados inclusive a partir do dev local.)
- Biblioteca inicial de modelos 3D (caneca, squeeze, camisa) cadastrada; produto vinculável a um modelo.
- Sessões de personalização: criar, atualizar estado, upload de arte, preview, aprovar; lojista vê sessões da própria loja.

---

## Construído sobre a Fase 1 (reusar, não recriar)

- **Autorização:** gate com `require_permission("catalog.product.update")` etc. — o **catálogo de permissões `catalog.*` já está seedado** (`P1-PERM-02`); só usar as chaves do doc [08](../08_modules_and_permissions.md).
- **Tenancy:** rotas sob `/api/v1/stores/{store_id}/...` com `get_active_store`/`ActiveStore`; acessar recurso por **`store_id + id`** via `get_store_scoped` (`P1-TEN-01`, INV-T2) — nunca buscar só por id.
- **API:** paginação/erro via `app/core/api.py` (`Page[T]`, `pagination_params`, `AppError`); listas retornam `{data, count}`.
- **Convenção de módulo:** `models.py`/`enums.py`/`schemas.py`/`services.py`/`repositories.py`/`routes.py`; `slug` **único por loja quando ativo** (índice parcial `WHERE deleted_at IS NULL`, como em `store_stores`).

---

## Etapa 5 — Módulo `catalog`

### Modelos (`app/modules/catalog/models.py`) — todos com `store_id` + soft delete
- [ ] `catalog_products`: `store_id`, `slug` (único por loja quando ativo), `name`, `description`, `type` (`simple|customizable_3d`), `status` (`draft|published|archived`), `price`, `is_featured`, timestamps. Doc [22](../22_product_customization_3d.md)/[07](../07_database_strategy.md).
- [ ] `catalog_product_variants`: `store_id`, `product_id`, atributos (ex.: tamanho/cor), `price_override?`, `status`.
- [ ] `catalog_product_images`: `store_id`, `product_id`, `media_file_id`, `position`.
- [ ] `catalog_categories`: `store_id`, `slug` (único por loja quando ativo), `name`.
- [ ] `catalog_product_categories`: relação produto×categoria.
- [ ] `catalog_inventory_items`: `store_id`, `product_id`, `variant_id`, `quantity`.
- [ ] `catalog_collections`: vitrines/coleções (usado no destaque da home).

### Rotas/serviço (`/api/v1/stores/{store_id}/...`, `require_permission`)
- [ ] Produtos: listar (paginado), criar, atualizar, arquivar, publicar/despublicar. Doc [09](../09_merchant_dashboard.md)/[20](../20_api_contracts_todo.md).
- [ ] Categorias, variações, estoque, imagens.
- [ ] Marcar produto como personalizável + vincular modelo 3D (consome `product_customization`).
- [ ] Índices do doc [07](../07_database_strategy.md): `store_id+slug` único, `store_id+status`, `store_id+created_at`, variantes/imagens/estoque conforme listado.

---

## Etapa 5 — Módulo `media` + S3/CDN

### Modelo
- [ ] `media_files`: `store_id`, `owner_type`, `owner_id`, `key` (S3), `url`, `variants` (json: thumbnail/card/product/zoom), `content_type`, `size`, timestamps. Índices `store_id+id`, `store_id+owner_type+owner_id`. Doc [07](../07_database_strategy.md)/[13](../13_performance_cache_and_cdn.md).

### Pipeline de upload (doc [13](../13_performance_cache_and_cdn.md)/[14](../14_security_strategy.md))
- [ ] Validar tipo/extensão/MIME/tamanho no backend.
- [ ] Enviar **original** ao S3 (nunca salvar binário no banco; nunca servir imagem pelo backend).
- [ ] Worker gera versões otimizadas (`thumbnail`, `card`, `product`, `zoom`) → S3.
- [ ] Servir por CloudFront/CDN.
- [ ] Config S3/CDN em `config.py` (`S3_BUCKET`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL`); cliente **boto3** em `app/core/storage.py`.
- [ ] **Setup AWS de dev:** criar **bucket S3 de dev** + **distribuição CloudFront** + usuário/credenciais **IAM** com acesso mínimo. Usado **inclusive a partir do dev local**.
- [ ] URLs assinadas para arquivos privados (artes de cliente). Doc [14](../14_security_strategy.md).

**Reconciliação:** usar **AWS S3 + CloudFront reais** desde o dev local (sem MinIO/stand-ins), conforme decisão do projeto e doc [12](../12_aws_infrastructure_and_deployment.md). Implementação normal via boto3. Registrar a escolha do worker (Fase 0).

---

## Etapa 6 — Módulo `product_customization` (3D)

### Modelos globais (biblioteca da Loja Club — sem `store_id`)
- [ ] `customization_3d_models`: catálogo global (caneca, squeeze, camisa...), categoria, status publicado. Doc [22](../22_product_customization_3d.md)/[07](../07_database_strategy.md).
- [ ] `customization_3d_model_versions`: arquivos (GLB), parâmetros, áreas personalizáveis, limites (área imprimível, tipos/aceitos, tamanho máx). Doc [22](../22_product_customization_3d.md).

### Modelos por loja/produto (com `store_id`)
- [ ] `customization_product_settings`: `store_id`, `product_id` (único), `model_id`, permite cor?, observações de produção. Doc [09](../09_merchant_dashboard.md)/[22](../22_product_customization_3d.md).
- [ ] `customization_sessions`: campos exatos do doc [07](../07_database_strategy.md): `store_id`, `product_id`, `guest_session_id`, `customer_id`, `cart_id`, `model_id`, `model_version_id`, `status`, `state_json`, `preview_url`, `approved_snapshot_url`, `expires_at`, `approved_at`. Status `draft|approved|added_to_cart|ordered|abandoned|expired` (doc [22](../22_product_customization_3d.md)).
- [ ] `customization_uploads`: arquivos enviados pelo cliente, por sessão, privados. Doc [14](../14_security_strategy.md).
- [ ] `customization_cart_items` / `customization_order_items`: criados quando consumidos (Fase 4 — carrinho/checkout), mas **definir o modelo aqui**. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] Listar modelos 3D disponíveis; obter config de personalização do produto.
- [ ] Iniciar sessão; obter sessão; atualizar `state_json` (autosave); upload de arte (validado, privado, URL assinada); registrar preview; **aprovar** (congela snapshot + versão do modelo + data).
- [ ] Listar sessões da loja (visão do lojista); expirar sessões abandonadas (30 dias → `expired`, soft delete). Doc [22](../22_product_customization_3d.md)/[23](../23_customer_identity_and_guest_checkout.md).
- [ ] Índices do doc [07](../07_database_strategy.md): `store_id+product_id+status`, `store_id+guest_session_id+status`, `store_id+customer_id+status`, `expires_at+status`, etc.
- [ ] Enum de status de arte/produção (`received|reviewing|needs_contact|approved_for_production|in_production|production_done`) — usado em pedidos (Fase 4). Doc [22](../22_product_customization_3d.md).

### Conteúdo (não é código)
- [ ] Produzir/otimizar os GLB iniciais (caneca, squeeze, camisa) com áreas imprimíveis — responsabilidade da Loja Club. Doc [22](../22_product_customization_3d.md)/[13](../13_performance_cache_and_cdn.md). (Seed mínimo via migration/admin enquanto o frontend-admin não existe.)

---

## Etapa 5/6 — Frontend (painel)
- [ ] Tela de **Produtos**: listar/criar/editar/arquivar, publicar, imagens, variações, estoque, categoria, slug, destaque. Doc [09](../09_merchant_dashboard.md).
- [ ] Em produto compatível: habilitar personalização + escolher modelo 3D + observações de produção + preview básico. Doc [09](../09_merchant_dashboard.md)/[22](../22_product_customization_3d.md).
- [ ] Componente de upload de imagem (estado de processamento). Doc [21](../21_design_system_todo.md).

---

## Etapa 5/6 — Testes (doc [16](../16_testing_strategy.md))
- [ ] Criar/publicar/despublicar produto; alterar estoque; slug único por loja; mesmo slug em lojas diferentes.
- [ ] Upload valida tipo/tamanho.
- [ ] Produto simples não exige personalização; `customizable_3d` exige sessão aprovada para ir ao checkout (regra exercida na Fase 4).
- [ ] Cliente inicia sessão; `state_json` é salvo; upload valida tipo/tamanho; preview/snapshot registrado; lojista só vê sessões da própria loja.

---

## Reconciliações (registrar aqui)
- (preencher conforme surgirem)
