# Fase 5 — Produtos 3D (lojista gera via API)

> Objetivo: a loja passa a vender **produtos 3D** e **3D personalizáveis**. O **lojista gera o próprio modelo 3D (GLB) via API de terceiros** a partir de uma imagem/descrição; o cliente personaliza no storefront (editor 3D), aprova, e a personalização é **congelada no pedido**. Construída sobre as Fases 2 (catálogo), 3 (storefront) e 4 (checkout).

Docs de referência: [22](../22_product_customization_3d.md), [07](../07_database_strategy.md), [13](../13_performance_cache_and_cdn.md), [14](../14_security_strategy.md), [18](../18_open_decisions.md), [10](../10_storefront_and_layouts.md), [09](../09_merchant_dashboard.md), [16](../16_testing_strategy.md).

> Os modelos 3D são gerados pelo **lojista**, via **API de terceiros** (image/text → GLB) — candidatos **Meshy / Tripo3D / Hyper3D** (decisão no doc [18](../18_open_decisions.md)). Não há catálogo 3D da plataforma; os modelos são **por loja** (`store_id`).

## Definition of Done da fase

- Produto pode ser **`image`**, **`image_3d`** ou **`image_3d_customizable`** (campo `type` no `catalog_products`).
- O lojista **gera um modelo 3D via API** a partir de uma imagem/descrição; o GLB fica no storage da loja (S3/CloudFront) e é vinculado ao produto.
- Cliente personaliza no **editor 3D do storefront** (Three.js): arte, cor, texto, posição/escala/rotação, preview, autosave e **aprovação** antes do carrinho.
- Personalização aprovada é **congelada no pedido** (cópia própria; não depende da sessão viva).
- Lojista vê as sessões/arte da própria loja e atualiza o **status de arte/produção**.
- Testes: isolamento (sessão só da loja), arte **privada** (URL assinada), congelamento no pedido.

## Etapas

### 5.1 — Geração de modelo 3D via API (integração)
- [ ] Abstração fina do provedor de geração 3D (`app/core/...` ou módulo `product_customization`): submeter imagem/descrição → obter GLB; tratar fila/assíncrono (geração leva tempo) via worker. Doc [18](../18_open_decisions.md)/[22](../22_product_customization_3d.md).
- [ ] Persistir o GLB no storage **por loja** (S3) e servir por CDN. Reaproveita `app/core/storage.py` (Fase 2).
- [ ] Decisão fechada do provedor (Meshy/Tripo3D/Hyper3D) registrada no doc [18](../18_open_decisions.md).

### 5.2 — Catálogo: tipo de produto 3D
- [ ] Adicionar `type` (`image|image_3d|image_3d_customizable`) ao `catalog_products` (migration). Doc [07](../07_database_strategy.md)/[22](../22_product_customization_3d.md).
- [ ] Vincular produto ao modelo 3D gerado (config por produto).

### 5.3 — Modelos por loja + versões + config
- [ ] `customization_3d_models` (por loja), `customization_3d_model_versions` (GLB, parâmetros, áreas, limites), `customization_product_settings` (permite cor?, observações de produção). Doc [07](../07_database_strategy.md).

### 5.4 — Sessões de personalização (backend)
- [ ] `customization_sessions` (campos do doc [07](../07_database_strategy.md)) + `customization_uploads` (arte privada). Status `draft|approved|added_to_cart|ordered|abandoned|expired`.
- [ ] Rotas: iniciar/obter sessão; **autosave** do `state_json`; upload de arte (validado, privado, URL assinada); preview; **aprovar** (congela snapshot + versão + data). Expirar 30 dias → `expired` (worker).
- [ ] Enum de status de arte/produção (`received…production_done`).

### 5.5 — Editor 3D no storefront (Three.js)
- [ ] Carregar o GLB do modelo+versão **do lojista** (CDN); upload de arte; texto/cor/posição/escala/rotação dentro da área imprimível; preview; **autosave**; **aprovação** obrigatória antes do carrinho; restaurar pela `guest_session_id`. Doc [10](../10_storefront_and_layouts.md)/[22](../22_product_customization_3d.md).

### 5.6 — Carrinho/pedido: congelar personalização
- [ ] `customization_cart_items` / `customization_order_items` — cópia congelada da personalização aprovada no pedido (INV-P5). Regra: item `image_3d_customizable` só entra com sessão `approved`. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).

### 5.7 — Painel do lojista
- [ ] Habilitar personalização no produto + **gerar o modelo via API** + observações de produção + preview.
- [ ] Ver sessões/arte da loja (polling), baixar arquivos (URL assinada), atualizar status de arte/produção. Doc [09](../09_merchant_dashboard.md).

## Reconciliações (registrar aqui)
- **Modelos gerados pelo lojista via API**, por loja — **não** há biblioteca da plataforma. Ver doc [22](../22_product_customization_3d.md).
- **Decisão do provedor de geração 3D** (Meshy/Tripo3D/Hyper3D) fica no doc [18](../18_open_decisions.md) — fechar ao iniciar esta fase.
- **Restringir a personalização a plano pago** é da **Fase 6** (planos/pagamentos); aqui a geração/personalização é livre. O gancho de plano já existe em `require_permission` (Fase 1).
